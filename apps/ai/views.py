from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.urls import reverse
from .models import Product, ProductAIVersion
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse

@login_required
def update_ai_details(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    
    if not hasattr(product, 'ai_version'):
        # If there is no AI version associated with the product, return a 404 or handle appropriately
        messages.error(request, "AI details not found for this product.")
        return redirect(reverse('scraper:product_detail', kwargs={'product_id': product_id}))

    ai_version = product.ai_version

    if request.method == 'POST':
        # Get form data from POST request
        ai_title = request.POST.get('ai_title')
        ai_expanded_description = request.POST.get('ai_expanded_description')
        ai_short_description = request.POST.get('ai_short_description')
        ai_meta_description = request.POST.get('ai_meta_description')
        ai_focus_keyphrase = request.POST.get('ai_focus_keyphrase')

        # Update AI Version fields
        ai_version.title = ai_title
        ai_version.expanded_description = ai_expanded_description
        ai_version.short_description = ai_short_description
        ai_version.meta_description = ai_meta_description
        ai_version.focus_keyphrase = ai_focus_keyphrase
        
        # Save the updated AI version
        ai_version.save()

        # Add success message
        messages.success(request, "AI details updated successfully.")

        # Redirect to product detail view with query parameter to scroll to AI details
        return redirect(f"{reverse('scraper:product_detail', kwargs={'product_id': product.id})}?scroll_to_ai=true")

    return redirect('scraper:product_detail', product_id=product.id)


@login_required
def regenerate_ai(request, product_id):
    if request.method == 'POST':
        # Get the product by ID or return a 404 if not found
        product = get_object_or_404(Product, id=product_id)
        ai_details = product.generate_ai_details()
        product.create_or_update(ai_details=ai_details)
        # Return JSON response for successful approval
        return JsonResponse({
            'ai_details': ai_details,
            'success': True, 
            'message': f'Details has been updated.'
        })
    
    # If not a POST request, return a 405 Method Not Allowed
    return JsonResponse({'success': False, 'message': 'Invalid request method.'}, status=405)
