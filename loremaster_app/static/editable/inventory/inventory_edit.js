// Snippets for inventory creation
var editor_snippet = `<div class="editor">
<input type="text" name="single_editor" class="single_editor" placeholder="Editor">
<input type="text" name="editor_id" id="editor_id" hidden>
<button type="button" class="remove_editor">-</button>
</div>`

var item_snippet = `
<div class="item">
    <img src="" alt="">
    <div class="counter">
        <button type="button" class="plus_one">+1</button>
        <input class="value" type="text" value="0">
        <button type="button" class="minus_one">-1</button>
    </div>
</div>
`

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

    // When a 'remove X' is clicked, remove it from the DOM
    $(document).on('click', '.remove_editor', function (evt) {
        $(this).parent().remove()
    })

    $(document).on('click', '.plus_one, .minus_one', function (evt) {
        var current_val = parseFloat($(this).siblings('.value').val());
        if($(this).hasClass('plus_one')){
            current_val += 1;
        }else{
            current_val -= 1;
        }
        $(this).siblings('.value').val(current_val);
    })

    // If the user submits form with enter key
    $('#inventory_form').on("submit", e => {
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
        // Bit of a hack, a div with ID of inventory_page defines if this is an edit, or a creaction.
        if($('#inventory_page').length > 0){
            submitinventoryEdit();
        }else{
            submitinventoryCreation();
        }
    }

    // Edits a inventory through the /api/inventory_edit
    function submitinventoryEdit() {
        // Header options
        const options = {
            method: 'POST',
            body: createinventoryData()
        };

        // API call
        fetch('/api/inventory_edit', options).then((response) => {
            if (!response.ok) {
                throw new Error(`HTTP error! Status: ${response.status}`);
            } else {
                // Redirect to inventory page on success
                window.location.replace($('#inventory_page').data('inventory_url'));
            }
        })
    }

    // Creates a inventory through the /api/inventory_create
    function submitinventoryCreation() {
        // Header options
        const options = {
            method: 'POST',
            body: createinventoryData()
        };

        // API call
        fetch('/api/inventory_create', options).then((response) => {
            if (!response.ok) {
                throw new Error(`HTTP error! Status: ${response.status}`);
            } else {
                // Redirect to inventory page on success
                response.json().then((data) => {
                    window.location.replace(data.url);
                })
            }
        })
    }

    // If button with ID log clicked, console out the form data as a JSON object
    $('#log').on('click', function (evt) {
        console.log(JSON.stringify(createinventoryData()))
    })

    function createinventoryData() {
        // Retrieve form data to be parsed
        var form = new FormData(document.getElementById('inventory_form'))

        // Creates an array of integers from all #sortable objects, referencing a data field on each labeled 'editable_id'
        $("#sortable").sortable().find('.item').each(function(){
            form.append('item_id', $(this).data('editable_id'))
        })

        $("#sortable").sortable().find('.value').each(function(){
            form.append('item_count', $(this).val())
        })

		form.append('description', tinymce.get("description").getContent())

        return form
    }

    // Bit of a hack, when any input that needs autocomplete is clicked, refresh autocomplete fields. Needed because fields come/go by user choice
    $(document).on('click', '.single_editor', function (evt) {

        // All autocomplete fields similar to this. Reccomended to copy/paste, edit url, data, and select. Read jQuery UI docs for more detail
        // https://jqueryui.com/autocomplete/
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
                $(this).val(ui.inventory.label);
                $(this).siblings().first().val(ui.inventory.value);
            },
            delay: 200
        });
    });

    // Image sorting/grid, also jQuery UI
    $("#sortable").sortable();
    $("#sortable").disableSelection();

    // Dialog/Modal, jQuery UI
    let dialog = $("#item_selection").dialog({
        autoOpen: false,
        height: (window.innerHeight / 10) * 8,
        width: (window.innerWidth / 10) * 8,
        modal: true,
        open: function (event, ui) {
            $.ajax({
                url: '/api/user_item_grid',
                method: 'GET',
            }).done(function (data) {
                // Insert html snippet into dialog div
                $('#item_selection').html(data)
            });
        },
        buttons: {
            "Select": function(){
                $('#sortable').children().remove();

                $('.image_grid').children().each(function (index) {
                    if ($(this).data('selected')) {
                        var html = $.parseHTML(item_snippet);
                        var snippet = $('#sortable').append(html);

                        var image_src = $(this).children().attr('src');
                        var item_id = $(this).children().data('editable_id');
                        
                        //ungodly selection
                        snippet.children().last().children('img').attr('src', image_src)
                        snippet.children().last().data('editable_id', item_id)

                        $('#sortable').append(snippet);
                    }
                });

                dialog.dialog('close');
            },
            "Disregard": function(){
                dialog.dialog('close');
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
    $('#select_items').on('click', function (evt) {
        dialog.dialog('open')
    });

    // Log image ids on button click
    $('#image_ids').on('click', function (evt) {
        console.log($("#sortable").sortable("toArray", { attribute: "data-editable_id" }))
    });

});