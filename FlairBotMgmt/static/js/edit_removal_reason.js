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


function deleteReason(reason_id) {
    $('#confirmationModal').modal('hide');
    $('#delete').prop('disabled', true);
    $('#delete').html('<div class="spinner-grow spinner-grow-sm text-primary" role="status"></div> Deleting...');
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
                $('#delete').html('Deleted');
                $('#delete').prop('class', 'btn btn-danger');
            }
        });
    event.preventDefault();
    return false;
}

$(function () {
    $(function () {
        let form = document.getElementById('createRemovalReasonForm');
        let commentToggle = document.getElementById('commentToggle');
        let banToggle = document.getElementById('banToggle');
        let banGroup = document.getElementById('banGroup');
        let usernoteGroup = document.getElementById('usernoteGroup');
        let commentEntry = document.getElementById('commentEntry');
        let commentInput = document.getElementById('commentinput');
        commentEntry.hidden = !commentToggle.checked;
        commentInput.required = commentToggle.checked;
        banGroup.hidden = !banToggle.checked;
        usernoteGroup.hidden = !usernoteToggle.checked;

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
});
