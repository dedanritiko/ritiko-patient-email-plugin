"""
Patient Model Extensions

This module extends the Patient model with email functionality using monkey patching.
This allows adding methods to the Patient model without modifying the original model file.
"""

from patients.models.people import Patient


def get_email_profile(self):
    """
    Get or create the email profile for this patient.

    Returns:
        PatientEmail: The email profile for this patient
    """
    from .models import PatientEmail

    email_profile, created = PatientEmail.objects.get_or_create(
        patient=self, defaults={"organization": self.organization}
    )
    return email_profile


def send_email(
    self,
    subject,
    message=None,
    html_message=None,
    template_name=None,
    context=None,
    from_email=None,
):
    """
    Send an email to this patient using their email profile.

    This method is added to the Patient model to provide easy access to email functionality.

    Args:
        subject (str): Email subject
        message (str): Plain text message (optional if template_name provided)
        html_message (str): HTML message (optional)
        template_name (str): Template name to render (optional)
        context (dict): Template context (optional)
        from_email (str): Sender email (optional)

    Returns:
        bool: True if email was sent successfully, False otherwise

    Usage:
        patient = Patient.objects.get(pk=1)
        patient.send_email(
            subject="Test Email",
            message="This is a test email",
        )

        # Or with template
        patient.send_email(
            subject="Appointment Reminder",
            template_name="patient_email_plugin/emails/appointment_reminder.html",
            context={"appointment_date": "2024-01-15"}
        )
    """
    email_profile = self.get_email_profile()
    return email_profile.send_email(
        subject=subject,
        message=message,
        html_message=html_message,
        template_name=template_name,
        context=context,
        from_email=from_email,
    )


def has_email(self):
    """
    Check if this patient has an email address configured.

    Returns:
        bool: True if patient has an email address, False otherwise
    """
    try:
        email_profile = self.email_profile
        return bool(email_profile.get_preferred_email())
    except Exception:
        return False


def get_email(self):
    """
    Get the preferred email address for this patient.

    Returns:
        str: Email address or None if not available
    """
    try:
        email_profile = self.email_profile
        return email_profile.get_preferred_email()
    except Exception:
        return None


def send_appointment_reminder(self, appointment_date, appointment_time=None):
    """
    Send appointment reminder email to this patient.

    Args:
        appointment_date: The appointment date
        appointment_time: The appointment time (optional)

    Returns:
        bool: True if email was sent successfully, False otherwise
    """
    email_profile = self.get_email_profile()
    return email_profile.send_appointment_reminder(appointment_date, appointment_time)


def send_welcome_email(self):
    """
    Send welcome email to this patient.

    Returns:
        bool: True if email was sent successfully, False otherwise
    """
    email_profile = self.get_email_profile()
    return email_profile.send_welcome_email()


def send_care_plan_update(self, care_plan_details):
    """
    Send care plan update notification to this patient.

    Args:
        care_plan_details: Details about the care plan update

    Returns:
        bool: True if email was sent successfully, False otherwise
    """
    email_profile = self.get_email_profile()
    return email_profile.send_care_plan_update(care_plan_details)


# Add methods to the Patient model
Patient.add_to_class("get_email_profile", get_email_profile)
Patient.add_to_class("send_email", send_email)
Patient.add_to_class("has_email", has_email)
Patient.add_to_class("get_email", get_email)
Patient.add_to_class("send_appointment_reminder", send_appointment_reminder)
Patient.add_to_class("send_welcome_email", send_welcome_email)
Patient.add_to_class("send_care_plan_update", send_care_plan_update)

print("📧 Patient model extended with email functionality")
