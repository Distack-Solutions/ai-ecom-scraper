from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import ScrapingProcess, Product, License, PageScreenshot, ThumbnailImage, Image
from django.utils import timezone
from libs.printables import PrintablesProductScrap

@receiver(post_save, sender=ScrapingProcess)
def process_scraped_products(sender, instance, created, **kwargs):
    """
    This signal is triggered when a ScrapingProcess is saved.
    If the status is changed to 'completed', it will trigger product fetching logic.
    """
    # Check if the process was not just created and is marked as 'completed'
    if instance.status == 'pending':
        # Get the current time (when the scraping completed)
        completion_time = timezone.now()

        # Example: Fetch or process products related to the ScrapingProcess
        print(f"Scraping Process {instance.id} completed at {completion_time}.")

        # Placeholder logic for fetching products
        # You might want to add your scraping function here
        fetch_products(instance)

        print(f"Products processed for ScrapingProcess {instance.id}.")


def fetch_products(scraping_process):
    """
    Fetch products based on the scraping process.
    This is just an example function, replace it with actual scraping logic.
    """
    for website in scraping_process.source_websites.all():
        print(f"Fetching products from {website.name} for ScrapingProcess {scraping_process.id}")
        
        if website.script_name == "printables.py":
            printables_scraper = PrintablesProductScrap(
                scraping_process.search_query,
                scraping_process.max_records
            )
            printables_scraper.get_products()

            printables_products = printables_scraper.results

            for product in printables_products:
                try:
                    # Check if the product already exists
                    existing_product = Product.objects.filter(sku=product.get('id')).first()
                    if existing_product:
                        print(f"Product with SKU {product.get('id')} already exists. Skipping.")
                        continue
                    
                    # Get thumbnail and gallery images
                    thumbnail = printables_scraper.get_thumnail(product)
                    gallery_images = printables_scraper.get_gallery_images(product)

                    # Create License object if license data is present
                    license_data = product.get('license')
                    internal_license = None
                    if license_data:
                        internal_license = License.objects.create(
                            json=license_data
                        )

                    # Create Product instance
                    internal_product = Product(
                        scraped_by=scraping_process,
                        sku=product.get('id'),
                        title=product.get('name'),
                        description=product.get('description') or "No description available",
                        category=product.get('category').get('name') if product.get('category') else None,
                        source_website=website,
                        license=internal_license,
                    )

                    # If there's a thumbnail, associate it with the product
                    if thumbnail:
                        internal_product.thumbnail = ThumbnailImage.objects.create(url=thumbnail)

                    # Process the preview file (Page Screenshot)
                    preview_file_object = product.get('previewFile')
                    if preview_file_object:
                        preview_file_path = preview_file_object.get('filePreviewPath')
                        if preview_file_path:
                            preview_file_url = printables_scraper.get_media_url(preview_file_path)
                            internal_page_screenshot = PageScreenshot.objects.create(url=preview_file_url)
                            internal_product.page_screenshot = internal_page_screenshot

                    # Save the product
                    internal_product.save()

                    # Now handle the gallery images
                    for gallery_image_url in gallery_images:
                        Image.objects.create(
                            product=internal_product,
                            image_url=gallery_image_url
                        )

                    print(f"Product {internal_product.title} saved successfully.")

                except Exception as e:
                    # Handle any errors that occur during the product processing
                    print(f"Error processing product {product.get('id')}: {e}")
                    continue
