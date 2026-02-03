function openModal(id) { document.getElementById(id).classList.add('active'); }
    function closeModal(id) { document.getElementById(id).classList.remove('active'); }

    function openEditModal(id, name, desc, icon) {
        document.getElementById('edit_id').value = id;
        document.getElementById('edit_name').value = name;
        document.getElementById('edit_desc').value = desc;
        document.getElementById('edit_icon').value = icon;
        openModal('editModal');
    }

    function openDeleteModal(id) {
        document.getElementById('delete_id').value = id;
        openModal('deleteModal');
    }

    window.onclick = function (event) {
        if (event.target.classList.contains('modal')) {
            event.target.classList.remove('active');
        }
    }

 function openModal(id) { document.getElementById(id).classList.add('active'); }
    function closeModal(id) { document.getElementById(id).classList.remove('active'); }

    function viewActivity(btn) {
        const row = btn.closest('tr');
        document.getElementById('view_name').innerText = row.getAttribute('data-name');
        document.getElementById('view_type').innerText = row.getAttribute('data-type').charAt(0).toUpperCase() + row.getAttribute('data-type').slice(1);
        document.getElementById('view_priority').innerText = row.getAttribute('data-priority');
        document.getElementById('view_energy').innerText = row.getAttribute('data-energy') || '—';
        openModal('viewModal');
    }

    function editActivity(btn) {
        const row = btn.closest('tr');
        document.getElementById('edit_id').value = row.getAttribute('data-id');
        document.getElementById('edit_name').value = row.getAttribute('data-name');
        document.getElementById('edit_type').value = row.getAttribute('data-type');
        document.getElementById('edit_priority').value = row.getAttribute('data-priority');
        document.getElementById('edit_description').value = row.getAttribute('data-description');
        openModal('editModal');
    }

    function deleteActivity(btn) {
        const row = btn.closest('tr');
        document.getElementById('delete_id').value = row.getAttribute('data-id');
        openModal('deleteModal');
    }

    // Close modal on outside click
    window.onclick = function(event) {
        if (event.target.classList.contains('modal')) {
            event.target.classList.remove('active');
        }
    }

    // Close modal on ESC key
    document.addEventListener('keydown', function(e) {
        if (e.key === 'Escape') {
            document.querySelectorAll('.modal.active').forEach(modal => {
                modal.classList.remove('active');
            });
        }
    });

    function viewUser(btn) {
        const user = JSON.parse(btn.dataset.user);
        
        document.getElementById("detailFullName").innerText =
            `${user.first_name || ""} ${user.last_name || ""}`.trim() || user.username;
        
        document.getElementById("detailUsername").innerText = `@${user.username}`;
        document.getElementById("detailEmail").innerText = user.email || "—";
        
        const avatar = document.getElementById("detailAvatar");
        if (user.profile_picture) {
            avatar.innerHTML = `<img src="/static/uploads/${user.profile_picture}" style="width:100%; height:100%; object-fit:cover;">`;
        } else {
            avatar.innerHTML = `<span style="font-size: 2.5rem;">👤</span>`;
        }
        
        document.getElementById("viewUserModal").classList.add('active');
    }

    function closeViewModal() {
        document.getElementById("viewUserModal").classList.remove('active');
    }

    // Close modal on outside click
    window.onclick = function(event) {
        const modal = document.getElementById("viewUserModal");
        if (event.target === modal) {
            modal.classList.remove('active');
        }
    }

    // Close modal on ESC key
    document.addEventListener('keydown', function(e) {
        if (e.key === 'Escape') {
            const modal = document.getElementById("viewUserModal");
            if (modal.classList.contains('active')) {
                modal.classList.remove('active');
            }
        }
    });

    