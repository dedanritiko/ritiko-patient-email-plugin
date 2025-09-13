"""
Template hooks for extending patient pages.

This module provides template hooks that allow the patient email plugin
to inject content into existing patient detail and edit pages.
"""
from django.template.loader import render_to_string


class PatientTemplateHooks:
    """Template hooks for patient pages."""

    @staticmethod
    def patient_detail_email_section(context, request):
        """
        Template hook to add email section to patient detail page.

        Usage in patient detail template:
        {% load patient_hooks %}
        {% patient_detail_email_section %}
        """
        patient = context.get("patient")
        if not patient:
            return ""

        # Check if user has permission to view email information
        has_permission = request.user.has_perm(
            "patient_email_plugin.can_manage_patient_emails"
        )

        try:
            email_profile = patient.email_profile
        except:
            email_profile = None

        hook_context = {
            "patient": patient,
            "email_profile": email_profile,
            "has_email_permission": has_permission,
            "request": request,
        }

        return render_to_string(
            "patient_email_plugin/partials/patient_detail_email_section.html",
            hook_context,
            request=request,
        )

    @staticmethod
    def patient_edit_email_section(context, request):
        """
        Template hook to add email section to patient edit page.

        Usage in patient edit template:
        {% load patient_hooks %}
        {% patient_edit_email_section %}
        """
        patient = context.get("patient")
        if not patient:
            return ""

        # Check if user has permission to manage email information
        has_permission = request.user.has_perm(
            "patient_email_plugin.can_manage_patient_emails"
        )

        # Import here to avoid circular imports
        from .forms import PatientEmailForm
        from .models import PatientEmail

        # Get or create email profile
        try:
            email_profile, created = PatientEmail.objects.get_or_create(
                patient=patient, defaults={"organization": request.user.organization}
            )
        except:
            email_profile = None

        form = PatientEmailForm(instance=email_profile) if email_profile else None

        hook_context = {
            "patient": patient,
            "email_profile": email_profile,
            "email_form": form,
            "has_email_permission": has_permission,
            "request": request,
        }

        return render_to_string(
            "patient_email_plugin/partials/patient_edit_email_section.html",
            hook_context,
            request=request,
        )

    @staticmethod
    def patient_detail_sidebar_email_widget(context, request):
        """
        Template hook to add email widget to patient detail sidebar.

        Usage in patient detail template sidebar:
        {% load patient_hooks %}
        {% patient_detail_sidebar_email_widget %}
        """
        patient = context.get("patient")
        if not patient:
            return ""

        try:
            email_profile = patient.email_profile
            has_email = bool(email_profile and email_profile.get_preferred_email())
        except:
            email_profile = None
            has_email = False

        hook_context = {
            "patient": patient,
            "email_profile": email_profile,
            "has_email": has_email,
            "request": request,
        }

        return render_to_string(
            "patient_email_plugin/partials/patient_detail_sidebar_email_widget.html",
            hook_context,
            request=request,
        )


# Register template hooks with the plugin system
def register_template_hooks():
    """Register template hooks with the core template hook system."""
    try:
        from core.template_hooks import template_hook_registry

        # Register patient detail page hooks
        template_hook_registry.register_hook(
            "patient_detail_additional_sections",
            PatientTemplateHooks.patient_detail_email_section,
            plugin_id="patient_email_plugin",
            priority=10,
        )

        # Register patient edit page hooks
        template_hook_registry.register_hook(
            "patient_edit_additional_sections",
            PatientTemplateHooks.patient_edit_email_section,
            plugin_id="patient_email_plugin",
            priority=10,
        )

        # Register sidebar widget hook
        template_hook_registry.register_hook(
            "patient_detail_sidebar_widgets",
            PatientTemplateHooks.patient_detail_sidebar_email_widget,
            plugin_id="patient_email_plugin",
            priority=5,
        )

        print("📧 Patient email template hooks registered successfully")

    except ImportError:
        print("⚠️ Template hook registry not available, hooks not registered")


# Auto-register hooks when module is imported
register_template_hooks()
