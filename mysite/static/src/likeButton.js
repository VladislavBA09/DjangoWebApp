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

    $(".like-button, .dislike-button").click(function(e) {
        e.preventDefault();
        var form = $(this).closest('form');
        var post_id = form.find('input[name="post_id"]').val();
        var button = $(this);

        $.ajax({
            type: 'POST',
            url: form.attr('action'),
            data: {
                'post_id': post_id,
                'csrfmiddlewaretoken': csrftoken
            },
            success: function(data) {
                if (button.hasClass('like-button')) {
                    button.toggleClass('liked', data.liked);
                } else if (button.hasClass('dislike-button')) {
                    button.toggleClass('disliked', data.disliked);
                }
            }
        });
    });
});