"""
Vues pour la gestion des heures supplémentaires (weekend en télétravail).
"""

import logging
from datetime import date

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.shortcuts import get_object_or_404, redirect, render

from ..forms import OverTimeRequestForm, OverTimeRequestAdminForm
from ..models import OverTimeRequest

logger = logging.getLogger(__name__)


@login_required
def overtime_list(request):
    """
    Liste des demandes d'heures supplémentaires de l'utilisateur.
    """
    user = request.user
    overtime_requests = OverTimeRequest.objects.filter(user=user).order_by('-work_date')
    
    # Vérifier si l'utilisateur peut voir toutes les demandes (manager, RH, admin)
    can_see_all = user.is_superuser or (
        hasattr(user, "profile") 
        and getattr(user.profile, "role", None) in ["admin", "manager", "rh"]
    )
    
    all_requests = None
    if can_see_all:
        all_requests = OverTimeRequest.objects.all().order_by('-work_date')
    
    return render(
        request,
        "extranet/overtime_list.html",
        {
            "overtime_requests": overtime_requests,
            "all_requests": all_requests,
            "can_see_all": can_see_all,
        },
    )


@login_required
def overtime_create(request):
    """
    Créer une nouvelle demande d'heures supplémentaires.
    Les validateurs peuvent créer pour n'importe quel utilisateur.
    """
    user = request.user
    
    # Vérifier si l'utilisateur peut créer pour d'autres
    can_create_for_others = user.is_superuser or (
        hasattr(user, "profile") 
        and getattr(user.profile, "role", None) in ["admin", "manager", "rh"]
    )
    
    # Choisir le bon formulaire
    FormClass = OverTimeRequestAdminForm if can_create_for_others else OverTimeRequestForm
    
    if request.method == "POST":
        if can_create_for_others:
            form = FormClass(request.POST, current_user=user)
        else:
            form = FormClass(request.POST, user=user)
            
        if form.is_valid():
            try:
                overtime_request = form.save(commit=False)
                
                # Si utilisateur normal, forcer l'utilisateur connecté
                if not can_create_for_others:
                    overtime_request.user = user
                
                # Auto-approuver si créé par un validateur pour lui-même ou quelqu'un d'autre
                if can_create_for_others:
                    overtime_request.status = "approved"
                    overtime_request.manager_validated = True
                    overtime_request.rh_validated = True
                
                overtime_request.save()
                
                success_msg = f"Demande d'heures supplémentaires créée pour le {overtime_request.work_date} ({overtime_request.hours}h)"
                if can_create_for_others and overtime_request.user != user:
                    success_msg += f" pour {overtime_request.user.get_full_name() or overtime_request.user.username}"
                if can_create_for_others:
                    success_msg += " et automatiquement approuvée"
                    
                messages.success(request, success_msg + ".")
                return redirect("extranet:overtime_list")
            except ValidationError as e:
                messages.error(request, str(e))
    else:
        if can_create_for_others:
            form = FormClass(current_user=user)
        else:
            form = FormClass(user=user)
    
    return render(request, "extranet/overtime_form.html", {
        "form": form, 
        "can_create_for_others": can_create_for_others
    })


@login_required
def overtime_create_admin(request):
    """
    Créer et approuver une demande d'heures supplémentaires (managers/RH seulement).
    Version dédiée pour créer rapidement des heures supplémentaires approuvées.
    """
    user = request.user
    
    # Vérifier les permissions
    if not (user.is_superuser or (
        hasattr(user, "profile") 
        and getattr(user.profile, "role", None) in ["admin", "manager", "rh"]
    )):
        messages.error(request, "Vous n'avez pas les permissions pour accéder à cette fonctionnalité.")
        return redirect("extranet:overtime_list")
    
    if request.method == "POST":
        form = OverTimeRequestAdminForm(request.POST, current_user=user)
        
        if form.is_valid():
            try:
                overtime_request = form.save(commit=False)
                
                # Auto-approuver automatiquement
                overtime_request.status = "approved"
                overtime_request.manager_validated = True
                overtime_request.rh_validated = True
                
                overtime_request.save()
                
                success_msg = f"Heures supplémentaires créées et approuvées pour {overtime_request.user.get_full_name() or overtime_request.user.username} "
                success_msg += f"le {overtime_request.work_date} ({overtime_request.hours}h)."
                    
                messages.success(request, success_msg)
                return redirect("extranet:overtime_list")
            except ValidationError as e:
                messages.error(request, str(e))
    else:
        form = OverTimeRequestAdminForm(current_user=user)
    
    return render(request, "extranet/overtime_admin_form.html", {
        "form": form
    })


@login_required
def overtime_edit(request, overtime_id):
    """
    Modifier une demande d'heures supplémentaires existante.
    """
    user = request.user
    overtime_request = get_object_or_404(OverTimeRequest, id=overtime_id)
    
    # Vérifier les permissions : propriétaire ou validateur
    can_edit_others = user.is_superuser or (
        hasattr(user, "profile") 
        and getattr(user.profile, "role", None) in ["admin", "manager", "rh"]
    )
    
    if overtime_request.user != user and not can_edit_others:
        messages.error(request, "Vous n'avez pas les permissions pour modifier cette demande.")
        return redirect("extranet:overtime_list")
    
    # Ne peut être modifiée que si elle est en attente (sauf pour les validateurs)
    if overtime_request.status != "pending" and not can_edit_others:
        messages.error(request, "Seules les demandes en attente peuvent être modifiées.")
        return redirect("extranet:overtime_list")
    
    # Choisir le bon formulaire
    FormClass = OverTimeRequestAdminForm if can_edit_others else OverTimeRequestForm
    
    if request.method == "POST":
        if can_edit_others:
            form = FormClass(request.POST, instance=overtime_request, current_user=user)
        else:
            form = FormClass(request.POST, instance=overtime_request, user=user)
            
        if form.is_valid():
            try:
                form.save()
                messages.success(request, "Demande d'heures supplémentaires modifiée avec succès.")
                return redirect("extranet:overtime_list")
            except ValidationError as e:
                messages.error(request, str(e))
    else:
        if can_edit_others:
            form = FormClass(instance=overtime_request, current_user=user)
        else:
            form = FormClass(instance=overtime_request, user=user)
    
    return render(
        request, 
        "extranet/overtime_form.html", 
        {
            "form": form, 
            "overtime_request": overtime_request,
            "can_create_for_others": can_edit_others
        }
    )


@login_required
def overtime_delete(request, overtime_id):
    """
    Supprimer une demande d'heures supplémentaires.
    """
    user = request.user
    overtime_request = get_object_or_404(OverTimeRequest, id=overtime_id)
    
    # Vérifier les permissions : propriétaire ou validateur
    can_delete_others = user.is_superuser or (
        hasattr(user, "profile") 
        and getattr(user.profile, "role", None) in ["admin", "manager", "rh"]
    )
    
    if overtime_request.user != user and not can_delete_others:
        messages.error(request, "Vous n'avez pas les permissions pour supprimer cette demande.")
        return redirect("extranet:overtime_list")
    
    # Ne peut être supprimée que si elle est en attente (sauf pour les validateurs)
    if overtime_request.status != "pending" and not can_delete_others:
        messages.error(request, "Seules les demandes en attente peuvent être supprimées.")
        return redirect("extranet:overtime_list")
    
    if request.method == "POST":
        owner_name = overtime_request.user.get_full_name() or overtime_request.user.username
        overtime_request.delete()
        
        msg = "Demande d'heures supplémentaires supprimée"
        if overtime_request.user != user:
            msg += f" pour {owner_name}"
        messages.success(request, msg + ".")
        return redirect("extranet:overtime_list")
    
    return render(
        request,
        "extranet/overtime_confirm_delete.html",
        {"overtime_request": overtime_request}
    )


@login_required
def overtime_validate(request, overtime_id):
    """
    Valider ou rejeter une demande d'heures supplémentaires (manager/RH uniquement).
    """
    user = request.user
    
    # Vérifier les permissions
    if not (user.is_superuser or (
        hasattr(user, "profile") 
        and getattr(user.profile, "role", None) in ["admin", "manager", "rh"]
    )):
        messages.error(request, "Vous n'avez pas les permissions pour valider cette demande.")
        return redirect("extranet:overtime_list")
    
    overtime_request = get_object_or_404(OverTimeRequest, id=overtime_id)
    
    if request.method == "POST":
        action = request.POST.get("action")
        
        if action == "approve":
            overtime_request.status = "approved"
            # Marquer comme validé par le bon rôle
            if hasattr(user, "profile") and user.profile.role == "manager":
                overtime_request.manager_validated = True
            elif hasattr(user, "profile") and user.profile.role in ["rh", "admin"]:
                overtime_request.rh_validated = True
                overtime_request.manager_validated = True  # RH peut valider directement
            
            overtime_request.save()
            messages.success(request, "Demande d'heures supplémentaires approuvée.")
            
        elif action == "reject":
            overtime_request.status = "rejected"
            overtime_request.save()
            messages.success(request, "Demande d'heures supplémentaires rejetée.")
        
        return redirect("extranet:overtime_list")
    
    return render(
        request,
        "extranet/overtime_validate.html",
        {"overtime_request": overtime_request}
    )
