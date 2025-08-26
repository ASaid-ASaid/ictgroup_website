"""
Command pour ajouter automatiquement les jours de congés mensuels.
À exécuter le 1er de chaque mois via cron.
"""
from django.core.management.base import BaseCommand
from django.utils import timezone
from django.contrib.auth.models import User
from datetime import datetime, date
from decimal import Decimal
from extranet.models import UserProfile, UserLeaveBalance


class Command(BaseCommand):
    help = 'Ajoute automatiquement les jours de congés mensuels (2.5 France, 1.8 Tunisie)'

    def add_arguments(self, parser):
        parser.add_argument(
            '--month',
            type=int,
            help='Mois spécifique (1-12). Par défaut: mois courant',
        )
        parser.add_argument(
            '--year',
            type=int,
            help='Année spécifique. Par défaut: année courante',
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Simulation sans modifications en base',
        )

    def handle(self, *args, **options):
        # Déterminer la période
        now = timezone.now()
        target_month = options.get('month') or now.month
        target_year = options.get('year') or now.year
        
        self.stdout.write(
            self.style.SUCCESS(
                f"🚀 Traitement des accruals de congés pour {target_month:02d}/{target_year}"
            )
        )
        
        # Compteurs
        processed = 0
        updated = 0
        errors = 0
        
        # Récupérer tous les utilisateurs actifs avec profil
        users = User.objects.filter(
            is_active=True,
            profile__isnull=False
        ).select_related('profile')
        
        for user in users:
            try:
                profile = user.profile
                
                # Déterminer les jours à ajouter selon le site
                site_lower = profile.site.lower() if profile.site else ''
                if site_lower in ['fr', 'france']:
                    monthly_days = Decimal('2.5')
                elif site_lower in ['tn', 'tunisie']:
                    monthly_days = Decimal('1.8')
                else:
                    self.stdout.write(
                        self.style.WARNING(
                            f"⚠️  Site inconnu pour {user.username}: {profile.site}"
                        )
                    )
                    continue
                
                # Récupérer ou créer le solde de congés pour la période courante
                period_start = date(target_year, 6, 1)  # Période fiscale du 1er juin au 31 mai
                period_end = date(target_year + 1, 5, 31)
                
                balance, created = UserLeaveBalance.objects.get_or_create(
                    user=user,
                    period_start=period_start,
                    defaults={
                        'days_acquired': Decimal('0'),
                        'days_taken': Decimal('0'),
                        'days_carry_over': Decimal('0'),
                        'period_end': period_end,
                    }
                )
                
                if not options['dry_run']:
                    # Ajouter les jours mensuels
                    balance.days_acquired += monthly_days
                    balance.last_updated = timezone.now()
                    balance.save()
                    
                    updated += 1
                    self.stdout.write(
                        f"✅ {user.username} ({profile.site}): +{monthly_days} jours "
                        f"(total acquis: {balance.days_acquired})"
                    )
                else:
                    # Mode simulation
                    new_acquired = balance.days_acquired + monthly_days
                    new_remaining = new_acquired + balance.days_carry_over - balance.days_taken
                    self.stdout.write(
                        f"🔍 [SIMULATION] {user.username} ({profile.site}): "
                        f"+{monthly_days} jours (nouveau total acquis: {new_acquired})"
                    )
                    updated += 1
                
                processed += 1
                
            except Exception as e:
                errors += 1
                self.stdout.write(
                    self.style.ERROR(
                        f"❌ Erreur pour {user.username}: {str(e)}"
                    )
                )
        
        # Résumé final
        mode_text = "SIMULATION" if options['dry_run'] else "PRODUCTION"
        self.stdout.write(
            self.style.SUCCESS(
                f"\n📊 Résumé {mode_text}:\n"
                f"   • Utilisateurs traités: {processed}\n"
                f"   • Soldes mis à jour: {updated}\n"
                f"   • Erreurs: {errors}\n"
            )
        )
        
        if options['dry_run']:
            self.stdout.write(
                self.style.WARNING(
                    "⚠️  Mode simulation activé - Aucune modification en base.\n"
                    "   Relancez sans --dry-run pour appliquer les changements."
                )
            )
        
        # Configuration cron suggérée
        self.stdout.write(
            self.style.SUCCESS(
                "\n📅 Pour automatiser cette commande, ajoutez à votre crontab:\n"
                "   # Accrual mensuel le 1er de chaque mois à 6h\n"
                "   0 6 1 * * cd /path/to/project && python manage.py monthly_leave_accrual\n"
            )
        )
