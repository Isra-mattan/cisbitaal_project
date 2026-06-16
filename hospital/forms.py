from django import forms
from .models import Patient, Doctor, Specialization, Appointment

class PatientForm(forms.ModelForm):
    class Meta:
        model = Patient
        fields = ['name', 'age', 'gender', 'blood_group', 'marital_status', 'patient_status', 'address', 'phone', 'doctor']
        
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Magaca Bukaanka'}),
            'age': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Da\'da'}),
            'gender': forms.Select(attrs={'class': 'form-select'}),
            'blood_group': forms.Select(attrs={'class': 'form-select'}),
            'marital_status': forms.Select(attrs={'class': 'form-select'}),
            'patient_status': forms.Select(attrs={'class': 'form-select'}),
            'address': forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'placeholder': 'Cinwaanka'}),
            'phone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Lambarka Telefoonka'}),
            'doctor': forms.Select(attrs={'class': 'form-select'}),
        }
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['doctor'].empty_label = "Select Doctor"
        self.fields['gender'].choices = [('', 'Select Gender')] + list(Patient._meta.get_field('gender').choices)
        self.fields['blood_group'].choices = [('', 'Select Blood Group')] + list(Patient._meta.get_field('blood_group').choices)
        self.fields['marital_status'].choices = [('', 'Select Marital Status')] + list(Patient._meta.get_field('marital_status').choices)
        self.fields['patient_status'].choices = [('', 'Select Patient Status')] + list(Patient._meta.get_field('patient_status').choices)
class DoctorForm(forms.ModelForm):
    full_name = forms.CharField(max_length=150, label='Fullname (Magaca Buuxa)', widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Geli magaca buuxa ee dhakhtarka'}))

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.pk and self.instance.user:
            self.fields['full_name'].initial = f"{self.instance.user.first_name} {self.instance.user.last_name}".strip() or self.instance.user.username
        
        self.fields['specialization'].empty_label = "Select Specialization"
        self.fields['department'].empty_label = "Select Department"
        self.fields['gender'].choices = [('', 'Select Gender')] + list(Doctor._meta.get_field('gender').choices)
        self.fields['status'].choices = [('', 'Select Status')] + list(Doctor._meta.get_field('status').choices)
        self.fields['shift_type'].choices = [('', 'Select Shift Type')] + list(Doctor._meta.get_field('shift_type').choices)
        
    class Meta:
        model = Doctor
        fields = ['specialization', 'department', 'phone', 'gender', 'status', 'shift_type']
        
        labels = {
            'specialization': 'Takhasuska (Specialization)',
            'department': 'Qaybta (Department)',
            'phone': 'Lambarka Telefoonka',
            'gender': 'Jinsiga (Gender)',
            'status': 'Xaaladda (Status)',
            'shift_type': 'Shaqada (Shift Type)'
        }
        
        widgets = {
            'specialization': forms.Select(attrs={'class': 'form-select'}),
            'department': forms.Select(attrs={'class': 'form-select'}),
            'phone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Geli talefoonka dhakhtarka'}),
            'gender': forms.Select(attrs={'class': 'form-select'}),
            'status': forms.Select(attrs={'class': 'form-select'}),
            'shift_type': forms.Select(attrs={'class': 'form-select'}),
        }
    def save(self, commit=True):
        doctor = super().save(commit=False)
        full_name = self.cleaned_data.get('full_name').strip()
        names = full_name.split(' ', 1)
        first_name = names[0]
        last_name = names[1] if len(names) > 1 else ''

        if not doctor.pk:
            # Haddii dhakhtar cusub la diiwaangelinayo, samee User account cusub
            from django.contrib.auth import get_user_model
            User = get_user_model()
            base_username = first_name.lower()
            username = base_username
            counter = 1
            while User.objects.filter(username=username).exists():
                username = f"{base_username}{counter}"
                counter += 1
            
            user = User.objects.create_user(
                username=username, 
                password='password123', # Password kumeel gaar ah
                first_name=first_name, 
                last_name=last_name, 
                role='Doctor'
            )
            doctor.user = user
        else:
            # Haddii magaca la bedelayo, cusboonaysii User-ka
            doctor.user.first_name = first_name
            doctor.user.last_name = last_name
            doctor.user.save()

        if commit:
            doctor.save()
        return doctor

class AppointmentForm(forms.ModelForm):
    class Meta:
        model = Appointment
        fields = ['patient', 'department', 'doctor', 'appointment_type', 'appointment_date', 'status']
        labels = {
            'patient': 'Bukaanka (Patient)',
            'department': 'Qaybta (Department)',
            'doctor': 'Dhakhtarka (Doctor)',
            'appointment_type': 'Nooca Ballanta (Type)',
            'appointment_date': 'Taariikhda iyo Saacadda (Date & Time)',
            'status': 'Xaaladda (Status)'
        }
        widgets = {
            'patient': forms.Select(attrs={'class': 'form-select'}),
            'department': forms.Select(attrs={'class': 'form-select', 'id': 'id_department_ajax'}),
            'doctor': forms.Select(attrs={'class': 'form-select', 'id': 'id_doctor_ajax'}),
            'appointment_type': forms.Select(attrs={'class': 'form-select'}),
            'appointment_date': forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'}),
            'status': forms.Select(attrs={'class': 'form-select'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['patient'].empty_label = "Select Patient"
        self.fields['department'].empty_label = "Select Department"
        self.fields['doctor'].empty_label = "Select Doctor"
        self.fields['appointment_type'].choices = [('', 'Select Type')] + list(Appointment._meta.get_field('appointment_type').choices)
        self.fields['status'].choices = [('', 'Select Status')] + list(Appointment._meta.get_field('status').choices)
        
        if 'department' in self.data:
            try:
                department_id = int(self.data.get('department'))
                self.fields['doctor'].queryset = Doctor.objects.filter(department_id=department_id).order_by('user__first_name')
            except (ValueError, TypeError):
                pass
        elif self.instance.pk and self.instance.department:
            self.fields['doctor'].queryset = self.instance.department.doctors.order_by('user__first_name')
        else:
            self.fields['doctor'].queryset = Doctor.objects.none()