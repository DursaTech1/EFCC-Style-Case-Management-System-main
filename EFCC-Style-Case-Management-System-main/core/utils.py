from .models import ActivityLog, Notification


def log_activity(user, case, action, details=''):
    ActivityLog.objects.create(user=user, case=case, action=action, details=details)


def role_redirect(user):
    return 'dashboard'


def notify(recipient, notif_type, message, case=None):
    """Create an in-app notification for a user."""
    if recipient:
        Notification.objects.create(
            recipient=recipient,
            notif_type=notif_type,
            message=message,
            case=case,
        )


def notify_case_assigned(case):
    if case.assigned_to:
        notify(
            case.assigned_to,
            'case_assigned',
            f'You have been assigned to case: "{case.title}"',
            case=case,
        )


def notify_status_changed(case, previous_status, new_status, changed_by):
    if case.assigned_to and case.assigned_to != changed_by:
        notify(
            case.assigned_to,
            'status_changed',
            f'Case "{case.title}" status changed from {previous_status} to {new_status}',
            case=case,
        )


def notify_comment_added(case, comment_author):
    recipients = set()
    if case.assigned_to:
        recipients.add(case.assigned_to)
    if case.created_by:
        recipients.add(case.created_by)
    recipients.discard(comment_author)
    for user in recipients:
        notify(
            user,
            'comment_added',
            f'{comment_author.username} commented on case "{case.title}"',
            case=case,
        )


def notify_evidence_uploaded(case, uploader):
    if case.assigned_to and case.assigned_to != uploader:
        notify(
            case.assigned_to,
            'evidence_uploaded',
            f'New evidence uploaded to case "{case.title}" by {uploader.username}',
            case=case,
        )
