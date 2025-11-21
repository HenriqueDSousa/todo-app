from django import forms
from django.contrib.auth.models import User
from django.utils import timezone
from .models import Task


class TaskForm(forms.ModelForm):
    """Form for creating and editing tasks"""
    
    class Meta:
        model = Task
        fields = ['title', 'description', 'deadline', 'priority', 'assigned_to']
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter task title'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Enter task description (optional)'
            }),
            'deadline': forms.DateTimeInput(attrs={
                'class': 'form-control',
                'type': 'datetime-local'
            }),
            'priority': forms.Select(attrs={
                'class': 'form-control'
            }),
            'assigned_to': forms.Select(attrs={
                'class': 'form-control'
            }),
        }
    
    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        # Only show users other than the creator in assigned_to
        if self.user:
            self.fields['assigned_to'].queryset = User.objects.exclude(id=self.user.id)
            self.fields['assigned_to'].required = False
            self.fields['assigned_to'].empty_label = "Assign to yourself (or leave empty)"
        
        # Make priority optional since model has default
        self.fields['priority'].required = False
    
    def clean_deadline(self):
        """Validate that deadline is not in the past"""
        deadline = self.cleaned_data.get('deadline')
        if deadline and deadline < timezone.now():
            raise forms.ValidationError("Deadline cannot be in the past.")
        return deadline
    
    def clean(self):
        """Additional form validation"""
        # Update queryset to include creator before validation
        # This allows validation to pass when we auto-assign to creator
        if self.user:
            # Check if assigned_to is empty in raw data
            assigned_to_value = None
            if hasattr(self, 'data') and self.data:
                assigned_to_value = self.data.get('assigned_to', '')
            
            # If assigned_to is empty, we'll auto-assign to creator
            # So update queryset to include creator for validation
            if not assigned_to_value or assigned_to_value == '':
                self.fields['assigned_to'].queryset = User.objects.all()
        
        cleaned_data = super().clean()
        assigned_to = cleaned_data.get('assigned_to')
        
        # If no one is assigned, assign to creator
        if not assigned_to and self.user:
            cleaned_data['assigned_to'] = self.user
        
        return cleaned_data


class TaskFilterForm(forms.Form):
    """Form for filtering tasks"""
    
    STATUS_CHOICES = [
        ('', 'All Statuses'),
        ('pending', 'Pending'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
    ]
    
    PRIORITY_CHOICES = [
        ('', 'All Priorities'),
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
    ]
    
    status = forms.ChoiceField(
        choices=STATUS_CHOICES,
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    priority = forms.ChoiceField(
        choices=PRIORITY_CHOICES,
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    show_completed = forms.BooleanField(
        required=False,
        initial=True,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )
    
    assigned_to_me = forms.BooleanField(
        required=False,
        initial=False,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )


