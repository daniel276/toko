from .utils.current_user import set_current_user, clear_current_user

class CurrentUserMiddleware:
    """
    Simpan request.user ke thread-local supaya bisa diakses di signals.
    Taruh ini di settings.MIDDLEWARE (setelah AuthenticationMiddleware).
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
        
    def __call__(self, request):
        try:
            user = getattr(request, 'user', None)
            if user and user.is_authenticated:
                set_current_user(user)
            response = self.get_response(request)
            return response
        finally:
            clear_current_user