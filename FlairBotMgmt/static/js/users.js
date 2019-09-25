function clearInvalidState(textBox) {
    textBox.className = "form-control"
}

function toggleUser(username, enabled) {
    $.ajax({
        data: {
            username: username,
            enabled: enabled
        },
        type: 'POST',
        url: '/api/user/toggle'
    })
        .done(function notify(data) {
            var elem = document.getElementById(`${data.username}_toggle`);
            var icon = document.getElementById(`${data.username}_icon`);
            if (data.enabled) {
                elem.textContent = "Disable";
                elem.style.color = "#E74C3C";
                icon.setAttribute("class", "fas fa-check");
                icon.style.color = "#00bc8c";
                var toastStatus = "enabled";
            }
            if (!data.enabled) {
                elem.textContent = "Enable";
                elem.style.color = "#00bc8c";
                icon.setAttribute("class", "fas fa-times");
                icon.style.color = "#E74C3C";
                var toastStatus = "disabled";
            }
            elem.setAttribute("class", "dropdown-item");
            popNotification(`Successfully ${toastStatus} user ${data.username}`, data.error);
        });
}

$(document).ready(function () {
    $("#users").tablesorter({
        theme: "bootstrap",
        cancelSelection: false,
        sortReset: true
    });
});

function showDeleteModal(username, row_id) {
    document.getElementById('delete-modal-body').innerHTML = `Are you <strong>sure</strong> you want to delete ${username}?`;
    document.getElementById('delete-modal-footer').innerHTML = `<button type="button" class="btn btn-secondary" data-dismiss="modal">Close</button><button type="button" class="btn btn-danger" onclick="deleteUser('${username}',${row_id})" data-dismiss="modal" id="deleteConfirm">Delete this user</button>`;
    $('#confirmationModal').modal('show')
}

function deleteUser(username, row_id) {
    $('#confirmationModal').modal('hide');
    $.ajax({
        data: {
            username: username
        },
        type: 'POST',
        url: '/api/user/delete'
    })
        .done(function (data) {
            console.log(data);
            if (data.success) {
                popNotification(`Successfully deleted user ${data.username}`, data.error);
                document.getElementById("users").deleteRow(row_id);
            }
        });
    event.preventDefault();
    return false;
}

$(function () {
    let form = document.getElementById('createUserForm');

    $('[data-toggle="tooltip"]').tooltip();

    $('#userCreate').click(function () {
        let username = document.getElementById('username');
        let password = document.getElementById('password');
        let usernameFeedback = document.getElementById('usernameFeedback');
        let adminToggle = document.getElementById('adminToggle');

        if (form.checkValidity()) {
            $('#userCreate').prop('disabled', true);
            $('#userCreate').html('<span class="spinner-grow spinner-grow-sm" role="status" aria-hidden="true"></span>Creating...');
            $.ajax({
                data: {
                    username: username.value,
                    password: password.value,
                    adminToggle: adminToggle.checked
                },
                type: 'POST',
                url: '/api/user/create'
            })
                .done(function (data) {
                    console.log(data);
                    if (data.userExists) {
                        username.className = "form-control is-invalid";
                        usernameFeedback.innerText = "That username is taken!"
                        $('#userCreate').prop('disabled', false);
                        $('#userCreate').prop('class', 'btn btn-primary');
                        $('#userCreate').html('Create');
                    }
                    if (!data.userExists) {
                        let usersTable = document.getElementById('users');
                        let row = usersTable.insertRow();
                        let username = row.insertCell();
                        username.innerHTML = `<a href="/u/${data.user.username}">${data.user.username}</a>`;
                        let admin = row.insertCell();
                        if (data.user.admin) {
                            admin.innerHTML = `<i class="fas fa-check" style="font-size: 28px;color: #00bc8c"></i>`;
                        } else {
                            admin.innerHTML = `<i class="fas fa-times" style="font-size: 28px; color: #E74C3C"></i>`;
                        }
                        let created = row.insertCell();
                        created.innerHTML = data.user.created;
                        let updated = row.insertCell();
                        updated.innerHTML = data.user.updated;
                        let updatedby = row.insertCell();
                        updatedby.innerHTML = data.user.updatedby;
                        let enabled = row.insertCell();
                        enabled.innerHTML = `<i class="fas fa-check" id="${data.user.username}_icon" style="font-size: 28px;color: #00bc8c"></i>`;
                        let edit = row.insertCell();
                        edit.innerHTML = `
                            <div class="btn-group" role="group" aria-label="Button group with nested dropdown">
                                <button type="button" class="btn btn-primary" onclick="location.href='/u/${data.user.username}'">Edit</button>
                                <div class="btn-group" role="group">
                                    <button id="btnGroupDrop1" type="button" class="btn btn-primary dropdown-toggle" data-toggle="dropdown" aria-haspopup="true" aria-expanded="false"></button>
                                    <div class="dropdown-menu" aria-labelledby="btnGroupDrop1">
                                        <a class="dropdown-item" href="/u/${data.user.username}">Edit</a>
                                        <a class="dropdown-item" id="${data.user.username}_toggle" style="color: #00bc8c" onclick="toggleUser('${data.user.username}', true)">Enable</a>
                                        <div class="dropdown-divider"></div>
                                        <a class="dropdown-item" onclick="showDeleteModal('${data.user.username}', ${row.rowIndex})" style="color: red">Delete</a>
                                    </div>
                                </div>
                            </div>`;
                        $('#userCreate').html('Created');
                        $('#newUserModal').modal('hide');
                        $('#userCreate').prop('disabled', false);
                        $('#userCreate').prop('class', 'btn btn-primary');
                        $('#userCreate').html('Create');
                    }
                    popNotification(data.success, data.error);
                });
        }
    });
});