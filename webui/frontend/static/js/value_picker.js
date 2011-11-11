$(document).ready(function () {
    $('.tree_element_tag_name').live('click', function () {
        $(this).parent().parent().children('.tree_element_content, .tree_element_ellipsis').toggleClass('hide');
    });
});

