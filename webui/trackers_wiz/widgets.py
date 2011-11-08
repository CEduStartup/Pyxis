from django.forms import Widget
from django.forms.util import flatatt

from shared.Parser import get_parser
from shared.trackers.datasources import get_datasource

from util import render_to

class ValuePickerWidget(Widget):

    input_type = 'text'

    def render(self, name, value, attrs=None):
        data_type = 1
        if attrs:
            data_type = attrs.get('data_type', 1)
        if data_type == 1:
            render_func = self.render_xml
"""        elif data_type == 2:
            render_func = self.render_csv
        elif data_type == 3:
            render_func = self.render_json
        elif data_type == 4:
            render_func = self.render_html"""
        else:
            render_func = lambda c: 'Data type not supported.'

        render_attrs = self.build_attrs(attrs, type=self.input_type, name=name)
        if value is None:
            value = ''
        else:
            render_attrs['value'] = value

        datasource = get_datasource(datasource_dict)
        datasource.initialize()
        return render_func(datasource.grab_data(), render_attrs)

    @render_to('trackers_wiz/widgets/xml_picker.html')
    def render_xml(self, content, attrs):
        parser = get_parser(gevent_safe=False)
        parser.initialize()
        parser.parse(content)
        return {'node': parser._etree_dom,
                'attrs': flatatt(attrs),
                'input_id': attrs['id']}

    def render_csv(self, content, attrs):
        pass

    def render_json(self, content, attrs):
        pass

    def render_html(self, content, attrs):
        pass

