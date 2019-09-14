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
            popNotification(`Successfully ${toastStatus} "${data.username}"!`, data.error);
        });
}

function deleteUser(username) {
    $('#confirmationModal').modal('hide');
    $('#delete').prop('disabled', true);
    $('#delete').html('<div class="spinner-grow spinner-grow-sm text-primary" role="status"></div> Deleting...');
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
                popNotification(`Successfully deleted user "${data.useranem}"!`, data.error);
                $('#delete').html('Deleted');
                $('#delete').prop('class', 'btn btn-danger');
            }
        });
    event.preventDefault();
    return false;
}

function saveUser() {
    let form = document.getElementById('createUserForm')
    let currentUser = document.getElementById('currentUser');
    let username = document.getElementById('username');
    let password = document.getElementById('password');
    let usernameFeedback = document.getElementById('usernameFeedback');
    let adminToggle = document.getElementById('adminToggle');

    if (form.checkValidity()) {
        $('#submit').prop('disabled', true);
        $('#submit').html('<span class="spinner-grow spinner-grow-sm" role="status" aria-hidden="true"></span>Saving...');
        $.ajax({
            data: {
                user: currentUser.innerText,
                username: username.value,
                password: password.value,
                adminToggle: adminToggle.checked
            },
            type: 'POST',
            url: '/api/user/edit'
        })
            .done(function (data) {
                if (data.userExists) {
                    username.className = "form-control is-invalid";
                    usernameFeedback.innerText = "That username is taken!"
                    $('#submit').prop('disabled', false);
                    $('#submit').prop('class', 'btn btn-primary');
                    $('#submit').html('Submit Changes');
                }
                if (!data.userExists) {
                    $('#submit').html('Updated');
                    $('#submit').prop('disabled', false);
                    $('#submit').prop('class', 'btn btn-primary');
                    $('#submit').html('Submit Changes');
                }
                popNotification(data.success, data.error);
            });
    }
};
$(function () {
    let updatePasswordToggle = document.getElementById('updatePasswordToggle');
    let passowrdEntry = document.getElementById('passowrdEntry');
    let passowrdInput = document.getElementById('password');
    passowrdEntry.hidden = !updatePasswordToggle.checked;
    passowrdInput.required = updatePasswordToggle.checked;

    $("#updatePasswordToggle").click(function () {
        passowrdEntry.hidden = !updatePasswordToggle.checked;
        passowrdInput.required = updatePasswordToggle.checked;
    });
    $("#createUserForm").submit(function (e) {
        e.preventDefault();
    });
});