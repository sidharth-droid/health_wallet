from django import forms
from django.contrib.auth.models import User
from .models import MedicalHistory, Prescription
import uuid  # Example: for generating a unique record_id
from django.contrib.auth import get_user_model

class UserRegistrationForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput)
    confirm_password = forms.CharField(widget=forms.PasswordInput)

    class Meta:
        model = get_user_model()
        fields = ['username', 'email', 'password']

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        confirm_password = cleaned_data.get("confirm_password")

        if password != confirm_password:
            raise forms.ValidationError("Passwords do not match.")

class MedicalHistoryForm(forms.ModelForm):

    class Meta:
        model = MedicalHistory
        fields = ['condition', 'treatment', 'date_diagnosed', 'notes']

    date_diagnosed = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date'}),
        input_formats=['%Y-%m-%d'],
    )

    def save(self, commit=True):
        instance = super().save(commit=False)
        if not instance.record_id:
            # Generate a unique record_id; adjust as needed
            instance.record_id = uuid.uuid4().int >> 64  # Generates a unique integer
        if commit:
            instance.save()
        return instance

class PrescriptionForm(forms.ModelForm):
    class Meta:
        model = Prescription
        fields = ['medication_name', 'dosage', 'prescribed_date', 'notes']
