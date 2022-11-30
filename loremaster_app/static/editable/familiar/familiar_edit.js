// Snippets for familiar creation
var trait_snippet = `<div class="trait">
<input type="text" name="single_trait" class="single_trait" placeholder="Trait">
<input type="text" name="single_trait_desc" class="single_trait_desc" placeholder="Short Description">
<button type="button" class="remove_trait remove">-</button>
</div>`

var stat_snippet = `<div class="stat">
<input type="text" name="single_stat" class="single_stat" placeholder="Trait">
<input type="text" name="single_stat_desc" class="single_stat_desc" placeholder="Short Description">
<button type="button" class="remove_stat remove">-</button>
</div>`

var relationship_snippet = `<div class="relationship">
        <input type="text" name="single_relationship" class="single_relationship" placeholder="Relationship">
        <input type="text" name="relationship_character" class="relationship_character" placeholder="Character">
        <input type="text" name="relationship_character_id" class="relationship_character_id" hidden>
        <input type="text" name="single_relationship_desc" class="single_relationship_desc" placeholder="Short Description">
        <button type="button" class="remove_relationship remove">-</button>
    </div>`

var familiar_snippet = `<div class="familiar">
    <input type="text" name="single_familiar" class="single_familiar" placeholder="Familiar">
    <input name="familiar_id" id="familiar_id" type="text" hidden>
    <button type="button" class="remove_familiar remove">-</button>
</div>`

var inventory_snippet = `<div class="inventories">
    <input type="text" name="single_inventory" class="single_inventory" placeholder="Inventory">
    <button type="button" class="remove_inventory remove">-</button>
</div>`

var editor_snippet = `<div class="editor">
<input type="text" name="single_editor" class="single_editor" placeholder="Editor">
<input type="text" name="editor_id" id="editor_id" hidden>
<button type="button" class="remove_editor remove">-</button>
</div>`

// Familiar Description class/template. Used for form submission as a container.
class FamiliarDescription {
    familiar;
    image_ids;
    description;
    location_id;
    traits;
    stats;
    relationships;
    familiar_ids;
    inventories;
    editor_ids;
    visibility;
    constructor(familiar = null, image_ids = null, description = null, traits = null, stats = null,
        relationships = null, familiar_ids = null, inventories = null, editor_ids = null, location_id = null, visibility = null) {
        this.familiar = familiar;
        this.image_ids = image_ids;
        this.description = description;
        this.traits = traits;
        this.stats = stats;
        this.relationships = relationships;
        this.familiar_ids = familiar_ids;
        this.editor_ids = editor_ids;
        this.location_id = location;
        this.visibility = visibility;
    }
}

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

    // Add traits on click of button with add_trait ID
    $('#add_trait').on('click', function (evt) {
        // If the button that was clicked has siblings
        if ($(this).siblings('.trait').length > 0) {
            // Append the trait field/snippet to the end of listed traits
            $(this).siblings('.trait').last().after(trait_snippet)
        } else {
            // Create a trait field
            $(this).before(trait_snippet)
        }
    })

    // Add stats, same as add traits
    $('#add_stat').on('click', function (evt) {
        if ($(this).siblings('.stat').length > 0) {
            $(this).siblings('.stat').last().after(stat_snippet)
        } else {
            $(this).before(stat_snippet)
        }
    })

    // Add familiar, same as add traits
    $('#add_familiar').on('click', function (evt) {
        if ($(this).siblings('.familiar').length > 0) {
            $(this).siblings('.familiar').last().after(familiar_snippet)
        } else {
            $(this).before(familiar_snippet)
        }
    })

    // Add relationship, same as add traits
    $('#add_relationship').on('click', function (evt) {
        if ($(this).siblings('.relationship').length > 0) {
            $(this).siblings('.relationship').last().after(relationship_snippet)
        } else {
            $(this).before(relationship_snippet)
        }
    })

    // Add inventory, same as add traits
    $('#add_inventory').on('click', function (evt) {
        if ($(this).siblings('.inventory').length > 0) {
            $(this).siblings('.inventory').last().after(inventory_snippet)
        } else {
            $(this).before(inventory_snippet)
        }
    })

    // Add editor, same as add traits
    $('#add_editor').on('click', function (evt) {
        if ($(this).siblings('.editor').length > 0) {
            $(this).siblings('.editor').last().after(editor_snippet)
        } else {
            $(this).before(editor_snippet)
        }
    })

    // When a 'remove X' is clicked, remove it from the DOM
    $(document).on('click', '.remove_trait,.remove_stat,.remove_familiar,.remove_relationship,.remove_inventory,.remove_editor', function (evt) {
        $(this).parent().remove()
    })

    // If the user submits form with enter key
    $('#familiar_form').on("submit", e => {
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
        // Bit of a hack, a div with ID of familiar_page defines if this is an edit, or a creaction.
        if($('#familiar_page').length > 0){
            submitFamiliarEdit();
        }else{
            submitFamiliarCreation();
        }
    }

    // Edits a familiar through the /api/familiar_edit
    function submitFamiliarEdit() {
        // Header options
        const options = {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(createFamiliarData())
        };

        // API call
        fetch('/api/familiar_edit', options).then((response) => {
            if (!response.ok) {
                throw new Error(`HTTP error! Status: ${response.status}`);
            } else {
                // Redirect to familiar page on success
                window.location.replace($('#familiar_page').data('familiar_url'));
            }
        })
    }

    // Creates a familiar through the /api/familiar_create
    function submitFamiliarCreation() {
        // Header options
        const options = {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(createFamiliarData())
        };

        // API call
        fetch('/api/familiar_create', options).then((response) => {
            if (!response.ok) {
                throw new Error(`HTTP error! Status: ${response.status}`);
            } else {
                // Redirect to familiar page on success
                response.json().then((data) => {
                    window.location.replace(data.url);
                })
            }
        })
    }

    // If button with ID log clicked, console out the form data as a JSON object
    $('#log').on('click', function (evt) {
        console.log(JSON.stringify(createFamiliarData()))
    })

    // Parses form/DOM and assembles a FamiliarDescription object to be sent.
    function createFamiliarData() {

        // Creates an array of integers from all #sortable objects, referencing a data field on each labeled 'editable_id'
        let image_array = $("#sortable").sortable("toArray", { attribute: "data-editable_id" }).map((num) => {
            return parseInt(num)
        })

        // Retrieve form data to be parsed
        var form = new FormData(document.getElementById('familiar_form'))

        // Get data from form, identified through the field's name
        let trait_names = form.getAll('single_trait')
        let trait_desc = form.getAll('single_trait_desc')

        let traits = []

        // For each trait in the form, create a simple container object
        for (let i = 0; i < trait_names.length; i++) {
            traits.push({ 'trait_name': trait_names[i], 'trait_description': trait_desc[i] })
        }

        // Same as traits
        let stat_names = form.getAll('single_stat')
        let stat_desc = form.getAll('single_stat_desc')

        let stats = []

        for (let i = 0; i < stat_names.length; i++) {
            stats.push({ 'stat_name': stat_names[i], 'stat_description': stat_desc[i] })
        }

        // Same as traits
        let relationship_names = form.getAll('single_relationship')
        let familiar_ids = form.getAll('relationship_familiar_id')
        let relationship_desc = form.getAll('single_relationship_desc')

        let relationships = []

        for (let i = 0; i < relationship_names.length; i++) {
            relationships.push({ 'relationship_name': relationship_names[i], 'familiar_id': parseInt(familiar_ids[i]), 'relationship_desc': relationship_desc[i] })
        }

        // Create familiar description object, assign values
        let familiarDescription = new FamiliarDescription();

        familiarDescription.familiar = { 'name': form.get('name'), 'id': parseInt(form.get('familiar_id')) };
        familiarDescription.description = tinymce.get("description").getContent();

        familiarDescription.editor_ids = form.getAll('editor_id').map((element) => {
            return parseInt(element);
        })

        if (image_array.length > 0){
            familiarDescription.image_ids = image_array;
        }

        if (form.get('single_trait')) {
            familiarDescription.traits = traits;
        }
        if (form.get('single_stat')) {
            familiarDescription.stats = stats;
        }
        if (form.get('single_relationship')) {
            familiarDescription.relationships = relationships;
        }

        /*familiarDescription.familiar_ids = form.getAll('familiar_id').map((element) => {
            return parseInt(element);
        })*/

        if (form.get('location')) {
            familiarDescription.location_id = parseInt(form.get('location_id'));
        }

        if (form.get('visibility')) {
            familiarDescription.visibility = form.get('visibility');
        }

        return familiarDescription
    }

    // Bit of a hack, when any input that needs autocomplete is clicked, refresh autocomplete fields. Needed because fields come/go by user choice
    $(document).on('click', '#location_input, .single_familiar, .single_editor, .relationship_character, #character_owner_input', function (evt) {

        // All autocomplete fields similar to this. Reccomended to copy/paste, edit url, data, and select. Read jQuery UI docs for more detail
        // https://jqueryui.com/autocomplete/
        $("#location_input").autocomplete({
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
                $('#location_input').val(ui.item.label);
                $('#location_id').val(ui.item.value);
            },
            delay: 200
        });

        $(".single_familiar").autocomplete({
            source: function (request, response) {
                $.ajax({
                    url: '/api/search',
                    method: 'POST',
                    dataType: 'json',
                    processData: false,
                    contentType: 'application/json',
                    data: JSON.stringify({
                        search_type: "familiar",
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

        $(".relationship_character").autocomplete({
            source: function (request, response) {
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
                $(this).siblings('.relationship_character_id').first().val(ui.item.value);
            },
            delay: 200
        });

        $("#character_owner_input").autocomplete({
            source: function (request, response) {
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
                $(this).siblings('.character_owner_id').first().val(ui.item.value);
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