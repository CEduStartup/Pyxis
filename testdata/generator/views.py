## Generator of test HTML and XML data fro trackers.
from django.http import HttpResponse
import sqlite3
import math
import time
import random


html_template = """
<html>
  <head>
  </head>
  <body>
    <div id="testdata">
      <input name="html_value" value="%(value)s">
    </div>
  </body
</html>"""


xml_template = """
<data>
  <temperature>
    <city id="lviv">
      <temperature val="%(value)s" />
    </city>
  </temperature>
</data>"""


def calculate_next_value(function):
    def sin():
        """Sin(time.current)."""
        return math.sin(time.time()/1000) * 100
    # Add your time functions here.

    # Add your time functions here.
    functions = {'sin': sin}
    return functions[function]()


def html(request, function):
    next_value = calculate_next_value(function)
    result_html = html_template %{'value': next_value}
    gevent.sleep(random.random()*2)
    return HttpResponse(result_html)


def xml(request, function):
    next_value = calculate_next_value(function)
    result_xml = xml_template %{'value': next_value}
    gevent.sleep(random.random()*2)
    return HttpResponse(result_xml)

