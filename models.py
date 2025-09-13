"""
Patient Email Plugin Models

Creates a related model to extend Patient functionality with email.
This approach allows extending the Patient model without modifying the original model file.
"""
from django.core.mail import send_mail
from django.core.validators import EmailValidator
from django.db import models
from django.template.loader import render_to_string
from django.utils.html import strip_tags

from core.models.utils import RitikoModel
from patients.models.people import Patient


class PatientEmail(RitikoModel):
    """
    Email extension for Patient model.

    This model creates a one-to-one relationship with Patient to add email functionality
    without modifying the original Patient model.
    """

    patient = models.OneToOneField(
        Patient,
        on_delete=models.CASCADE,
        related_name="email_profile",
        help_text="Patient this email profile belongs to",
    )

    email = models.EmailField(
        verbose_name="Email Address",
        help_text="Patient's primary email address",
        blank=True,
        null=True,
        validators=[EmailValidator()],
    )

    secondary_email = models.EmailField(
        verbose_name="Secondary Email",
        help_text="Patient's secondary email address (optional)",
        blank=True,
        null=True,
        validators=[EmailValidator()],
    )

    email_verified = models.BooleanField(
        default=False, help_text="Whether the primary email has been verified"
    )

    email_notifications_enabled = models.BooleanField(
        default=True, help_text="Whether patient wants to receive email notifications"
    )

    preferred_email = models.CharField(
        max_length=10,
        choices=[
            ("primary", "Primary Email"),
            ("secondary", "Secondary Email"),
        ],
        default="primary",
        help_text="Which email address to use for notifications",
    )

    email_bounced = models.BooleanField(
        default=False, help_text="Whether emails to this patient have bounced"
    )

    last_email_sent = models.DateTimeField(
        null=True, blank=True, help_text="When the last email was sent to this patient"
    )

    class Meta:
        db_table = "patient_email_profiles"
        verbose_name = "Patient Email Profile"
        verbose_name_plural = "Patient Email Profiles"

    def __str__(self):
        return f"{self.patient.get_full_name()} - {self.get_preferred_email()}"

    def get_preferred_email(self):
        """Get the preferred email address for this patient."""
        if self.preferred_email == "secondary" and self.secondary_email:
            return self.secondary_email
        return self.email or self.secondary_email

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
        Send an email to this patient.

        Args:
            subject (str): Email subject
            message (str): Plain text message (optional if template_name provided)
            html_message (str): HTML message (optional)
            template_name (str): Template name to render (optional)
            context (dict): Template context (optional)
            from_email (str): Sender email (optional)

        Returns:
            bool: True if email was sent successfully, False otherwise
        """
        if not self.email_notifications_enabled:
            return False

        if self.email_bounced:
            return False

        email_address = self.get_preferred_email()
        if not email_address:
            return False

        try:
            # If template_name is provided, render the email content
            if template_name and context is not None:
                # Add patient to context
                context["patient"] = self.patient
                context["email_profile"] = self

                # Render HTML message
                html_message = render_to_string(template_name, context)

                # Create plain text message from HTML if not provided
                if not message:
                    message = strip_tags(html_message)

            # Send the email
            result = send_mail(
                subject=subject,
                message=message or "",
                from_email=from_email,
                recipient_list=[email_address],
                html_message=html_message,
                fail_silently=False,
            )

            if result:
                # Update last email sent timestamp
                from django.utils import timezone

                self.last_email_sent = timezone.now()
                self.save(update_fields=["last_email_sent"])

            return bool(result)

        except Exception as e:
            print(f"Failed to send email to patient {self.patient.pk}: {e}")
            return False

    def send_appointment_reminder(self, appointment_date, appointment_time=None):
        """Send appointment reminder email."""
        context = {
            "appointment_date": appointment_date,
            "appointment_time": appointment_time,
        }

        return self.send_email(
            subject="Appointment Reminder",
            template_name="patient_email_plugin/emails/appointment_reminder.html",
            context=context,
        )

    def send_welcome_email(self):
        """Send welcome email to new patient."""
        return self.send_email(
            subject="Welcome to our healthcare system",
            template_name="patient_email_plugin/emails/welcome.html",
            context={},
        )

    def send_care_plan_update(self, care_plan_details):
        """Send care plan update notification."""
        context = {
            "care_plan_details": care_plan_details,
        }

        return self.send_email(
            subject="Care Plan Update",
            template_name="patient_email_plugin/emails/care_plan_update.html",
            context=context,
        )


class EmailTemplate(RitikoModel):
    """
    Reusable email templates for patient communications.
    """

    name = models.CharField(
        max_length=100, unique=True, help_text="Template name for reference"
    )

    subject = models.CharField(
        max_length=200, help_text="Email subject line (can include template variables)"
    )

    html_content = models.TextField(
        help_text="HTML email content (can include template variables)"
    )

    text_content = models.TextField(
        blank=True,
        help_text="Plain text email content (optional, will be auto-generated from HTML if not provided)",
    )

    is_active = models.BooleanField(
        default=True, help_text="Whether this template is active and can be used"
    )

    description = models.TextField(
        blank=True, help_text="Description of what this template is used for"
    )

    class Meta:
        db_table = "patient_email_templates"
        verbose_name = "Email Template"
        verbose_name_plural = "Email Templates"
        ordering = ["name"]

    def __str__(self):
        return self.name
