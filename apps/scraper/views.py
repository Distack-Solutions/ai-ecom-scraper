from pathlib import Path
from django.contrib.auth.decorators import login_required
from .models import *
from django.shortcuts import render, redirect
from .forms import ScrapingProcessForm
from apps.scraper.libs.printables import PrintablesProductScrap
from apps.scraper.libs.stlflix import StlflixProductScrap
from apps.scraper.libs.makerworld import MakerWorldProductScrap
from apps.scraper.libs.scraping_processor import ProductScraperProcessor
from django.shortcuts import render, get_object_or_404
from django.contrib import messages
from django.shortcuts import get_object_or_404, render
from django.contrib.auth.decorators import login_required
import os, time
from django.http import JsonResponse

from django.views.decorators.csrf import csrf_exempt
from apps.scraper.libs.wc import WooCommerceManager

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import Product
from django.http import StreamingHttpResponse
from time import sleep
import json
# Create your views here.
from django.core.paginator import Paginator
from django.shortcuts import render
from django.http import StreamingHttpResponse
from django.contrib import messages
from django.db.models import Q
from django.conf import settings
from datetime import datetime

def makerworld(request):
    scraper = MakerWorldProductScrap(query="apple", limit=10)
    scraper.get_products()
    structured_data = scraper.to_model_data()
    return JsonResponse(structured_data, safe=False)


@login_required
def all_products(request):
    # Retrieve query parameters
    search_query = request.GET.get('search', '')
    status_filter = request.GET.get('status', '')
    per_page = int(request.GET.get('per_page', 10))  # Default to 10 products per page

    # Start with all products
    products = Product.objects.all().order_by('-created_at')

    # Apply search filter
    if search_query:
        products = products.filter(title__icontains=search_query)

    # Apply status filter
    if status_filter and status_filter != 'all':
        products = products.filter(status=status_filter)

    # Implement pagination
    paginator = Paginator(products, per_page)  # Show per_page products per page
    page_number = request.GET.get('page')  # Get the page number from the request
    page_obj = paginator.get_page(page_number)  # Get the relevant page

    context = {
        'products': page_obj,  # Pass the paginated products
        'search_query': search_query,
        'status_filter': status_filter,
        'per_page': per_page,  # Pass per_page for UI controls
        'page': 'products',
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
        if product.page_screenshot.file:
            screenshot_url = product.page_screenshot.file.url
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
            structured_products = printables_scraper.to_model_data()

            for product in structured_products:
                try:
                    # Check if the product already exists
                    existing_product = Product.objects.filter(sku=product['sku']).first()
                    if existing_product:
                        print(f"Product with SKU {product['sku']} already exists. Skipping.")
                        continue

                    # Create License object if license data is present
                    internal_license = None
                    if product['license']:
                        internal_license = License.objects.create(
                            json=product['license']
                        )

                    # Create Product instance
                    internal_product = Product(
                        scraped_by=scraping_process,
                        sku=product['sku'],
                        title=product['title'],
                        description=product['description'],
                        category=product['category'],
                        source_website=website,
                        license=internal_license,
                    )

                    # If there's a thumbnail, associate it with the product
                    if product['thumbnail_url']:
                        internal_product.thumbnail = ThumbnailImage.objects.create(url=product['thumbnail_url'])

                    # Process the preview file (Page Screenshot)
                    if product['pdf_file_url']:
                        internal_page_screenshot = PageScreenshot.objects.create(url=product['pdf_file_url'])
                        internal_product.page_screenshot = internal_page_screenshot

                    # Save the product
                    internal_product.save()

                    # Now handle the gallery images
                    for gallery_image_url in product['images']:
                        Image.objects.create(
                            product=internal_product,
                            image_url=gallery_image_url
                        )

                    print(f"Product {internal_product.title} saved successfully.")

                except Exception as e:
                    # Handle any errors that occur during the product processing
                    print(f"Error processing product {product.get('sku')}: {e}")
                    continue


        if website.script_name == "stlflix.py":
            stlflix_scraper = StlflixProductScrap(
                scraping_process.search_query,
                scraping_process.max_records
            )
            stlflix_scraper.get_products()
            stlflix_products = stlflix_scraper.to_model_data()
            
            for product in stlflix_products:
                try:
                    # Check if the product already exists
                    existing_product = Product.objects.filter(sku=product['sku']).first()
                    if existing_product:
                        print(f"Product with SKU {product['sku']} already exists. Skipping.")
                        continue
                    
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

                except Exception as e:
                    # Handle any errors that occur during the product processing
                    print(f"Error processing product {product.get('sku')}: {e}")
                    continue


        if website.script_name == "makerworld.py":
            makerworld_scraper = MakerWorldProductScrap(
                scraping_process.search_query,
                scraping_process.max_records
            )
            makerworld_scraper.get_products()
            makerworld_products = makerworld_scraper.to_model_data()
            
            for product in makerworld_products:
                try:
                    # Check if the product already exists
                    existing_product = Product.objects.filter(sku=product['sku']).first()
                    if existing_product:
                        print(f"Product with SKU {product['sku']} already exists. Skipping.")
                        continue

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

                except Exception as e:
                    # Handle any errors that occur during the product processing
                    print(f"Error processing product {product.get('sku')}: {e}")
                    continue


@login_required
def initiate_process(request):
    if request.method == 'POST':
        form = ScrapingProcessForm(request.POST)
        if form.is_valid():
            scraping_process = form.save(commit=False)
            scraping_process.started_by = request.user  # Set the current user as 'started_by'
            scraping_process.status = 'pending'  # Set initial status
            scraping_process.save()
            form.save_m2m()  

            # Fetching products
            try:
                processor = ProductScraperProcessor(scraping_process)
                processor.run()
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


def initiate_scraping_process(request):
    if request.method == 'GET':  # Expecting query parameters in GET request
        form = ScrapingProcessForm(request.GET)
        
        # Validate the form data
        if not form.is_valid():
            errors = form.errors.as_json()
            return JsonResponse({"status": "error", "message": "Invalid form data", "errors": json.loads(errors)}, status=400)
        
        scraping_process = form.save(commit=False)
        scraping_process.started_by = request.user  # Set the current user as 'started_by'
        scraping_process.status = 'pending'  # Set initial status
        scraping_process.save()
        form.save_m2m()  # Save many-to-many relationships like source_websites

        def stream():
            # Yield the initial message
            yield f"data: {json.dumps({'status': 'starting', 'progress': 0, 'total': 0, 'in_percent': 0, 'message': 'Initializing scraping process'})}\n\n"

            try:
                processor = ProductScraperProcessor(scraping_process)
                for update in processor.run_with_streaming():
                    yield f"data: {json.dumps(update)}\n\n"
                scraping_process.status = "completed"
                scraping_process.completed_at = timezone.now() 
                scraping_process.save()
                messages.success(request, "Scraping process has been completed successfully.")

            except Exception as e:
                scraping_process.status = "failed"
                scraping_process.save()
                yield f"data: {json.dumps({'status': 'error', 'progress': 0, 'total': 0, 'in_percent': 0, 'message': str(e)})}\n\n"

        response = StreamingHttpResponse(stream(), content_type="text/event-stream")
        response["Cache-Control"] = "no-cache"
        response["X-Accel-Buffering"] = "no"  # Allow Stream over NGINX server
        return response

    # Return error for invalid method
    return JsonResponse({"status": "error", "message": "Invalid request method"}, status=405)



@login_required
def product_detail(request, product_id):
    # Fetch the product by ID
    product = get_object_or_404(Product, id=product_id)

    # wc_manager = WooCommerceManager()
    # product = wc_manager.upload_product(product.ai_version)
    


    # ai_details = product.generate_ai_details()
    context = {
        'product': product,
        'page': 'products'
    }
    # Render the product detail page
    return render(request, 'volt/product_detail.html', context)



@login_required
def processes_list(request):
    search_query = request.GET.get('q', '')  # Get search query
    per_page = int(request.GET.get('per_page', 10))  # Get products per page, default to 10

    # Filter processes based on the search query
    processes = ScrapingProcess.objects.filter(
        Q(search_query__icontains=search_query) |
        Q(status__icontains=search_query)
    ).distinct().order_by('-id')

    # Paginate the filtered processes
    paginator = Paginator(processes, per_page)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'page': 'processes',
        'processes': page_obj,
        'search_query': search_query,
        'per_page': per_page,
    }
    return render(request, "volt/process_monitoring.html", context)


def process_products_sse(request):
    verbs = {
      'publish': {
        'doing': 'Publishing',
        'done': 'Published'
      },
      'approve': {
        'doing': 'Approving',
        'done': 'Approved'
      },
      'decline': {
        'doing': 'Declining',
        'done': 'Declined'
      },
      'delete': {
        'doing': 'Deleting',
        'done': 'Deleted'
      }
    }
    operation = request.GET.get('operation')
    product_ids = request.GET.get('ids').split(',')
    total_products = len(product_ids)
    
    operationed = verbs[operation]['done']
    operationing = verbs[operation]['doing']

    def event_stream():
        for idx, product_id in enumerate(product_ids):
            done = idx
            total = total_products
            output = {
                'product_id': product_id,
                'done': done,
                'total': total
            }
            try:
                product = Product.objects.get(id = product_id)
                output['status'] = 'progress'
                output['percent'] = int((done) / total * 100)
                output['message'] = f'{operationing.capitalize()} product ' + product_id
                # Simulate operation (replace with actual logic like WooCommerce upload or AI generation)
                yield f"data: {json.dumps(output)}\n\n"

                # Perform operation
                if operation == 'delete':
                    product.delete()
                    time.sleep(1)
                
                if operation == 'approve' and product.status != 'approved':
                    product.status = 'approved'
                    product.save()

                if operation == 'publish' and product.status != 'published':
                    wc_manager = WooCommerceManager()
                    try:
                        wc_manager.upload_product(product_ai_version=product.ai_version)
                        product.status = 'published'
                        product.save()
                    except Exception as e:
                        # Retry once more
                        output['message'] = "Having problems, retrying without images"
                        yield f"data: {json.dumps(output)}\n\n"

                        try:
                            wc_manager.upload_product(
                                product_ai_version=product.ai_version,
                                exclude_images=True
                            )
                            product.publishing_message = "Published without images"
                            product.status = 'published'
                            product.save()
                        except Exception as second_e:
                            raise Exception(f"Failed to publish product {product_id} after two attempts: {second_e}")


                if operation == 'decline' and product.status != 'declined':
                    product.status = 'declined'
                    product.save()

                # Progress percentage
                done = idx + 1
                progress = int((done) / total * 100)
                output['status'] = 'progress'
                output['percent'] = progress
                output['message'] = f'{progress}% - {operationed.capitalize()} {done} of {total}'

                yield f"data: {json.dumps(output)}\n\n"

            except Exception as e:
                progress = int((done) / total * 100)
                output['status'] = 'error'
                output['percent'] = progress
                output['message'] = f'Error {operationing.capitalize()} product {product_id}: {str(e)}'
                yield f"data: {json.dumps(output)}\n\n"
                # return  # Stop processing on error

        yield f"data: {json.dumps({'status': 'completed', 'message': f'Products {operationed} successfully'})}\n\n"

    response = StreamingHttpResponse(event_stream(), content_type="text/event-stream")
    response["Cache-Control"] = "no-cache"
    response["X-Accel-Buffering"] = "no"  # Allow Stream over NGINX server
    return response

@csrf_exempt
def process_products_operation(request):
    if request.method == 'POST':
        operation = request.POST.get('operation')
        product_ids = request.POST.getlist('product_ids[]')

        if not product_ids:
            return JsonResponse({'success': False, 'message': 'No products selected'})

        try:
            products = Product.objects.filter(id__in=product_ids)
            raise Exception("Invalid product ids")

            if operation == 'publish':
                products.update(status='published')
            elif operation == 'approve':
                products.update(status='approved')
            elif operation == 'decline':
                products.update(status='declined')
            elif operation == 'delete':
                products.delete()
            else:
                return JsonResponse({'success': False, 'message': 'Invalid operation'})

            return JsonResponse({'success': True, 'message': f'{operation} operation completed successfully'})
        except Exception as e:
            return JsonResponse({'success': False, 'message': str(e)})
    return JsonResponse({'success': False, 'message': 'Invalid request method'}, status=405)


@csrf_exempt
def ajax_upload_product_to_wc(request):
    if request.method == 'POST':
        product_ids = request.POST.getlist('product_ids[]', [])

        if not product_ids:
            return JsonResponse({"success": False, "message": "No product IDs provided."}, status=400)

        wc_manager = WooCommerceManager()
        response = None
        if len(product_ids) > 1:
            selected_products = Product.objects.filter(id__in = product_ids)
            products_ai_version = list(map(lambda product: product.ai_version, selected_products))
            try:
                response = wc_manager.upload_bulk_products(products_ai_version)
            except Exception as e:
                return JsonResponse({"success": False, "message": str(e)}, status=500)

        else:
            selected_product = Product.objects.filter(id__in = product_ids).first()
            product_ai_version = selected_product.ai_version
            try:
                response = wc_manager.upload_product(product_ai_version)
            except Exception as e:
                return JsonResponse({"success": False, "message": str(e)}, status=500)

 
        return JsonResponse({"success": True, "message": "All selected products uploaded successfully!", "data": response})
    else:
        return JsonResponse({"success": False, "message": "Invalid request method."}, status=405)




def logs_view(request):
    log_file_path = os.path.join(settings.BASE_DIR, "logs", "scraping.log")
    logs = []

    try:
        if os.path.exists(log_file_path):
            with open(log_file_path, "r") as log_file:
                for line in log_file:
                    if 'scraping_process' in line.lower():
                        parts = line.strip().split(maxsplit=6)  # Split into 7 parts max
                        if len(parts) >= 6:
                            log_entry = {
                                "status": parts[0],
                                "timestamp": datetime.strptime(f"{parts[1]} {parts[2]}", "%Y-%m-%d %H:%M:%S,%f"),
                                "module": parts[3],
                                "process_id": parts[4],
                                "thread_id": parts[5],
                                "message": parts[6] if len(parts) > 6 else "",
                            }
                            logs.append(log_entry)
    except Exception as e:
        logs = [{"status": "ERROR", "timestamp": None, "module": "logs_view", "process_id": "-", "thread_id": "-", "message": f"Error reading log file: {str(e)}"}]


    logs = sorted(logs, key=lambda x: x['timestamp'], reverse=True)

    context = {
        "page": "logs",
        "logs": logs,
    }
    return render(request, "volt/logs.html", context)