// Snippets for character creation
var editor_snippet = `<div class="editor">
<input type="text" name="single_editor" class="single_editor" placeholder="Editor">
<input type="text" name="editor_id" id="editor_id" hidden>
<button type="button" class="remove_editor remove">-</button>
</div>`

var location_snippet = `<div class="child_location">
<input type="text" name="single_location" class="single_location" placeholder="Location">
<input type="text" name="single_location_id" id="single_location_id" value="" hidden>
<button type="button" class="remove_location remove">-</button>
</div>`

$(function () {

    // Create description editor
    tinymce.init({
        selector: 'textarea#description',
        promotion: false,
        resize: false,
        height: '100%',
        plugins: 'emoticons',
        toolbar: 'undo redo | styleselect | bold italic | ' +
            'alignleft aligncenter alignright alignjustify | ' +
            'outdent indent | numlist bullist | emoticons',
        setup: function (editor) {
            editor.on('init', function (e) {
                editor.setContent($('#hidden_description')[0].innerHTML);
            });
        }
    });

    $('#add_editor').on('click', function (evt) {
        if ($(this).siblings('.editor').length > 0) {
            $(this).siblings('.editor').last().after(editor_snippet)
        } else {
            $(this).before(editor_snippet)
        }
    })

    $('#add_location').on('click', function (evt) {
        if ($(this).siblings('.child_location').length > 0) {
            $(this).siblings('.child_location').last().after(location_snippet)
        } else {
            $(this).before(location_snippet)
        }
    })

    // When a 'remove X' is clicked, remove it from the DOM
    $(document).on('click', '.remove_editor, .remove_location', function (evt) {
        $(this).parent().remove()
    })

    // If the user submits form with enter key
    $('#location_form').on("submit", e => {
        // Do not send form as normal
        e.preventDefault();
        // Send form as modified
        submitForm()
    });

    // If the user submits form with button
    $('#confirm, #create').on('click', () => {
        // Send form as modified
        submitForm()
    })


    function submitForm(){
        // Bit of a hack, a div with ID of character_page defines if this is an edit, or a creaction.
        if($('#location_page').length > 0){
            submitLocationEdit();
            console.log(createLocationData())
        }else{
            submitLocationCreation();
            console.log(createLocationData())
        }
    }

    // Edits a character through the /api/character_edit
    function submitLocationEdit() {
        // Header options
        const options = {
            method: 'POST',
            body: createLocationData()
        };

        // API call
        fetch('/api/location_edit', options).then((response) => {
            if (!response.ok) {
                throw new Error(`HTTP error! Status: ${response.status}`);
            } else {
                // Redirect to character page on success
                window.location.replace($('#location_page').data('location_url'));
            }
        })
    }

    // Creates a character through the /api/character_create
    function submitLocationCreation() {
        // Header options
        const options = {
            method: 'POST',
            body: createLocationData()
        };

        // API call
        fetch('/api/location_create', options).then((response) => {
            if (!response.ok) {
                throw new Error(`HTTP error! Status: ${response.status}`);
            } else {
                // Redirect to character page on success
                response.json().then((data) => {
                    window.location.replace(data.url);
                })
            }
        })
    }

    // If button with ID log clicked, console out the form data as a JSON object
    $('#log').on('click', function (evt) {
        console.log(JSON.stringify(createLocationData()))
    })

    function createLocationData() {
        // Retrieve form data to be parsed
        var form = new FormData(document.getElementById('location_form'))

        // Creates an array of integers from all #sortable objects, referencing a data field on each labeled 'editable_id'
        $("#sortable").sortable("toArray", { attribute: "data-editable_id" }).forEach((num) => {
            form.append('image_id', num)
        })

		form.append('description', tinymce.get("description").getContent())

        return form
    }

    // Bit of a hack, when any input that needs autocomplete is clicked, refresh autocomplete fields. Needed because fields come/go by user choice
    $(document).on('click', '#parent_location, .single_location, .single_editor', function (evt) {

        // All autocomplete fields similar to this. Reccomended to copy/paste, edit url, data, and select. Read jQuery UI docs for more detail
        // https://jqueryui.com/autocomplete/
        $("#parent_location").autocomplete({
            source: function (request, response) {
                // Ajax is similar to fetch, tailored for jQuery objects
                $.ajax({
                    url: '/api/search',
                    method: 'POST',
                    dataType: 'json',
                    processData: false,
                    contentType: 'application/json',
                    data: JSON.stringify({
                        search_type: "location",
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
                $('#parent_location').val(ui.item.label);
                $('#parent_location_id').val(ui.item.value);
            },
            delay: 200
        });

        $(".single_location").autocomplete({
            source: function (request, response) {
                // Ajax is similar to fetch, tailored for jQuery objects
                $.ajax({
                    url: '/api/search',
                    method: 'POST',
                    dataType: 'json',
                    processData: false,
                    contentType: 'application/json',
                    data: JSON.stringify({
                        search_type: "location",
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
                $('.single_location').val(ui.item.label);
                $('#single_location_id').val(ui.item.value);
            },
            delay: 200
        });

        $(".single_editor").autocomplete({
            source: function (request, response) {
                $.ajax({
                    url: '/api/search',
                    method: 'POST',
                    dataType: 'json',
                    processData: false,
                    contentType: 'application/json',
                    data: JSON.stringify({
                        search_type: "user",
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
                $(this).val(ui.item.label);
                $(this).siblings().first().val(ui.item.value);
            },
            delay: 200
        });
    });

    // Image sorting/grid, also jQuery UI
    $("#sortable").sortable();
    $("#sortable").disableSelection();

    // Dialog/Modal, jQuery UI
    let dialog = $("#image_selection").dialog({
        autoOpen: false,
        height: (window.innerHeight / 10) * 8,
        width: (window.innerWidth / 10) * 8,
        modal: true,
        open: function (event, ui) {
            $.ajax({
                url: '/api/user_image_grid',
                method: 'GET',
            }).done(function (data) {
                // Insert html snippet into dialog div
                $('#image_selection').html(data)
            });
        },
        buttons: {
            "Select": function(){
                $('#sortable').children().remove();

                $('.image_grid').children().each(function (index) {
                    if ($(this).data('selected')) {
                        $(this).children()[0].removeAttribute('style');
                        $('#sortable').append($(this).children()[0]);
                    }
                });

                dialog.dialog('close');
            },
            "Disregard": function(){
                dialog.dialog("close");
            }
        }
    });

    // Image highlighting
    $(document).on('click', '.image_div > img', function (evt) {
        if ($(this).css('opacity') == 0.8) {
            $(this).css('opacity', 1);
            $(this).parent().data('selected', false);
        } else {
            $(this).css('opacity', 0.8);
            $(this).parent().data('selected', true);
        }
    });

    // Open dialog
    $('#select_images').on('click', function (evt) {
        dialog.dialog('open')
    });

    // Log image ids on button click
    $('#image_ids').on('click', function (evt) {
        console.log($("#sortable").sortable("toArray", { attribute: "data-editable_id" }))
    });

});