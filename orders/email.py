from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from django.conf import settings

def _send(subject_tpl: str, body_tpl: str, ctx: dict, to_email: str, bcc_email: str | None = None):
    subject = render_to_string(subject_tpl, ctx).strip()
    message = render_to_string(body_tpl, ctx)
    from_email = getattr(settings, "DEFAULT_FROM_EMAIL", "web@example.com")
    to = [to_email]
    bcc = [bcc_email] if bcc_email else None
    email = EmailMessage(subject=subject, body=message, from_email=from_email, to=to, bcc=bcc)
    email.send(fail_silently=False)

def send_order_confirmation(order):
    notify = getattr(settings, "SHOP_NOTIFY_EMAIL", None)
    _send("emails/order_confirmation_subject.txt",
          "emails/order_confirmation.txt",
          {"order": order}, order.email, notify)

def send_tracking_email(order):
    notify = getattr(settings, "SHOP_NOTIFY_EMAIL", None)
    _send("emails/tracking_subject.txt",
          "emails/tracking.txt",
          {"order": order}, order.email, notify)
