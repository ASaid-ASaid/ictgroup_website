"""
Vues de gestion du stock et des mouvements.
Accès autorisé pour tous les utilisateurs en France.
"""

import logging

from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.db.models import Q, Sum
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from ..models import StockItem, StockMovement

logger = logging.getLogger(__name__)


def can_manage_stock(user):
    """Vérifie si l'utilisateur peut gérer le stock - Accès pour tous les utilisateurs France."""
    # Accès pour tous les utilisateurs en France
    if hasattr(user, "profile"):
        return user.profile.site in ["france", "FR", "France"]
    # Si pas de profil, on autorise par défaut (compatibilité)
    return True


@login_required
@user_passes_test(can_manage_stock)
def stock(request):
    """Vue principale de gestion du stock - Accessible à tous les utilisateurs France."""

    # Récupération des articles de stock
    stock_items = StockItem.objects.all().order_by("designation")

    # Recherche
    search = request.GET.get("search", "")
    if search:
        stock_items = stock_items.filter(
            Q(designation__icontains=search)
            | Q(code__icontains=search)
            | Q(type__icontains=search)
        )

    # Statistiques
    total_items = stock_items.count()
    low_stock_items = stock_items.filter(quantity__lt=5)
    out_of_stock_items = stock_items.filter(quantity=0)

    context = {
        "stock_items": stock_items,
        "search": search,
        "total_items": total_items,
        "low_stock_count": low_stock_items.count(),
        "out_of_stock_count": out_of_stock_items.count(),
    }

    logger.info(
        "[stock] Utilisateur %s consulte le stock - %s articles",
        request.user.username,
        total_items,
    )

    return render(request, "extranet/stock.html", context)


@login_required
@user_passes_test(can_manage_stock)
def entry_exit(request):
    """Vue pour gérer les entrées et sorties de stock."""

    if request.method == "POST":
        # Création d'un nouvel article
        if "create_item" in request.POST:
            code = request.POST.get("code")
            designation = request.POST.get("designation")
            fournisseur = request.POST.get("fournisseur")
            type_item = request.POST.get("type")
            quantity = int(request.POST.get("quantity", 0))
            remarks = request.POST.get("remarks", "")

            if StockItem.objects.filter(code=code).exists():
                messages.error(
                    request, f"Un article avec le code '{code}' existe déjà."
                )
            else:
                StockItem.objects.create(
                    code=code,
                    designation=designation,
                    fournisseur=fournisseur,
                    type=type_item,
                    quantity=quantity,
                    remarks=remarks,
                )
                messages.success(request, f"Article '{designation}' créé avec succès.")
                logger.info(
                    f"[entry_exit] Nouvel article créé: {code} par {request.user.username}"
                )

        # Mouvement de stock
        elif "movement" in request.POST:
            item_id = request.POST.get("stock_item")
            movement_type = request.POST.get("movement_type")
            quantity = int(request.POST.get("quantity"))
            remarks = request.POST.get("remarks", "")

            stock_item = get_object_or_404(StockItem, id=item_id)

            # Vérification pour les sorties
            if movement_type == "exit" and quantity > stock_item.quantity:
                messages.error(
                    request,
                    f"Quantité insuffisante. Stock disponible: {stock_item.quantity}",
                )
            else:
                # Créer le mouvement
                StockMovement.objects.create(
                    stock_item=stock_item,
                    user=request.user,
                    movement_type=movement_type,
                    quantity=quantity,
                    remarks=remarks,
                )

                # Mettre à jour le stock
                if movement_type == "entry":
                    stock_item.quantity += quantity
                else:  # exit
                    stock_item.quantity -= quantity

                stock_item.save()

                messages.success(
                    request,
                    "Mouvement enregistré: %s de %s unité(s)"
                    % (movement_type, quantity),
                )
                logger.info(
                    "[entry_exit] Mouvement: %s %s %s par %s",
                    movement_type,
                    quantity,
                    stock_item.code,
                    request.user.username,
                )

        return redirect("extranet:entry_exit")

    # GET request
    stock_items = StockItem.objects.all().order_by("designation")

    context = {
        "stock_items": stock_items,
    }

    return render(request, "extranet/entry_exit.html", context)


@login_required
@user_passes_test(can_manage_stock)
def movements_view(request):
    """Vue pour afficher l'historique des mouvements de stock."""

    movements = StockMovement.objects.select_related("stock_item", "user").order_by(
        "-date"
    )

    # Filtres
    movement_type = request.GET.get("type", "")
    user_filter = request.GET.get("user", "")

    if movement_type:
        movements = movements.filter(movement_type=movement_type)

    if user_filter:
        movements = movements.filter(user__username__icontains=user_filter)

    # Pagination simple - derniers 100 mouvements
    movements = movements[:100]

    context = {
        "movements": movements,
        "movement_type": movement_type,
        "user_filter": user_filter,
    }

    return render(request, "extranet/movements.html", context)


def _handle_new_item_creation(request):
    """Traite la création d'un nouvel article de stock."""
    try:
        code = request.POST.get("code", "").strip()
        designation = request.POST.get("designation", "").strip()
        type_item = request.POST.get("type", "").strip()
        fournisseur = request.POST.get("fournisseur", "").strip()
        quantity = int(request.POST.get("quantity", 0))
        remarks = request.POST.get("remarks", "").strip()

        # Validation
        if not all([code, designation, type_item, fournisseur]):
            messages.error(
                request, "Tous les champs obligatoires doivent être remplis."
            )
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
            remarks=remarks,
        )

        # Création du mouvement initial si quantité > 0
        if quantity > 0:
            StockMovement.objects.create(
                stock_item=item,
                user=request.user,
                movement_type="entry",
                quantity=quantity,
                date=timezone.now().date(),
                remarks="Création initiale de l'article",
            )
        logger.info(
            "[stock] Nouvel article créé: %s par %s" % (code, request.user.username)
        )
        messages.success(request, "Article %s créé avec succès." % designation)
        return True

    except Exception as e:
        logger.error(f"[stock] Erreur création article: {e}")
        messages.error(request, "Erreur lors de la création de l'article.")
        return False


def _handle_stock_movement(request):
    """Traite l'enregistrement d'un mouvement de stock."""
    try:
        stock_item_id = request.POST.get("stock_item")
        movement_type = request.POST.get("movement_type")
        quantity = int(request.POST.get("quantity", 0))
        date_str = request.POST.get("date")
        remarks = request.POST.get("remarks", "").strip()

        # Validation
        if not all([stock_item_id, movement_type, quantity, date_str]):
            messages.error(
                request, "Tous les champs obligatoires doivent être remplis."
            )
            return False

        stock_item = get_object_or_404(StockItem, id=stock_item_id)
        movement_date = timezone.datetime.strptime(date_str, "%Y-%m-%d").date()

        # Validation stock disponible pour les sorties
        if movement_type == "exit" and quantity > stock_item.quantity:
            messages.error(
                request, f"Stock insuffisant. Disponible: {stock_item.quantity}"
            )
            return False

        # Création du mouvement
        StockMovement.objects.create(
            stock_item=stock_item,
            user=request.user,
            movement_type=movement_type,
            quantity=quantity,
            date=movement_date,
            remarks=remarks,
        )

        # Mise à jour du stock
        if movement_type == "entry":
            stock_item.quantity += quantity
        else:  # exit
            stock_item.quantity -= quantity

        stock_item.save()

        logger.info(
            "[stock] Mouvement enregistré: %s %s %s par %s",
            movement_type,
            quantity,
            stock_item.code,
            request.user.username,
        )
        messages.success(request, "Mouvement de stock enregistré avec succès.")
        return True

    except Exception as e:
        logger.error(f"[stock] Erreur mouvement: {e}")
        messages.error(request, "Erreur lors de l'enregistrement du mouvement.")
        return False


def _calculate_stock_stats(stock_items):
    """Calcule les statistiques du stock."""
    total_items = stock_items.count()
    total_quantity = stock_items.aggregate(total=Sum("quantity"))["total"] or 0

    # Articles en rupture (quantité <= 5)
    low_stock = stock_items.filter(quantity__lte=5).count()
    out_of_stock = stock_items.filter(quantity=0).count()

    return {
        "total_items": total_items,
        "total_quantity": total_quantity,
        "low_stock": low_stock,
        "out_of_stock": out_of_stock,
        "low_stock_percentage": (
            (low_stock / total_items * 100) if total_items > 0 else 0
        ),
    }


def _calculate_movement_stats(movements):
    """Calcule les statistiques des mouvements."""
    total_movements = movements.count()
    entries = movements.filter(movement_type="entry")
    exits = movements.filter(movement_type="exit")

    entries_count = entries.count()
    exits_count = exits.count()

    entries_quantity = entries.aggregate(total=Sum("quantity"))["total"] or 0
    exits_quantity = exits.aggregate(total=Sum("quantity"))["total"] or 0

    # Articles uniques concernés
    unique_items = movements.values("stock_item").distinct().count()

    return {
        "total_movements": total_movements,
        "entries_count": entries_count,
        "exits_count": exits_count,
        "entries_quantity": entries_quantity,
        "exits_quantity": exits_quantity,
        "unique_items": unique_items,
        "net_movement": entries_quantity - exits_quantity,
    }
