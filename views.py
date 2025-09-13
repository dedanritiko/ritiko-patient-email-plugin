"""
Patient Email Plugin Views

Views for managing patient email functionality and extending existing patient views.
"""
from django.contrib import messages
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.generic import ListView, UpdateView

from patients.models.people import Patient

from .forms import PatientEmailForm, SendEmailForm
from .models import PatientEmail


class PatientEmailListView(PermissionRequiredMixin, ListView):
    """List view for patient email profiles."""

    model = PatientEmail
    template_name = "patient_email_plugin/email_list.html"
    context_object_name = "email_profiles"
    permission_required = "patient_email_plugin.can_manage_patient_emails"
    paginate_by = 25

    def get_queryset(self):
        """Get email profiles for current organization."""
        return PatientEmail.objects.filter(
            organization=self.request.user.organization
        ).select_related("patient")


class PatientEmailEditView(PermissionRequiredMixin, UpdateView):
    """Edit view for patient email profile."""

    model = PatientEmail
    form_class = PatientEmailForm
    template_name = "patient_email_plugin/email_edit.html"
    permission_required = "patient_email_plugin.can_manage_patient_emails"

    def get_object(self):
        """Get or create email profile for the patient."""
        patient_id = self.kwargs.get("patient_id")
        patient = get_object_or_404(
            Patient, pk=patient_id, organization=self.request.user.organization
        )

        email_profile, created = PatientEmail.objects.get_or_create(
            patient=patient, defaults={"organization": self.request.user.organization}
        )
        return email_profile


def patient_detail_email_section(request, patient_id):
    """
    Render email section for patient detail page.
    This is a partial template that can be included in the main patient detail page.
    """
    patient = get_object_or_404(
        Patient, pk=patient_id, organization=request.user.organization
    )

    try:
        email_profile = patient.email_profile
    except PatientEmail.DoesNotExist:
        email_profile = None

    context = {
        "patient": patient,
        "email_profile": email_profile,
        "has_email_permission": request.user.has_perm(
            "patient_email_plugin.can_manage_patient_emails"
        ),
    }

    return render(
        request,
        "patient_email_plugin/partials/patient_detail_email_section.html",
        context,
    )


def patient_edit_email_section(request, patient_id):
    """
    Render email section for patient edit page.
    This is a partial template that can be included in the main patient edit form.
    """
    patient = get_object_or_404(
        Patient, pk=patient_id, organization=request.user.organization
    )

    # Get or create email profile
    email_profile, created = PatientEmail.objects.get_or_create(
        patient=patient, defaults={"organization": request.user.organization}
    )

    if request.method == "POST":
        form = PatientEmailForm(request.POST, instance=email_profile)
        if form.is_valid():
            form.save()
            messages.success(request, "Email settings updated successfully.")
            return JsonResponse({"success": True})
        else:
            return JsonResponse({"success": False, "errors": form.errors})
    else:
        form = PatientEmailForm(instance=email_profile)

    context = {
        "patient": patient,
        "email_profile": email_profile,
        "email_form": form,
        "has_email_permission": request.user.has_perm(
            "patient_email_plugin.can_manage_patient_emails"
        ),
    }

    return render(
        request,
        "patient_email_plugin/partials/patient_edit_email_section.html",
        context,
    )


def send_patient_email(request, patient_id):
    """Send email to a specific patient."""
    patient = get_object_or_404(
        Patient, pk=patient_id, organization=request.user.organization
    )

    if not request.user.has_perm("patient_email_plugin.can_send_patient_emails"):
        messages.error(request, "You don't have permission to send emails to patients.")
        return redirect("patients:detail", patient_id)

    if request.method == "POST":
        form = SendEmailForm(request.POST)
        if form.is_valid():
            success = patient.send_email(
                subject=form.cleaned_data["subject"],
                message=form.cleaned_data["message"],
                html_message=form.cleaned_data.get("html_message"),
            )

            if success:
                messages.success(
                    request, f"Email sent successfully to {patient.get_full_name()}"
                )
            else:
                messages.error(
                    request,
                    "Failed to send email. Please check patient's email configuration.",
                )

            return redirect("patients:detail", patient_id)
    else:
        form = SendEmailForm()

    context = {
        "patient": patient,
        "form": form,
    }

    return render(request, "patient_email_plugin/send_email.html", context)


def ajax_patient_email_quick_actions(request, patient_id):
    """AJAX endpoint for quick email actions from patient detail page."""
    if not request.user.has_perm("patient_email_plugin.can_send_patient_emails"):
        return JsonResponse({"success": False, "error": "Permission denied"})

    patient = get_object_or_404(
        Patient, pk=patient_id, organization=request.user.organization
    )
    action = request.POST.get("action")

    success = False
    message = "Unknown action"

    if action == "send_welcome":
        success = patient.send_welcome_email()
        message = "Welcome email sent" if success else "Failed to send welcome email"

    elif action == "send_appointment_reminder":
        appointment_date = request.POST.get("appointment_date")
        appointment_time = request.POST.get("appointment_time")
        success = patient.send_appointment_reminder(appointment_date, appointment_time)
        message = (
            "Appointment reminder sent"
            if success
            else "Failed to send appointment reminder"
        )

    elif action == "verify_email":
        # Logic to send email verification
        success = patient.send_email(
            subject="Please verify your email address",
            template_name="patient_email_plugin/emails/verify_email.html",
            context={},
        )
        message = (
            "Verification email sent"
            if success
            else "Failed to send verification email"
        )

    return JsonResponse(
        {
            "success": success,
            "message": message,
        }
    )
