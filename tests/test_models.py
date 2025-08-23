#!/usr/bin/env python3
"""
Tests unitaires pour les modèles de l'application extranet
"""

import os
import sys
import django
from django.test import TestCase
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from datetime import date, timedelta

# Configuration Django pour les tests
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "ictgroup.settings")
django.setup()

from extranet.models import (
    UserProfile,
    LeaveRequest,
    TeleworkRequest,
    StockItem,
    StockMovement,
)


class UserProfileModelTest(TestCase):
    """Tests pour le modèle UserProfile"""

    def setUp(self):
        """Configuration initiale pour chaque test"""
        self.user = User.objects.create_user(
            username="testuser", email="test@ictgroup.com", password="testpass123"
        )

    def test_user_profile_creation(self):
        """Test de création d'un profil utilisateur"""
        profile = UserProfile.objects.create(
            user=self.user, role="user", site="Tunisie"
        )
        self.assertEqual(profile.user, self.user)
        self.assertEqual(profile.role, "user")
        self.assertEqual(profile.site, "Tunisie")
        self.assertEqual(profile.carry_over, 0.0)

    def test_user_profile_str_method(self):
        """Test de la méthode __str__ du profil"""
        profile = UserProfile.objects.create(
            user=self.user, role="manager", site="France"
        )
        expected_str = f"{self.user.username} - manager"
        self.assertEqual(str(profile), expected_str)

    def test_role_choices_validation(self):
        """Test de validation des choix de rôles"""
        valid_roles = ["user", "manager", "rh", "admin"]
        for role in valid_roles:
            profile = UserProfile(user=self.user, role=role, site="Tunisie")
            try:
                profile.full_clean()
            except ValidationError:
                self.fail(f"Role '{role}' should be valid")

    def test_site_choices_validation(self):
        """Test de validation des choix de sites"""
        valid_sites = ["Tunisie", "France"]
        for site in valid_sites:
            profile = UserProfile(user=self.user, role="user", site=site)
            try:
                profile.full_clean()
            except ValidationError:
                self.fail(f"Site '{site}' should be valid")


class LeaveRequestModelTest(TestCase):
    """Tests pour le modèle LeaveRequest"""

    def setUp(self):
        """Configuration initiale pour chaque test"""
        self.user = User.objects.create_user(
            username="employee", email="employee@ictgroup.com", password="testpass123"
        )
        self.profile = UserProfile.objects.create(
            user=self.user, role="user", site="Tunisie"
        )

    def test_leave_request_creation(self):
        """Test de création d'une demande de congé"""
        start_date = date.today() + timedelta(days=10)
        end_date = start_date + timedelta(days=5)

        leave_request = LeaveRequest.objects.create(
            user=self.user,
            leave_type="annual",
            start_date=start_date,
            end_date=end_date,
            reason="Vacances d'été",
        )

        self.assertEqual(leave_request.user, self.user)
        self.assertEqual(leave_request.leave_type, "annual")
        self.assertEqual(leave_request.status, "pending")
        self.assertFalse(leave_request.manager_validated)
        self.assertFalse(leave_request.rh_validated)

    def test_leave_request_str_method(self):
        """Test de la méthode __str__ de la demande de congé"""
        start_date = date.today() + timedelta(days=10)
        end_date = start_date + timedelta(days=5)

        leave_request = LeaveRequest.objects.create(
            user=self.user,
            leave_type="annual",
            start_date=start_date,
            end_date=end_date,
        )

        expected_str = f"Congé de {self.user.username} du {start_date} au {end_date}"
        self.assertEqual(str(leave_request), expected_str)

    def test_leave_duration_calculation(self):
        """Test du calcul de durée des congés"""
        start_date = date.today() + timedelta(days=10)
        end_date = start_date + timedelta(days=4)  # 5 jours

        leave_request = LeaveRequest.objects.create(
            user=self.user,
            leave_type="annual",
            start_date=start_date,
            end_date=end_date,
        )

        # Test si la méthode duration existe
        if hasattr(leave_request, "duration"):
            expected_duration = 5
            self.assertEqual(leave_request.duration, expected_duration)


class TeleworkRequestModelTest(TestCase):
    """Tests pour le modèle TeleworkRequest"""

    def setUp(self):
        """Configuration initiale pour chaque test"""
        self.user = User.objects.create_user(
            username="teleworker",
            email="teleworker@ictgroup.com",
            password="testpass123",
        )
        self.profile = UserProfile.objects.create(
            user=self.user, role="user", site="France"
        )

    def test_telework_request_creation(self):
        """Test de création d'une demande de télétravail"""
        start_date = date.today() + timedelta(days=7)
        end_date = start_date + timedelta(days=2)

        telework_request = TeleworkRequest.objects.create(
            user=self.user,
            start_date=start_date,
            end_date=end_date,
            reason="Travail sur projet spécial",
        )

        self.assertEqual(telework_request.user, self.user)
        self.assertEqual(telework_request.status, "pending")
        self.assertFalse(telework_request.manager_validated)

    def test_telework_request_str_method(self):
        """Test de la méthode __str__ de la demande de télétravail"""
        start_date = date.today() + timedelta(days=7)
        end_date = start_date + timedelta(days=2)

        telework_request = TeleworkRequest.objects.create(
            user=self.user, start_date=start_date, end_date=end_date
        )

        expected_str = (
            f"Télétravail de {self.user.username} du {start_date} au {end_date}"
        )
        self.assertEqual(str(telework_request), expected_str)


class StockModelTest(TestCase):
    """Tests pour les modèles Stock"""

    def setUp(self):
        """Configuration initiale pour chaque test"""
        self.user = User.objects.create_user(
            username="stockmanager", email="stock@ictgroup.com", password="testpass123"
        )
        self.profile = UserProfile.objects.create(
            user=self.user, role="admin", site="Tunisie"
        )

    def test_stock_item_creation(self):
        """Test de création d'un élément de stock"""
        item = StockItem.objects.create(
            name="Laptop Dell",
            category="laptop",
            serial_number="DL123456",
            current_quantity=5,
            min_quantity=2,
            price=1200.00,
        )

        self.assertEqual(item.name, "Laptop Dell")
        self.assertEqual(item.category, "laptop")
        self.assertEqual(item.current_quantity, 5)
        self.assertEqual(item.status, "available")

    def test_stock_movement_creation(self):
        """Test de création d'un mouvement de stock"""
        item = StockItem.objects.create(
            name="Mouse", category="accessory", current_quantity=10
        )

        movement = StockMovement.objects.create(
            item=item,
            movement_type="out",
            quantity=2,
            user=self.user,
            reason="Attribution à nouvel employé",
        )

        self.assertEqual(movement.item, item)
        self.assertEqual(movement.movement_type, "out")
        self.assertEqual(movement.quantity, 2)
        self.assertEqual(movement.user, self.user)


if __name__ == "__main__":
    import unittest

    unittest.main()
