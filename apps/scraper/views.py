from django.contrib.auth.decorators import login_required
from .models import *
from django.shortcuts import render, redirect
from .forms import ScrapingProcessForm
from apps.scraper.libs.printables import PrintablesProductScrap
from apps.scraper.libs.stlflix import StlflixProductScrap
from django.shortcuts import render, get_object_or_404
from django.contrib import messages
from django.shortcuts import get_object_or_404, render
from django.contrib.auth.decorators import login_required
import os, time
from django.http import JsonResponse


# Create your views here.
@login_required
def all_products(request):
    context = {
        'products': Product.objects.all(),
        'page': 'products'
    }
    return render(request, "volt/product.html", context)

@login_required
def delete_product(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    product.delete()
    messages.success(request, "Product has been deleted successfully.")
    return redirect('scraper:products')

@login_required
def approve_product(request, product_id):
    # Get the product by ID or return a 404 if not found
    product = get_object_or_404(Product, id=product_id)
    
    # Change the product status to approved
    product.status = 'approved'
    product.save()

    # Display a success message
    messages.success(request, f'Product "{product.title}" has been approved.')
    
    return redirect('scraper:product_detail', product_id=product.id)
    # Redirect to the product list or some other page
    return redirect('scraper:products')  # Adjust URL name accordingly


@login_required
def approve_product_via_ajax(request, product_id):
    if request.method == 'POST':
        # Get the product by ID or return a 404 if not found
        product = get_object_or_404(Product, id=product_id)
        
        # Change the product status to approved
        product.status = 'approved'
        product.save()
        time.sleep(2)
        # Return JSON response for successful approval
        return JsonResponse({'success': True, 'message': f'Product "{product.title}" has been approved.'})
    
    # If not a POST request, return a 405 Method Not Allowed
    return JsonResponse({'success': False, 'message': 'Invalid request method.'}, status=405)


@login_required
def decline_product(request, product_id):
    # Get the product by ID or return a 404 if not found
    product = get_object_or_404(Product, id=product_id)
    
    # Change the product status to declined
    product.status = 'declined'
    product.save()

    # Display a success message
    messages.success(request, f'Product "{product.title}" has been declined.')
    return redirect('scraper:product_detail', product_id=product.id)
    
    # Redirect to the product list or some other page
    return redirect('scraper:products')  # Adjust URL name accordingly




@login_required
def view_screenshot(request, product_id):
    # Retrieve the product by its ID, or return 404 if not found
    product = get_object_or_404(Product, id=product_id)
    
    # Initialize variables
    screenshot_url = None
    is_pdf = False
    is_image = False
    
    # Check if the product has a screenshot, and determine the type (image or PDF)
    if product.page_screenshot:
        if product.page_screenshot.image:
            screenshot_url = product.page_screenshot.image.url
        elif product.page_screenshot.url:
            screenshot_url = product.page_screenshot.url
        
        # Determine the file type based on the extension
        if screenshot_url:
            file_extension = os.path.splitext(screenshot_url)[1].lower()
            if file_extension == '.pdf':
                is_pdf = True
            elif file_extension in ['.jpg', '.jpeg', '.png']:
                is_image = True
    
    # Pass the product, screenshot URL, and file type to the template
    context = {
        'product': product,
        'screenshot_url': screenshot_url,
        'is_pdf': is_pdf,
        'is_image': is_image,
        'page': 'products'

    }
    
    return render(request, 'volt/view_screenshot.html', context)


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
                    pdf_file_path = product.get('pdfFilePath')
                    if pdf_file_path:
                        pdf_file_path_url = printables_scraper.get_media_url(pdf_file_path)
                        internal_page_screenshot = PageScreenshot.objects.create(url=pdf_file_path_url)
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

        if website.script_name == "stlflix.py":
            stlflix_scraper = StlflixProductScrap(
                scraping_process.search_query,
                scraping_process.max_records
            )
            stlflix_scraper.get_products()
            stlflix_products = stlflix_scraper.to_model_data()
            
            for product in stlflix_products:
                # Create Product instance
                internal_product = Product(
                    scraped_by=scraping_process,
                    sku=product.get('sku'),
                    title=product.get('title'),
                    description=product.get('description') or "No description available",
                    category=product.get('category'),
                    is_commercial_allowed=product.get('is_commercial_allowed'),
                    source_website=website
                )

                # If there's a thumbnail, associate it with the product
                if product.get('thumbnail_url'):
                    internal_product.thumbnail = ThumbnailImage.objects.create(url=product.get('thumbnail_url'))

                # Save the product
                internal_product.save()

                # Now handle the gallery images
                for gallery_image_url in product.get('images'):
                    Image.objects.create(
                        product=internal_product,
                        image_url=gallery_image_url
                    )




            

@login_required
def initiate_process(request):
    if request.method == 'POST':
        form = ScrapingProcessForm(request.POST)
        if form.is_valid():
            scraping_process = form.save(commit=False)
            scraping_process.started_by = request.user  # Set the current user as 'started_by'
            scraping_process.status = 'pending'  # Set initial status
            scraping_process.save()
            form.save_m2m()  # Save the many-to-many data (source_websites, criterias)

            # Fetching products
            try:
                fetch_products(scraping_process)
                scraping_process.status = "completed"
                scraping_process.save()
                messages.success(request, "Scraping process has been initiated successfully.")
            except Exception as e:
                scraping_process.status = "failed"
                scraping_process.save()
                messages.error(request, str(e))
                raise Exception(e)

            return redirect('scraper:products')  # Redirect to a page, for example, a list of scraping processes
    else:
        form = ScrapingProcessForm()

    context = {
        'form': form,
        'page': 'initiate-process'

    }
    return render(request, "volt/initiate_process.html", context)




def product_detail(request, product_id):
    # Fetch the product by ID
    product = get_object_or_404(Product, id=product_id)
    # ai_details = product.generate_ai_details()
    context = {
        'product': product,
        'page': 'products'
    }
    # Render the product detail page
    return render(request, 'volt/product_detail.html', context)

@login_required
def processes_list(request):
    context = {
        'page': 'processes',
        'processes': ScrapingProcess.objects.all().order_by('-id')
    }
    return render(request, "volt/process_monitoring.html", context)