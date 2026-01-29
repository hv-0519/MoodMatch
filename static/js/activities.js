document.addEventListener('DOMContentLoaded', function() {
    console.log('Initializing Activity Management...');
    
    // Get all modal elements
    const addModal = document.getElementById('addModal');
    const editModal = document.getElementById('editModal');
    const deleteModal = document.getElementById('deleteModal');
    const viewModal = document.getElementById('viewModal');
    
    // Get all buttons
    const addActivityBtn = document.getElementById('addActivityBtn');
    const addFirstActivityBtn = document.getElementById('addFirstActivityBtn');
    const closeAddBtn = document.getElementById('closeAddBtn');
    const closeEditBtn = document.getElementById('closeEditBtn');
    const closeDeleteBtn = document.getElementById('closeDeleteBtn');
    const closeViewBtn = document.getElementById('closeViewBtn');
    
    // Modal functions
    function openAddModal() {
        console.log('Opening Add Modal');
        addModal.classList.add('active');
    }
    
    function closeAddModal() {
        console.log('Closing Add Modal');
        addModal.classList.remove('active');
        document.getElementById('add_name').value = '';
        document.getElementById('add_type').value = '';
        document.getElementById('add_priority').value = '1';
        const descField = document.getElementById('add_description');
        if (descField) descField.value = '';
    }
    
    function openEditModal(id, name, type, priority) {
        console.log('Opening Edit Modal for ID:', id);
        document.getElementById('edit_id').value = id;
        document.getElementById('edit_name').value = name;
        document.getElementById('edit_type').value = type;
        document.getElementById('edit_priority').value = priority;
        editModal.classList.add('active');
    }
    
    function closeEditModal() {
        console.log('Closing Edit Modal');
        editModal.classList.remove('active');
    }
    
    function openDeleteModal(id) {
        console.log('Opening Delete Modal for ID:', id);
        document.getElementById('delete_id').value = id;
        deleteModal.classList.add('active');
    }
    
    function closeDeleteModal() {
        console.log('Closing Delete Modal');
        deleteModal.classList.remove('active');
    }
    
    function openViewModal(id, name, type, priority) {
        console.log('Opening View Modal for ID:', id);
        document.getElementById('view_id').textContent = '#' + id;
        document.getElementById('view_name').textContent = name;
        document.getElementById('view_type').textContent = type.charAt(0).toUpperCase() + type.slice(1);
        document.getElementById('view_priority').textContent = priority;
        viewModal.classList.add('active');
    }
    
    function closeViewModal() {
        console.log('Closing View Modal');
        viewModal.classList.remove('active');
    }
    
    // Attach button listeners
    if (addActivityBtn) {
        addActivityBtn.addEventListener('click', function(e) {
            e.preventDefault();
            openAddModal();
        });
    }
    
    if (addFirstActivityBtn) {
        addFirstActivityBtn.addEventListener('click', function(e) {
            e.preventDefault();
            openAddModal();
        });
    }
    
    if (closeAddBtn) closeAddBtn.addEventListener('click', closeAddModal);
    if (closeEditBtn) closeEditBtn.addEventListener('click', closeEditModal);
    if (closeDeleteBtn) closeDeleteBtn.addEventListener('click', closeDeleteModal);
    if (closeViewBtn) closeViewBtn.addEventListener('click', closeViewModal);
    
    // Table action buttons
    const tableBody = document.getElementById('activitiesTableBody');
    if (tableBody) {
        tableBody.addEventListener('click', function(e) {
            const button = e.target.closest('.admin-icon-btn');
            if (!button) return;
            
            e.preventDefault();
            
            const row = button.closest('tr');
            const id = row.getAttribute('data-id');
            const name = row.getAttribute('data-name');
            const type = row.getAttribute('data-type');
            const priority = row.getAttribute('data-priority');
            
            if (button.classList.contains('view-btn')) {
                openViewModal(id, name, type, priority);
            } else if (button.classList.contains('edit-btn')) {
                openEditModal(id, name, type, priority);
            } else if (button.classList.contains('delete-btn')) {
                openDeleteModal(id);
            }
        });
    }
    
    // Close modals on backdrop click
    [addModal, editModal, deleteModal, viewModal].forEach(modal => {
        if (modal) {
            modal.addEventListener('click', function(e) {
                if (e.target === this) {
                    this.classList.remove('active');
                }
            });
        }
    });
    
    // Search functionality
    const searchInput = document.getElementById('activitySearch');
    if (searchInput && tableBody) {
        searchInput.addEventListener('keyup', function(e) {
            const searchTerm = e.target.value.toLowerCase();
            const rows = tableBody.querySelectorAll('tr');
            
            rows.forEach(row => {
                const text = row.textContent.toLowerCase();
                row.style.display = text.includes(searchTerm) ? '' : 'none';
            });
        });
    }
    
    console.log('✓ Initialization complete!');
});
