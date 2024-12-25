document.addEventListener("DOMContentLoaded", function () {
    // Get modal and controls
    const modal = document.getElementById('lightboxModal');
    const lightboxImage = document.getElementById('lightboxImage');
    const closeBtn = document.getElementById('closeBtn');
    const prevBtn = document.getElementById('prevBtn');
    const nextBtn = document.getElementById('nextBtn');

    const images = document.querySelectorAll('.lightbox-image'); // Select all images
    let currentIndex = 0;

    // Open the lightbox when an image is clicked
    images.forEach((image, index) => {
        image.addEventListener('click', () => {
            modal.style.display = 'block'; // Show the modal
            lightboxImage.src = image.src; // Set the modal image source
            currentIndex = index; // Update current index
            updateNavigationVisibility(); // Adjust navigation button visibility
        });
    });

    // Close the lightbox when the close button is clicked
    closeBtn.addEventListener('click', () => {
        modal.style.display = 'none'; // Hide the modal
    });

    // Navigate to the previous image
    prevBtn.addEventListener('click', () => {
        currentIndex = (currentIndex === 0) ? images.length - 1 : currentIndex - 1;
        lightboxImage.src = images[currentIndex].src; // Update image source
        updateNavigationVisibility();
    });

    // Navigate to the next image
    nextBtn.addEventListener('click', () => {
        currentIndex = (currentIndex === images.length - 1) ? 0 : currentIndex + 1;
        lightboxImage.src = images[currentIndex].src; // Update image source
        updateNavigationVisibility();
    });

    // Close the lightbox if the user clicks outside the image
    modal.addEventListener('click', (event) => {
        if (event.target === modal) {
            modal.style.display = 'none';
        }
    });

    // Helper function: Adjust navigation visibility
    function updateNavigationVisibility() {
        // If only one image, hide navigation buttons
        if (images.length === 1) {
            prevBtn.style.display = 'none';
            nextBtn.style.display = 'none';
        } else {
            prevBtn.style.display = 'block';
            nextBtn.style.display = 'block';
        }
    }
});
