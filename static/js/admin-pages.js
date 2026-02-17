(function () {
  'use strict';

  function byId(id) { return document.getElementById(id); }

  function parseJsonScript(id) {
    var el = byId(id);
    if (!el || !el.textContent) return null;
    try { return JSON.parse(el.textContent); }
    catch (err) { console.error('Invalid JSON in', id, err); return null; }
  }

  // ============================================================
  // MODAL MANAGER
  // ============================================================
  var ModalManager = {
    activeModals: new Set(),

    open: function (modalId) {
      var modal = byId(modalId);
      if (!modal) return;
      modal.classList.remove('modal-exit');
      modal.classList.add('active');
      this.activeModals.add(modalId);
      document.body.style.overflow = 'hidden';
    },

    close: function (modalId) {
      var modal = byId(modalId);
      if (!modal) return;
      // animate out
      modal.classList.add('modal-exit');
      var self = this;
      setTimeout(function () {
        modal.classList.remove('active', 'modal-exit');
        self.activeModals.delete(modalId);
        if (self.activeModals.size === 0) document.body.style.overflow = 'auto';
      }, 250);
    },

    closeAll: function () {
      var self = this;
      Array.from(this.activeModals).forEach(function (id) { self.close(id); });
    },

    init: function () {
      var self = this;
      window.addEventListener('click', function (e) {
        if (e.target && e.target.classList && e.target.classList.contains('modal'))
          self.close(e.target.id);
      });
      document.addEventListener('keydown', function (e) {
        if (e.key === 'Escape') self.closeAll();
      });
    }
  };

  // ============================================================
  // SIDEBAR
  // ============================================================
  function initSidebar() {
    var btn = byId('hamburgerBtn');
    var sidebar = byId('adminSidebar');
    var overlay = byId('sidebarOverlay');
    if (!btn || !sidebar || !overlay) return;

    btn.addEventListener('click', function (e) {
      e.stopPropagation();
      sidebar.classList.toggle('expanded');
      btn.classList.toggle('active');
      overlay.classList.toggle('active');
    });
    overlay.addEventListener('click', function () {
      sidebar.classList.remove('expanded');
      btn.classList.remove('active');
      overlay.classList.remove('active');
    });
    document.addEventListener('click', function (e) {
      if (!sidebar.contains(e.target) && !btn.contains(e.target) && sidebar.classList.contains('expanded')) {
        sidebar.classList.remove('expanded');
        btn.classList.remove('active');
        overlay.classList.remove('active');
      }
    });
    document.addEventListener('keydown', function (e) {
      if (e.key === 'Escape' && sidebar.classList.contains('expanded')) {
        sidebar.classList.remove('expanded');
        btn.classList.remove('active');
        overlay.classList.remove('active');
      }
    });
  }

  // ============================================================
  // CONFIRM MODAL
  // ============================================================
  var confirmState = { callback: null };

  function closeConfirmModal() {
    var m = byId('adminConfirmModal');
    if (!m) return;
    m.classList.add('modal-exit');
    setTimeout(function () {
      m.classList.remove('active', 'modal-exit');
      document.body.style.overflow = 'auto';
    }, 250);
    confirmState.callback = null;
  }

  function openConfirmModal(config) {
    var m = byId('adminConfirmModal');
    var t = byId('adminConfirmTitle');
    var msg = byId('adminConfirmMessage');
    var ok = byId('adminConfirmOk');

    if (!m || !t || !msg || !ok) {
      if (window.confirm((config && config.message) || 'Continue?'))
        config && typeof config.onConfirm === 'function' && config.onConfirm();
      return;
    }

    t.textContent = (config && config.title) || 'Please Confirm';
    msg.textContent = (config && config.message) || 'Do you want to continue?';
    ok.textContent = (config && config.confirmText) || 'Confirm';
    confirmState.callback = (config && config.onConfirm) || null;

    m.classList.remove('modal-exit');
    m.classList.add('active');
    document.body.style.overflow = 'hidden';
  }

  // ============================================================
  // SUCCESS MODAL
  // ============================================================
  function closeSuccessModal() {
    var m = byId('adminSuccessModal');
    if (!m) return;
    m.classList.add('modal-exit');
    setTimeout(function () {
      m.classList.remove('active', 'modal-exit');
      document.body.style.overflow = 'auto';
    }, 250);
  }

  function openSuccessModal(titleText, messageText) {
    var m = byId('adminSuccessModal');
    var t = byId('adminSuccessTitle');
    var msg = byId('adminSuccessMessage');
    if (!m || !t || !msg) return;
    t.textContent = titleText || 'Success';
    msg.textContent = messageText || 'Action completed successfully.';
    m.classList.remove('modal-exit');
    m.classList.add('active');
    document.body.style.overflow = 'hidden';
  }

  // ============================================================
  // LOADING MODAL
  // ============================================================
  function closeLoadingModal() {
    var m = byId('adminLoadingModal');
    if (!m) return;
    m.classList.add('modal-exit');
    setTimeout(function () { m.classList.remove('active', 'modal-exit'); }, 250);
  }

  function openLoadingModal(messageText) {
    var m = byId('adminLoadingModal');
    var msg = byId('adminLoadingText');
    if (!m) return;
    if (msg) msg.textContent = messageText || 'Preparing your request with care.';
    m.classList.remove('modal-exit');
    m.classList.add('active');
  }

  // ============================================================
  // GLOBAL MODAL BUTTONS WIRING
  // ============================================================
  function initGlobalModalButtons() {
    var cancel = byId('adminConfirmCancel');
    var ok = byId('adminConfirmOk');
    var successOk = byId('adminSuccessOk');

    if (cancel) cancel.addEventListener('click', closeConfirmModal);
    if (successOk) successOk.addEventListener('click', closeSuccessModal);
    if (ok) {
      ok.addEventListener('click', function () {
        var cb = confirmState.callback;
        closeConfirmModal();
        if (typeof cb === 'function') cb();
      });
    }

    window.addEventListener('click', function (e) {
      if (e.target && e.target.id === 'adminConfirmModal') closeConfirmModal();
      if (e.target && e.target.id === 'adminSuccessModal') closeSuccessModal();
    });
  }

  // ============================================================
  // FLASH MESSAGES → success modal
  // ============================================================
  function initFlashModal() {
    var flashes = parseJsonScript('adminFlashData') || [];
    if (!Array.isArray(flashes) || !flashes.length) return;
    var first = flashes[0];
    var category = Array.isArray(first) ? first[0] : 'success';
    var text = Array.isArray(first) ? first[1] : '';
    if (!text) return;
    var titles = { success: 'Success', error: 'Error', danger: 'Error' };
    openSuccessModal(titles[category] || 'Notice', text);
  }

  // ============================================================
  // FORM CONFIRMATIONS + LOADING  ← KEY FIX HERE
  // ============================================================
  function initFormConfirmations() {
    document.addEventListener('submit', function (event) {
      var form = event.target;
      if (!form || form.tagName !== 'FORM') return;
      if ((form.method || '').toUpperCase() !== 'POST') return;

      // already confirmed — just submit (don't intercept again)
      if (form.dataset.noConfirm === 'true' || form.dataset.confirmed === 'true') {
        form.dataset.confirmed = '';
        return;
      }

      event.preventDefault();

      var actionField = form.querySelector('input[name="action"]');
      var actionName = actionField ? actionField.value : 'submit';
      var message = form.dataset.confirmMessage || ('Are you sure you want to ' + actionName + '?');

      openConfirmModal({
        title: 'Confirm Action',
        message: message,
        confirmText: 'Yes, Continue',
        onConfirm: function () {
          // show loading FIRST, then after short delay submit
          openLoadingModal(getLoadingText(actionName));
          setTimeout(function () {
            form.dataset.confirmed = 'true';
            form.submit();
          }, 600);   // ← 600ms: loading modal is clearly visible
        }
      });
    });

    // Download links
    document.querySelectorAll('a.download-link').forEach(function (link) {
      link.addEventListener('click', function (event) {
        event.preventDefault();
        var href = link.getAttribute('href');
        openConfirmModal({
          title: 'Download Report',
          message: 'Do you want to download this report now?',
          confirmText: 'Download',
          onConfirm: function () {
            openLoadingModal('Generating your report and preparing download...');
            setTimeout(function () { window.location.href = href; }, 600);
          }
        });
      });
    });
  }

  function getLoadingText(action) {
    var map = {
      add: 'Creating new item...',
      edit: 'Saving your changes...',
      delete: 'Deleting item...',
      update_profile: 'Updating profile...',
      change_password: 'Updating password...'
    };
    return map[action] || 'Processing your request...';
  }

  // ============================================================
  // CATEGORIES PAGE
  // ============================================================
  function initManageCategories() {
    if (!byId('addModal') || !byId('editModal') || !byId('deleteModal') || !byId('edit_id')) return;

    window.CategoryManager = {
      openEditModal: function (id, name, description, icon) {
        byId('edit_id').value = id;
        byId('edit_name').value = name;
        byId('edit_desc').value = description || '';
        byId('edit_icon').value = icon || '';
        ModalManager.open('editModal');
      },
      openDeleteModal: function (id) {
        byId('delete_id').value = id;
        ModalManager.open('deleteModal');
      }
    };
  }

  // ============================================================
  // ACTIVITIES PAGE
  // ============================================================
  function initManageActivities() {
    var grid = byId('activitiesGrid');
    if (!grid) return;

    function applyFilters() {
      var q = (byId('searchInput') ? byId('searchInput').value.toLowerCase().trim() : '');
      var cat = (byId('categoryFilter') ? byId('categoryFilter').value : '');
      var eng = (byId('energyFilter') ? byId('energyFilter').value : '');
      var loc = (byId('locationFilter') ? byId('locationFilter').value : '');
      grid.querySelectorAll('.premium-card').forEach(function (card) {
        var ok = (card.dataset.name || '').toLowerCase().indexOf(q) !== -1
          && (!cat || card.dataset.categoryId === cat)
          && (!eng || (card.dataset.energy || '').toLowerCase() === eng)
          && (!loc || (card.dataset.location || '').toLowerCase() === loc);
        card.style.display = ok ? '' : 'none';
      });
    }

    ['searchInput', 'categoryFilter', 'energyFilter', 'locationFilter'].forEach(function (id) {
      var el = byId(id);
      if (el) el.addEventListener(id === 'searchInput' ? 'input' : 'change', applyFilters);
    });

    window.viewActivity = function (card) {
      byId('view-title').innerText = card.dataset.name;
      byId('view-emoji').innerText = card.dataset.categoryIcon || '🎯';
      byId('view-category').innerText = card.dataset.categoryName;
      byId('view-type').innerText = card.dataset.type;
      byId('view-energy').innerText = card.dataset.energy || 'Not specified';
      byId('view-location').innerText = card.dataset.location || 'Not specified';
      byId('view-social').innerText = card.dataset.social || 'Not specified';
      byId('view-time').innerText = (card.dataset.minTime && card.dataset.maxTime)
        ? card.dataset.minTime + ' - ' + card.dataset.maxTime + ' mins' : 'Not specified';
      byId('view-budget').innerText = (card.dataset.minBudget || card.dataset.maxBudget)
        ? 'Rs.' + card.dataset.minBudget + ' - Rs.' + card.dataset.maxBudget : 'Free';
      byId('view-priority').innerText = card.dataset.priority || '0';
      byId('view-description').innerText = card.dataset.desc || 'No description provided';

      var tags = byId('view-mood-tags');
      tags.innerHTML = '';
      (card.dataset.moodTags || '').split(',').map(function (t) { return t.trim(); }).filter(Boolean).forEach(function (tag) {
        var s = document.createElement('span');
        s.className = 'mood-tag';
        s.textContent = tag;
        tags.appendChild(s);
      });

      byId('view-status').innerHTML = card.dataset.isActive === '1'
        ? '<span style="color:#10b981;font-weight:700;">✅ Active</span>'
        : '<span style="color:#ef4444;font-weight:700;">❌ Inactive</span>';

      ModalManager.open('viewModal');
    };

    window.editActivity = function (card) {
      var set = function (id, val) { var el = byId(id); if (el) el.value = val || ''; };
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
      var cb = byId('edit_is_active');
      if (cb) cb.checked = card.dataset.isActive === '1';
      ModalManager.open('editModal');
    };

    window.deleteActivity = function (card) {
      byId('delete_id').value = card.dataset.id;
      byId('delete-name-preview').textContent = card.dataset.name;
      ModalManager.open('deleteModal');
    };
  }

  // ============================================================
  // USERS PAGE
  // ============================================================
  function initManageUsers() {
    var modal = byId('viewUserModal');
    if (!modal) return;

    window.viewUser = function (card) {
      var u = JSON.parse(card.dataset.user);
      var fullName = ((u.first_name || '') + ' ' + (u.last_name || '')).trim();
      byId('detailFullName').innerText = fullName || u.username;
      byId('detailUsername').innerText = '@' + u.username;
      byId('detailId').innerText = '#' + (u.id || '0');
      byId('detailGender').innerText = u.gender || 'Not Specified';
      byId('detailBirth').innerText = u.date_of_birth || 'N/A';
      byId('detailPhone').innerText = u.phone_number || 'N/A';
      byId('detailEmail').innerText = u.email || 'N/A';
      byId('detailStreet').innerText = u.street_address || 'No address provided';
      byId('detailCity').innerText = u.city || '-';
      byId('detailState').innerText = u.state || '-';
      byId('detailPostal').innerText = u.postal_code || '-';
      byId('detailCountry').innerText = u.country || 'N/A';

      if (byId('detailJoined'))
        byId('detailJoined').innerText = u.created_at
          ? new Date(u.created_at).toLocaleDateString('en-GB', { day: 'numeric', month: 'long', year: 'numeric' })
          : 'N/A';

      var avatarDiv = byId('detailAvatar');
      avatarDiv.innerHTML = (u.profile_picture && u.profile_picture !== 'default.png')
        ? '<img src="/static/uploads/' + u.profile_picture + '" style="width:100%;height:100%;object-fit:cover;">'
        : '👤';

      modal.classList.remove('modal-exit');
      modal.classList.add('active');
      document.body.style.overflow = 'hidden';
    };

    window.closeViewModal = function () {
      modal.classList.add('modal-exit');
      setTimeout(function () {
        modal.classList.remove('active', 'modal-exit');
        document.body.style.overflow = 'auto';
      }, 250);
    };

    document.addEventListener('keydown', function (e) {
      if (e.key === 'Escape' && modal.classList.contains('active')) window.closeViewModal();
    });
    window.addEventListener('click', function (e) {
      if (e.target && e.target.id === 'viewUserModal') window.closeViewModal();
    });
  }

  // ============================================================
  // DASHBOARD CHART
  // ============================================================
  function initDashboard() {
    var canvas = byId('registrationChart');
    if (!canvas || typeof window.Chart === 'undefined') return;
    var data = parseJsonScript('adminDashboardData');
    if (!data) return;

    var ctx = canvas.getContext('2d');
    var gradient = ctx.createLinearGradient(0, 0, 0, 350);
    gradient.addColorStop(0, 'rgba(190,18,60,0.3)');
    gradient.addColorStop(0.5, 'rgba(236,72,153,0.15)');
    gradient.addColorStop(1, 'rgba(190,18,60,0.02)');

    new Chart(ctx, {
      type: 'line',
      data: {
        labels: data.chart_labels || [],
        datasets: [{
          label: 'New Registrations',
          data: data.chart_data || [],
          borderColor: '#be123c', backgroundColor: gradient,
          borderWidth: 3, tension: 0.4, fill: true,
          pointRadius: 7, pointHoverRadius: 10,
          pointBackgroundColor: '#fff', pointBorderColor: '#be123c', pointBorderWidth: 3
        }]
      },
      options: {
        responsive: true, maintainAspectRatio: false,
        interaction: { mode: 'index', intersect: false },
        plugins: { legend: { display: true, position: 'top', labels: { font: { size: 14, weight: 'bold' }, color: '#1e293b', usePointStyle: true, padding: 15 } } },
        scales: {
          y: { beginAtZero: true, ticks: { color: '#64748b', stepSize: 1, precision: 0, callback: function (v) { return Number.isInteger(v) ? v : null; } }, grid: { color: 'rgba(190,18,60,0.08)', drawBorder: false } },
          x: { grid: { display: false, drawBorder: false }, ticks: { color: '#64748b' } }
        }
      }
    });

    var userSearch = byId('userSearch');
    if (userSearch) {
      userSearch.addEventListener('input', function (e) {
        var term = e.target.value.toLowerCase();
        document.querySelectorAll('.users-table tbody tr').forEach(function (row) {
          row.style.display = row.innerText.toLowerCase().indexOf(term) !== -1 ? '' : 'none';
        });
      });
    }
  }

  // ============================================================
  // ANALYTICS CHARTS
  // ============================================================
  function initAnalytics() {
    if (typeof window.Chart === 'undefined' || !byId('categoryUsageChart')) return;
    var data = parseJsonScript('adminAnalyticsData');
    if (!data) return;

    new Chart(byId('categoryUsageChart').getContext('2d'), {
      type: 'bar',
      data: { labels: data.category_labels || [], datasets: [{ label: 'Usage Count', data: data.category_counts || [], backgroundColor: 'rgba(190,18,60,0.7)', borderColor: '#be123c', borderWidth: 2, borderRadius: 8 }] },
      options: { responsive: true, maintainAspectRatio: true, plugins: { legend: { display: false } }, scales: { y: { beginAtZero: true } } }
    });

    new Chart(byId('moodDistChart').getContext('2d'), {
      type: 'doughnut',
      data: { labels: ['Positive', 'Neutral', 'Negative'], datasets: [{ data: [data.mood_positive || 0, data.mood_neutral || 0, data.mood_negative || 0], backgroundColor: ['#10b981', '#6366f1', '#ef4444'], borderColor: '#fff', borderWidth: 3 }] },
      options: { responsive: true, plugins: { legend: { display: false } }, cutout: '65%' }
    });

    new Chart(byId('moodTrendsChart').getContext('2d'), {
      type: 'line',
      data: {
        labels: data.mood_trend_labels || [], datasets: [
          { label: 'Positive', data: data.mood_trend_positive || [], borderColor: '#10b981', backgroundColor: 'rgba(16,185,129,0.1)', fill: true, tension: 0.4 },
          { label: 'Neutral', data: data.mood_trend_neutral || [], borderColor: '#6366f1', backgroundColor: 'rgba(99,102,241,0.1)', fill: true, tension: 0.4 },
          { label: 'Negative', data: data.mood_trend_negative || [], borderColor: '#ef4444', backgroundColor: 'rgba(239,68,68,0.1)', fill: true, tension: 0.4 }
        ]
      },
      options: { responsive: true, plugins: { legend: { display: true } }, scales: { y: { beginAtZero: true } } }
    });

    new Chart(byId('feedbackChart').getContext('2d'), {
      type: 'bar',
      data: { labels: ['1 Star', '2 Stars', '3 Stars', '4 Stars', '5 Stars'], datasets: [{ label: 'Feedback Count', data: data.feedback_distribution || [0, 0, 0, 0, 0], backgroundColor: ['rgba(239,68,68,0.7)', 'rgba(251,146,60,0.7)', 'rgba(250,204,21,0.7)', 'rgba(163,230,53,0.7)', 'rgba(34,197,94,0.7)'], borderRadius: 8 }] },
      options: { responsive: true, plugins: { legend: { display: false } }, scales: { y: { beginAtZero: true } } }
    });

    if (byId('interestActivityChart') && data.interest_labels && data.interest_labels.length) {
      new Chart(byId('interestActivityChart').getContext('2d'), {
        type: 'bar',
        data: { labels: data.interest_labels, datasets: [{ label: 'Activity Tries', data: data.interest_activity_tries || [], backgroundColor: 'rgba(99,102,241,0.7)', borderColor: '#6366f1', borderWidth: 2, borderRadius: 8 }] },
        options: { responsive: true, plugins: { legend: { display: false } }, scales: { y: { beginAtZero: true } } }
      });
    }
  }

  // ============================================================
  // INJECT ANIMATION CSS
  // ============================================================
  function injectModalCSS() {
    var style = document.createElement('style');
    style.textContent = [
      /* --- page modals (.modal class) --- */
      '.modal { transition: opacity 0.25s ease; opacity: 0; }',
      '.modal.active { opacity: 1; }',
      '.modal.active .modal-content, .modal.active .admin-global-modal-content, .modal.active .admin-loading-card {',
      '  animation: mmSlideIn 0.28s cubic-bezier(0.34,1.4,0.64,1) forwards; }',
      '.modal.modal-exit { opacity: 0; transition: opacity 0.25s ease; }',
      '.modal.modal-exit .modal-content, .modal.modal-exit .admin-global-modal-content, .modal.modal-exit .admin-loading-card {',
      '  animation: mmSlideOut 0.22s ease forwards; }',

      /* --- admin global modals --- */
      '.admin-global-modal { transition: opacity 0.25s ease; opacity: 0; }',
      '.admin-global-modal.active { opacity: 1; }',
      '.admin-global-modal.active .admin-global-modal-content {',
      '  animation: mmSlideIn 0.28s cubic-bezier(0.34,1.4,0.64,1) forwards; }',
      '.admin-global-modal.modal-exit { opacity: 0; transition: opacity 0.25s ease; }',
      '.admin-global-modal.modal-exit .admin-global-modal-content {',
      '  animation: mmSlideOut 0.22s ease forwards; }',

      /* --- loading modal --- */
      '.admin-loading-modal { transition: opacity 0.25s ease; opacity: 0; }',
      '.admin-loading-modal.active { opacity: 1; }',
      '.admin-loading-modal.active .admin-loading-card {',
      '  animation: mmSlideIn 0.28s cubic-bezier(0.34,1.4,0.64,1) forwards; }',
      '.admin-loading-modal.modal-exit { opacity: 0; transition: opacity 0.25s ease; }',
      '.admin-loading-modal.modal-exit .admin-loading-card {',
      '  animation: mmSlideOut 0.22s ease forwards; }',

      /* --- keyframes --- */
      '@keyframes mmSlideIn {',
      '  from { transform: translateY(-24px) scale(0.93); opacity: 0; }',
      '  to   { transform: translateY(0)     scale(1);    opacity: 1; } }',

      '@keyframes mmSlideOut {',
      '  from { transform: translateY(0)    scale(1);    opacity: 1; }',
      '  to   { transform: translateY(16px) scale(0.95); opacity: 0; } }'
    ].join('\n');
    document.head.appendChild(style);
  }

  // ============================================================
  // BOOT
  // ============================================================
  function init() {
    injectModalCSS();

    window.ModalManager = ModalManager;
    window.openModal = function (id) { ModalManager.open(id); };
    window.closeModal = function (id) { ModalManager.close(id); };
    window.openLoadingModal = openLoadingModal;
    window.closeLoadingModal = closeLoadingModal;

    ModalManager.init();
    initSidebar();
    initGlobalModalButtons();
    initFormConfirmations();
    initFlashModal();

    initManageCategories();
    initManageActivities();
    initManageUsers();
    initDashboard();
    initAnalytics();

    closeLoadingModal();   // hide any leftover loading on page load
  }

  document.addEventListener('DOMContentLoaded', init);
})();