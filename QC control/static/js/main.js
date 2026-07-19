/* ═══════════════════════════════════════════════════════
   Digital QC System — Client-Side Logic
   ═══════════════════════════════════════════════════════ */

document.addEventListener('DOMContentLoaded', function () {

    // ─── Theme Toggle ───
    const themeToggle = document.getElementById('themeToggle');
    const html = document.documentElement;

    // Restore saved theme
    const savedTheme = localStorage.getItem('qc-theme') || 'light';
    html.setAttribute('data-theme', savedTheme);
    html.setAttribute('data-bs-theme', savedTheme);
    updateThemeIcon(savedTheme);

    if (themeToggle) {
        themeToggle.addEventListener('click', () => {
            const current = html.getAttribute('data-theme');
            const next = current === 'dark' ? 'light' : 'dark';
            html.setAttribute('data-theme', next);
            html.setAttribute('data-bs-theme', next);
            localStorage.setItem('qc-theme', next);
            updateThemeIcon(next);
        });
    }

    function updateThemeIcon(theme) {
        if (!themeToggle) return;
        const icon = themeToggle.querySelector('i');
        if (icon) {
            icon.className = theme === 'dark' ? 'bi bi-sun' : 'bi bi-moon-stars';
        }
    }

    // ─── Auto-dismiss Alerts ───
    document.querySelectorAll('.glass-alert').forEach(alert => {
        setTimeout(() => {
            const bsAlert = bootstrap.Alert.getOrCreateInstance(alert);
            bsAlert.close();
        }, 5000);
    });

    // ─── Form Stepper ───
    initStepper();

    // ─── Checklist Logic ───
    initChecklist();

    // ─── Image Upload ───
    initImageUpload();

    // ─── Submit Button Loading ───
    initSubmitLoading();

    // ─── Lightbox ───
    initLightbox();

    // ─── Modern Top Progress Bar ───
    initTopProgressBar();

    // ─── Animations ───
    document.querySelectorAll('.animate-in').forEach((el, i) => {
        el.style.animationDelay = `${0.05 + i * 0.05}s`;
    });
});


/* ═══════════════════════════════════════════════════════
   Form Stepper
   ═══════════════════════════════════════════════════════ */

function initStepper() {
    const sections = document.querySelectorAll('.form-section');
    const steps = document.querySelectorAll('.step');
    const nextBtns = document.querySelectorAll('.btn-next');
    const prevBtns = document.querySelectorAll('.btn-prev');

    if (sections.length === 0) return;

    let currentStep = 0;

    function showStep(index) {
        sections.forEach((s, i) => {
            if (i === index) {
                s.style.display = 'block';
                // Remove and re-add class to trigger animation reflow
                s.classList.remove('fade-in');
                void s.offsetWidth; 
                s.classList.add('fade-in');
            } else {
                s.style.display = 'none';
                s.classList.remove('fade-in');
            }
        });
        steps.forEach((s, i) => {
            s.classList.remove('active', 'completed');
            if (i < index) s.classList.add('completed');
            if (i === index) s.classList.add('active');
        });
        currentStep = index;

        // Scroll to top of form smoothly
        const formTop = document.querySelector('.form-stepper');
        if (formTop) {
            formTop.scrollIntoView({ behavior: 'smooth', block: 'start' });
        }
    }

    nextBtns.forEach(btn => {
        btn.addEventListener('click', (e) => {
            e.preventDefault();
            // Validate current section
            const currentSection = sections[currentStep];
            const requiredFields = currentSection.querySelectorAll('[required]');
            let valid = true;

            requiredFields.forEach(field => {
                if (!field.value.trim()) {
                    field.classList.add('is-invalid');
                    valid = false;
                } else {
                    field.classList.remove('is-invalid');
                }
            });

            if (valid && currentStep < sections.length - 1) {
                showStep(currentStep + 1);
            }
        });
    });

    prevBtns.forEach(btn => {
        btn.addEventListener('click', (e) => {
            e.preventDefault();
            if (currentStep > 0) {
                showStep(currentStep - 1);
            }
        });
    });

    showStep(0);
}


/* ═══════════════════════════════════════════════════════
   Checklist Auto-Status
   ═══════════════════════════════════════════════════════ */

function initChecklist() {
    const checklistInputs = document.querySelectorAll('input[name^="checklist_"]');
    if (checklistInputs.length === 0) return;

    checklistInputs.forEach(input => {
        input.addEventListener('change', updateOverallStatus);
    });
}

function updateOverallStatus() {
    const items = document.querySelectorAll('.checklist-item');
    let allPassed = true;
    let anyFailed = false;
    let allAnswered = true;

    items.forEach(item => {
        const passRadio = item.querySelector('input[value="pass"]');
        const failRadio = item.querySelector('input[value="fail"]');

        if (!passRadio || !failRadio) return;

        if (!passRadio.checked && !failRadio.checked) {
            allAnswered = false;
        } else if (failRadio.checked) {
            anyFailed = true;
            allPassed = false;
        }
    });

    const statusIndicator = document.getElementById('overallStatus');
    if (statusIndicator) {
        if (!allAnswered) {
            statusIndicator.textContent = 'Incomplete';
            statusIndicator.className = 'badge-status badge-pending';
        } else if (anyFailed) {
            statusIndicator.textContent = 'FAIL';
            statusIndicator.className = 'badge-status badge-fail';
        } else {
            statusIndicator.textContent = 'PASS';
            statusIndicator.className = 'badge-status badge-pass';
        }
    }

    // Update hidden status field
    const statusField = document.getElementById('inspectionStatus');
    if (statusField) {
        if (!allAnswered) {
            statusField.value = 'pending';
        } else if (anyFailed) {
            statusField.value = 'fail';
        } else {
            statusField.value = 'pass';
        }
    }
}


/* ═══════════════════════════════════════════════════════
   Image Upload with Drag & Drop + Preview
   ═══════════════════════════════════════════════════════ */

function initImageUpload() {
    const uploadZone = document.getElementById('uploadZone');
    const fileInput = document.getElementById('imageInput');
    const previewGrid = document.getElementById('imagePreviewGrid');

    if (!uploadZone || !fileInput) return;

    const maxFiles = 3;
    const maxSize = 5 * 1024 * 1024; // 5MB
    const allowedTypes = ['image/jpeg', 'image/jpg', 'image/png'];
    let selectedFiles = [];

    uploadZone.addEventListener('click', () => fileInput.click());

    uploadZone.addEventListener('dragover', (e) => {
        e.preventDefault();
        uploadZone.classList.add('dragover');
    });

    uploadZone.addEventListener('dragleave', () => {
        uploadZone.classList.remove('dragover');
    });

    uploadZone.addEventListener('drop', (e) => {
        e.preventDefault();
        uploadZone.classList.remove('dragover');
        handleFiles(e.dataTransfer.files);
    });

    fileInput.addEventListener('change', () => {
        handleFiles(fileInput.files);
    });

    function handleFiles(files) {
        for (let file of files) {
            if (selectedFiles.length >= maxFiles) {
                showToast('Maximum ' + maxFiles + ' images allowed', 'warning');
                break;
            }
            if (!allowedTypes.includes(file.type)) {
                showToast(file.name + ' — Invalid file type. Only JPG, JPEG, PNG allowed.', 'danger');
                continue;
            }
            if (file.size > maxSize) {
                showToast(file.name + ' — File too large. Maximum 5MB.', 'danger');
                continue;
            }
            selectedFiles.push(file);
        }
        updatePreviews();
        updateFileInput();
    }

    function updatePreviews() {
        if (!previewGrid) return;
        previewGrid.innerHTML = '';

        selectedFiles.forEach((file, index) => {
            const reader = new FileReader();
            reader.onload = (e) => {
                const div = document.createElement('div');
                div.className = 'image-preview-item';
                div.innerHTML = `
                    <img src="${e.target.result}" alt="Preview ${index + 1}">
                    <button type="button" class="remove-btn" data-index="${index}" title="Remove">
                        <i class="bi bi-x"></i>
                    </button>
                `;
                div.querySelector('.remove-btn').addEventListener('click', (evt) => {
                    evt.stopPropagation();
                    selectedFiles.splice(index, 1);
                    updatePreviews();
                    updateFileInput();
                });
                previewGrid.appendChild(div);
            };
            reader.readAsDataURL(file);
        });

        // Update zone text
        const countText = uploadZone.querySelector('.upload-count');
        if (countText) {
            countText.textContent = `${selectedFiles.length} / ${maxFiles} images selected`;
        }
    }

    function updateFileInput() {
        // Create a new DataTransfer to update the file input
        const dt = new DataTransfer();
        selectedFiles.forEach(f => dt.items.add(f));
        fileInput.files = dt.files;
    }
}


/* ═══════════════════════════════════════════════════════
   Submit Button Loading State
   ═══════════════════════════════════════════════════════ */

function initSubmitLoading() {
    document.querySelectorAll('form[data-loading]').forEach(form => {
        form.addEventListener('submit', function () {
            const btn = form.querySelector('button[type="submit"]');
            if (btn) {
                btn.classList.add('btn-loading');
                btn.disabled = true;
            }
        });
    });
}


/* ═══════════════════════════════════════════════════════
   Image Lightbox
   ═══════════════════════════════════════════════════════ */

function initLightbox() {
    document.querySelectorAll('.gallery-item').forEach(item => {
        item.addEventListener('click', () => {
            const img = item.querySelector('img');
            if (!img) return;

            const overlay = document.createElement('div');
            overlay.className = 'lightbox-overlay';
            overlay.innerHTML = `
                <button class="lightbox-close"><i class="bi bi-x-lg"></i></button>
                <img src="${img.src}" alt="${img.alt || 'Defect photo'}">
            `;
            overlay.addEventListener('click', (e) => {
                if (e.target === overlay || e.target.closest('.lightbox-close')) {
                    overlay.remove();
                }
            });
            document.body.appendChild(overlay);
        });
    });
}


/* ═══════════════════════════════════════════════════════
   Toast Notifications
   ═══════════════════════════════════════════════════════ */

function showToast(message, type = 'info') {
    // Create toast container if not exists
    let container = document.getElementById('toastContainer');
    if (!container) {
        container = document.createElement('div');
        container.id = 'toastContainer';
        container.style.cssText = 'position:fixed;top:1rem;right:1rem;z-index:9999;display:flex;flex-direction:column;gap:0.5rem;';
        document.body.appendChild(container);
    }

    const icons = {
        success: 'check-circle',
        danger: 'exclamation-triangle',
        warning: 'exclamation-circle',
        info: 'info-circle'
    };

    const toast = document.createElement('div');
    toast.className = `alert alert-${type} d-flex align-items-center gap-2 shadow-lg mb-0`;
    toast.style.cssText = 'min-width:300px;animation:slideUp 0.3s ease;font-size:0.875rem;';
    toast.innerHTML = `
        <i class="bi bi-${icons[type] || 'info-circle'}"></i>
        <span>${message}</span>
    `;
    container.appendChild(toast);

    setTimeout(() => {
        toast.style.opacity = '0';
        toast.style.transform = 'translateX(100%)';
        toast.style.transition = 'all 0.3s ease';
        setTimeout(() => toast.remove(), 300);
    }, 4000);
}


/* ═══════════════════════════════════════════════════════
   Modern Top Progress Bar
   ═══════════════════════════════════════════════════════ */
function initTopProgressBar() {
    const progressBar = document.getElementById('topProgressBar');
    if (!progressBar) return;

    function startProgress() {
        progressBar.style.opacity = '1';
        progressBar.style.width = '30%';
        setTimeout(() => {
            if (progressBar.style.opacity === '1') {
                progressBar.style.width = '70%';
            }
        }, 500);
    }

    // Trigger on valid link clicks
    document.querySelectorAll('a').forEach(link => {
        link.addEventListener('click', (e) => {
            const href = link.getAttribute('href');
            if (href && !href.startsWith('#') && !href.startsWith('javascript') && link.target !== '_blank') {
                startProgress();
            }
        });
    });

    // Trigger on form submits
    document.querySelectorAll('form').forEach(form => {
        form.addEventListener('submit', () => {
            startProgress();
        });
    });

    // Finish progress instantly when page is done loading or shown from cache
    window.addEventListener('pageshow', () => {
        progressBar.style.width = '100%';
        setTimeout(() => {
            progressBar.style.opacity = '0';
            setTimeout(() => {
                progressBar.style.width = '0%';
            }, 300);
        }, 200);
    });
}
