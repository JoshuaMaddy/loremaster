$(function(){
    $(document).on('click', '.ban_button, .unban_button', function (evt) {
        var url = $(this).data('url')
        $.ajax({
            url: url,
            method: 'POST',
            success: function (data) {
                console.log('yey')
            }
        });
    })
})