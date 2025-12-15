odoo.define('website_signup_approval.file_validation', function (require) {
    "use strict";

    const publicWidget = require('web.public.widget');

    publicWidget.registry.FileValidation = publicWidget.Widget.extend({
        selector: ".oe_import_file",

        events: {
            'change': '_checkFileType',
        },

        _checkFileType: function (ev) {
            let fileInput = ev.target;
            let file = fileInput.files[0];

            if (!file) {
                return;
            }

            let allowedTypes = ['image/jpeg', 'image/png'];

            if (!allowedTypes.includes(file.type)) {
                alert("⚠️ Only JPG or PNG files are allowed!");
                fileInput.value = "";   // Clear the wrong file
            }
        },
    });
});
