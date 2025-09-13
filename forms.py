"""
Patient Email Plugin Forms

Forms for managing patient email functionality.
"""
from django import forms

from .models import EmailTemplate, PatientEmail


class PatientEmailForm(forms.ModelForm):
    """Form for editing patient email profile."""

    class Meta:
        model = PatientEmail
        fields = [
            "email",
            "secondary_email",
            "email_notifications_enabled",
            "preferred_email",
        ]
        widgets = {
            "email": forms.EmailInput(
                attrs={"class": "form-control", "placeholder": "patient@example.com"}
            ),
            "secondary_email": forms.EmailInput(
                attrs={"class": "form-control", "placeholder": "secondary@example.com"}
            ),
            "email_notifications_enabled": forms.CheckboxInput(
                attrs={"class": "form-check-input"}
            ),
            "preferred_email": forms.Select(attrs={"class": "form-control"}),
        }

    def clean(self):
        """Custom validation for email form."""
        cleaned_data = super().clean()
        email = cleaned_data.get("email")
        secondary_email = cleaned_data.get("secondary_email")
        preferred_email = cleaned_data.get("preferred_email")

        # Ensure at least one email is provided if notifications are enabled
        if cleaned_data.get("email_notifications_enabled"):
            if not email and not secondary_email:
                raise forms.ValidationError(
                    "At least one email address is required when email notifications are enabled."
                )

        # Ensure preferred email exists
        if preferred_email == "secondary" and not secondary_email:
            raise forms.ValidationError(
                "Secondary email address is required when it's set as preferred."
            )
        elif preferred_email == "primary" and not email:
            raise forms.ValidationError(
                "Primary email address is required when it's set as preferred."
            )

        return cleaned_data


class SendEmailForm(forms.Form):
    """Form for sending emails to patients."""

    subject = forms.CharField(
        max_length=200,
        widget=forms.TextInput(
            attrs={"class": "form-control", "placeholder": "Email subject"}
        ),
    )

    message = forms.CharField(
        widget=forms.Textarea(
            attrs={
                "class": "form-control",
                "rows": 6,
                "placeholder": "Email message (plain text)",
            }
        )
    )

    html_message = forms.CharField(
        required=False,
        widget=forms.Textarea(
            attrs={
                "class": "form-control",
                "rows": 8,
                "placeholder": "HTML email content (optional)",
            }
        ),
    )

    template = forms.ModelChoiceField(
        queryset=EmailTemplate.objects.none(),
        required=False,
        widget=forms.Select(attrs={"class": "form-control"}),
        help_text="Select a template to auto-fill content",
    )

    def __init__(self, *args, **kwargs):
        organization = kwargs.pop("organization", None)
        super().__init__(*args, **kwargs)

        if organization:
            self.fields["template"].queryset = EmailTemplate.objects.filter(
                organization=organization, is_active=True
            )


class BulkEmailForm(forms.Form):
    """Form for sending bulk emails to multiple patients."""

    recipient_filter = forms.ChoiceField(
        choices=[
            ("all", "All Active Patients"),
            ("with_email", "Patients with Email"),
            ("category", "By Patient Category"),
            ("program", "By Program"),
            ("custom", "Custom Selection"),
        ],
        widget=forms.Select(attrs={"class": "form-control"}),
        help_text="Select which patients to email",
    )

    subject = forms.CharField(
        max_length=200,
        widget=forms.TextInput(
            attrs={"class": "form-control", "placeholder": "Email subject"}
        ),
    )

    message = forms.CharField(
        widget=forms.Textarea(
            attrs={"class": "form-control", "rows": 8, "placeholder": "Email message"}
        )
    )

    template = forms.ModelChoiceField(
        queryset=EmailTemplate.objects.none(),
        required=False,
        widget=forms.Select(attrs={"class": "form-control"}),
        help_text="Select a template to use",
    )

    test_mode = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(attrs={"class": "form-check-input"}),
        help_text="Send test emails only (to your email address)",
    )


class EmailTemplateForm(forms.ModelForm):
    """Form for creating and editing email templates."""

    class Meta:
        model = EmailTemplate
        fields = [
            "name",
            "subject",
            "html_content",
            "text_content",
            "description",
            "is_active",
        ]
        widgets = {
            "name": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "Template name"}
            ),
            "subject": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "Email subject"}
            ),
            "html_content": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 12,
                    "placeholder": "HTML email content",
                }
            ),
            "text_content": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 8,
                    "placeholder": "Plain text version (optional)",
                }
            ),
            "description": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 3,
                    "placeholder": "Template description",
                }
            ),
            "is_active": forms.CheckboxInput(attrs={"class": "form-check-input"}),
        }

    def clean_name(self):
        """Ensure template name is unique within organization."""
        name = self.cleaned_data.get("name")
        if name:
            # Convert to lowercase and replace spaces with underscores for consistency
            name = name.lower().replace(" ", "_")
        return name
