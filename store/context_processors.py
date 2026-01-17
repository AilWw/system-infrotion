from .models import SiteSettings


def site_settings(request):
    """Add site settings to all templates"""
    try:
        settings = SiteSettings.objects.get(pk=1)
    except SiteSettings.DoesNotExist:
        settings = None
    
    return {'site_settings': settings}
