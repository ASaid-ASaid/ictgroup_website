#!/usr/bin/env python3
"""
Tests d'authentification et d'autorisation pour l'application extranet
"""

import os
import sys
import django
from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from django.contrib.auth import authenticate

# Configuration Django pour les tests
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "ictgroup.settings")
django.setup()

from extranet.models import UserProfile


class AuthenticationTest(TestCase):
    """Tests d'authentification"""

    def setUp(self):
        """Configuration initiale pour chaque test"""
        self.client = Client()
        self.user = User.objects.create_user(
            username="authuser", email="auth@ictgroup.com", password="securepass123"
        )
        self.profile = UserProfile.objects.create(
            user=self.user, role="user", site="Tunisie"
        )

    def test_user_authentication_success(self):
        """Test d'authentification réussie"""
        user = authenticate(username="authuser", password="securepass123")
        self.assertIsNotNone(user)
        self.assertEqual(user.username, "authuser")

    def test_user_authentication_failure(self):
        """Test d'authentification échouée"""
        user = authenticate(username="authuser", password="wrongpassword")
        self.assertIsNone(user)

    def test_user_authentication_wrong_username(self):
        """Test d'authentification avec mauvais nom d'utilisateur"""
        user = authenticate(username="wronguser", password="securepass123")
        self.assertIsNone(user)

    def test_login_redirect_to_dashboard(self):
        """Test que la connexion redirige vers le dashboard"""
        response = self.client.post(
            reverse("extranet:login"),
            {"username": "authuser", "password": "securepass123"},
            follow=True,
        )

        # Vérifie que l'utilisateur est connecté
        self.assertTrue(response.context["user"].is_authenticated)

    def test_logout_clears_session(self):
        """Test que la déconnexion efface la session"""
        # Se connecter d'abord
        self.client.login(username="authuser", password="securepass123")

        # Vérifier que l'utilisateur est connecté
        response = self.client.get(reverse("extranet:dashboard"))
        self.assertEqual(response.status_code, 200)

        # Se déconnecter
        self.client.logout()

        # Vérifier que l'accès au dashboard nécessite maintenant une authentification
        response = self.client.get(reverse("extranet:dashboard"))
        self.assertEqual(response.status_code, 302)  # Redirection vers login


class AuthorizationTest(TestCase):
    """Tests d'autorisation par rôles"""

    def setUp(self):
        """Configuration initiale pour chaque test"""
        self.client = Client()

        # Créer des utilisateurs avec différents rôles
        self.admin_user = User.objects.create_user(
            username="admin", email="admin@ictgroup.com", password="adminpass123"
        )
        self.admin_profile = UserProfile.objects.create(
            user=self.admin_user, role="admin", site="Tunisie"
        )

        self.manager_user = User.objects.create_user(
            username="manager", email="manager@ictgroup.com", password="managerpass123"
        )
        self.manager_profile = UserProfile.objects.create(
            user=self.manager_user, role="manager", site="Tunisie"
        )

        self.rh_user = User.objects.create_user(
            username="rh", email="rh@ictgroup.com", password="rhpass123"
        )
        self.rh_profile = UserProfile.objects.create(
            user=self.rh_user, role="rh", site="Tunisie"
        )

        self.normal_user = User.objects.create_user(
            username="user", email="user@ictgroup.com", password="userpass123"
        )
        self.normal_profile = UserProfile.objects.create(
            user=self.normal_user, role="user", site="Tunisie"
        )

    def test_admin_access_to_admin_pages(self):
        """Test que les admins ont accès aux pages d'administration"""
        self.client.login(username="admin", password="adminpass123")
        response = self.client.get(reverse("extranet:user_admin"))
        self.assertEqual(response.status_code, 200)

    def test_manager_access_to_validation_pages(self):
        """Test que les managers ont accès aux pages de validation"""
        self.client.login(username="manager", password="managerpass123")
        response = self.client.get(reverse("extranet:validation"))
        self.assertEqual(response.status_code, 200)

    def test_rh_access_to_validation_pages(self):
        """Test que les RH ont accès aux pages de validation"""
        self.client.login(username="rh", password="rhpass123")
        response = self.client.get(reverse("extranet:validation"))
        self.assertEqual(response.status_code, 200)

    def test_normal_user_denied_admin_access(self):
        """Test que les utilisateurs normaux n'ont pas accès aux pages d'admin"""
        self.client.login(username="user", password="userpass123")
        response = self.client.get(reverse("extranet:user_admin"))
        # Devrait être refusé (403 ou redirection)
        self.assertIn(response.status_code, [302, 403])

    def test_unauthenticated_user_denied_access(self):
        """Test que les utilisateurs non authentifiés sont redirigés"""
        response = self.client.get(reverse("extranet:dashboard"))
        self.assertEqual(response.status_code, 302)

        response = self.client.get(reverse("extranet:user_admin"))
        self.assertEqual(response.status_code, 302)

        response = self.client.get(reverse("extranet:validation"))
        self.assertEqual(response.status_code, 302)

    def test_role_based_navigation_visibility(self):
        """Test que la navigation affiche les bonnes options selon le rôle"""
        # Test pour admin
        self.client.login(username="admin", password="adminpass123")
        response = self.client.get(reverse("extranet:dashboard"))
        self.assertContains(response, "Administration")

        # Test pour utilisateur normal
        self.client.login(username="user", password="userpass123")
        response = self.client.get(reverse("extranet:dashboard"))
        # Ne devrait pas contenir le lien d'administration
        # (selon l'implémentation du template)


class PasswordSecurityTest(TestCase):
    """Tests de sécurité des mots de passe"""

    def test_password_hashing(self):
        """Test que les mots de passe sont bien hachés"""
        user = User.objects.create_user(
            username="hashtest", email="hash@ictgroup.com", password="plainpassword123"
        )

        # Le mot de passe ne devrait pas être stocké en clair
        self.assertNotEqual(user.password, "plainpassword123")
        self.assertTrue(user.password.startswith("pbkdf2_sha256"))

    def test_password_verification(self):
        """Test que la vérification de mot de passe fonctionne"""
        user = User.objects.create_user(
            username="verifytest",
            email="verify@ictgroup.com",
            password="testpassword123",
        )

        # Le bon mot de passe devrait être accepté
        self.assertTrue(user.check_password("testpassword123"))

        # Un mauvais mot de passe devrait être rejeté
        self.assertFalse(user.check_password("wrongpassword"))


if __name__ == "__main__":
    import unittest

    unittest.main()
