window.addEventListener('keydown', function (e) {
    if (e.keyIdentifier == 'U+000A' || e.keyIdentifier == 'Enter' || e.keyCode == 13) {
        if (e.target.nodeName == 'INPUT' && e.target.type == 'textarea') {
            e.preventDefault();
            return false;
        }
    } else if (e.key == " ") {
        // e.preventDefault(); // Prevent the spacebar from toggling and firing the click event
        e.target.offsetParent.children[0].click()
    }
}, true);

function popNotification(success, error) {
    if (error) {
        $.toast({
            title: 'Error Occurred',
            content: error,
            type: 'error'
        });
    }
    if (success) {
        $.toast({
            title: 'Success!',
            content: success,
            type: 'success',
            delay: 1500
        });
    }
}

$(document).ready(function () {
    $('[data-toggle="tooltip"]').tooltip();
});

$(function () {
    $('a').each(function () {
        if ($(this).prop('href') == window.location.href) {
            $(this).addClass('active');
        }
    });
});