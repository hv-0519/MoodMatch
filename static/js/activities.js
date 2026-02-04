function openModal(id) {
        document.getElementById(id).classList.add('active');
        document.body.style.overflow = 'hidden';
    }

    function closeModal(id) {
        document.getElementById(id).classList.remove('active');
        document.body.style.overflow = 'auto';
    }

    // ==================== FILTERING ====================
    const searchInput = document.getElementById('searchInput');
    const categoryFilter = document.getElementById('categoryFilter');
    const energyFilter = document.getElementById('energyFilter');
    const locationFilter = document.getElementById('locationFilter');
    const grid = document.getElementById('activitiesGrid');

    function applyFilters() {
        const searchTerm = searchInput.value.toLowerCase().trim();
        const selectedCategory = categoryFilter.value;
        const selectedEnergy = energyFilter.value;
        const selectedLocation = locationFilter.value;

        const cards = grid.querySelectorAll('.premium-card');

        cards.forEach(card => {
            const name = card.dataset.name.toLowerCase();
            const categoryId = card.dataset.categoryId;
            const energy = card.dataset.energy.toLowerCase();
            const location = card.dataset.location.toLowerCase();

            const matchesSearch = name.includes(searchTerm);
            const matchesCategory = !selectedCategory || categoryId === selectedCategory;
            const matchesEnergy = !selectedEnergy || energy === selectedEnergy;
            const matchesLocation = !selectedLocation || location === selectedLocation;

            card.style.display = (matchesSearch && matchesCategory && matchesEnergy && matchesLocation) ? '' : 'none';
        });
    }

    searchInput.addEventListener('input', applyFilters);
    categoryFilter.addEventListener('change', applyFilters);
    energyFilter.addEventListener('change', applyFilters);
    locationFilter.addEventListener('change', applyFilters);

    // ==================== VIEW ACTIVITY ====================
    function viewActivity(card) {
        document.getElementById('view-title').innerText = card.dataset.name;
        document.getElementById('view-emoji').innerText = card.dataset.categoryIcon;
        document.getElementById('view-category').innerText = card.dataset.categoryName;
        document.getElementById('view-type').innerText = card.dataset.type;
        document.getElementById('view-energy').innerText = card.dataset.energy || 'Not specified';
        document.getElementById('view-location').innerText = card.dataset.location || 'Not specified';
        document.getElementById('view-social').innerText = card.dataset.social || 'Not specified';

        const minTime = card.dataset.minTime || 0;
        const maxTime = card.dataset.maxTime || 0;
        document.getElementById('view-time').innerText = minTime && maxTime ? `${minTime} - ${maxTime} mins` : 'Not specified';

        const minBudget = card.dataset.minBudget || 0;
        const maxBudget = card.dataset.maxBudget || 0;
        document.getElementById('view-budget').innerText = minBudget || maxBudget ? `₹${minBudget} - ₹${maxBudget}` : 'Free';

        document.getElementById('view-priority').innerText = card.dataset.priority || '0';
        document.getElementById('view-description').innerText = card.dataset.desc || 'No description provided';

        // Mood tags
        const moodTagsContainer = document.getElementById('view-mood-tags');
        moodTagsContainer.innerHTML = '';
        const moodTags = card.dataset.moodTags.split(',').map(tag => tag.trim());
        moodTags.forEach(tag => {
            const span = document.createElement('span');
            span.className = 'mood-tag';
            span.textContent = tag;
            moodTagsContainer.appendChild(span);
        });

        const isActive = card.dataset.isActive === '1';
        document.getElementById('view-status').innerHTML = isActive
            ? '<span style="color:#10b981; font-weight:700;">✅ Active</span>'
            : '<span style="color:#ef4444; font-weight:700;">❌ Inactive</span>';

        openModal('viewModal');
    }

    // ==================== EDIT ACTIVITY ====================
    function editActivity(card) {
        document.getElementById('edit_id').value = card.dataset.id;
        document.getElementById('edit_name').value = card.dataset.name;
        document.getElementById('edit_execution_type').value = card.dataset.type;
        document.getElementById('edit_category_id').value = card.dataset.categoryId;
        document.getElementById('edit_priority').value = card.dataset.priority;
        document.getElementById('edit_mood_tags').value = card.dataset.moodTags;
        document.getElementById('edit_description').value = card.dataset.desc;
        document.getElementById('edit_energy_level').value = card.dataset.energy;
        document.getElementById('edit_location_type').value = card.dataset.location;
        document.getElementById('edit_social_type').value = card.dataset.social;
        document.getElementById('edit_min_time').value = card.dataset.minTime;
        document.getElementById('edit_max_time').value = card.dataset.maxTime;
        document.getElementById('edit_min_budget').value = card.dataset.minBudget;
        document.getElementById('edit_max_budget').value = card.dataset.maxBudget;
        document.getElementById('edit_is_active').checked = card.dataset.isActive === '1';

        openModal('editModal');
    }

    // ==================== DELETE ACTIVITY ====================
    function deleteActivity(card) {
        document.getElementById('delete_id').value = card.dataset.id;
        document.getElementById('delete-name-preview').textContent = card.dataset.name;
        openModal('deleteModal');
    }

    // ==================== CLOSE ON OUTSIDE CLICK ====================
    window.onclick = function (e) {
        if (e.target.classList.contains('modal')) {
            e.target.classList.remove('active');
            document.body.style.overflow = 'auto';
        }
    };

    // ==================== ESCAPE KEY CLOSES MODAL ====================
    document.addEventListener('keydown', function (e) {
        if (e.key === 'Escape') {
            document.querySelectorAll('.modal.active').forEach(modal => {
                modal.classList.remove('active');
            });
            document.body.style.overflow = 'auto';
        }
    });