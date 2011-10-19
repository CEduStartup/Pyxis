from django import template

register = template.Library()


@register.inclusion_tag('frontend/templatetags/value_picker/value_picker.html')
def value_picker():
    return locals()

@register.inclusion_tag('frontend/templatetags/value_picker/xml_picker_node.html')
def xml_picker_node(node, generator):
    node_name = node.tag
    node_value = node.text
    nodes = node.getchildren()
    attributes = node.items()
    node_id = 'tree_node_%s' % (generator.get_id(),)
    node_xpath = node.getroottree().getpath(node)
    return locals()

@register.inclusion_tag('frontend/templatetags/value_picker/xml_picker_attribute.html')
def xml_picker_attribute(attribute):
    attribute_name = attribute[0]
    attribute_value = attribute[1]
    return locals()

@register.inclusion_tag('frontend/templatetags/value_picker/html_picker_node.html')
def html_picker_node(node):
    pass

@register.inclusion_tag('frontend/templatetags/value_picker/html_picker_node.html')
def html_picker_attribute(attribute):
    pass

@register.inclusion_tag('frontend/templatetags/value_picker/json_picker.html')
def json_picker():
    pass

