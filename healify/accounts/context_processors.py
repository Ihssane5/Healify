from .models import Patient


def patient_context(request):
    current_patient = None
    patient_id = request.session.get('current_patient_id')

    if patient_id:
        try:
            current_patient = Patient.objects.get(id=patient_id)
        except Patient.DoesNotExist:
            current_patient = None

    return {'current_patient': current_patient}

