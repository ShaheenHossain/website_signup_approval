/** @odoo-module **/

import { patch } from '@web/core/utils/patch';
import { FormController } from '@web/views/form/form_controller';

patch(FormController.prototype, {
    name: 'website_signup_approval.password_toggle',
    doActionButton(button) {
        // Check if the clicked button is our custom toggle button
        if (button.getAttribute('name') === '__toggle_password') {
            const passwordField = this.el.querySelector("input[name='password']");
            if (passwordField) {
                passwordField.type = (passwordField.type === 'password') ? 'text' : 'password';
            }
            // Return a resolved promise so that no server action is attempted.
            return Promise.resolve();
        }
        // For all other buttons, proceed with the original behavior.
        return this._super.apply(this, arguments);
    },
});