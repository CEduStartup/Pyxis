from django import template

register = template.Library()


@register.inclusion_tag('trackers_wiz/templatetags/value_picker/xml_picker_node.html')
def xml_picker_node(node):
    """Renders XML node.

    :Parameters:
        - `node`: etree node that should be rendered.
    """
    node_name = node.tag
    node_value = node.text
    nodes = node.getchildren()
    attributes = node.items()
    node_xpath = node.getroottree().getpath(node)
    return locals()

@register.inclusion_tag('trackers_wiz/templatetags/value_picker/xml_picker_attribute.html')
def xml_picker_attribute(attribute):
    """Renders XML attribute for node

    :Parameters:
        - `attribute`: tuple (name, value).
    """
    attribute_name = attribute[0]
    attribute_value = attribute[1]
    return locals()

@register.inclusion_tag('trackers_wiz/templatetags/value_picker/html_picker_node.html')
def html_picker_node(node):
    """Renders HTML node.

    :Parameters:
        - `node`: etree node that should be rendered.
    """
    pass

@register.inclusion_tag('trackers_wiz/templatetags/value_picker/html_picker_attribute.html')
def html_picker_attribute(attribute):
    """Renders HTML attribute for node

    :Parameters:
        - `attribute`: tuple (name, value).
    """
    pass

@register.inclusion_tag('trackers_wiz/templatetags/value_picker/json_picker_node.html')
def json_picker_node(node):
    pass

@register.inclusion_tag('trackers_wiz/templatetags/value_picker/json_picker_attribute.html')
def json_picker_attribute(attribute):
    pass

