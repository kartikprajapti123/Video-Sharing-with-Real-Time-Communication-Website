from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from decouple import config


def send_email_verfication(subject, to, context):
    html_content = render_to_string('verify-otp.html', context)
    text_content = strip_tags(html_content)

    email = EmailMultiAlternatives(
        subject,
        text_content,
        config('SEND_EMAIL'),  # From email
        [to]  # To email
    )
    email.attach_alternative(html_content, "text/html")
    email.send()
    

def send_reset_password_mail(subject, to, context):
    html_content = render_to_string('reset-password-mail.html', context)
    text_content = strip_tags(html_content)

    email = EmailMultiAlternatives(
        subject,
        text_content,
        config('SEND_EMAIL'),  # From email
        [to]  # To email
    )
    email.attach_alternative(html_content, "text/html")
    email.send()
    
    