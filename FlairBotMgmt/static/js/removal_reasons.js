function clearInvalidState(textBox) {
    textBox.className = "form-control"
}

function deleteFlair(reason_id, row_id) {
    $('#confirmationModal').modal('hide');
    $.ajax({
        data: {
            reason_id: reason_id
        },
        type: 'POST',
        url: '/api/reason/delete'
    })
        .done(function (data) {
            console.log(data);
            if (data.success) {
                popNotification(`Successfully deleted flair "${data.flair_text}" for r/${data.subreddit}`, data.error);
                document.getElementById("reasons").deleteRow(row_id);
            }
        });
    event.preventDefault();
    return false;
}

function showDeleteModalFlair(flair_text, subreddit, flair_id, row_id) {
    document.getElementById('delete-modal-body').innerHTML = `Are you <strong>sure</strong> you want to delete the "${flair_text}" flair for /r/${subreddit}?`;
    document.getElementById('delete-modal-footer').innerHTML = `<button type="button" class="btn btn-secondary" data-dismiss="modal">Close</button><button type="button" class="btn btn-danger" onclick="deleteFlair(${flair_id}, ${row_id})" data-dismiss="modal" id="deleteConfirm">Delete this flair</button>`;
    $('#confirmationModal').modal('show')
}

function resetForm(preserveSubreddit) {
    // let subreddit = document.getElementById('subreddit');
    // let flair_text = document.getElementById('flair_text');
    // let description = document.getElementById('description');
    // let lockToggle = document.getElementById('lockToggle');
    // let commentLockToggle = document.getElementById('commentLockToggle');
    // let banToggle = document.getElementById('banToggle');
    // let ban_duration = document.getElementById('ban_duration');
    // let ban_reason = document.getElementById('ban_reason');
    // let ban_message = document.getElementById('ban_message');
    // let ban_note = document.getElementById('ban_note');
    // let usernoteToggle = document.getElementById('usernoteToggle');
    // let usernote_note = document.getElementById('usernote_note');
    // let usernote_warning_type = document.getElementById('usernote_warning_type');
    // let commentToggle = document.getElementById('commentToggle');
    // let commentInput = document.getElementById('commentinput');
    // let commentOutput = document.getElementById('commentoutput');
    // let enableOnAdd = document.getElementById('enableOnAdd');
    // let banGroup = document.getElementById('banGroup');
    // let usernoteGroup = document.getElementById('usernoteGroup');
    // let commentEntry = document.getElementById('commentEntry');
    // if (!preserveSubreddit) {
    //     subreddit.value = ""
    // }
    // flair_text.value = null;
    // description.value = null;
    // lockToggle.checked = false;
    // commentLockToggle.checked = false;
    // banToggle.checked = false;
    // ban_duration.value = 0;
    // ban_reason.value = null;
    // ban_message.value = null;
    // ban_note.value = null;
    // usernoteToggle.checked = false;
    // usernote_note.value = null;
    // usernote_warning_type.value = null;
    // commentToggle.checked = false;
    // commentInput.value = null;
    // commentOutput.value = null;
    // enableOnAdd.checked = true;
    // commentEntry.hidden = !commentToggle.checked;
    // banGroup.hidden = !banToggle.checked;
    // usernoteGroup.hidden = !usernoteToggle.checked;
    document.getElementById('createRemovalReasonForm').reset()
}

function toggleReason(id, enabled) {
    $.ajax({
        data: {
            id: id,
            enabled: enabled
        },
        type: 'POST',
        url: '/api/reason/toggle'
    })
        .done(function notify(data) {
            var elem = document.getElementById(`${data.id}_toggle`);
            var icon = document.getElementById(`${data.id}_icon`);
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
            popNotification(`Successfully ${toastStatus} "${data.flair_text}"!`, data.error);
        });
}

$(document).ready(function () {
    $("#reasons").tablesorter({
        theme: "bootstrap",
        cancelSelection: false,
        sortReset: true
    });
});

$(function () {
    let form = document.getElementById('createRemovalReasonForm');
    let commentToggle = document.getElementById('commentToggle');
    let banToggle = document.getElementById('banToggle');
    let usernoteToggle = document.getElementById('usernoteToggle');
    let banGroup = document.getElementById('banGroup');
    let usernoteGroup = document.getElementById('usernoteGroup');
    let commentEntry = document.getElementById('commentEntry');
    let commentInput = document.getElementById('commentinput');
    commentEntry.hidden = !commentToggle.checked;
    commentInput.required = commentToggle.checked;
    banGroup.hidden = !banToggle.checked;
    usernoteGroup.hidden = !usernoteToggle.checked;

    $('[data-toggle="tooltip"]').tooltip();

    function createRow(data) {
        let reasonsTable = document.getElementById('reasons');
        let row = reasonsTable.insertRow();
        let flair_text = row.insertCell();
        flair_text.innerHTML = `<a href="/reasons/${data.reason.id}">${data.reason.flair_text}</a>`;
        let description = row.insertCell();
        description.innerHTML = data.reason.description;
        let subreddit = row.insertCell();
        subreddit.innerHTML = `<a href="/subreddits/${data.reason.subreddit}">${data.reason.subreddit}</a>`;
        let comment = row.insertCell();
        if (data.reason.comment) {
            comment.innerHTML = `<i class="fas fa-check" id="${data.reason.id}_comment_icon" style="font-size: 28px;color: #00bc8c"></i>`
        } else {
            comment.innerHTML = `<i class="fas fa-times" id="${data.reason.id}_comment_icon" style="font-size: 28px; color: #E74C3C"></i>`
        }
        let lock = row.insertCell();
        if (data.reason.lock) {
            lock.innerHTML = `<i class="fas fa-check" id="${data.reason.id}_lock_icon" style="font-size: 28px;color: #00bc8c"></i>`
        } else {
            lock.innerHTML = `<i class="fas fa-times" id="${data.reason.id}_lock_icon" style="font-size: 28px; color: #E74C3C"></i>`
        }
        let lock_comment = row.insertCell();
        if (data.reason.lock_comment) {
            lock_comment.innerHTML = `<i class="fas fa-check" id="${data.reason.id}_lock_comment_icon" style="font-size: 28px;color: #00bc8c"></i>`
        } else {
            lock_comment.innerHTML = `<i class="fas fa-times" id="${data.reason.id}_lock_comment_icon" style="font-size: 28px; color: #E74C3C"></i>`
        }
        let ban = row.insertCell();
        if (data.reason.ban) {
            ban.innerHTML = `<i class="fas fa-check" id="${data.reason.id}_ban_icon" style="font-size: 28px;color: #00bc8c"></i>`
        } else {
            ban.innerHTML = `<i class="fas fa-times" id="${data.reason.id}_ban_icon" style="font-size: 28px; color: #E74C3C"></i>`
        }
        let usernote = row.insertCell();
        if (data.reason.usernote) {
            usernote.innerHTML = `<i class="fas fa-check" id="${data.reason.id}_usernote_icon" style="font-size: 28px;color: #00bc8c"></i>`
        } else {
            usernote.innerHTML = `<i class="fas fa-times" id="${data.reason.id}_usernote_icon" style="font-size: 28px; color: #E74C3C"></i>`
        }
        let enabled = row.insertCell();
        let options = row.insertCell();
        if (data.reason.enabled) {
            enabled.innerHTML = `<i class="fas fa-check" id="${data.reason.id}_enabled_icon" style="font-size: 28px;color: #00bc8c"></i>`;
            enableToggle = `<a class="dropdown-item" id="${data.reason.id}_toggle" style="color: #E74C3C" onclick="toggleReason('${data.reason.id}', false)">Disable</a>`;
        } else {
            enabled.innerHTML = `<i class="fas fa-times" id="${data.reason.id}_enabled_icon" style="font-size: 28px; color: #E74C3C"></i>`;
            enableToggle = `<a class="dropdown-item" id="${data.reason.id}_toggle" style="color: #00bc8c" onclick="toggleReason('${data.reason.id}', false)">Enable</a>`;
        }
        options.innerHTML = `
                        <div class="btn-group" role="group" aria-label="Button group with nested dropdown">
                            <button type="button" class="btn btn-primary" onclick="location.href='/reasons/${data.reason.id}'">Edit</button>
                            <div class="btn-group" role="group">
                                <button id="btnGroupDrop1" type="button" class="btn btn-primary dropdown-toggle" data-toggle="dropdown" aria-haspopup="true" aria-expanded="false"></button>
                                <div class="dropdown-menu" aria-labelledby="btnGroupDrop1">
                                    <a class="dropdown-item" href="/reasons/${data.reason.id}">Edit</a>
                                    ${enableToggle}
                                    <div class="dropdown-divider"></div>
                                    <a class="dropdown-item" onclick="showDeleteModalFlair('${data.reason.id}', ${row.rowIndex})" style="color: red">Delete</a>
                                </div>
                            </div>
                        </div>`;
    }

    $('#reasonCreate').click(function () {
        let subreddit = document.getElementById('subreddit');
        let flair_text = document.getElementById('flair_text');
        let description = document.getElementById('description');
        let lockToggle = document.getElementById('lockToggle');
        let commentLockToggle = document.getElementById('commentLockToggle');
        let banToggle = document.getElementById('banToggle');
        let ban_duration = document.getElementById('ban_duration');
        let ban_reason = document.getElementById('ban_reason');
        let ban_message = document.getElementById('ban_message');
        let ban_note = document.getElementById('ban_note');
        let usernoteToggle = document.getElementById('usernoteToggle');
        let usernote_note = document.getElementById('usernote_note');
        let usernote_warning_type = document.getElementById('usernote_warning_type');
        let commentToggle = document.getElementById('commentToggle');
        let commentInput = document.getElementById('commentinput');
        let enableOnAdd = document.getElementById('enableOnAdd');

        if (form.checkValidity()) {
            $('#reasonCreate').prop('disabled', true);
            $('#reasonCreate').html('<span class="spinner-grow spinner-grow-sm" role="status" aria-hidden="true"></span>Adding...');
            $.ajax({
                data: {
                    subreddit: subreddit.value,
                    flair_text: flair_text.value,
                    description: description.value,
                    commentToggle: commentToggle.checked,
                    commentInput: commentInput.value,
                    lockToggle: lockToggle.checked,
                    commentLockToggle: commentLockToggle.checked,
                    banToggle: banToggle.checked,
                    ban_duration: ban_duration.value,
                    ban_reason: ban_reason.value,
                    ban_message: ban_message.value,
                    ban_note: ban_note.value,
                    usernoteToggle: usernoteToggle.checked,
                    usernote_note: usernote_note.value,
                    usernote_warning_type: usernote_warning_type.value,
                    enableOnAdd: enableOnAdd.checked
                },
                type: 'POST',
                url: '/api/reason/create'
            })
                .done(function (data) {
                    console.log(data);
                    if (data.reasonExists) {
                        flair_text.className = "form-control is-invalid";
                        flair_textFeedback.innerText = "This flair already exists for this subreddit!"
                        $('#reasonCreate').prop('disabled', false);
                        $('#reasonCreate').prop('class', 'btn btn-primary');
                        $('#reasonCreate').html('Create');
                    } else {
                        createRow(data);
                        $('#reasonCreate').html('Created');
                        $('#newSubredditModal').modal('hide');
                        $('#reasonCreate').prop('disabled', false);
                        $('#reasonCreate').prop('class', 'btn btn-primary');
                        $('#reasonCreate').html('Create');
                        resetForm(false);
                        event.preventDefault();
                        return false;
                        popNotification(data.success, data.error);
                    }
                });
        }
    });

    $('#reasonCreateNew').click(function () {
        let subreddit = document.getElementById('subreddit');
        let flair_text = document.getElementById('flair_text');
        let description = document.getElementById('description');
        let lockToggle = document.getElementById('lockToggle');
        let commentLockToggle = document.getElementById('commentLockToggle');
        let banToggle = document.getElementById('banToggle');
        let ban_duration = document.getElementById('ban_duration');
        let ban_reason = document.getElementById('ban_reason');
        let ban_message = document.getElementById('ban_message');
        let ban_note = document.getElementById('ban_note');
        let usernoteToggle = document.getElementById('usernoteToggle');
        let usernote_note = document.getElementById('usernote_note');
        let usernote_warning_type = document.getElementById('usernote_warning_type');
        let commentToggle = document.getElementById('commentToggle');
        let commentInput = document.getElementById('commentinput');
        let enableOnAdd = document.getElementById('enableOnAdd');

        if (form.checkValidity()) {
            $('#reasonCreateNew').prop('disabled', true);
            $('#reasonCreateNew').html('<span class="spinner-grow spinner-grow-sm" role="status" aria-hidden="true"></span>Adding...');
            $.ajax({
                data: {
                    subreddit: subreddit.value,
                    flair_text: flair_text.value,
                    description: description.value,
                    commentToggle: commentToggle.checked,
                    commentInput: commentInput.value,
                    lockToggle: lockToggle.checked,
                    commentLockToggle: commentLockToggle.checked,
                    banToggle: banToggle.checked,
                    ban_duration: ban_duration.value,
                    ban_reason: ban_reason.value,
                    ban_message: ban_message.value,
                    ban_note: ban_note.value,
                    usernoteToggle: usernoteToggle.checked,
                    usernote_note: usernote_note.value,
                    usernote_warning_type: usernote_warning_type.value,
                    enableOnAdd: enableOnAdd.checked
                },
                type: 'POST',
                url: '/api/reason/create'
            })
                .done(function (data) {
                    console.log(data);
                    createRow(data);
                    $('#reasonCreateNew').html('Created');
                    $('#reasonCreateNew').prop('disabled', false);
                    $('#reasonCreateNew').prop('class', 'btn btn-primary');
                    $('#reasonCreateNew').html('Create and New');
                    resetForm(true);
                    event.preventDefault();
                    return false;
                    popNotification(data.success, data.error);
                })
        }
    });


    $("#commentToggle").click(function () {
        commentEntry.hidden = !commentToggle.checked;
        commentInput.required = commentToggle.checked;
        commentInput.style.minHeight = '54px'
    });
    $("#banToggle").click(function () {
        banGroup.hidden = !banToggle.checked;
    });
    $("#usernoteToggle").click(function () {
        usernoteGroup.hidden = !usernoteToggle.checked;
    });
});