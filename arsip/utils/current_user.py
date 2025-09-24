import threading
_local = threading.local()

def set_current_user(user):
    _local.user = user
    
def get_current_user():
    return getattr(_local, 'user', None)

def clear_current_user():
    if hasattr(_local, 'user'):
        delattr(_local, 'user')