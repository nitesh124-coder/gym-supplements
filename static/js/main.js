// Hero Image Slideshow
document.addEventListener('DOMContentLoaded', function() {
    const heroContainer = document.getElementById('hero-image-container');
    if (heroContainer) {
        const imageUrls = JSON.parse(heroContainer.dataset.imageUrls);
        const heroImage = document.getElementById('hero-banner-image');
        let currentIndex = 0;

        function updateImage() {
            currentIndex = (currentIndex + 1) % imageUrls.length;
            heroImage.style.opacity = '0';
            setTimeout(() => {
                heroImage.src = imageUrls[currentIndex];
                heroImage.style.opacity = '1';
            }, 500);
        }

        // Change image every 5 seconds
        setInterval(updateImage, 5000);
    }
});

// Add to Cart with AJAX and Animation
document.addEventListener('DOMContentLoaded', function() {
    const addToCartForms = document.querySelectorAll('form[action*="/add_to_cart/"]');

    addToCartForms.forEach(form => {
        form.addEventListener('submit', function(e) {
            e.preventDefault(); // Prevent default form submission

            const button = form.querySelector('button[type="submit"]');
            const originalText = button.textContent;
            const formData = new FormData(form);

            // Show loading state
            button.textContent = 'Adding...';
            button.disabled = true;

            // Send AJAX request
            fetch(form.action, {
                method: 'POST',
                headers: {
                    'X-Requested-With': 'XMLHttpRequest'
                },
                body: formData
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    // Update cart count in header
                    updateCartCount(data.cart_count);

                    // Show success state
                    button.textContent = 'Added!';
                    button.classList.add('btn-success');
                    button.classList.remove('btn-warning');

                    // Reset button after 2 seconds
                    setTimeout(() => {
                        button.textContent = originalText;
                        button.classList.add('btn-warning');
                        button.classList.remove('btn-success');
                        button.disabled = false;
                    }, 2000);
                } else {
                    // Handle error
                    button.textContent = 'Error!';
                    button.classList.add('btn-danger');
                    button.classList.remove('btn-warning');

                    setTimeout(() => {
                        button.textContent = originalText;
                        button.classList.add('btn-warning');
                        button.classList.remove('btn-danger');
                        button.disabled = false;
                    }, 2000);
                }
            })
            .catch(error => {
                console.error('Error:', error);
                // Fallback to regular form submission
                form.submit();
            });
        });
    });
});

// Function to update cart count in header
function updateCartCount(count) {
    const cartCountElement = document.getElementById('cart-count');
    if (cartCountElement) {
        cartCountElement.textContent = count;

        // Add a small animation to draw attention
        cartCountElement.style.transform = 'scale(1.3)';
        cartCountElement.style.transition = 'transform 0.2s ease';

        setTimeout(() => {
            cartCountElement.style.transform = 'scale(1)';
        }, 200);
    }
}

// Function to refresh cart count (useful for page loads)
function refreshCartCount() {
    fetch('/api/cart_count')
        .then(response => response.json())
        .then(data => {
            updateCartCount(data.cart_count);
        })
        .catch(error => {
            console.error('Error fetching cart count:', error);
        });
}

// Add to Wishlist with AJAX and Animation
document.addEventListener('DOMContentLoaded', function() {
    const addToWishlistForms = document.querySelectorAll('form[action*="/add_to_wishlist/"]');

    addToWishlistForms.forEach(form => {
        form.addEventListener('submit', function(e) {
            e.preventDefault(); // Prevent default form submission

            const button = form.querySelector('button[type="submit"]');
            const originalIcon = button.innerHTML;
            const formData = new FormData(form);

            // Show loading state
            button.innerHTML = '<i class="fas fa-spinner fa-spin"></i>';
            button.disabled = true;

            // Send AJAX request
            fetch(form.action, {
                method: 'POST',
                headers: {
                    'X-Requested-With': 'XMLHttpRequest'
                },
                body: formData
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    // Update wishlist count in header
                    updateWishlistCount(data.wishlist_count);

                    // Show success state
                    button.innerHTML = '<i class="fas fa-heart text-danger"></i>';
                    button.classList.remove('btn-outline-danger');
                    button.classList.add('btn-danger');

                    // Reset button after 2 seconds
                    setTimeout(() => {
                        button.innerHTML = originalIcon;
                        button.classList.add('btn-outline-danger');
                        button.classList.remove('btn-danger');
                        button.disabled = false;
                    }, 2000);
                } else {
                    // Handle error
                    button.innerHTML = '<i class="fas fa-exclamation-triangle"></i>';
                    button.classList.add('btn-warning');
                    button.classList.remove('btn-outline-danger');

                    setTimeout(() => {
                        button.innerHTML = originalIcon;
                        button.classList.add('btn-outline-danger');
                        button.classList.remove('btn-warning');
                        button.disabled = false;
                    }, 2000);
                }
            })
            .catch(error => {
                console.error('Error:', error);
                // Fallback to regular form submission
                form.submit();
            });
        });
    });
});

// Function to update wishlist count in header
function updateWishlistCount(count) {
    const wishlistCountElement = document.getElementById('wishlist-count');
    if (wishlistCountElement) {
        wishlistCountElement.textContent = count;

        // Add a small animation to draw attention
        wishlistCountElement.style.transform = 'scale(1.3)';
        wishlistCountElement.style.transition = 'transform 0.2s ease';

        setTimeout(() => {
            wishlistCountElement.style.transform = 'scale(1)';
        }, 200);
    }
}

// Function to refresh wishlist count (useful for page loads)
function refreshWishlistCount() {
    fetch('/api/wishlist_count')
        .then(response => response.json())
        .then(data => {
            updateWishlistCount(data.wishlist_count);
        })
        .catch(error => {
            console.error('Error fetching wishlist count:', error);
        });
}

// Product Filters Functionality
document.addEventListener('DOMContentLoaded', function() {
    const applyFiltersBtn = document.getElementById('apply-filters-btn');

    if (applyFiltersBtn) {
        applyFiltersBtn.addEventListener('click', function() {
            const currentUrl = new URL(window.location);
            const params = new URLSearchParams();

            // Keep existing category parameter
            if (currentUrl.searchParams.get('category')) {
                params.append('category', currentUrl.searchParams.get('category'));
            }

            // Get brand filters
            const brandFilters = document.querySelectorAll('.brand-filter:checked');
            brandFilters.forEach(filter => {
                params.append('brand', filter.value);
            });

            // Get discount filters
            const discountFilters = document.querySelectorAll('.discount-filter:checked');
            discountFilters.forEach(filter => {
                params.append('discount', filter.value);
            });

            // Get type filters (for accessories)
            const typeFilters = document.querySelectorAll('.type-filter:checked');
            typeFilters.forEach(filter => {
                params.append('type', filter.value);
            });

            // Redirect with filters
            window.location.href = currentUrl.pathname + '?' + params.toString();
        });
    }
});