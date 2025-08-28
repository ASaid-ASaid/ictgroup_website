#!/usr/bin/env python3
"""
Tests unitaires pour les vues de l'application extranet
"""

import os
import sys
import django
from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from django.contrib.messages import get_messages
from datetime import date, timedelta

# Configuration Django pour les tests
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ictgroup.settings')
django.setup()

from extranet.models import UserProfile, LeaveRequest, TeleworkRequest


class AuthViewsTest(TestCase):
    """Tests pour les vues d'authentification"""
    
    def setUp(self):
        """Configuration initiale pour chaque test"""
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@ictgroup.com',
            password='testpass123'
        )
        self.profile = UserProfile.objects.create(
            user=self.user,
            role='user',
            site='Tunisie'
        )
    
    def test_login_page_loads(self):
        """Test que la page de connexion se charge correctement"""
        response = self.client.get(reverse('extranet:login'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Connexion')
    
    def test_successful_login(self):
        """Test de connexion réussie"""
        response = self.client.post(reverse('extranet:login'), {
            'username': 'testuser',
            'password': 'testpass123'
        })
        # Devrait rediriger vers le dashboard
        self.assertEqual(response.status_code, 302)
    
    def test_invalid_login(self):
        """Test de connexion avec des identifiants invalides"""
        response = self.client.post(reverse('extranet:login'), {
            'username': 'testuser',
            'password': 'wrongpassword'
        })
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Nom d\'utilisateur ou mot de passe incorrect')
    
    def test_logout_redirects(self):
        """Test que la déconnexion redirige correctement"""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('extranet:logout'))
        self.assertEqual(response.status_code, 302)


class DashboardViewsTest(TestCase):
    """Tests pour les vues du dashboard"""
    
    def setUp(self):
        """Configuration initiale pour chaque test"""
        self.client = Client()
        self.user = User.objects.create_user(
            username='dashboard_user',
            email='dashboard@ictgroup.com',
            password='testpass123'
        )
        self.profile = UserProfile.objects.create(
            user=self.user,
            role='user',
            site='Tunisie'
        )
    
    def test_dashboard_requires_login(self):
        """Test que le dashboard nécessite une connexion"""
        response = self.client.get(reverse('extranet:dashboard'))
        self.assertEqual(response.status_code, 302)  # Redirection vers login
    
    def test_dashboard_loads_for_authenticated_user(self):
        """Test que le dashboard se charge pour un utilisateur connecté"""
        self.client.login(username='dashboard_user', password='testpass123')
        response = self.client.get(reverse('extranet:dashboard'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Tableau de bord')


class LeaveViewsTest(TestCase):
    """Tests pour les vues de gestion des congés"""
    
    def setUp(self):
        """Configuration initiale pour chaque test"""
        self.client = Client()
        self.user = User.objects.create_user(
            username='leave_user',
            email='leave@ictgroup.com',
            password='testpass123'
        )
        self.profile = UserProfile.objects.create(
            user=self.user,
            role='user',
            site='Tunisie'
        )
    
    def test_leave_list_requires_login(self):
        """Test que la liste des congés nécessite une connexion"""
        response = self.client.get(reverse('extranet:leave_list'))
        self.assertEqual(response.status_code, 302)
    
    def test_leave_list_loads_for_authenticated_user(self):
        """Test que la liste des congés se charge pour un utilisateur connecté"""
        self.client.login(username='leave_user', password='testpass123')
        response = self.client.get(reverse('extranet:leave_list'))
        self.assertEqual(response.status_code, 200)
    
    def test_leave_request_form_loads(self):
        """Test que le formulaire de demande de congé se charge"""
        self.client.login(username='leave_user', password='testpass123')
        response = self.client.get(reverse('extranet:new_leave_request'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Demande de congé')
    
    def test_leave_request_submission(self):
        """Test de soumission d'une demande de congé"""
        self.client.login(username='leave_user', password='testpass123')
        
        start_date = date.today() + timedelta(days=30)
        end_date = start_date + timedelta(days=5)
        
        response = self.client.post(reverse('extranet:new_leave_request'), {
            'leave_type': 'annual',
            'start_date': start_date.strftime('%Y-%m-%d'),
            'end_date': end_date.strftime('%Y-%m-%d'),
            'reason': 'Vacances test'
        })
        
        # Vérifie que la demande a été créée
        self.assertTrue(LeaveRequest.objects.filter(user=self.user).exists())


class TeleworkViewsTest(TestCase):
    """Tests pour les vues de gestion du télétravail"""
    
    def setUp(self):
        """Configuration initiale pour chaque test"""
        self.client = Client()
        self.user = User.objects.create_user(
            username='telework_user',
            email='telework@ictgroup.com',
            password='testpass123'
        )
        self.profile = UserProfile.objects.create(
            user=self.user,
            role='user',
            site='France'
        )
    
    def test_telework_list_requires_login(self):
        """Test que la liste du télétravail nécessite une connexion"""
        response = self.client.get(reverse('extranet:telework_list'))
        self.assertEqual(response.status_code, 302)
    
    def test_telework_list_loads_for_authenticated_user(self):
        """Test que la liste du télétravail se charge pour un utilisateur connecté"""
        self.client.login(username='telework_user', password='testpass123')
        response = self.client.get(reverse('extranet:telework_list'))
        self.assertEqual(response.status_code, 200)
    
    def test_telework_request_form_loads(self):
        """Test que le formulaire de demande de télétravail se charge"""
        self.client.login(username='telework_user', password='testpass123')
        response = self.client.get(reverse('extranet:new_telework_request'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Nouvelle demande de télétravail')


class AdminViewsTest(TestCase):
    """Tests pour les vues d'administration"""
    
    def setUp(self):
        """Configuration initiale pour chaque test"""
        self.client = Client()
        
        # Utilisateur admin
        self.admin_user = User.objects.create_user(
            username='admin_user',
            email='admin@ictgroup.com',
            password='adminpass123'
        )
        self.admin_profile = UserProfile.objects.create(
            user=self.admin_user,
            role='admin',
            site='Tunisie'
        )
        
        # Utilisateur normal
        self.normal_user = User.objects.create_user(
            username='normal_user',
            email='normal@ictgroup.com',
            password='normalpass123'
        )
        self.normal_profile = UserProfile.objects.create(
            user=self.normal_user,
            role='user',
            site='Tunisie'
        )
    
    def test_admin_pages_require_admin_role(self):
        """Test que les pages d'admin nécessitent le rôle admin"""
        # Test avec utilisateur normal
        self.client.login(username='normal_user', password='normalpass123')
        response = self.client.get(reverse('extranet:user_admin'))
        # Devrait être refusé (403 ou redirection)
        self.assertIn(response.status_code, [302, 403])
    
    def test_admin_pages_accessible_to_admin(self):
        """Test que les pages d'admin sont accessibles aux admins"""
        self.client.login(username='admin_user', password='adminpass123')
        response = self.client.get(reverse('extranet:user_admin'))
        self.assertEqual(response.status_code, 200)
    
    def test_validation_page_for_managers(self):
        """Test de la page de validation pour les managers"""
        # Créer un manager
        manager = User.objects.create_user(
            username='manager_user',
            email='manager@ictgroup.com',
            password='managerpass123'
        )
        manager_profile = UserProfile.objects.create(
            user=manager,
            role='manager',
            site='Tunisie'
        )
        
        self.client.login(username='manager_user', password='managerpass123')
        response = self.client.get(reverse('extranet:validation'))
        self.assertEqual(response.status_code, 200)


class VitrineViewsTest(TestCase):
    """Tests pour les vues du site vitrine"""
    
    def setUp(self):
        """Configuration initiale pour chaque test"""
        self.client = Client()
    
    def test_homepage_loads(self):
        """Test que la page d'accueil se charge correctement"""
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
    
    def test_homepage_contains_expected_content(self):
        """Test que la page d'accueil contient le contenu attendu"""
        response = self.client.get('/')
        self.assertContains(response, 'ICTGROUP')


if __name__ == '__main__':
    import unittest
    unittest.main()
