"""
Formulaires pour l'application extranet.
Séparation des formulaires pour une meilleure maintenance.
"""

from django import forms
from django.contrib.auth.models import User

from .models import LeaveRequest, TeleworkRequest, UserProfile, Document, OverTimeRequest

# Reusable CSS class fragments to keep widget attrs under line-length limits
INPUT_DATE_CLASS = (
    "w-full p-3 border border-gray-300 rounded-lg "
    "focus:border-primary focus:ring-2 focus:ring-primary/20 "
    "transition-all duration-200"
)

INPUT_SMALL_CLASS = (
    "w-full p-2 border border-gray-300 rounded-lg "
    "focus:border-primary focus:ring-2 focus:ring-primary/20 transition-all duration-200"
)


class LeaveRequestForm(forms.ModelForm):
    """Formulaire pour les demandes de congé."""

    demi_jour = forms.ChoiceField(
        choices=LeaveRequest.DEMI_JOUR_CHOICES,
        widget=forms.RadioSelect(
            attrs={"class": "form-radio text-primary focus:ring-primary"}
        ),
        label="Demi-journée",
        required=False,
    )

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)

    class Meta:
        model = LeaveRequest
        fields = ["start_date", "end_date", "reason", "demi_jour"]
        # keep widget classes short by reusing module-level constants

        widgets = {
            "start_date": forms.DateInput(
                attrs={
                    "type": "date",
                    "class": INPUT_DATE_CLASS,
                    "required": True,
                }
            ),
            "end_date": forms.DateInput(
                attrs={
                    "type": "date",
                    "class": INPUT_DATE_CLASS,
                    "required": True,
                }
            ),
            "reason": forms.Textarea(
                attrs={
                    "rows": 4,
                    "class": f"{INPUT_DATE_CLASS} resize-vertical",
                    "placeholder": "Motif (optionnel)",
                }
            ),
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

        # Validation des conflits avec les télétravails approuvés si l'utilisateur est fourni
        if self.user and start_date and end_date:
            from .models import TeleworkRequest
            overlapping_telework = TeleworkRequest.objects.filter(
                user=self.user,
                status='approved',
                start_date__lte=end_date,
                end_date__gte=start_date
            )
            
            # Les congés ont priorité sur le télétravail
            # On informe l'utilisateur mais on permet la création
            if overlapping_telework.exists():
                # Stocker les télétravails qui seront annulés pour information
                self.conflicting_teleworks = list(overlapping_telework)
                
                # Ajouter un message d'avertissement (mais pas d'erreur)
                from django.contrib import messages
                telework_list = ", ".join([
                    f"#{tw.id} ({tw.start_date.strftime('%d/%m/%Y')} - {tw.end_date.strftime('%d/%m/%Y')})"
                    for tw in overlapping_telework
                ])
                
                # Note : ce message sera affiché après la validation réussie
                # Il sera ajouté dans la vue lors de la sauvegarde

        return cleaned_data


class TeleworkRequestForm(forms.ModelForm):
    """Formulaire pour les demandes de télétravail."""

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)

    class Meta:
        model = TeleworkRequest
        fields = ["start_date", "end_date", "reason"]
        widgets = {
            "start_date": forms.DateInput(
                attrs={
                    "type": "date",
                    "class": INPUT_DATE_CLASS,
                    "required": True,
                }
            ),
            "end_date": forms.DateInput(
                attrs={
                    "type": "date",
                    "class": INPUT_DATE_CLASS,
                    "required": True,
                }
            ),
            "reason": forms.Textarea(
                attrs={
                    "rows": 4,
                    "class": f"{INPUT_DATE_CLASS} resize-vertical",
                    "placeholder": "Justification (optionnel)",
                }
            ),
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
                    "❌ La date de fin doit être postérieure à la date de début."
                )

        # Validation des conflits avec les congés approuvés si l'utilisateur est fourni
        if self.user and start_date and end_date:
            from .models import LeaveRequest, TeleworkRequest
            
            # 1. Vérification des conflits avec les congés approuvés
            overlapping_leaves = LeaveRequest.objects.filter(
                user=self.user,
                status='approved',
                start_date__lte=end_date,
                end_date__gte=start_date
            )
            
            if overlapping_leaves.exists():
                leave = overlapping_leaves.first()
                raise forms.ValidationError(
                    f"🚫 Conflit avec congé approuvé : Vous avez déjà un congé approuvé "
                    f"du {leave.start_date.strftime('%d/%m/%Y')} au {leave.end_date.strftime('%d/%m/%Y')}. "
                    f"Le télétravail n'est pas autorisé pendant les congés."
                )
            
            # 2. Vérification des conflits avec d'autres demandes de télétravail approuvées
            overlapping_telework = TeleworkRequest.objects.filter(
                user=self.user,
                status='approved',
                start_date__lte=end_date,
                end_date__gte=start_date
            )
            
            # Exclure la demande actuelle si on est en édition
            if self.instance and self.instance.pk:
                overlapping_telework = overlapping_telework.exclude(pk=self.instance.pk)
            
            if overlapping_telework.exists():
                telework = overlapping_telework.first()
                raise forms.ValidationError(
                    f"🔄 Conflit avec télétravail existant : Vous avez déjà une demande de télétravail approuvée "
                    f"du {telework.start_date.strftime('%d/%m/%Y')} au {telework.end_date.strftime('%d/%m/%Y')}. "
                    f"Les périodes de télétravail ne peuvent pas se chevaucher."
                )
            
            # 3. Vérification des conflits avec des demandes en attente
            pending_telework = TeleworkRequest.objects.filter(
                user=self.user,
                status='pending',
                start_date__lte=end_date,
                end_date__gte=start_date
            )
            
            # Exclure la demande actuelle si on est en édition
            if self.instance and self.instance.pk:
                pending_telework = pending_telework.exclude(pk=self.instance.pk)
            
            if pending_telework.exists():
                telework = pending_telework.first()
                raise forms.ValidationError(
                    f"⏳ Conflit avec demande en attente : Vous avez déjà une demande de télétravail en attente "
                    f"du {telework.start_date.strftime('%d/%m/%Y')} au {telework.end_date.strftime('%d/%m/%Y')}. "
                    f"Veuillez attendre la validation de cette demande ou la modifier."
                )

        return cleaned_data


class UserProfileForm(forms.ModelForm):
    """Formulaire pour la gestion des profils utilisateurs."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Personnaliser les querysets pour les champs manager et rh
        # Manager : utilisateurs avec rôle manager ou admin
        self.fields['manager'].queryset = User.objects.filter(
            profile__role__in=['manager', 'admin'],
            is_active=True
        ).order_by('first_name', 'last_name')
        
        # RH : utilisateurs avec rôle rh, admin OU manager (pour les doubles rôles)
        self.fields['rh'].queryset = User.objects.filter(
            profile__role__in=['rh', 'admin', 'manager'],
            is_active=True
        ).order_by('first_name', 'last_name')
        
        # Ajouter une aide contextuelle
        self.fields['rh'].help_text = "Peut être un utilisateur avec rôle RH, Admin ou Manager (double rôle)"

    class Meta:
        model = UserProfile
        fields = ["role", "manager", "rh", "site"]
        widgets = {
            "role": forms.Select(attrs={"class": INPUT_SMALL_CLASS}),
            "manager": forms.Select(attrs={"class": INPUT_SMALL_CLASS}),
            "rh": forms.Select(attrs={"class": INPUT_SMALL_CLASS}),
            "site": forms.Select(attrs={"class": INPUT_SMALL_CLASS}),
        }


class UserCreationForm(forms.ModelForm):
    """Formulaire pour créer de nouveaux utilisateurs."""

    password = forms.CharField(
        widget=forms.PasswordInput(
            attrs={
                "class": INPUT_SMALL_CLASS,
                "placeholder": "••••••••",
            }
        ),
        label="Mot de passe",
    )

    role = forms.ChoiceField(
        choices=[
            ("user", "Utilisateur"),
            ("manager", "Manager"),
            ("rh", "RH"),
            ("admin", "Admin"),
        ],
        widget=forms.Select(attrs={"class": INPUT_SMALL_CLASS}),
        label="Rôle",
    )

    site = forms.ChoiceField(
        choices=UserProfile.SITE_CHOICES,
        widget=forms.Select(attrs={"class": INPUT_SMALL_CLASS}),
        label="Site",
    )

    class Meta:
        model = User
        fields = ["username", "first_name", "last_name", "email"]
        widgets = {
            "username": forms.TextInput(
                attrs={"class": INPUT_SMALL_CLASS, "placeholder": "nom.prenom"}
            ),
            "first_name": forms.TextInput(
                attrs={"class": INPUT_SMALL_CLASS, "placeholder": "Prénom"}
            ),
            "last_name": forms.TextInput(
                attrs={"class": INPUT_SMALL_CLASS, "placeholder": "Nom"}
            ),
            "email": forms.EmailInput(
                attrs={"class": INPUT_SMALL_CLASS, "placeholder": "email@ictgroup.com"}
            ),
        }
        labels = {
            "username": "Login",
            "first_name": "Prénom",
            "last_name": "Nom",
            "email": "Email",
        }

    def clean_email(self):
        """Validation de l'email."""
        email = self.cleaned_data.get("email")
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("Un utilisateur avec cet email existe déjà.")
        return email

    def clean_username(self):
        """Validation du nom d'utilisateur."""
        username = self.cleaned_data.get("username")
        if User.objects.filter(username=username).exists():
            raise forms.ValidationError("Ce nom d'utilisateur existe déjà.")
        return username


class DocumentForm(forms.ModelForm):
    """Formulaire pour l'upload et la modification de documents et liens."""
    
    class Meta:
        model = Document
        fields = [
            'title', 'description', 'category', 'document_type', 
            'file', 'link_url', 'target_type', 'target_users', 'target_roles'
        ]
        
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'w-full p-3 border border-gray-300 rounded-lg focus:border-primary focus:ring-2 focus:ring-primary/20 transition-all duration-200',
                'placeholder': 'Titre du document ou lien'
            }),
            'description': forms.Textarea(attrs={
                'class': 'w-full p-3 border border-gray-300 rounded-lg focus:border-primary focus:ring-2 focus:ring-primary/20 transition-all duration-200',
                'rows': 3,
                'placeholder': 'Description du document ou lien (optionnelle)'
            }),
            'category': forms.Select(attrs={
                'class': 'w-full p-3 border border-gray-300 rounded-lg focus:border-primary focus:ring-2 focus:ring-primary/20 transition-all duration-200'
            }),
            'document_type': forms.Select(attrs={
                'class': 'w-full p-3 border border-gray-300 rounded-lg focus:border-primary focus:ring-2 focus:ring-primary/20 transition-all duration-200',
                'id': 'id_document_type'
            }),
            'file': forms.FileInput(attrs={
                'class': 'w-full p-3 border border-gray-300 rounded-lg focus:border-primary focus:ring-2 focus:ring-primary/20 transition-all duration-200',
                'accept': '.pdf,.doc,.docx,.xls,.xlsx,.ppt,.pptx,.jpg,.jpeg,.png,.gif',
                'id': 'id_file'
            }),
            'link_url': forms.URLInput(attrs={
                'class': 'w-full p-3 border border-gray-300 rounded-lg focus:border-primary focus:ring-2 focus:ring-primary/20 transition-all duration-200',
                'placeholder': 'https://exemple.com',
                'id': 'id_link_url'
            }),
            'target_type': forms.Select(attrs={
                'class': 'w-full p-3 border border-gray-300 rounded-lg focus:border-primary focus:ring-2 focus:ring-primary/20 transition-all duration-200',
                'id': 'id_target_type'
            }),
            'target_users': forms.SelectMultiple(attrs={
                'class': 'w-full p-3 border border-gray-300 rounded-lg focus:border-primary focus:ring-2 focus:ring-primary/20 transition-all duration-200',
                'size': '6'
            }),
            'target_roles': forms.TextInput(attrs={
                'class': 'w-full p-3 border border-gray-300 rounded-lg focus:border-primary focus:ring-2 focus:ring-primary/20 transition-all duration-200',
                'placeholder': 'ex: manager,rh (séparés par des virgules)'
            })
        }
        
        labels = {
            'title': 'Titre',
            'description': 'Description',
            'category': 'Catégorie',
            'document_type': 'Type',
            'file': 'Fichier',
            'link_url': 'URL du lien',
            'target_type': 'Qui peut accéder',
            'target_users': 'Utilisateurs spécifiques',
            'target_roles': 'Rôles (séparés par des virgules)'
        }
        
        help_texts = {
            'target_roles': 'Rôles disponibles: user, manager, rh, admin',
            'file': 'Formats acceptés: PDF, DOC, XLS, PPT, images (requis si type=fichier)',
            'link_url': 'URL complète (requis si type=lien)',
            'document_type': 'Choisissez entre un fichier à uploader ou un lien externe'
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Filtrer les utilisateurs actifs seulement
        self.fields['target_users'].queryset = User.objects.filter(is_active=True).order_by('first_name', 'last_name')
        
    def clean(self):
        """Validation croisée des champs"""
        cleaned_data = super().clean()
        document_type = cleaned_data.get('document_type')
        file = cleaned_data.get('file')
        link_url = cleaned_data.get('link_url')
        
        if document_type == 'file':
            if not file:
                raise forms.ValidationError("Un fichier est requis si le type est 'Fichier'")
            if link_url:
                cleaned_data['link_url'] = None  # Nettoyer le lien si un fichier est sélectionné
        elif document_type == 'link':
            if not link_url:
                raise forms.ValidationError("Une URL est requise si le type est 'Lien'")
            if file:
                cleaned_data['file'] = None  # Nettoyer le fichier si un lien est sélectionné
        
        return cleaned_data
    
    def clean_target_roles(self):
        """Validation des rôles"""
        target_roles = self.cleaned_data.get('target_roles')
        if target_roles:
            valid_roles = ['user', 'manager', 'rh', 'admin']
            roles = [role.strip().lower() for role in target_roles.split(',')]
            invalid_roles = [role for role in roles if role not in valid_roles]
            
            if invalid_roles:
                raise forms.ValidationError(f"Rôles invalides: {', '.join(invalid_roles)}")
                
            return ','.join(roles)
        return target_roles
    
    def clean_file(self):
        """Validation du fichier"""
        file = self.cleaned_data.get('file')
        document_type = self.cleaned_data.get('document_type')
        
        if file and document_type == 'file':
            # Vérifier la taille (max 10MB)
            if file.size > 10 * 1024 * 1024:
                raise forms.ValidationError("Le fichier ne doit pas dépasser 10MB.")
            
            # Vérifier l'extension
            allowed_extensions = [
                '.pdf', '.doc', '.docx', '.xls', '.xlsx', 
                '.ppt', '.pptx', '.jpg', '.jpeg', '.png', '.gif'
            ]
            
            file_extension = file.name.lower().split('.')[-1]
            if f'.{file_extension}' not in allowed_extensions:
                raise forms.ValidationError("Type de fichier non autorisé.")
                
        return file


class OverTimeRequestForm(forms.ModelForm):
    """Formulaire pour les demandes d'heures supplémentaires (weekend en télétravail)."""
    
    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)

    class Meta:
        model = OverTimeRequest
        fields = ["work_date", "hours", "description"]
        widgets = {
            "work_date": forms.DateInput(
                attrs={
                    "type": "date",
                    "class": INPUT_DATE_CLASS,
                    "required": True,
                }
            ),
            "hours": forms.NumberInput(
                attrs={
                    "class": INPUT_SMALL_CLASS,
                    "step": "0.5",
                    "min": "0.5",
                    "max": "12",
                    "placeholder": "Ex: 4.0"
                }
            ),
            "description": forms.Textarea(
                attrs={
                    "class": "w-full p-3 border border-gray-300 rounded-lg "
                            "focus:border-primary focus:ring-2 focus:ring-primary/20 "
                            "transition-all duration-200 resize-none",
                    "rows": 4,
                    "placeholder": "Décrivez le travail effectué..."
                }
            ),
        }
        labels = {
            "work_date": "Date de travail (weekend)",
            "hours": "Nombre d'heures",
            "description": "Description du travail effectué",
        }

    def clean_work_date(self):
        """Validation : s'assurer que la date est un weekend"""
        work_date = self.cleaned_data.get('work_date')
        if work_date:
            # Vérifier que c'est un weekend (samedi=5, dimanche=6)
            if work_date.weekday() not in [5, 6]:
                raise forms.ValidationError("Vous ne pouvez déclarer des heures supplémentaires que pour les weekends (samedi/dimanche).")
            
            # Vérifier qu'il n'y a pas déjà une demande pour cette date
            if self.user:
                existing = OverTimeRequest.objects.filter(
                    user=self.user,
                    work_date=work_date
                )
                if self.instance.pk:
                    existing = existing.exclude(pk=self.instance.pk)
                
                if existing.exists():
                    raise forms.ValidationError("Vous avez déjà une demande d'heures supplémentaires pour cette date.")
        
        return work_date

    def clean_hours(self):
        """Validation des heures"""
        hours = self.cleaned_data.get('hours')
        if hours:
            if hours < 0.5:
                raise forms.ValidationError("Le minimum est de 0.5 heure.")
            if hours > 12:
                raise forms.ValidationError("Le maximum est de 12 heures par jour.")
        return hours


class OverTimeRequestAdminForm(forms.ModelForm):
    """Formulaire pour les managers/RH pour créer des demandes d'heures supplémentaires pour tous les utilisateurs."""
    
    def __init__(self, *args, **kwargs):
        self.current_user = kwargs.pop('current_user', None)
        super().__init__(*args, **kwargs)
        
        # Permettre sélection d'utilisateur seulement si c'est un validateur
        if self.current_user and hasattr(self.current_user, 'profile'):
            role = self.current_user.profile.role
            if role in ['manager', 'rh', 'admin']:
                # Afficher tous les utilisateurs actifs pour les validateurs
                self.fields['user'].queryset = User.objects.filter(is_active=True).order_by('last_name', 'first_name')
                self.fields['user'].empty_label = "Sélectionner un utilisateur"
            else:
                # Cacher le champ pour les utilisateurs normaux
                self.fields['user'].widget = forms.HiddenInput()

    class Meta:
        model = OverTimeRequest
        fields = ["user", "work_date", "hours", "description"]
        widgets = {
            "user": forms.Select(
                attrs={
                    "class": INPUT_SMALL_CLASS,
                }
            ),
            "work_date": forms.DateInput(
                attrs={
                    "type": "date",
                    "class": INPUT_DATE_CLASS,
                    "required": True,
                }
            ),
            "hours": forms.NumberInput(
                attrs={
                    "class": INPUT_SMALL_CLASS,
                    "step": "0.5",
                    "min": "0.5",
                    "max": "12",
                    "placeholder": "Ex: 4.0"
                }
            ),
            "description": forms.Textarea(
                attrs={
                    "class": "w-full p-3 border border-gray-300 rounded-lg "
                            "focus:border-primary focus:ring-2 focus:ring-primary/20 "
                            "transition-all duration-200 resize-none",
                    "rows": 4,
                    "placeholder": "Décrivez le travail effectué..."
                }
            ),
        }
        labels = {
            "user": "Utilisateur",
            "work_date": "Date de travail (weekend)",
            "hours": "Nombre d'heures",
            "description": "Description du travail effectué",
        }

    def clean_work_date(self):
        """Validation : s'assurer que la date est un weekend"""
        work_date = self.cleaned_data.get('work_date')
        if work_date:
            # Vérifier que c'est un weekend (samedi=5, dimanche=6)
            if work_date.weekday() not in [5, 6]:
                raise forms.ValidationError("Vous ne pouvez déclarer des heures supplémentaires que pour les weekends (samedi/dimanche).")
            
            # Vérifier qu'il n'y a pas déjà une demande pour cette date et cet utilisateur
            selected_user = self.cleaned_data.get('user')
            if selected_user:
                existing = OverTimeRequest.objects.filter(
                    user=selected_user,
                    work_date=work_date
                )
                if self.instance.pk:
                    existing = existing.exclude(pk=self.instance.pk)
                
                if existing.exists():
                    raise forms.ValidationError(f"{selected_user.get_full_name() or selected_user.username} a déjà une demande d'heures supplémentaires pour cette date.")
        
        return work_date

    def clean_hours(self):
        """Validation des heures"""
        hours = self.cleaned_data.get('hours')
        if hours:
            if hours < 0.5:
                raise forms.ValidationError("Le minimum est de 0.5 heure.")
            if hours > 12:
                raise forms.ValidationError("Le maximum est de 12 heures par jour.")
        return hours
