from django.conf import settings

def cdn_enable(context):
    """ Return global CDN variable for templates.
    """
    return {'CDN': settings.CDN}
