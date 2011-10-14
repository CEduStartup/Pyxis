from shared.Parser import get_parser
from util import render_to, IdGenerator

@render_to('frontend/value_picker/value_picker.html')
def xml_picker(request):
    return locals()

@render_to('frontend/value_picker/xml_picker.html')
def load_xml(request):
    parser = get_parser(gevent_safe=False)
    parser.initialize()
    linestring = open('xml.xml', 'r').read()
    parser.parse(linestring)
    generator = IdGenerator()
    return {'node': parser._etree_dom,
            'generator': generator}

