// Main JavaScript functionality for Travel Itinerary Planner

// Global variables
let currentSlide = 0;
let slideInterval;

// Initialize slideshow functionality
function initializeSlideshow() {
    const slides = document.querySelectorAll('.slide');
    
    if (slides.length === 0) return;
    
    // Start automatic slideshow
    slideInterval = setInterval(() => {
        nextSlide();
    }, 4000); // Change slide every 4 seconds
    
    // Pause slideshow on hover
    const slideshowContainer = document.querySelector('.slideshow-container');
    if (slideshowContainer) {
        slideshowContainer.addEventListener('mouseenter', () => {
            clearInterval(slideInterval);
        });
        
        slideshowContainer.addEventListener('mouseleave', () => {
            slideInterval = setInterval(() => {
                nextSlide();
            }, 4000);
        });
    }
}

// Move to next slide
function nextSlide() {
    const slides = document.querySelectorAll('.slide');
    if (slides.length === 0) return;
    
    // Remove active class from current slide
    slides[currentSlide].classList.remove('active');
    
    // Move to next slide
    currentSlide = (currentSlide + 1) % slides.length;
    
    // Add active class to new current slide
    slides[currentSlide].classList.add('active');
}

// Initialize loading animation on landing page
function initializeLoadingAnimation() {
    const getStartedBtn = document.querySelector('.get-started-btn');
    const loadingText = document.querySelector('.loading-text');

    if (getStartedBtn && loadingText) {
        getStartedBtn.addEventListener('click', () => {
            // Hide the button and show the loading text
            getStartedBtn.style.display = 'none';
            loadingText.style.display = 'block';

            // Simulate loading (e.g., before redirecting to planner)
            // If you redirect immediately, this might not be fully visible.
            // This is more for a simulated effect or if an AJAX call is made.
            setTimeout(() => {
                window.location.href = '/planner';
            }, 1500); // Redirect to planner page after 1.5 seconds
        });
    }
}


// Initialize loading page functionality (for /loading route)
function initializeLoadingPage() {
    const steps = document.querySelectorAll('.loading-steps .step');
    const progressBar = document.querySelector('.progress-bar');
    let currentStep = 0;

    function updateLoading() {
        if (currentStep < steps.length) {
            steps[currentStep].classList.add('active');
            progressBar.style.width = ((currentStep + 1) / steps.length) * 100 + '%';
            currentStep++;
            setTimeout(updateLoading, 1000); // Advance every 1 second
        } else {
            // All steps complete, potentially redirect or show content
            // console.log("Loading complete!");
        }
    }

    if (steps.length > 0 && progressBar) {
        updateLoading();
    }
}

// Function to show Bootstrap alerts
function showAlert(message, type = 'success') {
    const flashContainer = document.querySelector('.flash-container');
    if (!flashContainer) return;

    const alertHtml = `
        <div class="alert alert-${type} alert-dismissible fade show" role="alert">
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
        </div>
    `;
    flashContainer.insertAdjacentHTML('beforeend', alertHtml);

    // Auto-close after 5 seconds
    setTimeout(() => {
        const currentAlert = flashContainer.querySelector('.alert:last-child');
        if (currentAlert) {
            new bootstrap.Alert(currentAlert).close();
        }
    }, 5000);
}


// Sidebar toggle functionality
document.addEventListener('DOMContentLoaded', function() {
    var sidebarToggle = document.getElementById('sidebarToggle');
    var wrapper = document.getElementById('wrapper');

    if (sidebarToggle && wrapper) {
        sidebarToggle.addEventListener('click', function() {
            wrapper.classList.toggle('toggled');
        });
    }

    // Handle form submission for 'planner.html' to show loading or processing state
    const tripForm = document.querySelector('.trip-form');
    if (tripForm) {
        tripForm.addEventListener('submit', function() {
            const submitBtn = this.querySelector('.generate-itinerary-btn');
            if (submitBtn) {
                const originalText = submitBtn.innerHTML;
                submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin me-2"></i>Processing...';
                submitBtn.disabled = true;
                
                // Re-enable after 10 seconds as fallback
                setTimeout(() => {
                    if (submitBtn.disabled) {
                        submitBtn.innerHTML = originalText;
                        submitBtn.disabled = false;
                    }
                }, 10000);
            }
        });
    }
});

// Handle page visibility changes
document.addEventListener('visibilitychange', function() {
    if (document.hidden) {
        // Pause animations when page is not visible
        if (slideInterval) {
            clearInterval(slideInterval);
        }
    } else {
        // Resume animations when page becomes visible
        if (document.querySelector('.slideshow-container')) {
            initializeSlideshow();
        }
    }
});

// Handle window resize
window.addEventListener('resize', function() {
    // Adjust layout for mobile devices
    const vh = window.innerHeight * 0.01;
    document.documentElement.style.setProperty('--vh', `${vh}px`);
});

// Set initial viewport height
window.addEventListener('load', function() {
    const vh = window.innerHeight * 0.01;
    document.documentElement.style.setProperty('--vh', `${vh}px`);
});

// Export functions for external use
window.TravelPlanner = {
    showAlert,
    initializeSlideshow,
    initializeLoadingPage,
    nextSlide
};
