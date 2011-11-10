## Generator of test HTML and XML data fro trackers.
from django.http import HttpResponse
import sqlite3
import math
import time
import random
import gevent


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

TEMPLATES = {
    'html': html_template,
    'xml':  xml_template
}

def calculate_next_value(function, divider):
    def sin():
        """Sin(time.current)."""
        return math.sin(time.time()/(10*divider)) * 100
    # Add your time functions here.

    # Add your time functions here.
    functions = {'sin': sin}
    return functions[function]()

def value(request, format, function, divider):
    next_value = calculate_next_value(function, int(divider or 100))
    time.sleep(random.random()*2)
    return HttpResponse(
        TEMPLATES[format] % {'value': next_value}
    )

