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
    
    if (!getStartedBtn || !loadingText) return;
    
    getStartedBtn.addEventListener('click', function(e) {
        e.preventDefault();
        
        // Show loading text with animation
        loadingText.style.opacity = '1';
        
        // Add button loading state
        this.innerHTML = 'Loading...';
        this.disabled = true;
        
        // Redirect after animation
        setTimeout(() => {
            window.location.href = '/planner';
        }, 3000);
    });
}

// Initialize loading page functionality
function initializeLoadingPage() {
    const steps = document.querySelectorAll('.step');
    const progressBar = document.querySelector('.progress-bar');
    
    if (steps.length === 0) return;
    
    let currentStep = 0;
    
    // Animate through loading steps
    const stepInterval = setInterval(() => {
        if (currentStep < steps.length) {
            // Remove active class from all steps
            steps.forEach(step => step.classList.remove('active'));
            
            // Add active class to current step
            steps[currentStep].classList.add('active');
            
            currentStep++;
        } else {
            clearInterval(stepInterval);
            
            // Redirect to planner after loading
            setTimeout(() => {
                window.location.href = '/planner';
            }, 1000);
        }
    }, 1000);
}

// Smooth scrolling for internal links
function initializeSmoothScrolling() {
    const links = document.querySelectorAll('a[href^="#"]');
    
    links.forEach(link => {
        link.addEventListener('click', function(e) {
            e.preventDefault();
            
            const targetId = this.getAttribute('href').substring(1);
            const targetElement = document.getElementById(targetId);
            
            if (targetElement) {
                targetElement.scrollIntoView({
                    behavior: 'smooth',
                    block: 'start'
                });
            }
        });
    });
}

// Form validation for trip planner
function initializeFormValidation() {
    const form = document.querySelector('.trip-form');
    
    if (!form) return;
    
    form.addEventListener('submit', function(e) {
        const destination = document.getElementById('destination');
        const startDate = document.getElementById('start_date');
        const endDate = document.getElementById('end_date');
        
        // Validate destination
        if (!destination.value.trim()) {
            e.preventDefault();
            showAlert('Please enter a destination', 'error');
            destination.focus();
            return false;
        }
        
        // Validate dates
        if (!startDate.value || !endDate.value) {
            e.preventDefault();
            showAlert('Please select both start and end dates', 'error');
            return false;
        }
        
        const start = new Date(startDate.value);
        const end = new Date(endDate.value);
        const today = new Date();
        today.setHours(0, 0, 0, 0);
        
        if (start < today) {
            e.preventDefault();
            showAlert('Start date cannot be in the past', 'error');
            startDate.focus();
            return false;
        }
        
        if (end <= start) {
            e.preventDefault();
            showAlert('End date must be after start date', 'error');
            endDate.focus();
            return false;
        }
        
        // Show loading state
        const submitBtn = form.querySelector('button[type="submit"]');
        if (submitBtn) {
            submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin me-2"></i>Creating Your Itinerary...';
            submitBtn.disabled = true;
        }
    });
}

// Show alert messages
function showAlert(message, type = 'info') {
    // Remove existing alerts
    const existingAlerts = document.querySelectorAll('.custom-alert');
    existingAlerts.forEach(alert => alert.remove());
    
    // Create new alert
    const alert = document.createElement('div');
    alert.className = `alert alert-${type === 'error' ? 'danger' : 'success'} alert-dismissible fade show custom-alert`;
    alert.style.position = 'fixed';
    alert.style.top = '20px';
    alert.style.right = '20px';
    alert.style.zIndex = '1060';
    alert.style.maxWidth = '400px';
    
    alert.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    
    document.body.appendChild(alert);
    
    // Auto-dismiss after 5 seconds
    setTimeout(() => {
        if (alert.parentNode) {
            alert.remove();
        }
    }, 5000);
}

// Initialize tooltip functionality
function initializeTooltips() {
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    
    if (typeof bootstrap !== 'undefined' && bootstrap.Tooltip) {
        tooltipTriggerList.map(function (tooltipTriggerEl) {
            return new bootstrap.Tooltip(tooltipTriggerEl);
        });
    }
}

// Initialize modal functionality
function initializeModals() {
    const modalTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="modal"]'));
    
    if (typeof bootstrap !== 'undefined' && bootstrap.Modal) {
        modalTriggerList.map(function (modalTriggerEl) {
            return new bootstrap.Modal(modalTriggerEl);
        });
    }
}

// Animate elements on scroll
function initializeScrollAnimations() {
    const observerOptions = {
        threshold: 0.1,
        rootMargin: '0px 0px -50px 0px'
    };
    
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('animate-in');
            }
        });
    }, observerOptions);
    
    // Observe elements that should animate on scroll
    const animateElements = document.querySelectorAll('.feature-item, .day-plan, .activity');
    animateElements.forEach(el => observer.observe(el));
}

// Auto-resize textareas
function initializeAutoResizeTextareas() {
    const textareas = document.querySelectorAll('textarea');
    
    textareas.forEach(textarea => {
        textarea.addEventListener('input', function() {
            this.style.height = 'auto';
            this.style.height = (this.scrollHeight) + 'px';
        });
    });
}

// Initialize all functionality when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    // Core functionality
    initializeSlideshow();
    initializeLoadingAnimation();
    initializeSmoothScrolling();
    initializeFormValidation();
    
    // UI enhancements
    initializeTooltips();
    initializeModals();
    initializeScrollAnimations();
    initializeAutoResizeTextareas();
    
    // Page-specific functionality
    const currentPage = window.location.pathname;
    
    if (currentPage === '/loading') {
        initializeLoadingPage();
    }
    
    // Add smooth transitions to all buttons
    const buttons = document.querySelectorAll('.btn');
    buttons.forEach(btn => {
        btn.addEventListener('mouseenter', function() {
            this.style.transform = 'translateY(-2px)';
        });
        
        btn.addEventListener('mouseleave', function() {
            this.style.transform = 'translateY(0)';
        });
    });
    
    // Add loading states to all form submissions
    const forms = document.querySelectorAll('form');
    forms.forEach(form => {
        form.addEventListener('submit', function() {
            const submitBtn = this.querySelector('button[type="submit"]');
            if (submitBtn && !submitBtn.disabled) {
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
    });
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
