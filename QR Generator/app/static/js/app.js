/**
 * QR Code Machine Documentation System — App JavaScript
 * =====================================================
 * Features:
 *   1. Auto-dismiss flash messages
 *   2. Delete confirmation dialogs
 *   3. Sidebar toggle for mobile
 *   4. Machine search live filter
 *   5. Image preview on file input
 *   6. Tab persistence via URL hash
 *   7. Print QR functionality
 *   8. Form validation enhancement
 *   9. Animate elements on scroll (IntersectionObserver)
 *  10. Active sidebar link highlight
 */

document.addEventListener('DOMContentLoaded', function () {

    // ─── 1. Auto-dismiss flash messages after 5 seconds ───
    const flashMessages = document.querySelectorAll('.flash-message');
    flashMessages.forEach(function (msg) {
        setTimeout(function () {
            msg.classList.add('fade-out');
            // Remove the element from DOM after the fade-out transition ends
            setTimeout(function () {
                msg.remove();
            }, 400);
        }, 5000);
    });


    // ─── 2. Delete confirmation dialogs ───
    const deleteForms = document.querySelectorAll('.delete-form');
    deleteForms.forEach(function (form) {
        form.addEventListener('submit', function (e) {
            if (!confirm('Are you sure you want to delete this? This action cannot be undone.')) {
                e.preventDefault();
            }
        });
    });


    // ─── 3. Sidebar toggle for mobile ───
    const sidebarToggle = document.getElementById('sidebarToggle');
    const sidebar = document.querySelector('.sidebar');
    const sidebarOverlay = document.querySelector('.sidebar-overlay');

    if (sidebarToggle && sidebar) {
        sidebarToggle.addEventListener('click', function () {
            sidebar.classList.toggle('active');
            if (sidebarOverlay) {
                sidebarOverlay.classList.toggle('active');
            }
        });

        // Close sidebar when clicking the overlay
        if (sidebarOverlay) {
            sidebarOverlay.addEventListener('click', function () {
                sidebar.classList.remove('active');
                sidebarOverlay.classList.remove('active');
            });
        }

        // Close sidebar on Escape key
        document.addEventListener('keydown', function (e) {
            if (e.key === 'Escape' && sidebar.classList.contains('active')) {
                sidebar.classList.remove('active');
                if (sidebarOverlay) sidebarOverlay.classList.remove('active');
            }
        });
    }


    // ─── 4. Machine search live filter ───
    const machineSearch = document.getElementById('machineSearch');
    if (machineSearch) {
        machineSearch.addEventListener('keyup', function () {
            const query = this.value.toLowerCase().trim();
            const cards = document.querySelectorAll('.machine-card');

            cards.forEach(function (card) {
                const name = (card.dataset.name || '').toLowerCase();
                const id = (card.dataset.id || '').toLowerCase();
                const department = (card.dataset.department || '').toLowerCase();
                // Show card if any attribute matches the search query
                const match = name.includes(query) || id.includes(query) || department.includes(query);
                // Hide the column wrapper (parent) if using Bootstrap grid
                const wrapper = card.closest('.col') || card.closest('[class*="col-"]') || card;
                wrapper.style.display = match ? '' : 'none';
            });
        });
    }


    // ─── 5. Image preview on file input ───
    const machineImage = document.getElementById('machineImage');
    const imagePreview = document.getElementById('imagePreview');

    if (machineImage && imagePreview) {
        machineImage.addEventListener('change', function () {
            const file = this.files[0];
            if (file && file.type.startsWith('image/')) {
                const reader = new FileReader();
                reader.onload = function (e) {
                    // If the preview container has an <img>, update its src; otherwise create one
                    let img = imagePreview.querySelector('img');
                    if (!img) {
                        img = document.createElement('img');
                        img.classList.add('img-fluid', 'rounded');
                        img.style.maxHeight = '200px';
                        imagePreview.appendChild(img);
                    }
                    img.src = e.target.result;
                    imagePreview.style.display = 'block';
                };
                reader.readAsDataURL(file);
            }
        });
    }


    // ─── 6. Tab persistence via URL hash ───
    const tabLinks = document.querySelectorAll('.nav-tabs .nav-link[data-bs-toggle="tab"]');

    // Activate tab from URL hash on page load
    if (window.location.hash) {
        const hashTarget = document.querySelector('.nav-tabs .nav-link[href="' + window.location.hash + '"]') ||
                           document.querySelector('.nav-tabs .nav-link[data-bs-target="' + window.location.hash + '"]');
        if (hashTarget) {
            const tab = new bootstrap.Tab(hashTarget);
            tab.show();
        }
    }

    // Update URL hash when a tab is clicked (without scrolling)
    tabLinks.forEach(function (link) {
        link.addEventListener('shown.bs.tab', function (e) {
            const target = e.target.getAttribute('href') || e.target.getAttribute('data-bs-target');
            if (target) {
                history.replaceState(null, null, target);
            }
        });
    });


    // ─── 7. Print QR functionality ───
    const printQRBtn = document.getElementById('printQR');
    if (printQRBtn) {
        printQRBtn.addEventListener('click', function () {
            window.print();
        });
    }


    // ─── 8. Form validation enhancement ───
    const forms = document.querySelectorAll('form.needs-validation');
    forms.forEach(function (form) {
        form.addEventListener('submit', function (e) {
            if (!form.checkValidity()) {
                e.preventDefault();
                e.stopPropagation();
            }
            form.classList.add('was-validated');
        });
    });


    // ─── 9. Animate elements on scroll into view ───
    if ('IntersectionObserver' in window) {
        const animateTargets = document.querySelectorAll('.stat-card, .machine-card');

        const observer = new IntersectionObserver(function (entries) {
            entries.forEach(function (entry) {
                if (entry.isIntersecting) {
                    entry.target.classList.add('animate-in');
                    observer.unobserve(entry.target); // Animate only once
                }
            });
        }, {
            threshold: 0.15,
            rootMargin: '0px 0px -40px 0px'
        });

        animateTargets.forEach(function (el) {
            observer.observe(el);
        });
    } else {
        // Fallback: show all immediately if IntersectionObserver is unsupported
        document.querySelectorAll('.stat-card, .machine-card').forEach(function (el) {
            el.classList.add('animate-in');
        });
    }


    // ─── 10. Active sidebar link highlight ───
    const currentPath = window.location.pathname;
    const sidebarLinks = document.querySelectorAll('.sidebar-link');

    sidebarLinks.forEach(function (link) {
        const href = link.getAttribute('href');
        if (!href) return;

        // Exact match or starts-with for nested routes (but not just '/')
        if (href === currentPath || (href !== '/' && currentPath.startsWith(href))) {
            link.classList.add('active');
        }
    });

});
