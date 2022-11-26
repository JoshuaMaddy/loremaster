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

    // If the user submits form with enter key
    $('#user_form').on("submit", e => {
        // Do not send form as normal
        e.preventDefault();
        // Send form as modified
        submitForm()
    });

    // If the user submits form with button
    $('#confirm').on('click', () => {
        // Send form as modified
        submitForm()
    })


    function submitForm(){
        // Bit of a hack, a div with ID of character_page defines if this is an edit, or a creaction.
            submitUserEdit();
            console.log(createUserData())
    }

    // Edits a character through the /api/character_edit
    function submitUserEdit() {
        // Header options
        const options = {
            method: 'POST',
            body: createUserData()
        };

        // API call
        fetch('/api/user_edit', options).then((response) => {
            if (!response.ok) {
                throw new Error(`HTTP error! Status: ${response.status}`);
            } else {
                // Redirect to character page on success
                window.location.replace("/");
            }
        })
    }


    // If button with ID log clicked, console out the form data as a JSON object
    $('#log').on('click', function (evt) {
        console.log(JSON.stringify(createUserData()))
    })

    function createUserData() {
        // Retrieve form data to be parsed
        var form = new FormData(document.getElementById('user_form'))

		form.append('description', tinymce.get("description").getContent())

        return form
    }

});