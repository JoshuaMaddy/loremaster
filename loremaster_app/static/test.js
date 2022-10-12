const { default: tinymce } = require("tinymce");



tinymce.init({
    selector: 'textarea#description',
    promotion: false
});