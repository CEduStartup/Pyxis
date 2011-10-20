$.ajaxSetup({ 
     beforeSend: function(xhr, settings) {
         function getCookie(name) {
             var cookieValue = null;
             if (document.cookie && document.cookie != '') {
                 var cookies = document.cookie.split(';');
                 for (var i = 0; i < cookies.length; i++) {
                     var cookie = jQuery.trim(cookies[i]);
                     // Does this cookie string begin with the name we want?
                 if (cookie.substring(0, name.length + 1) == (name + '=')) {
                     cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                     break;
                 }
             }
         }
         return cookieValue;
         }
         if (!(/^http:.*/.test(settings.url) || /^https:.*/.test(settings.url))) {
             // Only send the token to relative URLs i.e. locally.
             xhr.setRequestHeader("X-CSRFToken", getCookie('csrftoken'));
         }
     } 
});

function value_picker_load (content, data_type) {
    $.ajax({
        type: 'POST',
        url: '{% url frontend.views.value_picker.load_xml %}/' + data_type + '/',
        success: function (data) {
            $("#value_picker").html(data);
        },
        error: function (XMLHttpRequest, textStatus, errorThrown) {
            /*TODO put error handling here*/
        },
    });
}

$(document).ready(function () {
    $('.tree_element_tag_name').live('click', function () {
        $(this).parent().parent().children('.tree_element_content, .tree_element_footer').toggleClass('hide');
    });
});

