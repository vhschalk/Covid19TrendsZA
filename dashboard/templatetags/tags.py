from django import template
import os

register = template.Library()

@register.simple_tag
def analytics_id():

    analytics_id = os.environ.get('G_ANALYTICS_ID')
    return analytics_id

@register.simple_tag
def script_id():
    
    script_id = os.environ.get('SCRIPT_ID')
    return script_id
