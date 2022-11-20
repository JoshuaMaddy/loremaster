
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

var search_by = {};
search_by["character"] = $('<option>');
search_by["character"].attr('value', "character").text("Character");
search_by["owner"] = $('<option>');
search_by["owner"].attr('value', "user").text("Owner");
search_by["guild"] = $('<option>');
search_by["guild"].attr('value', "guild").text("Guild");
search_by["item"] = $('<option>');
search_by["item"].attr('value', "item").text("Item");
search_by["familiar"] = $('<option>');
search_by["familiar"].attr('value', "familiar").text("Familiar");
search_by["location"] = $('<option>');
search_by["location"].attr('value', "location").text("Location");
search_by["leader"] = $('<option>');
search_by["leader"].attr('value', "leader").text("Leader");





$(function(){

    $("#searchtype_dropdown").change(function () {
        var selection = this.value;
        $("#tagtype_dropdown").empty()
        switch(selection) {
            case "character":
                $("#tagtype_dropdown").append(search_by["character"]);
                $("#tagtype_dropdown").append(search_by["location"]);
                $("#tagtype_dropdown").append(search_by["familiar"]);
                $("#tagtype_dropdown").append(search_by["item"]);
                $("#tagtype_dropdown").append(search_by["guild"]);
                break;
            case "location":
                $("#tagtype_dropdown").append(search_by["location"]);   
                $("#tagtype_dropdown").append(search_by["character"]);    
                break;
            case "item":
                $("#tagtype_dropdown").append(search_by["item"]); 
                $("#tagtype_dropdown").append(search_by["character"]);    
                break;
            case "guild":
                $("#tagtype_dropdown").append(search_by["guild"]); 
                $("#tagtype_dropdown").append(search_by["character"]);
                $("#tagtype_dropdown").append(search_by["leader"]);  
                break;
            case "familiar":
                $("#tagtype_dropdown").append(search_by["familiar"]);
                $("#tagtype_dropdown").append(search_by["character"]);  
                break;
        }   
        $("#tagtype_dropdown").append(search_by["owner"]);
    });
})

function submitForm(){
    var form = new FormData(document.getElementById('search_form'))
    
    var req = $.ajax({
        url: '/api/list_query',
        method: 'POST',
        dataType: 'json',
        processData: false,
        contentType: 'application/json',
        data: JSON.stringify({
            search_type: form.get('searchtype'),
            query: form.get("tags"),
            tag: form.get('tagtype')
        }) 
    })
    
    req.always(function(snippet){
        console.log(snippet.responseText)
        $('.public_characters').html(snippet.responseText);
    })
}