document.addEventListener("DOMContentLoaded", function() {
// Get the modal and image elements
var modal = document.getElementById('lightboxModal');
var lightboxImage = document.getElementById('lightboxImage');
var closeBtn = document.getElementById('closeBtn');
var prevBtn = document.getElementById('prevBtn');
var nextBtn = document.getElementById('nextBtn');

var images = document.querySelectorAll('.lightbox-image');
var currentIndex = 0;

// Open the lightbox when an image is clicked
images.forEach(function(image, index) {
    image.addEventListener('click', function() {
    modal.style.display = 'block';
    lightboxImage.src = image.src;
    currentIndex = index;
    });
});

// Close the lightbox when the close button is clicked
closeBtn.addEventListener('click', function() {
    modal.style.display = 'none';
});

// Go to the previous image
prevBtn.addEventListener('click', function() {
    currentIndex = (currentIndex === 0) ? images.length - 1 : currentIndex - 1;
    lightboxImage.src = images[currentIndex].src;
});

// Go to the next image
nextBtn.addEventListener('click', function() {
    currentIndex = (currentIndex === images.length - 1) ? 0 : currentIndex + 1;
    lightboxImage.src = images[currentIndex].src;
});

// Close the lightbox if the user clicks outside the image
window.addEventListener('click', function(event) {
    if (event.target === modal) {
    modal.style.display = 'none';
    }
});
});
