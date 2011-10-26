from django.forms import Widget
from shared.trackers import DATA_TYPE
from shared.trackers.datasources import get_datasource
from util import render_to

class ValuePickerWidget(Widget):

    def render(self, name, value, attrs=None):
        data_type = 1
        if attrs:
            data_type = attrs.get('data_type', 1)
        if data_type == 1:
            render_func = self.render_xml
        elif data_type == 2:
            render_func = self.render_csv
        elif data_type == 3:
            render_func = self.render_json
        elif data_type == 4:
            render_func = self.render_html
        else:
            render_func = lambda c: 'Data type not supported.'
        
        datasource = get_datasource(datasource_dict)
        datasource.initialize()
        return render_func(datasource.grab_data())

    @render_to('')
    def render_xml(self, content):
        pass

    def render_csv(self, content):
        pass

    def render_json(self, content):
        pass

    def render_html(self, content):
        pass

