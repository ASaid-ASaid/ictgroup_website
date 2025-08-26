"""
Command pour annuler/réinitialiser l'accrual mensuel automatique.
Utile pour corriger les doubles exécutions ou tests.
"""
from django.core.management.base import BaseCommand
from django.utils import timezone
from django.contrib.auth.models import User
from datetime import datetime, date
from decimal import Decimal
from django.core.cache import cache
from extranet.models import UserProfile, UserLeaveBalance


class Command(BaseCommand):
    help = 'Annule/réinitialise l\'accrual mensuel automatique'

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
            '--subtract-only',
            action='store_true',
            help='Seulement soustraire les jours ajoutés en double',
        )
        parser.add_argument(
            '--clear-cache',
            action='store_true',
            help='Effacer le cache pour permettre un nouvel accrual',
        )

    def handle(self, *args, **options):
        # Déterminer la période
        now = timezone.now()
        target_month = options.get('month') or now.month
        target_year = options.get('year') or now.year
        
        self.stdout.write(
            self.style.SUCCESS(
                f"🔧 Réinitialisation accrual pour {target_month:02d}/{target_year}"
            )
        )
        
        # Effacer le cache si demandé
        if options['clear_cache']:
            cache_key = f"monthly_accrual_{target_year}_{target_month:02d}"
            cache.delete(cache_key)
            self.stdout.write(
                self.style.SUCCESS("✅ Cache accrual effacé")
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
                
                # Déterminer les jours à soustraire selon le site
                if profile.site.lower() in ['fr', 'france']:
                    monthly_days = Decimal('2.5')
                elif profile.site.lower() in ['tn', 'tunisie']:
                    monthly_days = Decimal('1.8')
                else:
                    continue
                
                # Période fiscale
                if target_month >= 6:
                    period_start = date(target_year, 6, 1)
                else:
                    period_start = date(target_year - 1, 6, 1)
                
                try:
                    balance = UserLeaveBalance.objects.get(
                        user=user,
                        period_start=period_start
                    )
                    
                    if options['subtract_only']:
                        # Soustraire les jours ajoutés en double
                        if balance.days_acquired >= monthly_days:
                            balance.days_acquired -= monthly_days
                            balance.save()
                            updated += 1
                            self.stdout.write(
                                f"✅ {user.username}: -{monthly_days} jours "
                                f"(nouveau total: {balance.days_acquired})"
                            )
                        else:
                            self.stdout.write(
                                f"⚠️  {user.username}: solde insuffisant pour soustraire "
                                f"{monthly_days} (actuel: {balance.days_acquired})"
                            )
                    else:
                        # Réinitialiser complètement
                        old_acquired = balance.days_acquired
                        balance.days_acquired = Decimal('0')
                        balance.save()
                        updated += 1
                        self.stdout.write(
                            f"🔄 {user.username}: remis à zéro "
                            f"(ancien: {old_acquired}, nouveau: 0)"
                        )
                    
                except UserLeaveBalance.DoesNotExist:
                    self.stdout.write(
                        f"ℹ️  {user.username}: aucun solde trouvé pour cette période"
                    )
                
                processed += 1
                
            except Exception as e:
                errors += 1
                self.stdout.write(
                    self.style.ERROR(
                        f"❌ Erreur pour {user.username}: {str(e)}"
                    )
                )
        
        # Résumé final
        action = "Soustraction" if options['subtract_only'] else "Réinitialisation"
        self.stdout.write(
            self.style.SUCCESS(
                f"\n📊 Résumé {action}:\n"
                f"   • Utilisateurs traités: {processed}\n"
                f"   • Soldes modifiés: {updated}\n"
                f"   • Erreurs: {errors}\n"
            )
        )
