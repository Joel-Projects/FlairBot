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