$(document).ready(function () {
    $('.tree_element_tag_name').live('click', function () {
        $(this).parent().parent().children('.tree_element_content, .tree_element_ellipsis').toggleClass('hide');
    });

    $('.value_picker_selectable').live('click', function () {
        $('#value_picker input:text').attr('value', $(this).attr('xpath'));
        if(typeof(valuePickerOnChange) == 'function'){
            valuePickerOnChange($(this).text());
        }
    });
});

