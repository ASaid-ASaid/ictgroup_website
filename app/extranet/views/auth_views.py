"""
Vues d'authentification et de gestion des comptes.
"""

import logging

from django.contrib import messages
from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import PasswordChangeForm
from django.shortcuts import redirect, render

from ..models import UserProfile, get_leave_balance

logger = logging.getLogger(__name__)


def login_view(request):
    """Vue de connexion personnalisée."""
    if request.user.is_authenticated:
        return redirect("extranet:home")

    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            logger.info(f"Connexion réussie pour {username}")
            messages.success(
                request, f"Bienvenue {user.get_full_name() or user.username} !"
            )

            # Redirection vers la page demandée ou l'accueil
            next_url = request.GET.get("next", "extranet:home")
            return redirect(next_url)
        else:
            logger.warning(f"Tentative de connexion échouée pour {username}")
            messages.error(request, "Nom d'utilisateur ou mot de passe incorrect.")

    return render(request, "extranet/login.html")


@login_required
def logout_view(request):
    """Vue de déconnexion."""
    username = request.user.username
    logout(request)
    logger.info(f"Déconnexion de {username}")
    messages.info(request, "Vous avez été déconnecté avec succès.")
    return redirect("extranet:login")


@login_required
def account_settings(request):
    """Vue de gestion des paramètres du compte utilisateur."""
    user = request.user
    profile, created = UserProfile.objects.get_or_create(user=user)

    # Calcul du solde de congés
    leave_balance = get_leave_balance(user)

    # Gestion du changement de mot de passe
    password_form = None
    if request.method == "POST":
        if "change_password" in request.POST:
            password_form = PasswordChangeForm(user, request.POST)
            if password_form.is_valid():
                user = password_form.save()
                update_session_auth_hash(request, user)  # Maintient la session
                logger.info(f"Mot de passe modifié pour {user.username}")
                messages.success(
                    request, "Votre mot de passe a été modifié avec succès."
                )
                return redirect("extranet:account_settings")
            else:
                messages.error(
                    request, "Veuillez corriger les erreurs dans le formulaire."
                )

        elif "update_profile" in request.POST:
            # Mise à jour des informations du profil
            user.first_name = request.POST.get("first_name", "")
            user.last_name = request.POST.get("last_name", "")
            user.email = request.POST.get("email", "")
            user.save()

            logger.info(f"Profil mis à jour pour {user.username}")
            messages.success(request, "Vos informations ont été mises à jour.")
            return redirect("extranet:account_settings")

    if not password_form:
        password_form = PasswordChangeForm(user)

    context = {
        "user": user,
        "profile": profile,
        "leave_balance": leave_balance,
        "password_form": password_form,
    }

    return render(request, "extranet/account_settings.html", context)
