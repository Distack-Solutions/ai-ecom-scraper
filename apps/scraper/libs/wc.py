import os, json
from woocommerce import API
# from django.conf import settings


class WooCommerceManager:
    def __init__(self):
        """
        Initialize WooCommerceManager with credentials from settings.py.
        This class handles connection setup, single product creation, bulk product uploads, and fetching product details.
        """
        # self.store_url = settings.WOOCOMMERCE_URL
        # self.consumer_key = settings.WOOCOMMERCE_CONSUMER_KEY
        # self.consumer_secret = settings.WOOCOMMERCE_CONSUMER_SECRET
        self.store_url = "https://theproductpit.com"
        self.consumer_key = "ck_12132560102604c5912db08390704658fe1957bb"
        self.consumer_secret = "cs_3d54b11d665680064e424c79a6228fec65399942"

        self.client = None
        self._setup_connection()

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
        print(product_data)
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