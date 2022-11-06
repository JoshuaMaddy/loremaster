
$(document).on('click', '#tags',  function (evt){

            // All autocomplete fields similar to this. Reccomended to copy/paste, edit url, data, and select. Read jQuery UI docs for more detail
        // https://jqueryui.com/autocomplete/
        var form = new FormData(document.getElementById('search_form'))
        $("#tags").autocomplete({
            source: function (request, response) {
                // Ajax is similar to fetch, tailored for jQuery objects
                $.ajax({
                    url: '/api/search',
                    method: 'POST',
                    dataType: 'json',
                    processData: false,
                    contentType: 'application/json',
                    data: JSON.stringify({
                        search_type: form.get('tagtype'),
                        query: request.term
                    }),
                    success: function (data) {
                        response($.map(data, function (result) {
                            return {
                                label: result.label,
                                value: result.value,
                            }
                        }));
                    }
                });
            },
            focus: function (event, ui) {
                event.preventDefault();
            },
            select: function (event, ui) {
                event.preventDefault();
                $('#tags').val(ui.item.label);
                $('#name_id').val(ui.item.value);
            },
            delay: 200
        });

});

$(document).on('click', '#search',  function (evt){
    // Send form as modified
    console.log("submitting")
    submitForm()
});

function submitForm(){
    var form = new FormData(document.getElementById('search_form'))
    
    var req = $.ajax({
        url: '/api/list_query',
        method: 'POST',
        dataType: 'json',
        processData: false,
        contentType: 'application/json',
        data: JSON.stringify({
            search_type: "character",
            query: form.get("tags"),
            tag: form.get('tagtype')
        }) 
    })
    
    req.always(function(snippet){
        console.log(snippet.responseText)
        $('.public_characters').html(snippet.responseText);
    })
}