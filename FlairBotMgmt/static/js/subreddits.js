function clearInvalidState(textBox) {
    textBox.className = "form-control"
}

function toggleSubreddit(subreddit, enabled) {
    $.ajax({
        data: {
            subreddit: subreddit,
            enabled: enabled
        },
        type: 'POST',
        url: '/api/subreddit/toggle'
    })
        .done(function notify(data) {
            var elem = document.getElementById(`${data.subreddit}_toggle`);
            var icon = document.getElementById(`${data.subreddit}_icon`);
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
            popNotification(`Successfully ${toastStatus} FlairBot for r/${data.subreddit}`, data.error);
        });
}

$(document).ready(function () {
    $(document).on("keyup", '[data-toggle="buttons"] input[type="checkbox"]', function (e) {
        if (e.key == " ") {
            e.preventDefault(); // Prevent the spacebar from toggling and firing the click event
            $(this).closest('[data-toggle="buttons"]').button("toggle"); // Let Bootstrap toggle
        }
    });

    $("#subreddits").tablesorter({
        theme: "bootstrap",
        cancelSelection: false,
        sortReset: true
    });
});

function showDeleteModal(subreddit, row_id) {
    document.getElementById('delete-modal-body').innerHTML = `Are you <strong>sure</strong> you want to delete /r/${subreddit} and all of its associated removal reasons?`;
    document.getElementById('delete-modal-footer').innerHTML = `<button type="button" class="btn btn-secondary" data-dismiss="modal">Close</button><button type="button" class="btn btn-danger" onclick="deleteSubreddit('${subreddit}',${row_id})" data-dismiss="modal" id="deleteConfirm">Delete this subreddit</button>`;
    $('#confirmationModal').modal('show')
}

function deleteSubreddit(subreddit, row_id) {
    $('#confirmationModal').modal('hide');
    $.ajax({
        data: {
            subreddit: subreddit,
            cascade: true
        },
        type: 'POST',
        url: '/api/subreddit/delete'
    })
        .done(function (data) {
            console.log(data);
            if (data.success) {
                popNotification(`Successfully deleted FlairBot for r/${data.subreddit}`, data.error);
                document.getElementById("subreddits").deleteRow(row_id);
            }
        });
    event.preventDefault();
    return false;
}

$(function () {
    let form = document.getElementById('addSubredditForm');
    let headerToggle = document.getElementById('headerToggle');
    let footerToggle = document.getElementById('footerToggle');
    let headerEntry = document.getElementById('headerEntry');
    let headerinput = document.getElementById('headerinput');
    let footerEntry = document.getElementById('footerEntry');
    let footerinput = document.getElementById('footerinput');
    let webhookType = document.getElementById('webhookType');
    let customWebhookLabel = document.getElementById('customWebhookLabel');
    let customWebhookType = document.getElementById('customWebhookType');
    let webhookurlLabel = document.getElementById('webhookurlLabel');
    let webhookurl = document.getElementById('webhookurl');
    headerEntry.hidden = !headerToggle.checked;
    headerinput.required = headerToggle.checked;
    footerEntry.hidden = !footerToggle.checked;
    footerinput.required = footerToggle.checked;
    webhookurlLabel.hidden = webhookType.value == "None";
    webhookurl.hidden = webhookType.value == "None";
    webhookurl.required = webhookType.value != "None";

    $("#subreddits").tablesorter({
        theme: "bootstrap",
        cancelSelection: false,
        sortReset: true
    });

    $('[data-toggle="tooltip"]').tooltip();

    $('#subredditAdd').click(function () {
        let subreddit = document.getElementById('subreddit');
        let subredditFeedback = document.getElementById('subredditFeedback');
        let botAccount = document.getElementById('bot_account');
        let bot_accountFeedback = document.getElementById('bot_accountFeedback');
        let headerToggle = document.getElementById('headerToggle');
        let footerToggle = document.getElementById('footerToggle');
        let headerinput = document.getElementById('headerinput');
        let footerinput = document.getElementById('footerinput');
        let webhookType = document.getElementById('webhookType');
        let webhookurl = document.getElementById('webhookurl');
        let enableOnAdd = document.getElementById('enableOnAdd');

        if (form.checkValidity()) {
            $('#subredditAdd').prop('disabled', true);
            $('#subredditAdd').html('<span class="spinner-grow spinner-grow-sm" role="status" aria-hidden="true"></span>Adding...');
            $.ajax({
                data: {
                    subreddit: subreddit.value,
                    bot_account: botAccount.value,
                    webhook_type: webhookType.value,
                    webhook: webhookurl.value,
                    headerToggle: headerToggle.checked,
                    footerToggle: footerToggle.checked,
                    header: headerinput.value,
                    footer: footerinput.value,
                    enable: enableOnAdd.checked
                },
                type: 'POST',
                url: '/api/subreddit/add'
            })
                .done(function (data) {
                    console.log(data);
                    if (!data.validSubreddit) {
                        subreddit.className = "form-control is-invalid";
                        subredditFeedback.innerText = "That subreddit doesn't exist!"
                        $('#subredditAdd').prop('disabled', false);
                        $('#subredditAdd').prop('class', 'btn btn-primary');
                        $('#subredditAdd').html('Add');
                    } else if (data.subredditExists) {
                        subreddit.className = "form-control is-invalid";
                        subredditFeedback.innerText = "That subreddit already exists!"
                        $('#subredditAdd').prop('disabled', false);
                        $('#subredditAdd').prop('class', 'btn btn-primary');
                        $('#subredditAdd').html('Add');
                    }
                    if (!data.validRedditor) {
                        botAccount.className = "form-control is-invalid";
                        bot_accountFeedback.innerText = "That redditor doesn't exist!"
                        $('#subredditAdd').prop('disabled', false);
                        $('#subredditAdd').prop('class', 'btn btn-primary');
                        $('#subredditAdd').html('Add');
                    }
                    if (data.validSubreddit && !data.subredditExists && data.validRedditor) {
                        let subredditsTable = document.getElementById('subreddits');
                        let row = subredditsTable.insertRow();
                        let subredditName = row.insertCell();
                        subredditName.innerHTML = `<a href="/subreddits/${data.subreddit.subreddit}">${data.subreddit.subreddit}</a>`;
                        let bot_account = row.insertCell();
                        bot_account.innerHTML = data.subreddit.bot_account;
                        let removalReasonCount = row.insertCell();
                        removalReasonCount.innerHTML = `<a href="/subreddits/${data.subreddit.subreddit}#removalReasons">0</a>`;
                        let webhook_type = row.insertCell();
                        if (data.subreddit.webhook_type) {
                            webhookType = data.subreddit.webhook_type;
                        } else {
                            webhookType = 'None';
                        }
                        webhook_type.innerHTML = webhookType;
                        let enabled = row.insertCell();
                        if (data.subreddit.enabled) {
                            enabled.innerHTML = `<i class="fas fa-check" id="${data.subreddit.subreddit}_icon" style="font-size: 28px;color: #00bc8c"></i>`;
                            enableButtonStatus = `<a class="dropdown-item" id="${data.subreddit.subreddit}_toggle" style="color: #E74C3C" onclick="toggleSubreddit('${data.subreddit.subreddit}', false)">Disable</a>`;
                        } else {
                            enabled.innerHTML = `<i class="fas fa-times" id="${data.subreddit.subreddit}_icon" style="font-size: 28px; color: #E74C3C"></i>`;
                            enableButtonStatus = `<a class="dropdown-item" id="${data.subreddit.subreddit}_toggle" style="color: #00bc8c" onclick="toggleSubreddit('${data.subreddit.subreddit}', true)">Enable</a>`;
                        }
                        let edit = row.insertCell();
                        edit.innerHTML = `<div class="btn-group" role="group" aria-label="Button group with nested dropdown">
                                <button type="button" class="btn btn-primary" onclick="location.href='/subreddits/${data.subreddit.subreddit}'">Edit</button>
                                <div class="btn-group" role="group">
                                    <button id="btnGroupDrop1" type="button" class="btn btn-primary dropdown-toggle" data-toggle="dropdown" aria-haspopup="true" aria-expanded="false"></button>
                                    <div class="dropdown-menu" aria-labelledby="btnGroupDrop1">
                                        <a class="dropdown-item" href="/subreddits/${data.subreddit.subreddit}">Edit</a>
                                        ${enableButtonStatus}
                                        <div class="dropdown-divider"></div>
                                        <a class="dropdown-item" onclick="showDeleteModal('${data.subreddit.subreddit}', ${row.rowIndex})" style="color: red">Delete</a>
                                    </div>
                                </div>
                            </div>`;
                        $('#subredditAdd').html('Added');
                        $('#newSubredditModal').modal('hide');
                        $('#subredditAdd').prop('disabled', false);
                        $('#subredditAdd').prop('class', 'btn btn-primary');
                        $('#subredditAdd').html('Add');
                    }
                    popNotification(data.success, data.error);
                });
        }
    });

    $("#webhookType").change(function () {
        if (webhookType.value == "custom") {
            customWebhookLabel.hidden = false;
            customWebhookType.hidden = false;
            customWebhookType.required = true;
            customWebhookType.value = ''
        } else {
            customWebhookLabel.hidden = true;
            customWebhookType.hidden = true;
            customWebhookType.required = false;
            customWebhookType.value = webhookType.value
        }
        webhookurlLabel.hidden = (webhookType.value == "None");
        webhookurl.hidden = (webhookType.value == "None");
    });

    $("#customWebhookType").change(function () {
        webhookType.value = 'custom'
        customWebhookType.hidden = false;
        customWebhookType.required = true;
        customWebhookLabel.hidden = false;
    });

    $("#headerToggle").click(function () {
        headerEntry.hidden = !headerToggle.checked;
        headerinput.required = headerToggle.checked;
        headerinput.style.minHeight = '54px'
    });

    $("#footerToggle").click(function () {
        footerEntry.hidden = !footerToggle.checked;
        footerinput.required = footerToggle.checked;
        footerinput.style.minHeight = '54px'
    });

});