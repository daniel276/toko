from django.contrib.auth.decorators import login_required, user_passes_test
from django.shortcuts import render

from accounts.views import is_staff


# Create your views here.

@login_required
@user_passes_test(is_staff)
def dashboard_view(request):
    return render(request, 'main/dashboard.html')

def custom_permission_denied_view(request, exception=None):
    return render(request, 'main/403.html', status=403)

def custom_page_not_found_view(request, exception=None):
    return render(request, 'main/404.html', status=404)