import os, json
from woocommerce import API
from django.core.cache import cache
from django.conf import settings

WC_CONFIG_FILE = os.path.join(settings.BASE_DIR, "wc_config.json")

class WooCommerceManager:
    def __init__(self):
        """
        Initialize WooCommerceManager with credentials from wc_config.json.
        This class handles connection setup, single product creation, bulk product uploads, and fetching product details.
        """
        self.store_url = None
        self.consumer_key = None
        self.consumer_secret = None

        self.client = None
        self._load_config()
        self._setup_connection()

    def _load_config(self):
        """
        Load WooCommerce configuration from cache or wc_config.json.
        """
        store_url = cache.get('store_url')
        consumer_key = cache.get('consumer_key')
        consumer_secret = cache.get('consumer_secret')

        # If any parameter is missing in the cache, read from the wc_config.json file
        if not store_url or not consumer_key or not consumer_secret:
            print("Reading from file.")
            if not os.path.exists(WC_CONFIG_FILE):
                raise FileNotFoundError(f"Configuration file {WC_CONFIG_FILE} not found.")

            with open(WC_CONFIG_FILE, "r") as file:
                try:
                    config = json.load(file)
                    store_url = config.get('store_url', '')
                    consumer_key = config.get('consumer_key', '')
                    consumer_secret = config.get('consumer_secret', '')

                    # Cache the individual values
                    cache.set('store_url', store_url, timeout=None)  # Cache indefinitely
                    cache.set('consumer_key', consumer_key, timeout=None)  # Cache indefinitely
                    cache.set('consumer_secret', consumer_secret, timeout=None)  # Cache indefinitely
                except Exception as e:
                    raise ValueError(f"Error reading configuration file: {e}")
        else:
            print("Reading from cache.")

        # Set the instance variables
        self.store_url = store_url
        self.consumer_key = consumer_key
        self.consumer_secret = consumer_secret

        # Validate the loaded configuration
        if not self.store_url or not self.consumer_key or not self.consumer_secret:
            raise ValueError("One or more WooCommerce credentials are missing in the configuration file or cache.")


    def _setup_connection(self):
        """Sets up the WooCommerce API client connection."""
        self.client = API(
            url=self.store_url,  # Your WooCommerce store URL
            consumer_key=self.consumer_key,
            consumer_secret=self.consumer_secret,
            wp_api=True,
            version="wc/v3",  # WooCommerce API version
            timeout=30
        )

    def get_client(self):
        """Get the WooCommerce API client."""
        if not self.client:
            self._setup_connection()
        return self.client

    def create_product(self, product_data):
        """Create a new product in WooCommerce."""
        wcapi = self.get_client()
        response = wcapi.post("products", product_data)
        if response.status_code == 201:
            return response.json()  # Successfully created product
        else:
            raise Exception(f"Error creating product: {response.text}")

    def create_bulk_products(self, products_data):
        """Create multiple products at once in WooCommerce."""
        wcapi = self.get_client()
        response = wcapi.post("products/batch", {"create": products_data})

        if response.status_code == 200:
            return response.json()  # Successfully bulk uploaded products
        else:
            raise Exception(f"Error uploading products: {response.text}")

    def get_products(self, params=None):
        """Get product details from WooCommerce."""
        wcapi = self.get_client()
        response = wcapi.get("products", params=params)

        if response.status_code == 200:
            return response.json()  # Successfully fetched products
        else:
            raise Exception(f"Error fetching products: {response.text}")

    def create_single_product_data(self, ai_version, exclude_images=False):
        """Prepare data to upload product with AI-generated details."""
        # Collect product data
        product_data = {
            "name": ai_version.title,
            "type": "simple",
            "regular_price": "0",  # Set this to 0 for testing (draft status)
            "description": ai_version.expanded_description,  # Use the AI-generated expanded description
            "short_description": ai_version.short_description,  # Use the AI-generated short description
            "categories": [{"id": 9}],  # Example category ID (adjust as needed)
            "status": "draft"  # Set to 'draft' for testing
        }
        if not exclude_images:
            product_data['images'] = ai_version.get_images()

        return product_data

    def create_bulk_product_data(self, ai_version_list):
        bulk_product_data = []
        for ai_version in ai_version_list:
            single_product_data = self.create_single_product_data(ai_version)
            bulk_product_data.append(single_product_data)
        return bulk_product_data

    def upload_product(self, product_ai_version, exclude_images=False):
        """Handle the uploading of a single product."""
        try:
            wc_product = self.create_single_product_data(product_ai_version, exclude_images)
            response = self.create_product(wc_product)
            return response  # Return the product response
        except Exception as e:
            raise Exception(f"Failed to upload product: {str(e)}")

    def upload_bulk_products(self, products_ai_version):
        """Handle the uploading of multiple products."""
        try:
            wc_products = self.create_bulk_product_data(products_ai_version)
            response = self.create_bulk_products(wc_products)
            return response  # Return the bulk upload response
        except Exception as e:
            raise Exception(f"Failed to upload bulk products: {str(e)}")



if __name__ == "__main__":
    wc_manager = WooCommerceManager()
    product = {
        'name': 'Noise-Reducing 3D Printed Chair Stoppers for Garden Chairs', 
        'type': 'simple', 
        'regular_price': '0', 
        'description': 'Enhance your garden chairs with our 3D printed noise-reducing chair stoppers, designed specifically for use on ceramic floors. Crafted from high-quality SUNLU TPU material, the chair stoppers have a Shore hardness of 95A, ensuring a durable and flexible fit. With a full inner diameter of 24.20 mm, these stoppers are perfect for replacing worn-out plugs on your chairs. The 0.30 mm layer height allows for precision printing and a smooth surface finish, ensuring your chairs glide silently, even during nighttime movements. Feel free to modify the design to suit your specific needs. Say goodbye to annoying squeaks and protect your flooring with this essential accessory for outdoor furniture.', 
        'short_description': '3D printed chair stoppers designed for ceramic floors, reducing noise while protecting your furniture.', 
        'categories': [{'id': 9}], 
        'images': [
            {
                'name': 'Chair stoppers legs - Gallery image 1', 
                'src': 'https://media.printables.com/media/prints/577049/images/4610435_04f787e0-1ebb-4fc9-a2ca-7a29fdd66343/2023-09-09_00-40-30_178.jpg'
            }
        ], 
        'status': 'draft'
    }


    response = wc_manager.create_product(product)
    print(response)