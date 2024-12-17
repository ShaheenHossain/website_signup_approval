/** @odoo-module **/
    import publicWidget from "@web/legacy/js/public/public_widget";
    import { jsonrpc } from "@web/core/network/rpc_service";
    var MySignUpForm = publicWidget.registry.SignUpForm.extend({
        _onSubmit: function (el) {
        /**
        *Override onSubmit function for sending approval request
        */
        var file = this.$('.get_attach');
        var email = this.$('input[name=login]').val();
        var username = this.$('input[name=name]').val();
        var password = this.$('input[name=password]').val();
        var gender = this.$('input[name=gender]').val();
        var first_name = this.$('input[name=first_name]').val();
        var last_name = this.$('input[name=last_name]').val();
        var birthday = this.$('input[name=birthday]').val();
        var street = this.$('input[name=street]').val();
        var city = this.$('input[name=city]').val();
        var postal_code = this.$('input[name=postal_code]').val();
        var country_id = this.$('input[name=country_id]').val();
        var phone = this.$('input[name=phone]').val();
        var recommended_by = this.$('input[name=recommended_by]').val();
        var accept_terms = this.$('input[name=accept_terms]').val();
        //Get signup information's from user
        const data_array = []
        var count=0;
        for (var doc = 0; doc < file.length; doc++) {
              var SelectedFile = new FileReader();
              var data = SelectedFile.readAsDataURL(file[doc].files[0]);
              SelectedFile.addEventListener('load', (e) => {
                 count++;
                 const data = e.target.result;
                 data_array.push(data)
                 if (count===(file.length)){
                 //Pass parameters to the route
                      const route = jsonrpc("/web/signup/approve",
                      {
                          'data':data_array,
                          'email':email,
                          'username':username,
                          'password':password,
                          'gender':gender,
                          'first_name':first_name,
                          'last_name':last_name,
                          'birthday':birthday,
                          'street':street,
                          'city':city,
                          'postal_code':postal_code,
                          'country_id':country_id,
                          'phone':phone,
                          'recommended_by':recommended_by,
                          'accept_terms':accept_terms
                      }
                      )
                 }
              });
            }
        },
    });
    publicWidget.registry.MySignUpForm = MySignUpForm;
    return MySignUpForm;
