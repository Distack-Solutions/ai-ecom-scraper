document.addEventListener('DOMContentLoaded', function () {
const thumbnails = document.querySelectorAll('.thumbnail-wrapper img');
thumbnails.forEach(img => {
    const wrapper = img.closest('.thumbnail-wrapper');
    
    // Listen for the image load event
    img.onload = function () {
        wrapper.classList.remove('loading', 'shimmer'); // Remove shimmer effect
        img.classList.add('loaded'); // Show the image with a fade-in effect
    };

    // Handle cases where the image fails to load
    img.onerror = function () {
        wrapper.classList.remove('loading', 'shimmer'); // Remove shimmer effect even on error
    };

    // In case the image is already cached and loaded
    if (img.complete) {
        img.onload();
    }
});
});