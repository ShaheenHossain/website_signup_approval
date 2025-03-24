/** @odoo-module **/


import publicWidget from "@web/legacy/js/public/public_widget";
import { jsonrpc } from "@web/core/network/rpc_service";

var MySignUpForm = publicWidget.registry.SignUpForm.extend({
    _onSubmit: function (el) {
        el.preventDefault();  // Prevent default form submission

        var self = this;
        var files = this.$('.get_attach')[0]?.files || [];
        var email = this.$('input[name=login]').val();
        var username = this.$('input[name=name]').val();
        var password = this.$('input[name=password]').val();
        var first_name = this.$('input[name=first_name]').val();
        var last_name = this.$('input[name=last_name]').val();
        var company_name = this.$('input[name=company_name]').val();
        var birthday = this.$('input[name=birthday]').val();
        var street = this.$('input[name=street]').val();
        var address_supplement = this.$('input[name=address_supplement]').val();
        var province = this.$('input[name=province]').val();
        var city = this.$('input[name=city]').val();
        var postal_code = this.$('input[name=postal_code]').val();
        var phone = this.$('input[name=phone]').val();
        var recommended_by = this.$('input[name=recommended_by]').val();
        var gender = this.$('select[name=gender]').val();
        var accept_terms = this.$('input[name=accept_terms]').is(':checked');

        var data_array = [];
        var promises = [];

        // Remove any previous success or error messages
        this.$('.signup-message').remove();

        // Process file uploads asynchronously
        if (files.length > 0) {
            for (let i = 0; i < files.length; i++) {
                promises.push(
                    new Promise((resolve, reject) => {
                        var reader = new FileReader();
                        reader.onload = (e) => {
                            data_array.push(e.target.result);
                            resolve();
                        };
                        reader.onerror = reject;
                        reader.readAsDataURL(files[i]);
                    })
                );
            }
        }

        // Show loading spinner
        this.$el.addClass('o_submitting');

        // After all files are processed, send data
        Promise.all(promises)
            .then(() => {
                return jsonrpc("/web/signup/approve", {
                    'data': data_array,
                    'email': email,
                    'username': username,
                    'password': password,
                    'first_name': first_name,
                    'last_name': last_name,
                    'company_name': company_name,
                    'birthday': birthday,
                    'street': street,
                    'address_supplement': address_supplement,
                    'province': province,
                    'city': city,
                    'postal_code': postal_code,
                    'phone': phone,
                    'recommended_by': recommended_by,
                    'gender': gender,
                    'accept_terms': accept_terms,
                });
            })
            .then((result) => {
                console.log("Sign-up request sent successfully!", result);

                // Remove loading spinner
                self.$el.removeClass('o_submitting');

                // Show success message
                self.$el.append('<p class="signup-message text-success">Signup request sent successfully!</p>');

                // Ensure message is visible
                $('.signup-message').fadeIn().delay(3000).fadeOut();

                // Optionally redirect after success
                setTimeout(() => {
                    window.location.href = "/web/login";  // Redirect to login page
                }, 3000);
            })
            .catch((error) => {
                console.error("Error uploading files or submitting form:", error);

                // Remove loading spinner
                self.$el.removeClass('o_submitting');

                // Show error message
                self.$el.append('<p class="signup-message text-danger">Signup failed. Please try again.</p>');
                $('.signup-message').fadeIn().delay(5000).fadeOut();
            });
    },
});

publicWidget.registry.MySignUpForm = MySignUpForm;
export default MySignUpForm;



/*

*/
/** @odoo-module **//*

import publicWidget from "@web/legacy/js/public/public_widget";
import { jsonrpc } from "@web/core/network/rpc_service";

var MySignUpForm = publicWidget.registry.SignUpForm.extend({
    selector: '.oe_signup_form',

    start: function () {
        this._super.apply(this, arguments);
        this.$('.get_attach').on('change', this._validateFile.bind(this));
    },

    _validateFile: function () {
        var fileInput = this.$('.get_attach')[0];
        var signupButton = this.$('button[type="submit"]');
        var warningMessage = this.$('.file-warning-message');

        if (warningMessage.length === 0) {
            this.$el.append('<p class="file-warning-message text-danger" style="display: none;">Sie sollten ein Bild (JPG oder PNG) hochladen. Andere Formate werden nicht unterstützt.</p>');
//            this.$el.append('<p class="file-warning-message text-danger" style="display: none;">You should upload an image (JPG or PNG). Other formats are not supported.</p>');
            warningMessage = this.$('.file-warning-message');
        }

        if (fileInput.files.length > 0) {
            var file = fileInput.files[0];
            var allowedFormats = ['image/jpeg', 'image/png'];

            if (!allowedFormats.includes(file.type)) {
                signupButton.prop('disabled', true);
                warningMessage.show();
            } else {
                signupButton.prop('disabled', false);
                warningMessage.hide();
            }
        } else {
            signupButton.prop('disabled', true);
            warningMessage.hide();
        }
    },

    _onSubmit: function (el) {
        el.preventDefault();

        var self = this;
        var files = this.$('.get_attach')[0]?.files || [];
        var email = this.$('input[name=login]').val();
        var username = this.$('input[name=name]').val();
        var password = this.$('input[name=password]').val();
        var first_name = this.$('input[name=first_name]').val();
        var last_name = this.$('input[name=last_name]').val();
        var company_name = this.$('input[name=company_name]').val();
        var birthday = this.$('input[name=birthday]').val();
        var street = this.$('input[name=street]').val();
        var address_supplement = this.$('input[name=address_supplement]').val();
        var province = this.$('input[name=province]').val();
        var city = this.$('input[name=city]').val();
        var postal_code = this.$('input[name=postal_code]').val();
        var phone = this.$('input[name=phone]').val();
        var recommended_by = this.$('input[name=recommended_by]').val();
        var gender = this.$('select[name=gender]').val();
        var accept_terms = this.$('input[name=accept_terms]').is(':checked');

        var data_array = [];
        var promises = [];

        this.$('.signup-message').remove();

        if (files.length > 0) {
            for (let i = 0; i < files.length; i++) {
                promises.push(
                    new Promise((resolve, reject) => {
                        var reader = new FileReader();
                        reader.onload = (e) => {
                            data_array.push(e.target.result);
                            resolve();
                        };
                        reader.onerror = reject;
                        reader.readAsDataURL(files[i]);
                    })
                );
            }
        }

        this.$el.addClass('o_submitting');

        Promise.all(promises)
            .then(() => {
                return jsonrpc("/web/signup/approve", {
                    'data': data_array,
                    'email': email,
                    'username': username,
                    'password': password,
                    'first_name': first_name,
                    'last_name': last_name,
                    'company_name': company_name,
                    'birthday': birthday,
                    'street': street,
                    'address_supplement': address_supplement,
                    'province': province,
                    'city': city,
                    'postal_code': postal_code,
                    'phone': phone,
                    'recommended_by': recommended_by,
                    'gender': gender,
                    'accept_terms': accept_terms,
                });
            })
            .then((result) => {
                console.log("Sign-up request sent successfully!", result);
                self.$el.removeClass('o_submitting');
                self.$el.append('<p class="signup-message text-success">Signup request sent successfully!</p>');
                $('.signup-message').fadeIn().delay(3000).fadeOut();
                setTimeout(() => {
                    window.location.href = "/web/login";
                }, 3000);
            })
            .catch((error) => {
                console.error("Error uploading files or submitting form:", error);
                self.$el.removeClass('o_submitting');
                self.$el.append('<p class="signup-message text-danger">Signup failed. Please try again.</p>');
                $('.signup-message').fadeIn().delay(5000).fadeOut();
            });
    },
});

publicWidget.registry.MySignUpForm = MySignUpForm;
export default MySignUpForm;


*/
