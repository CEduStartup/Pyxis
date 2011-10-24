import bjsonrpc
import simplejson

from django.conf import settings
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from ..forms import OptionsForm

@csrf_exempt
def tracker_data(request):
    if request.POST:
        #TODO Need validate POST data
        print request.POST.getlist('methods')
        c = bjsonrpc.connect()
        data = c.method.get_tracker_data(1)
        print data()
        return HttpResponse(simplejson.dumps(data()), mimetype='application/javascript')
