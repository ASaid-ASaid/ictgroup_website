"""
Vues de gestion du stock et des mouvements.
"""

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.utils import timezone
from django.db.models import Q, Sum, F
from django.http import JsonResponse
import logging

from ..models import StockItem, StockMovement

logger = logging.getLogger(__name__)


def can_manage_stock(user):
    """Vérifie si l'utilisateur peut gérer le stock."""
    return (hasattr(user, 'profile') and 
            user.profile.role in ['admin', 'manager'])


@login_required
@user_passes_test(can_manage_stock)
def stock(request):
    """Vue principale de gestion du stock."""
    
    # Récupération des articles de stock
    stock_items = StockItem.objects.all().order_by('designation')
    
    # Recherche
    search = request.GET.get('search', '')
    if search:
        stock_items = stock_items.filter(
            Q(designation__icontains=search) |
            Q(code__icontains=search) |
            Q(type__icontains=search)
        )
    
    # Statistiques
    stats = _calculate_stock_stats(stock_items)
    
    context = {
        'stock_items': stock_items,
        'search': search,
        'stats': stats,
    }
    
    return render(request, 'extranet/stock.html', context)


@login_required
@user_passes_test(can_manage_stock)
def entry_exit(request):
    """Vue pour enregistrer les entrées et sorties de stock."""
    
    if request.method == 'POST':
        if 'add_new_item' in request.POST:
            success = _handle_new_item_creation(request)
        else:
            success = _handle_stock_movement(request)
            
        if success:
            return redirect('extranet:entry_exit')
    
    # Récupération des articles pour le formulaire
    stock_items = StockItem.objects.all().order_by('designation')
    
    context = {
        'stock_items': stock_items,
    }
    
    return render(request, 'extranet/entry_exit.html', context)


@login_required
@user_passes_test(can_manage_stock)
def movements_view(request):
    """Vue de l'historique des mouvements de stock."""
    
    # Récupération des mouvements
    movements = StockMovement.objects.select_related(
        'stock_item', 'user'
    ).all().order_by('-date')
    
    # Filtres
    item_filter = request.GET.get('item')
    type_filter = request.GET.get('type')
    date_from = request.GET.get('date_from')
    date_to = request.GET.get('date_to')
    
    if item_filter:
        movements = movements.filter(stock_item__id=item_filter)
    if type_filter:
        movements = movements.filter(movement_type=type_filter)
    if date_from:
        movements = movements.filter(date__gte=date_from)
    if date_to:
        movements = movements.filter(date__lte=date_to)
    
    # Statistiques des mouvements
    movement_stats = _calculate_movement_stats(movements)
    
    context = {
        'movements': movements,
        'stock_items': StockItem.objects.all(),
        'movement_stats': movement_stats,
        'filters': {
            'item': item_filter,
            'type': type_filter,
            'date_from': date_from,
            'date_to': date_to,
        }
    }
    
    return render(request, 'extranet/movements.html', context)


def _handle_new_item_creation(request):
    """Traite la création d'un nouvel article de stock."""
    try:
        code = request.POST.get('code', '').strip()
        designation = request.POST.get('designation', '').strip()
        type_item = request.POST.get('type', '').strip()
        fournisseur = request.POST.get('fournisseur', '').strip()
        quantity = int(request.POST.get('quantity', 0))
        remarks = request.POST.get('remarks', '').strip()
        
        # Validation
        if not all([code, designation, type_item, fournisseur]):
            messages.error(request, "Tous les champs obligatoires doivent être remplis.")
            return False
        
        # Vérification unicité du code
        if StockItem.objects.filter(code=code).exists():
            messages.error(request, f"Un article avec le code {code} existe déjà.")
            return False
        
        # Création de l'article
        item = StockItem.objects.create(
            code=code,
            designation=designation,
            type=type_item,
            fournisseur=fournisseur,
            quantity=quantity,
            remarks=remarks
        )
        
        # Création du mouvement initial si quantité > 0
        if quantity > 0:
            StockMovement.objects.create(
                stock_item=item,
                user=request.user,
                movement_type='entry',
                quantity=quantity,
                date=timezone.now().date(),
                remarks=f"Création initiale de l'article"
            )
        
        logger.info(f"[stock] Nouvel article créé: {code} par {request.user.username}")
        messages.success(request, f"Article {designation} créé avec succès.")
        return True
        
    except Exception as e:
        logger.error(f"[stock] Erreur création article: {e}")
        messages.error(request, "Erreur lors de la création de l'article.")
        return False


def _handle_stock_movement(request):
    """Traite l'enregistrement d'un mouvement de stock."""
    try:
        stock_item_id = request.POST.get('stock_item')
        movement_type = request.POST.get('movement_type')
        quantity = int(request.POST.get('quantity', 0))
        date_str = request.POST.get('date')
        remarks = request.POST.get('remarks', '').strip()
        
        # Validation
        if not all([stock_item_id, movement_type, quantity, date_str]):
            messages.error(request, "Tous les champs obligatoires doivent être remplis.")
            return False
        
        stock_item = get_object_or_404(StockItem, id=stock_item_id)
        movement_date = timezone.datetime.strptime(date_str, '%Y-%m-%d').date()
        
        # Validation stock disponible pour les sorties
        if movement_type == 'exit' and quantity > stock_item.quantity:
            messages.error(request, f"Stock insuffisant. Disponible: {stock_item.quantity}")
            return False
        
        # Création du mouvement
        movement = StockMovement.objects.create(
            stock_item=stock_item,
            user=request.user,
            movement_type=movement_type,
            quantity=quantity,
            date=movement_date,
            remarks=remarks
        )
        
        # Mise à jour du stock
        if movement_type == 'entry':
            stock_item.quantity += quantity
        else:  # exit
            stock_item.quantity -= quantity
        
        stock_item.save()
        
        logger.info(f"[stock] Mouvement enregistré: {movement_type} {quantity} {stock_item.code} par {request.user.username}")
        messages.success(request, f"Mouvement de stock enregistré avec succès.")
        return True
        
    except Exception as e:
        logger.error(f"[stock] Erreur mouvement: {e}")
        messages.error(request, "Erreur lors de l'enregistrement du mouvement.")
        return False


def _calculate_stock_stats(stock_items):
    """Calcule les statistiques du stock."""
    total_items = stock_items.count()
    total_quantity = stock_items.aggregate(total=Sum('quantity'))['total'] or 0
    
    # Articles en rupture (quantité <= 5)
    low_stock = stock_items.filter(quantity__lte=5).count()
    out_of_stock = stock_items.filter(quantity=0).count()
    
    return {
        'total_items': total_items,
        'total_quantity': total_quantity,
        'low_stock': low_stock,
        'out_of_stock': out_of_stock,
        'low_stock_percentage': (low_stock / total_items * 100) if total_items > 0 else 0,
    }


def _calculate_movement_stats(movements):
    """Calcule les statistiques des mouvements."""
    total_movements = movements.count()
    entries = movements.filter(movement_type='entry')
    exits = movements.filter(movement_type='exit')
    
    entries_count = entries.count()
    exits_count = exits.count()
    
    entries_quantity = entries.aggregate(total=Sum('quantity'))['total'] or 0
    exits_quantity = exits.aggregate(total=Sum('quantity'))['total'] or 0
    
    # Articles uniques concernés
    unique_items = movements.values('stock_item').distinct().count()
    
    return {
        'total_movements': total_movements,
        'entries_count': entries_count,
        'exits_count': exits_count,
        'entries_quantity': entries_quantity,
        'exits_quantity': exits_quantity,
        'unique_items': unique_items,
        'net_movement': entries_quantity - exits_quantity,
    }
