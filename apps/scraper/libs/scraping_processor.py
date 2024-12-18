from apps.scraper.libs.printables import PrintablesProductScrap
from apps.scraper.libs.makerworld import MakerWorldProductScrap
from apps.scraper.libs.stlflix import StlflixProductScrap
from apps.scraper.models import *

class ProductScraperProcessor:
    def __init__(self, scraping_process):
        self.scraping_process = scraping_process

    def process_product(self, product_data, website):
        """
        Process and save a single product.
        """
        try:
            # Check if the product already exists
            existing_product = Product.objects.filter(sku=product_data['sku']).first()
            if existing_product:
                print(f"Product with SKU {product_data['sku']} already exists. Skipping.")
                return

            # Create License object if license data is present
            internal_license = None
            if product_data.get('license'):
                internal_license = License.objects.create(json=product_data['license'])

            # Create Product instance
            internal_product = Product(
                scraped_by=self.scraping_process,
                sku=product_data['sku'],
                title=product_data['title'],
                description=product_data['description'],
                category=product_data['category'],
                source_website=website,
                license=internal_license,
                is_commercial_allowed=product_data.get('is_commercial_allowed', False),
            )

            # If there's a thumbnail, associate it with the product
            if product_data.get('thumbnail_url'):
                internal_product.thumbnail = ThumbnailImage.objects.create(
                    url=product_data['thumbnail_url']
                )

            # Process the preview file (Page Screenshot)
            if product_data.get('pdf_file_url'):
                internal_page_screenshot = PageScreenshot.objects.create(
                    url=product_data['pdf_file_url']
                )
                internal_product.page_screenshot = internal_page_screenshot

            # Save the product
            internal_product.save()

            # Now handle the gallery images
            for gallery_image_url in product_data.get('images', []):
                Image.objects.create(
                    product=internal_product,
                    image_url=gallery_image_url
                )

            print(f"Product {internal_product.title} saved successfully.")

        except Exception as e:
            print(f"Error processing product {product_data.get('sku')}: {e}")

    def fetch_and_process(self, scraper_class, website):
        """
        Fetch and process products using a specific scraper class.
        """
        scraper = scraper_class(
            query=self.scraping_process.search_query,
            limit=self.scraping_process.max_records
        )
        scraper.get_products()
        structured_products = scraper.to_model_data()

        for product_data in structured_products:
            self.process_product(product_data, website)

    def run(self):
        """
        Run the scraping and processing workflow for all websites.
        """
        for website in self.scraping_process.source_websites.all():
            print(f"Fetching products from {website.name} for ScrapingProcess {self.scraping_process.id}")

            scraper_mapping = {
                "printables.py": PrintablesProductScrap,
                "stlflix.py": StlflixProductScrap,
                "makerworld.py": MakerWorldProductScrap,
            }

            scraper_class = scraper_mapping.get(website.script_name)
            if not scraper_class:
                print(f"No scraper found for {website.script_name}. Skipping.")
                continue

            self.fetch_and_process(scraper_class, website)
            
