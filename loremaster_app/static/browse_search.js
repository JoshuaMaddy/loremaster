
$(document).on('click', '#tags',  function (evt){

            // All autocomplete fields similar to this. Reccomended to copy/paste, edit url, data, and select. Read jQuery UI docs for more detail
        // https://jqueryui.com/autocomplete/
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
                        search_type: "character",
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
    submitCharacterCreation()
});

function submitForm(){
    var form = new FormData(document.getElementById('search_form'))
    
    $.ajax({
        url: '/api/list_query',
        method: 'POST',
        dataType: 'json',
        processData: false,
        contentType: 'application/json',
        data: JSON.stringify({
            search_type: "character",
            query: form.get("tags"),
            tag: "name"
        }),
        success: function (data) {
            console.log("success")
            response($.map(data, function (result) {
                console.log(result)
                return {
                    label: result.label,
                    value: result.value,
                }
            }));
        }
    });
}

// Creates a character through the /api/character_create
function submitCharacterCreation() {
    // Header options
    var form = new FormData(document.getElementById('search_form'))
    const options = {
        method: 'POST',
        dataType: 'json',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
            search_type: "character",
            query: form.get("tags"),
            tag: "name"
        }),
    };

    // API call
    fetch('/api/list_query', options).then((response) => {
        if (!response.ok) {
            throw new Error(`HTTP error! Status: ${response.status}`);
        } else {
            // Redirect to character page on success
            console.log(response.json)
            response.json().then((data) => {
                window.location.replace(data.url);
            })
        }
    })
}