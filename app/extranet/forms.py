"""
Formulaires pour l'application extranet.
Séparation des formulaires pour une meilleure maintenance.
"""

from django import forms
from .models import LeaveRequest, TeleworkRequest, UserProfile
from django.contrib.auth.models import User


class LeaveRequestForm(forms.ModelForm):
    """Formulaire pour les demandes de congé."""
    
    demi_jour = forms.ChoiceField(
        choices=LeaveRequest.DEMI_JOUR_CHOICES,
        widget=forms.RadioSelect(attrs={
            'class': 'form-radio text-primary focus:ring-primary'
        }),
        label="Demi-journée",
        required=False,
    )

    class Meta:
        model = LeaveRequest
        fields = ["start_date", "end_date", "reason", "demi_jour"]
        widgets = {
            "start_date": forms.DateInput(attrs={
                "type": "date",
                "class": "w-full p-3 border border-gray-300 rounded-lg focus:border-primary focus:ring-2 focus:ring-primary/20 transition-all duration-200",
                "required": True,
            }),
            "end_date": forms.DateInput(attrs={
                "type": "date", 
                "class": "w-full p-3 border border-gray-300 rounded-lg focus:border-primary focus:ring-2 focus:ring-primary/20 transition-all duration-200",
                "required": True,
            }),
            "reason": forms.Textarea(attrs={
                "rows": 4,
                "class": "w-full p-3 border border-gray-300 rounded-lg focus:border-primary focus:ring-2 focus:ring-primary/20 transition-all duration-200 resize-vertical",
                "placeholder": "Motif de votre demande de congé (optionnel)...",
            }),
        }
        labels = {
            "start_date": "Date de début",
            "end_date": "Date de fin", 
            "reason": "Motif (optionnel)",
            "demi_jour": "Type de congé",
        }

    def clean(self):
        """Validation personnalisée du formulaire."""
        cleaned_data = super().clean()
        start_date = cleaned_data.get("start_date")
        end_date = cleaned_data.get("end_date")
        
        if start_date and end_date:
            if end_date < start_date:
                raise forms.ValidationError(
                    "La date de fin doit être postérieure à la date de début."
                )
                
        return cleaned_data


class TeleworkRequestForm(forms.ModelForm):
    """Formulaire pour les demandes de télétravail."""
    
    class Meta:
        model = TeleworkRequest
        fields = ["start_date", "end_date", "reason"]
        widgets = {
            "start_date": forms.DateInput(attrs={
                "type": "date",
                "class": "w-full p-3 border border-gray-300 rounded-lg focus:border-primary focus:ring-2 focus:ring-primary/20 transition-all duration-200",
                "required": True,
            }),
            "end_date": forms.DateInput(attrs={
                "type": "date",
                "class": "w-full p-3 border border-gray-300 rounded-lg focus:border-primary focus:ring-2 focus:ring-primary/20 transition-all duration-200", 
                "required": True,
            }),
            "reason": forms.Textarea(attrs={
                "rows": 4,
                "class": "w-full p-3 border border-gray-300 rounded-lg focus:border-primary focus:ring-2 focus:ring-primary/20 transition-all duration-200 resize-vertical",
                "placeholder": "Justification de votre demande de télétravail (optionnel)...",
            }),
        }
        labels = {
            "start_date": "Date de début",
            "end_date": "Date de fin",
            "reason": "Justification (optionnel)",
        }

    def clean(self):
        """Validation personnalisée du formulaire."""
        cleaned_data = super().clean()
        start_date = cleaned_data.get("start_date")
        end_date = cleaned_data.get("end_date")
        
        if start_date and end_date:
            if end_date < start_date:
                raise forms.ValidationError(
                    "La date de fin doit être postérieure à la date de début."
                )
                
        return cleaned_data


class UserProfileForm(forms.ModelForm):
    """Formulaire pour la gestion des profils utilisateurs."""
    
    class Meta:
        model = UserProfile
        fields = ['role', 'manager', 'rh', 'site', 'carry_over']
        widgets = {
            'role': forms.Select(attrs={
                'class': 'w-full p-2 border border-gray-300 rounded-lg focus:border-primary focus:ring-2 focus:ring-primary/20 transition-all duration-200'
            }),
            'manager': forms.Select(attrs={
                'class': 'w-full p-2 border border-gray-300 rounded-lg focus:border-primary focus:ring-2 focus:ring-primary/20 transition-all duration-200'
            }),
            'rh': forms.Select(attrs={
                'class': 'w-full p-2 border border-gray-300 rounded-lg focus:border-primary focus:ring-2 focus:ring-primary/20 transition-all duration-200'
            }),
            'site': forms.Select(attrs={
                'class': 'w-full p-2 border border-gray-300 rounded-lg focus:border-primary focus:ring-2 focus:ring-primary/20 transition-all duration-200'
            }),
            'carry_over': forms.NumberInput(attrs={
                'class': 'w-full p-2 border border-gray-300 rounded-lg focus:border-primary focus:ring-2 focus:ring-primary/20 transition-all duration-200',
                'min': '0',
                'step': '0.1'
            }),
        }


class UserCreationForm(forms.ModelForm):
    """Formulaire pour créer de nouveaux utilisateurs."""
    
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'w-full p-2 border border-gray-300 rounded-lg focus:border-primary focus:ring-2 focus:ring-primary/20 transition-all duration-200',
            'placeholder': '••••••••'
        }),
        label="Mot de passe"
    )
    
    role = forms.ChoiceField(
        choices=[
            ("user", "Utilisateur"),
            ("manager", "Manager"),
            ("rh", "RH"),
            ("admin", "Admin"),
        ],
        widget=forms.Select(attrs={
            'class': 'w-full p-2 border border-gray-300 rounded-lg focus:border-primary focus:ring-2 focus:ring-primary/20 transition-all duration-200'
        }),
        label="Rôle"
    )
    
    site = forms.ChoiceField(
        choices=UserProfile.SITE_CHOICES,
        widget=forms.Select(attrs={
            'class': 'w-full p-2 border border-gray-300 rounded-lg focus:border-primary focus:ring-2 focus:ring-primary/20 transition-all duration-200'
        }),
        label="Site"
    )

    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email']
        widgets = {
            'username': forms.TextInput(attrs={
                'class': 'w-full p-2 border border-gray-300 rounded-lg focus:border-primary focus:ring-2 focus:ring-primary/20 transition-all duration-200',
                'placeholder': 'nom.prenom'
            }),
            'first_name': forms.TextInput(attrs={
                'class': 'w-full p-2 border border-gray-300 rounded-lg focus:border-primary focus:ring-2 focus:ring-primary/20 transition-all duration-200',
                'placeholder': 'Prénom'
            }),
            'last_name': forms.TextInput(attrs={
                'class': 'w-full p-2 border border-gray-300 rounded-lg focus:border-primary focus:ring-2 focus:ring-primary/20 transition-all duration-200',
                'placeholder': 'Nom'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'w-full p-2 border border-gray-300 rounded-lg focus:border-primary focus:ring-2 focus:ring-primary/20 transition-all duration-200',
                'placeholder': 'email@ictgroup.com'
            }),
        }
        labels = {
            'username': 'Login',
            'first_name': 'Prénom',
            'last_name': 'Nom',
            'email': 'Email',
        }

    def clean_email(self):
        """Validation de l'email."""
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("Un utilisateur avec cet email existe déjà.")
        return email

    def clean_username(self):
        """Validation du nom d'utilisateur."""
        username = self.cleaned_data.get('username')
        if User.objects.filter(username=username).exists():
            raise forms.ValidationError("Ce nom d'utilisateur existe déjà.")
        return username
