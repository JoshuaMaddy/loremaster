// Snippets for image creation
var editor_snippet = `<div class="editor">
<input type="text" name="single_editor" class="single_editor" placeholder="Editor">
<input type="text" name="editor_id" id="editor_id" hidden>
<button type="button" class="remove_editor remove">-</button>
</div>`

$(function (){

	// Reference to file input field
    let chooseFile = document.getElementById("choose-file");;
	// Reference to image preview div
    let imagePreview = $("#image_preview");

	// When user submits the file to the field
    $('#choose-file').on('change', function(){
        getImgData();
    })

	// Read the file, create a temp local URL, insert image in preview div
    function getImgData() {
        const files = chooseFile.files[0];
        if (files) {
          const fileReader = new FileReader();
          fileReader.readAsDataURL(files);
          fileReader.addEventListener("load", function () {
            imagePreview.css('display', 'block')
            imagePreview.html('<img src="' + this.result + '" />');
          });
        }
    }

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

    // Add editor, see character_edit.js for details.
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

    // If the user submits form with enter key
    $('#character_form').on("submit", e => {
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
        // Bit of a hack, a div with ID of image_page defines if this is an edit, or a creaction.
        if($('#image_page').length > 0){
            submitImageEdit();
        }else{
            submitImageCreation();
        }
    }

    // Edits an image through the /api/image_edit
    async function submitImageEdit() {
        // Header options
        const options = {
            method: 'POST',
            body: createImageData()
        };

        // API call
        fetch('/api/image_edit', options).then((response) => {
            if (!response.ok) {
				throw new Error(`HTTP error! Status: ${response.status}`);
            } else {
				// Relocate to revised character page
				response.json().then((data) => {
                    window.location.replace(data.url);
                })
            }
        })
    }

    // Creates an image through the /api/image_create
    async function submitImageCreation() {
        // Header options
        const options = {
            method: 'POST',
            body: createImageData()
        };

        // API call
        fetch('/api/image_create', options).then((response) => {
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

    // If button with ID 'log' clicked, console out the form data as a JSON object
    $('#log').on('click', function (evt) {
        console.log(JSON.stringify(createImageData()))
    })

    // Adds description data to form, sends form, rather than JSON (in contrast to character_edit.js)
    // View fetch functions to see further changes between JSON submission and Form submission.
	function createImageData() {
		// Retrieve form data to be parsed
		var form = new FormData(document.getElementById('image_form'))

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
                $(this).val(ui.item.label);
                $(this).siblings().first().val(ui.item.value);
            },
            delay: 200
        });
    });
});