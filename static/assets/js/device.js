
var current_step = "select-user";
var selected_user = null;

function open_select_user_section() {
    $("#add-device-details-section, #review-info-section, #finish-setup-section").hide();
    $(".device-creation-step").removeClass("active");

    $("#select-user-section").show();
    $("#select-user-step-header").addClass("active");
    current_step = "select-user";
}


function open_device_details_section() {
    $("#select-user-section, #review-info-section, #finish-setup-section").hide();
    $(".device-creation-step").removeClass("active");

    $("#add-device-details-section").show();
    $("#device-details-step-header").addClass("active");
    current_step = "add-device-details";
}


function open_review_info_section() {
    $("#select-user-section, #add-device-details-section, #finish-setup-section").hide();
    $(".device-creation-step").removeClass("active");

    $("#review-info-section").show();
    $("#review-info-step-header").addClass("active");
    current_step = "review-info";
}


function open_finish_section() {
    $("#select-user-section, #add-device-details-section, #review-info-section").hide();
    $(".device-creation-step").removeClass("active");

    $("#finish-setup-section").show();
    $("#finish-setup-step-header").addClass("active");
    current_step = "finish-setup";
    
}


function select_default_user() {
    if (selected_user && selected_user.user_id && selected_user.name && selected_user.email) {
        $("#user_id_container").val(selected_user.user_id);
        $("#user_name_container").text(selected_user.name);
        $("#user_email_container").text(selected_user.email);
        $("#user_error").text("");
        open_device_details_section();        
    }
}


function select_user(element) {
    let user_id = $(element).attr("data-user-id");
    let name = $(element).attr("data-name");
    let email = $(element).attr("data-email");
    $("#user_id_container").val(user_id);
    $("#user_name_container").text(name);
    $("#user_email_container").text(email);
    $("#user_error").text("");
    open_device_details_section();
}


function toggle_configuration(element) {
    let device_type = element.value;
    console.log(device_type);
    if (device_type=="mirror") {
        $("#device-configuration").show();
    }else{
        $("#device-configuration").hide();
    }
    
}


$("#device-form").on("submit", function () {
    console.log("Submit function");
    let URL = $("#device-form").attr("action");
    console.log(URL);
    let form = $("#device-form").serialize();
    $(".is-invalid").removeClass("is-invalid");

    // Show finish loading
    if(current_step == "review-info") {
        open_finish_section();
    }

    $.ajax({
        type: 'POST',
        url: URL,  // Replace with the actual URL of your view
        data: `${form}&step=${current_step}`,
        success: function (response) {
            $("#device_config_show").hide();
            $('#main-error').hide();
            $(".is-invalid").removeClass("is-invalid");
            $(".invalid-feedback, .invalid-error").text("");

            let review_data = response;
            console.log(review_data);

            // Setup the device info
            let device = review_data.device;
            $("#device_name_show").text(device.name);
            $("#device_location_show").text(device.location);
            $("#device_type_show").text(device.type);

            // Setup user info
            $("#user_name_show").text(review_data.user.name);
            $("#user_email_show").text(review_data.user.email);


            // Setup configuration
            if (review_data.type.toLowerCase() == 'mirror') {
                // Remove pre exists sections
                $("#device_config_show").show();
                $("#card-review-container").empty();
                $("#card-review-container-show").empty();


                let form_review = review_data.form_review;
                for (let i = 0; i < form_review.length; i++) {
                    let section = form_review[i];
                    let section_fields_element_string = '';
                    let section_field_list = section.field_values

                    for (let [name, value] of Object.entries(section_field_list)) {
                        value = (value) ? value : "Not provided";
                        section_fields_element_string += `
                            <div class="col-sm-6 py-1">
                                <div class="form-group my-2">
                                    <p class="label-title">${name}</p>
                                    <span>${value}</span>                                        
                                </div>
                            </div>
                        `;  
                    
                    }
                    

                    let section_element_string = `
                    
                        
                            <div class="accordion-item">
                                <h2 class="accordion-header" id="panelsStayOpen-heading_${i}">
                                    
                                    <button class="accordion-button" type="button" data-bs-toggle="collapse" data-bs-target="#panelsStayOpen-collapse_${i}" aria-expanded="true" aria-controls="panelsStayOpen-collapse_${i}">
                                        <i class="material-icons">${section.section_icon}</i> <span class="mx-3">${section.section_name}</span>
                                    </button>
                                </h2>
                                <div id="panelsStayOpen-collapse_${i}" class="accordion-collapse collapse show" aria-labelledby="panelsStayOpen-heading_${i}">
                                    <div class="accordion-body">
                                        <div class="row">
                                            ${section_fields_element_string}
                                        </div>
                                    </div>
                                </div>
                            </div>
                    `;

                    $("#card-review-container-show").append(section_element_string);
                }
            }

            if (current_step == "add-device-details") {
                open_review_info_section();
            }else{
                $("#device-success-msg").show();
                $("#device-creating-msg").hide();
                setTimeout(() => {
                    window.location.assign(device.url);
                }, 1000);
            }
            return false;

        },

        error: function (errors) {
            open_device_details_section();
            $('#main-error').show();
            let form_errors = errors.responseJSON;
            for (const [key, error_list] of Object.entries(form_errors)) {
                let error_element_id = `#${key}_error`;
                let input_element_id = `#id_${key}`;
                let error_string = "";
                $(input_element_id).addClass("is-invalid");
                for (let i = 0; i < error_list.length; i++) {
                    const single_error = error_list[i];
                    error_string += `${single_error.message}<br>`;
                }
                $(error_element_id).html(error_string);
            }
            return false;

        }
    });

    return false;
});