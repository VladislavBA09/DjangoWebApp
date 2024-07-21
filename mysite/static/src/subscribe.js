import $ from 'jquery';

$(document).ready(function() {
    function getCookie(name) {
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            const cookies = document.cookie.split(';');
            for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }

    const csrftoken = getCookie('csrftoken');

    $(".subscribe-button, .unsubscribe-button").click(function(e) {
        e.preventDefault();
        var form = $(this).closest('form');
        var profile_id = form.data('profile-id');
        var button = $(this);
        var unsubscribe_url = form.data('unsubscribe-url');
        var subscribe_url = form.data('subscribe-url');

        $.ajax({
            type: 'POST',
            url: form.attr('action'),
            data: form.serialize() + '&csrfmiddlewaretoken=' + csrftoken,
            success: function(data) {
                if (button.hasClass('subscribe-button')) {
                    button.removeClass('subscribe-button').addClass('unsubscribe-button').text('Unsubscribe');
                    form.attr('action', unsubscribe_url);
                    form.find('input[name="user_to_follow"]').attr('name', 'user_to_unfollow');
                } else if (button.hasClass('unsubscribe-button')) {
                    button.removeClass('unsubscribe-button').addClass('subscribe-button').text('Subscribe');
                    form.attr('action', subscribe_url);
                    form.find('input[name="user_to_unfollow"]').attr('name', 'user_to_follow');
                }
            }
        });
    });
});