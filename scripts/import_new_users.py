#!/usr/bin/env python3
"""
Script sécurisé pour importer de nouveaux utilisateurs et leurs données de congés
Sans écraser les données existantes
"""
import csv
import os
import sys
from datetime import date, datetime
from decimal import Decimal

import django
from django.contrib.auth import get_user_model
from django.db import transaction

# Configuration Django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "ictgroup.settings")
django.setup()

from extranet.models import LeaveBalance, MonthlyUserStats


User = get_user_model()


def import_new_users_from_csv(csv_file_path, dry_run=True):
    """
    Importe de nouveaux utilisateurs depuis un CSV sans écraser les données existantes
    
    Args:
        csv_file_path (str): Chemin vers le fichier CSV
        dry_run (bool): Si True, simule l'import sans modifications réelles
    """
    if not os.path.exists(csv_file_path):
        print(f"❌ Fichier CSV introuvable: {csv_file_path}")
        return False
    
    print(f"📂 Lecture du fichier: {csv_file_path}")
    print(f"🔍 Mode: {'SIMULATION' if dry_run else 'IMPORT RÉEL'}")
    print("-" * 60)
    
    new_users = []
    existing_users = []
    invalid_rows = []
    
    try:
        with open(csv_file_path, 'r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            
            # Vérification des colonnes requises
            required_columns = [
                'username', 'email', 'first_name', 'last_name',
                'annual_leave_days', 'used_leave_days', 'year', 'month'
            ]
            
            missing_columns = [col for col in required_columns if col not in reader.fieldnames]
            if missing_columns:
                print(f"❌ Colonnes manquantes: {missing_columns}")
                print(f"📋 Colonnes disponibles: {reader.fieldnames}")
                return False
            
            for row_num, row in enumerate(reader, start=2):
                try:
                    username = row['username'].strip()
                    email = row['email'].strip()
                    
                    if not username or not email:
                        invalid_rows.append(f"Ligne {row_num}: username ou email vide")
                        continue
                    
                    # Vérifier si l'utilisateur existe déjà
                    if User.objects.filter(username=username).exists():
                        existing_users.append(username)
                        continue
                    
                    # Données utilisateur
                    user_data = {
                        'username': username,
                        'email': email,
                        'first_name': row['first_name'].strip(),
                        'last_name': row['last_name'].strip(),
                        'is_active': True,
                        'annual_leave_days': Decimal(row['annual_leave_days']),
                        'used_leave_days': Decimal(row['used_leave_days']),
                        'year': int(row['year']),
                        'month': int(row['month'])
                    }
                    
                    new_users.append(user_data)
                    
                except ValueError as e:
                    invalid_rows.append(f"Ligne {row_num}: Erreur de format - {e}")
                except Exception as e:
                    invalid_rows.append(f"Ligne {row_num}: Erreur - {e}")
    
    except Exception as e:
        print(f"❌ Erreur lors de la lecture du CSV: {e}")
        return False
    
    # Rapport de pré-import
    print(f"📊 RAPPORT DE PRÉ-IMPORT:")
    print(f"   ✅ Nouveaux utilisateurs à créer: {len(new_users)}")
    print(f"   ⚠️  Utilisateurs existants (ignorés): {len(existing_users)}")
    print(f"   ❌ Lignes invalides: {len(invalid_rows)}")
    print()
    
    if existing_users:
        print("👥 UTILISATEURS EXISTANTS (seront ignorés):")
        for username in existing_users[:10]:  # Limite à 10 pour l'affichage
            print(f"   - {username}")
        if len(existing_users) > 10:
            print(f"   ... et {len(existing_users) - 10} autres")
        print()
    
    if invalid_rows:
        print("⚠️  LIGNES INVALIDES:")
        for error in invalid_rows[:5]:  # Limite à 5 pour l'affichage
            print(f"   - {error}")
        if len(invalid_rows) > 5:
            print(f"   ... et {len(invalid_rows) - 5} autres erreurs")
        print()
    
    if new_users:
        print("🆕 NOUVEAUX UTILISATEURS À CRÉER:")
        for user_data in new_users[:5]:  # Limite à 5 pour l'affichage
            print(f"   - {user_data['username']} ({user_data['first_name']} {user_data['last_name']})")
        if len(new_users) > 5:
            print(f"   ... et {len(new_users) - 5} autres")
        print()
    
    if not new_users:
        print("ℹ️  Aucun nouvel utilisateur à importer.")
        return True
    
    if dry_run:
        print("🔍 SIMULATION TERMINÉE - Utilisez --real pour l'import réel")
        return True
    
    # Import réel
    print("🚀 DÉBUT DE L'IMPORT RÉEL...")
    created_users = 0
    created_balances = 0
    created_stats = 0
    
    try:
        with transaction.atomic():
            for user_data in new_users:
                try:
                    # Créer l'utilisateur
                    user = User.objects.create_user(
                        username=user_data['username'],
                        email=user_data['email'],
                        first_name=user_data['first_name'],
                        last_name=user_data['last_name'],
                        password='TempPass123!'  # Mot de passe temporaire
                    )
                    created_users += 1
                    print(f"   ✅ Utilisateur créé: {user.username}")
                    
                    # Créer le solde de congés
                    leave_balance, created = LeaveBalance.objects.get_or_create(
                        user=user,
                        year=user_data['year'],
                        defaults={
                            'annual_leave_days': user_data['annual_leave_days'],
                            'used_leave_days': user_data['used_leave_days'],
                            'remaining_leave_days': user_data['annual_leave_days'] - user_data['used_leave_days']
                        }
                    )
                    if created:
                        created_balances += 1
                        print(f"      📊 Solde créé: {leave_balance.remaining_leave_days} jours restants")
                    
                    # Créer les statistiques mensuelles
                    monthly_stats, created = MonthlyUserStats.objects.get_or_create(
                        user=user,
                        year=user_data['year'],
                        month=user_data['month'],
                        defaults={
                            'total_leave_days': user_data['used_leave_days'],
                            'overtime_hours': Decimal('0.00'),
                            'telework_days': 0
                        }
                    )
                    if created:
                        created_stats += 1
                        print(f"      📈 Stats créées pour {user_data['month']}/{user_data['year']}")
                
                except Exception as e:
                    print(f"   ❌ Erreur pour {user_data['username']}: {e}")
                    # Continue avec les autres utilisateurs
    
    except Exception as e:
        print(f"❌ Erreur lors de l'import: {e}")
        return False
    
    print()
    print("🎉 IMPORT TERMINÉ!")
    print(f"   👥 Utilisateurs créés: {created_users}")
    print(f"   📊 Soldes de congés créés: {created_balances}")
    print(f"   📈 Statistiques créées: {created_stats}")
    
    return True


def validate_csv_format(csv_file_path):
    """Valide le format du CSV avant import"""
    print("🔍 VALIDATION DU FORMAT CSV...")
    
    if not os.path.exists(csv_file_path):
        print(f"❌ Fichier introuvable: {csv_file_path}")
        return False
    
    try:
        with open(csv_file_path, 'r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            
            required_columns = [
                'username', 'email', 'first_name', 'last_name',
                'annual_leave_days', 'used_leave_days', 'year', 'month'
            ]
            
            missing_columns = [col for col in required_columns if col not in reader.fieldnames]
            if missing_columns:
                print(f"❌ Colonnes manquantes: {missing_columns}")
                return False
            
            # Vérifier quelques lignes
            sample_rows = []
            for i, row in enumerate(reader):
                if i >= 3:  # Limite à 3 lignes d'exemple
                    break
                sample_rows.append(row)
            
            print("✅ Format CSV valide!")
            print(f"📋 Colonnes détectées: {reader.fieldnames}")
            print(f"📄 Lignes d'exemple: {len(sample_rows)}")
            
            return True
    
    except Exception as e:
        print(f"❌ Erreur de validation: {e}")
        return False


def create_csv_template():
    """Crée un template CSV pour les nouveaux utilisateurs"""
    template_path = "migration_data/new_users_template.csv"
    
    # Créer le répertoire si nécessaire
    os.makedirs("migration_data", exist_ok=True)
    
    headers = [
        'username', 'email', 'first_name', 'last_name',
        'annual_leave_days', 'used_leave_days', 'year', 'month'
    ]
    
    sample_data = [
        ['jdupont', 'j.dupont@ictgroup.fr', 'Jean', 'Dupont', '25', '5', '2025', '8'],
        ['mmartin', 'm.martin@ictgroup.fr', 'Marie', 'Martin', '25', '10', '2025', '8'],
    ]
    
    try:
        with open(template_path, 'w', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            writer.writerow(headers)
            writer.writerows(sample_data)
        
        print(f"✅ Template créé: {template_path}")
        print("📝 Modifiez ce fichier avec vos données avant l'import")
        return template_path
    
    except Exception as e:
        print(f"❌ Erreur lors de la création du template: {e}")
        return None


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Import sécurisé de nouveaux utilisateurs")
    parser.add_argument('--file', required=False, help='Chemin vers le fichier CSV')
    parser.add_argument('--real', action='store_true', help='Import réel (sinon simulation)')
    parser.add_argument('--validate', action='store_true', help='Valider le format CSV uniquement')
    parser.add_argument('--template', action='store_true', help='Créer un template CSV')
    
    args = parser.parse_args()
    
    if args.template:
        create_csv_template()
    elif args.validate:
        if not args.file:
            print("❌ Spécifiez le fichier avec --file")
            sys.exit(1)
        validate_csv_format(args.file)
    elif args.file:
        success = import_new_users_from_csv(args.file, dry_run=not args.real)
        if not success:
            sys.exit(1)
    else:
        print("Usage:")
        print("  python import_new_users.py --template")
        print("  python import_new_users.py --file fichier.csv --validate")
        print("  python import_new_users.py --file fichier.csv")
        print("  python import_new_users.py --file fichier.csv --real")
