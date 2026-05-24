from django.http import HttpResponseForbidden
from functools import wraps
from .models import Case

def admin_or_assigned_required(view_func):
    @wraps(view_func)
    def _wrapped_view(request, pk, *args, **kwargs):
        case = Case.objects.filter(pk=pk).first()
        if not case:
            return HttpResponseForbidden("Case not found.")
        if not (request.user.role == 'admin' or case.assigned_to == request.user):
            return HttpResponseForbidden("You do not have permission to access this case.")
        return view_func(request, pk, *args, **kwargs)
    return _wrapped_view
