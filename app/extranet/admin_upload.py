"""
Vue d'upload CSV pour l'administration Django
Permet aux administrateurs d'importer des utilisateurs via l'interface admin
"""
import os
import csv
import tempfile
from django.contrib import admin, messages
from django.shortcuts import render, redirect
from django.urls import path, reverse
from django.contrib.admin.views.decorators import staff_member_required
from django.utils.decorators import method_decorator
from django.http import HttpResponseRedirect
from django.core.management import call_command
from io import StringIO
from django.utils.html import format_html


class UserImportAdmin:
    """
    Classe pour gérer l'upload CSV dans l'admin
    """
    
    def get_urls(self):
        """Ajouter l'URL d'upload CSV"""
        urls = [
            path('import-users/', self.admin_site.admin_view(self.import_users_view), name='import_users'),
        ]
        return urls
    
    @method_decorator(staff_member_required)
    def import_users_view(self, request):
        """Vue pour l'upload et traitement du CSV"""
        if request.method == 'POST':
            return self.process_csv_upload(request)
        
        # Affichage du formulaire d'upload
        context = {
            'title': 'Importer des utilisateurs depuis un CSV',
            'has_permission': True,
            'site_url': reverse('admin:index'),
            'csv_format_example': self.get_csv_format_example(),
            'required_columns': [
                'username', 'nom', 'prenom', 'days_acquired', 'days_taken', 
                'days_carry_over', 'site', 'mail', 'password', 'role', 'manager', 'rh'
            ]
        }
        
        return render(request, 'admin/import_users.html', context)
    
    def process_csv_upload(self, request):
        """Traite l'upload du fichier CSV"""
        if 'csv_file' not in request.FILES:
            messages.error(request, 'Aucun fichier sélectionné.')
            return redirect('admin:import_users')
        
        csv_file = request.FILES['csv_file']
        dry_run = request.POST.get('dry_run') == 'on'
        overwrite = request.POST.get('overwrite') == 'on'
        
        # Validation du fichier
        if not csv_file.name.endswith('.csv'):
            messages.error(request, 'Le fichier doit être au format CSV.')
            return redirect('admin:import_users')
        
        if csv_file.size > 5 * 1024 * 1024:  # 5MB max
            messages.error(request, 'Le fichier est trop volumineux (max 5MB).')
            return redirect('admin:import_users')
        
        try:
            # Sauvegarde temporaire du fichier
            with tempfile.NamedTemporaryFile(mode='w+b', suffix='.csv', delete=False) as temp_file:
                for chunk in csv_file.chunks():
                    temp_file.write(chunk)
                temp_file_path = temp_file.name
            
            # Exécution de la commande d'import
            output = StringIO()
            
            # Arguments pour la commande
            args = ['import_update_users', '--file', temp_file_path]
            if dry_run:
                args.append('--dry-run')
            if overwrite:
                args.append('--overwrite')
            
            try:
                call_command(*args, stdout=output)
                
                # Récupération du résultat
                result = output.getvalue()
                
                if dry_run:
                    messages.success(request, f'Simulation terminée avec succès!\\n\\n{result}')
                else:
                    messages.success(request, f'Import terminé avec succès!\\n\\n{result}')
                    
            except Exception as e:
                messages.error(request, f'Erreur lors de l\\'import: {str(e)}')
            
            finally:
                # Nettoyage du fichier temporaire
                try:
                    os.unlink(temp_file_path)
                except:
                    pass
        
        except Exception as e:
            messages.error(request, f'Erreur lors du traitement: {str(e)}')
        
        return redirect('admin:import_users')
    
    def get_csv_format_example(self):
        """Retourne un exemple de format CSV"""
        return '''username,nom,prenom,days_acquired,days_taken,days_carry_over,site,mail,password,role,manager,rh
jdupont,Dupont,Jean,25.0,5.0,3.0,france,j.dupont@ictgroup.fr,Password123!,user,manager_user,rh_user
mmartin,Martin,Marie,22.0,8.0,0.0,tunisie,m.martin@ictgroup.fr,Password123!,manager,admin_user,rh_user'''


# Instance globale pour l'intégration admin
user_import_admin = UserImportAdmin()


def get_import_link():
    """Génère le lien d'import pour l'affichage dans l'admin"""
    return format_html(
        '<a href="{}" class="button" style="margin-left: 10px;">📂 Importer CSV</a>',
        reverse('admin:import_users')
    )
