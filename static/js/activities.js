// ============================================================
// MOODMATCH ADMIN - admin-pages.js
// Single clean file. No duplicates. No conflicts.
// ============================================================

// ============================================================
// 1. MODAL MANAGER
// ============================================================
const ModalManager = {
    open(id) {
        const m = document.getElementById(id);
        if (m) { m.classList.add('active'); document.body.style.overflow = 'hidden'; }
    },
    close(id) {
        const m = document.getElementById(id);
        if (m) { m.classList.remove('active'); document.body.style.overflow = ''; }
    },
    closeAll() {
        document.querySelectorAll('.modal.active').forEach(m => m.classList.remove('active'));
        document.body.style.overflow = '';
    }
};

// ============================================================
// 2. LOADING MODAL  (uses adminLoadingModal from admin_base)
// ============================================================
const AdminLoading = {
    show(text = 'Processing your request...') {
        const el = document.getElementById('adminLoadingText');
        if (el) el.textContent = text;
        const m = document.getElementById('adminLoadingModal');
        if (m) m.classList.add('active');
    },
    hide() {
        const m = document.getElementById('adminLoadingModal');
        if (m) m.classList.remove('active');
    }
};

// ============================================================
// 3. CONFIRM MODAL  (uses adminConfirmModal from admin_base)
// ============================================================
const AdminConfirm = {
    _cb: null,
    show(title, message, onConfirm) {
        const t = document.getElementById('adminConfirmTitle');
        const msg = document.getElementById('adminConfirmMessage');
        if (t) t.textContent = title;
        if (msg) msg.textContent = message;
        this._cb = onConfirm;
        const m = document.getElementById('adminConfirmModal');
        if (m) m.classList.add('active');
    },
    hide() {
        const m = document.getElementById('adminConfirmModal');
        if (m) m.classList.remove('active');
        this._cb = null;
    },
    confirm() {
        if (this._cb) this._cb();
        this.hide();
    }
};

// ============================================================
// 4. SUCCESS MODAL  (uses adminSuccessModal from admin_base)
// ============================================================
const AdminSuccess = {
    show(title, message) {
        const t = document.getElementById('adminSuccessTitle');
        const msg = document.getElementById('adminSuccessMessage');
        if (t) t.textContent = title || 'Success';
        if (msg) msg.textContent = message || 'Action completed successfully.';
        const m = document.getElementById('adminSuccessModal');
        if (m) m.classList.add('active');
    },
    hide() {
        const m = document.getElementById('adminSuccessModal');
        if (m) m.classList.remove('active');
    }
};

// ============================================================
// 5. CATEGORY MANAGER
// ============================================================
const CategoryManager = {
    openEditModal(id, name, description, icon) {
        document.getElementById('edit_id').value = id;
        document.getElementById('edit_name').value = name;
        document.getElementById('edit_desc').value = description || '';
        document.getElementById('edit_icon').value = icon || '';
        ModalManager.open('editModal');
    },
    openDeleteModal(id) {
        AdminConfirm.show(
            'Delete Category?',
            'All activities in this category will become uncategorized. This cannot be undone.',
            () => {
                document.getElementById('delete_id').value = id;
                AdminLoading.show('Deleting category...');
                document.querySelector('#deleteModal form').submit();
            }
        );
    }
};

// ============================================================
// 6. ACTIVITY FUNCTIONS  (manage_activities page)
// ============================================================
function openModal(id) { ModalManager.open(id); }
function closeModal(id) { ModalManager.close(id); }

function viewActivity(card) {
    const $ = id => document.getElementById(id);
    $('view-title').innerText = card.dataset.name;
    $('view-emoji').innerText = card.dataset.categoryIcon || '🎯';
    $('view-category').innerText = card.dataset.categoryName;
    $('view-type').innerText = card.dataset.type;
    $('view-energy').innerText = card.dataset.energy || 'Not specified';
    $('view-location').innerText = card.dataset.location || 'Not specified';
    $('view-social').innerText = card.dataset.social || 'Not specified';
    $('view-time').innerText = (card.dataset.minTime && card.dataset.maxTime)
        ? `${card.dataset.minTime} - ${card.dataset.maxTime} mins` : 'Not specified';
    $('view-budget').innerText = (card.dataset.minBudget || card.dataset.maxBudget)
        ? `₹${card.dataset.minBudget} - ₹${card.dataset.maxBudget}` : 'Free';
    $('view-priority').innerText = card.dataset.priority || '0';
    $('view-description').innerText = card.dataset.desc || 'No description';

    const tags = $('view-mood-tags');
    tags.innerHTML = '';
    (card.dataset.moodTags || '').split(',').forEach(t => {
        t = t.trim();
        if (t) {
            const s = document.createElement('span');
            s.className = 'mood-tag';
            s.textContent = t;
            tags.appendChild(s);
        }
    });

    $('view-status').innerHTML = card.dataset.isActive === '1'
        ? '<span style="color:#10b981;font-weight:700;">✅ Active</span>'
        : '<span style="color:#ef4444;font-weight:700;">❌ Inactive</span>';

    ModalManager.open('viewModal');
}

function editActivity(card) {
    const set = (id, val) => { const el = document.getElementById(id); if (el) el.value = val || ''; };
    set('edit_id', card.dataset.id);
    set('edit_name', card.dataset.name);
    set('edit_execution_type', card.dataset.type);
    set('edit_category_id', card.dataset.categoryId);
    set('edit_priority', card.dataset.priority);
    set('edit_mood_tags', card.dataset.moodTags);
    set('edit_description', card.dataset.desc);
    set('edit_energy_level', card.dataset.energy);
    set('edit_location_type', card.dataset.location);
    set('edit_social_type', card.dataset.social);
    set('edit_min_time', card.dataset.minTime);
    set('edit_max_time', card.dataset.maxTime);
    set('edit_min_budget', card.dataset.minBudget);
    set('edit_max_budget', card.dataset.maxBudget);
    const cb = document.getElementById('edit_is_active');
    if (cb) cb.checked = card.dataset.isActive === '1';
    ModalManager.open('editModal');
}

function deleteActivity(card) {
    const preview = document.getElementById('delete-name-preview');
    if (preview) preview.textContent = card.dataset.name;
    document.getElementById('delete_id').value = card.dataset.id;
    ModalManager.open('deleteModal');
}

// ============================================================
// 7. USER MANAGER  (manage_users page)
// ============================================================
function viewUser(card) {
    const u = JSON.parse(card.dataset.user);
    const $ = id => document.getElementById(id);

    const avatar = $('detailAvatar');
    avatar.innerHTML = u.profile_picture
        ? `<img src="/static/uploads/${u.profile_picture}" style="width:100%;height:100%;object-fit:cover;">`
        : '👤';

    $('detailFullName').textContent = (`${u.first_name || ''} ${u.last_name || ''}`).trim() || u.username;
    $('detailUsername').textContent = `@${u.username}`;
    $('detailEmail').textContent = u.email || 'Not provided';
    $('detailGender').textContent = u.gender || '-';
    $('detailBirth').textContent = u.date_of_birth || '-';
    $('detailPhone').textContent = u.phone_number || '-';
    $('detailId').textContent = `#${u.id}`;
    $('detailStreet').textContent = u.street_address || 'Not provided';
    $('detailCity').textContent = u.city || '-';
    $('detailState').textContent = u.state || '-';
    $('detailPostal').textContent = u.postal_code || '-';
    $('detailCountry').textContent = u.country || 'Not provided';
    $('detailJoined').textContent = u.created_at
        ? new Date(u.created_at).toLocaleDateString() : 'Unknown';

    ModalManager.open('viewUserModal');
}
function closeViewModal() { ModalManager.close('viewUserModal'); }

// ============================================================
// 8. FILTER — manage_activities page only
// ============================================================
function initActivityFilters() {
    const searchInput = document.getElementById('searchInput');
    const categoryFilter = document.getElementById('categoryFilter');
    const energyFilter = document.getElementById('energyFilter');
    const locationFilter = document.getElementById('locationFilter');
    const grid = document.getElementById('activitiesGrid');
    if (!searchInput || !grid) return;

    function applyFilters() {
        const q = searchInput.value.toLowerCase().trim();
        const cat = categoryFilter.value;
        const eng = energyFilter.value;
        const loc = locationFilter.value;
        grid.querySelectorAll('.premium-card').forEach(card => {
            const ok = card.dataset.name.toLowerCase().includes(q)
                && (!cat || card.dataset.categoryId === cat)
                && (!eng || card.dataset.energy.toLowerCase() === eng)
                && (!loc || card.dataset.location.toLowerCase() === loc);
            card.style.display = ok ? '' : 'none';
        });
    }
    searchInput.addEventListener('input', applyFilters);
    categoryFilter.addEventListener('change', applyFilters);
    energyFilter.addEventListener('change', applyFilters);
    locationFilter.addEventListener('change', applyFilters);
}

// ============================================================
// 9. FORM SUBMIT → show loading
// ============================================================
function initFormLoading() {
    document.querySelectorAll('form[method="POST"]').forEach(form => {
        form.addEventListener('submit', function () {
            const action = (this.querySelector('input[name="action"]')?.value || '').toLowerCase();
            const msgs = {
                add: 'Creating...', edit: 'Saving changes...', delete: 'Deleting...',
                update_profile: 'Updating profile...', change_password: 'Updating password...'
            };
            AdminLoading.show(msgs[action] || 'Processing...');
        });
    });
}

// ============================================================
// 10. FLASH MESSAGES → show success modal
// ============================================================
function initFlashMessages() {
    const el = document.getElementById('adminFlashData');
    if (!el) return;
    try {
        const messages = JSON.parse(el.textContent || '[]');
        messages.forEach(([cat, msg]) => {
            if (cat === 'success') {
                // small delay so page has rendered
                setTimeout(() => AdminSuccess.show('Success!', msg), 200);
            }
        });
    } catch (e) { }
}

// ============================================================
// 11. SIDEBAR TOGGLE
// ============================================================
function initSidebar() {
    const btn = document.getElementById('hamburgerBtn');
    const sidebar = document.getElementById('adminSidebar');
    const overlay = document.getElementById('sidebarOverlay');
    if (!btn || !sidebar) return;

    btn.addEventListener('click', e => {
        e.stopPropagation();
        sidebar.classList.toggle('expanded');
        btn.classList.toggle('active');
        overlay?.classList.toggle('active');
    });
    overlay?.addEventListener('click', () => {
        sidebar.classList.remove('expanded');
        btn.classList.remove('active');
        overlay.classList.remove('active');
    });
}

// ============================================================
// 12. GLOBAL MODAL CLOSE — ESC + outside click
// ============================================================
function initGlobalModalClose() {
    // Close page modals (class="modal") on outside click
    window.addEventListener('click', e => {
        if (e.target.classList.contains('modal')) ModalManager.close(e.target.id);
    });
    // Close admin global modals on outside click
    window.addEventListener('click', e => {
        ['adminConfirmModal', 'adminSuccessModal'].forEach(id => {
            const m = document.getElementById(id);
            if (m && e.target === m) m.classList.remove('active');
        });
    });
    document.addEventListener('keydown', e => {
        if (e.key === 'Escape') {
            ModalManager.closeAll();
            ['adminConfirmModal', 'adminSuccessModal', 'adminLoadingModal'].forEach(id => {
                document.getElementById(id)?.classList.remove('active');
            });
        }
    });
}

// ============================================================
// 13. WIRE UP CONFIRM/SUCCESS BUTTONS
// ============================================================
function initModalButtons() {
    document.getElementById('adminConfirmCancel')?.addEventListener('click', () => AdminConfirm.hide());
    document.getElementById('adminConfirmOk')?.addEventListener('click', () => AdminConfirm.confirm());
    document.getElementById('adminSuccessOk')?.addEventListener('click', () => AdminSuccess.hide());
}

// ============================================================
// 14. BOOT
// ============================================================
document.addEventListener('DOMContentLoaded', () => {
    initSidebar();
    initGlobalModalClose();
    initModalButtons();
    initFormLoading();
    initFlashMessages();
    initActivityFilters();   // no-ops safely if elements absent
});

// Expose globals
window.ModalManager = ModalManager;
window.AdminLoading = AdminLoading;
window.AdminConfirm = AdminConfirm;
window.AdminSuccess = AdminSuccess;
window.CategoryManager = CategoryManager;
window.openModal = openModal;
window.closeModal = closeModal;
window.viewActivity = viewActivity;
window.editActivity = editActivity;
window.deleteActivity = deleteActivity;
window.viewUser = viewUser;
window.closeViewModal = closeViewModal;