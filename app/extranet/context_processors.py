from extranet.models import LeaveRequest, TeleworkRequest, Document, DocumentDownload
from datetime import datetime, timedelta
from django.db.models import Q


def validation_context(request):
    """Context processor pour afficher les notifications de validation dans le menu."""
    if not request.user.is_authenticated or not hasattr(request.user, "profile"):
        return {
            "validation_count": 0,
            "leave_validation_count": 0,
            "telework_validation_count": 0,
        }

    user = request.user
    role = user.profile.role
    validation_count = 0
    leave_validation_count = 0
    telework_validation_count = 0

    # Pour les managers
    if role in ["manager", "admin"]:
        # Demandes de congé en attente de validation manager (exclure ses propres demandes)
        leave_pending = LeaveRequest.objects.filter(
            status="pending", 
            user__profile__manager=user, 
            manager_validated=False
        ).exclude(
            user=user  # Exclure ses propres demandes
        ).count()
        leave_validation_count += leave_pending
        validation_count += leave_pending

        # Demandes de télétravail en attente de validation manager (inclure ses propres demandes)
        telework_pending = TeleworkRequest.objects.filter(
            status="pending", 
            manager_validated=False
        ).filter(
            Q(user__profile__manager=user) | Q(user=user)  # Ses subordonnés OU lui-même
        ).count()
        telework_validation_count += telework_pending
        validation_count += telework_pending

    # Pour les RH
    if role in ["rh", "admin"]:
        # Demandes de congé validées par manager mais en attente RH
        leave_rh_pending = LeaveRequest.objects.filter(
            status="pending",
            user__profile__rh=user,
            manager_validated=True,
            rh_validated=False,
        ).count()
        leave_validation_count += leave_rh_pending
        validation_count += leave_rh_pending

    return {
        "validation_count": validation_count,
        "leave_validation_count": leave_validation_count,
        "telework_validation_count": telework_validation_count,
    }


def document_context(request):
    """Context processor pour afficher les nouveaux documents."""
    if not request.user.is_authenticated:
        return {"new_documents_count": 0}
    
    # Documents ajoutés dans les 7 derniers jours que l'utilisateur peut voir
    seven_days_ago = datetime.now() - timedelta(days=7)
    
    # Récupérer tous les documents récents actifs
    recent_documents = Document.objects.filter(
        is_active=True,
        uploaded_at__gte=seven_days_ago
    )
    
    # Récupérer les IDs des documents déjà téléchargés par l'utilisateur
    downloaded_doc_ids = DocumentDownload.objects.filter(
        user=request.user
    ).values_list('document_id', flat=True)
    
    # Filtrer selon les droits d'accès de l'utilisateur et exclure les téléchargés
    accessible_new_docs = []
    for doc in recent_documents:
        if doc.can_user_access(request.user) and doc.id not in downloaded_doc_ids:
            accessible_new_docs.append(doc)
    
    return {"new_documents_count": len(accessible_new_docs)}
