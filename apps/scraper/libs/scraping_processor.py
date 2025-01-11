import logging
from apps.scraper.libs.printables import PrintablesProductScrap
from apps.scraper.libs.makerworld import MakerWorldProductScrap
from apps.scraper.libs.stlflix import StlflixProductScrap
from apps.scraper.models import *
import time
import requests
from django.core.files.base import ContentFile
from django.core.files.temp import NamedTemporaryFile

logger = logging.getLogger('scraper')



class ProductScraperProcessor:
    def __init__(self, scraping_process):
        self.scraping_process = scraping_process
        self.total_websites = self.scraping_process.source_websites.all().count()
        self.total_products = self.total_websites * self.scraping_process.max_records
        self.total_progress = 0
        

    def get_percent(self):
        return f'{int(self.total_progress/self.total_products * 100)}'

    def process_product(self, product_data, website):
        """
        Process and save a single product.
        """
        try:
            logger.info(f"Processing product with SKU: {product_data['sku']}")

            # Check if the product already exists
            existing_product = Product.objects.filter(sku=product_data['sku']).first()
            if existing_product:
                logger.warning(f"Product with SKU {product_data['sku']} already exists. Skipping.")
                return

            # Create License object if license data is present
            internal_license = None
            if product_data.get('license'):
                internal_license = License.objects.create(json=product_data['license'])
                logger.info(f"License created for product {product_data['sku']}")

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
                logger.info(f"Thumbnail created for product {product_data['sku']}")

            # Process the preview file (Page Screenshot)
            if product_data.get('pdf_file_url'):
                try:
                    # Download the file
                    response = requests.get(product_data['pdf_file_url'], stream=True)
                    response.raise_for_status()  # Raise an error for bad status codes

                    # Get the filename from the URL or fallback to a default
                    filename = product_data['pdf_file_url'].split("/")[-1] or "screenshot.pdf"

                    # Read the file content
                    file_content = response.content

                    # Create a PageScreenshot instance with the file
                    internal_page_screenshot = PageScreenshot.objects.create(
                        file=ContentFile(file_content, name=filename)
                    )
                    internal_product.page_screenshot = internal_page_screenshot

                    logger.info(f"Page screenshot saved locally for product {product_data['sku']}")

                except requests.RequestException as e:
                    logger.error(f"Error downloading file: {e}")
                except Exception as e:
                    logger.error(f"Error saving screenshot for product {product_data['sku']}: {e}")

            # Save the product
            internal_product.save()
            logger.info(f"Product {internal_product.title} saved successfully.")

            # Now handle the gallery images
            for gallery_image_url in product_data.get('images', []):
                Image.objects.create(
                    product=internal_product,
                    image_url=gallery_image_url
                )
            logger.info(f"Gallery images saved for product {product_data['sku']}")

        except Exception as e:
            logger.error(f"Error processing product {product_data.get('sku')}: {e}")
            raise

    def fetch_and_process(self, scraper_class, website):
        """
        Fetch and process products using a specific scraper class.
        """
        logger.info(f"Starting scraping for website: {website.name}")
        scraper = scraper_class(
            query=self.scraping_process.search_query,
            limit=self.scraping_process.max_records
        )

        try:
            scraper.get_products()
            logger.info(f"Scraping completed for website: {website.name}")

            structured_products = scraper.to_model_data()
            logger.info(f"Total {len(structured_products)} products fetched from {website.name}")

            for product_data in structured_products:
                self.process_product(product_data, website)

        except Exception as e:
            logger.error(f"Error during scraping for website {website.name}: {e}")
            raise

    def get_output(self, status, message):
        return {
            "status": status,
            "progress": self.total_progress,
            "total": self.total_products,
            "in_percent": self.get_percent(),
            "message": message
        }

    def fetch_and_process_sse(self, scraper_class, website):
        """
        Fetch and process products using a specific scraper class, with progress updates for SSE.
        """
        scraper = scraper_class(
            query=self.scraping_process.search_query,
            limit=self.scraping_process.max_records
        )

        yield self.get_output("progress", f"Scraping for {website.name}")

        try:
            scraper.get_products()
            structured_products = scraper.to_model_data()

            yield self.get_output("progress", f"Scraped from {website.name}, Recording in database.")


            for idx, product_data in enumerate(structured_products, start=1):
                self.total_progress += 1
                try:
                    self.process_product(product_data, website)
                    time.sleep(0.5)                   
                    yield self.get_output(
                        "progress", 
                        f"{self.total_progress}/{self.total_products} products processed.")

                except Exception as e:
                    yield self.get_output("error", f'Error processing product {product_data.get("sku")}. Skipping...')
                    continue

        except Exception as e:
            yield self.get_output("error", f"Error during scraping for {website.name}: {str(e)}")


    def run_with_streaming(self):
        """
        Run the scraping and processing workflow for all websites with streaming updates.
        """
        for website in self.scraping_process.source_websites.all():
            scraper_mapping = {
                "printables.py": PrintablesProductScrap,
                "stlflix.py": StlflixProductScrap,
                "makerworld.py": MakerWorldProductScrap,
            }

            scraper_class = scraper_mapping.get(website.script_name)
            if not scraper_class:
                self.get_output("error", f"No scraper found for {website.script_name}. Skipping {website.name}.")
                continue

            yield from self.fetch_and_process_sse(scraper_class, website)

        yield self.get_output("completed", "Scraping process completed for all websites.")


    def run(self):
        """
        Run the scraping and processing workflow for all websites.
        """
        logger.info(f"Starting scraping process {self.scraping_process.id}")
        for website in self.scraping_process.source_websites.all():
            logger.info(f"Processing website: {website.name}")

            scraper_mapping = {
                "printables.py": PrintablesProductScrap,
                "stlflix.py": StlflixProductScrap,
                "makerworld.py": MakerWorldProductScrap,
            }

            scraper_class = scraper_mapping.get(website.script_name)
            if not scraper_class:
                logger.warning(f"No scraper found for {website.script_name}. Skipping website {website.name}.")
                continue

            try:
                self.fetch_and_process(scraper_class, website)
            except Exception as e:
                logger.error(f"Failed to process website {website.name}: {e}")
                continue

        logger.info(f"Scraping process {self.scraping_process.id} completed.")
