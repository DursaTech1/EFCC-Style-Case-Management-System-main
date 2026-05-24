from .models import ActivityLog

def log_activity(user, case, action, details=''):
    ActivityLog.objects.create(
        user=user,
        case=case,
        action=action,
        details=details
    )



def role_redirect(user):
    # All roles use the main dashboard; extend this when role-specific dashboards are added
    return 'dashboard'
