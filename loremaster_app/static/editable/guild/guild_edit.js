// Snippets for character creation
var editor_snippet = `<div class="editor">
<input type="text" name="single_editor" class="single_editor" placeholder="Editor">
<input type="text" name="editor_id" id="editor_id" hidden>
<button type="button" class="remove_editor remove">-</button>
</div>`

var guild_snippet = `<div class="guild_member">
<input type="text" name="guild_member" class="guild_member" placeholder="Member">
<input type="text" name="guild_member_id" id="guild_member_id" value="" hidden>
<button type="button" class="remove_member remove">-</button>
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

    $('#add_member').on('click', function (evt) {
        if ($(this).siblings('.guild_member').length > 0) {
            $(this).siblings('.guild_member').last().after(guild_snippet)
        } else {
            $(this).before(guild_snippet)
        }
    })

    // When a 'remove X' is clicked, remove it from the DOM
    $(document).on('click', '.remove_editor, .remove_member', function (evt) {
        $(this).parent().remove()
    })

    // If the user submits form with enter key
    $('#guild_form').on("submit", e => {
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
        if($('#guild_page').length > 0){
            submitGuildEdit();
            console.log("editting")
        }else{
            submitGuildCreation();
            console.log(createGuildData())
        }
    }

    // Edits a character through the /api/character_edit
    function submitGuildEdit() {
        // Header options
        const options = {
            method: 'POST',
            body: createGuildData()
        };

        // API call
        fetch('/api/guild_edit', options).then((response) => {
            if (!response.ok) {
                throw new Error(`HTTP error! Status: ${response.status}`);
            } else {
                // Redirect to character page on success
                window.location.replace($('#guild_page').data('guild_url'));
            }
        })
    }

    // Creates a character through the /api/character_create
    function submitGuildCreation() {
        // Header options
        const options = {
            method: 'POST',
            body: createGuildData()
        };

        // API call
        fetch('/api/guild_create', options).then((response) => {
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
        console.log(JSON.stringify(createGuildData()))
    })

    function createGuildData() {
        // Retrieve form data to be parsed
        var form = new FormData(document.getElementById('guild_form'))

        // Creates an array of integers from all #sortable objects, referencing a data field on each labeled 'editable_id'
        $("#sortable").sortable("toArray", { attribute: "data-editable_id" }).forEach((num) => {
            form.append('image_id', num)
        })

		form.append('description', tinymce.get("description").getContent())

        return form
    }

    // Bit of a hack, when any input that needs autocomplete is clicked, refresh autocomplete fields. Needed because fields come/go by user choice
    $(document).on('click', '#guild_leader, .guild_member, .single_editor', function (evt) {

        // All autocomplete fields similar to this. Reccomended to copy/paste, edit url, data, and select. Read jQuery UI docs for more detail
        // https://jqueryui.com/autocomplete/
        $("#guild_leader").autocomplete({
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
                $('#guild_leader').val(ui.item.label);
                $('#guild_leader_id').val(ui.item.value);
            },
            delay: 200
        });

        $(".guild_member").autocomplete({
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
                $(this).val(ui.item.label);
                $(this).siblings().first().val(ui.item.value);
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