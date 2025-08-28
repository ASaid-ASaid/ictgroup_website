# =====================
# Vues pour la gestion des documents
# Upload, téléchargement et gestion des accès
# =====================

import os
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.http import HttpResponse, Http404, FileResponse
from django.core.paginator import Paginator
from django.db.models import Q
from django.conf import settings
from django.utils.encoding import smart_str
from django.views.decorators.http import require_POST

from ..models import Document, DocumentDownload, UserProfile
from ..forms import DocumentForm


def can_upload_documents(user):
    """Vérifie si l'utilisateur peut uploader des documents"""
    return (
        hasattr(user, "profile") 
        and user.profile.role in ["manager", "rh", "admin"]
    )


@login_required
def document_list(request):
    """Liste des documents accessibles à l'utilisateur"""
    user = request.user
    
    # Récupérer tous les documents actifs
    documents = Document.objects.filter(is_active=True)
    
    # Filtrer selon les droits d'accès
    accessible_docs = []
    for doc in documents:
        if doc.can_user_access(user):
            accessible_docs.append(doc)
    
    # Filtrage par catégorie
    category_filter = request.GET.get("category")
    if category_filter:
        accessible_docs = [doc for doc in accessible_docs if doc.category == category_filter]
    
    # Recherche
    search_query = request.GET.get("search")
    if search_query:
        accessible_docs = [
            doc for doc in accessible_docs 
            if (search_query.lower() in doc.title.lower() or
                (doc.description and search_query.lower() in doc.description.lower()))
        ]
    
    # Pagination
    paginator = Paginator(accessible_docs, 10)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)
    
    context = {
        "documents": page_obj,
        "categories": Document.CATEGORY_CHOICES,
        "category_filter": category_filter,
        "search_query": search_query,
        "can_upload": can_upload_documents(user),
    }
    
    return render(request, "extranet/document_list.html", context)


@login_required
@user_passes_test(can_upload_documents)
def document_upload(request):
    """Upload de nouveaux documents"""
    if request.method == "POST":
        form = DocumentForm(request.POST, request.FILES)
        if form.is_valid():
            document = form.save(commit=False)
            document.uploaded_by = request.user
            document.save()
            
            # Sauvegarder les relations Many-to-Many
            form.save_m2m()
            
            messages.success(request, f"Document '{document.title}' uploadé avec succès.")
            return redirect("extranet:document_list")
    else:
        form = DocumentForm()
    
    context = {
        "form": form,
        "title": "Uploader un document",
    }
    
    return render(request, "extranet/document_form.html", context)


@login_required
def document_download(request, document_id):
    """Téléchargement d'un document ou redirection vers un lien"""
    document = get_object_or_404(Document, id=document_id, is_active=True)
    user = request.user
    
    # Vérifier les droits d'accès
    if not document.can_user_access(user):
        messages.error(request, "Vous n'avez pas accès à ce document.")
        return redirect("extranet:document_list")
    
    if document.document_type == 'link':
        # Pour les liens, enregistrer le clic et rediriger
        DocumentDownload.objects.create(
            document=document,
            user=user,
            ip_address=request.META.get('REMOTE_ADDR')
        )
        
        # Incrémenter le compteur
        document.increment_download_count()
        
        # Rediriger vers le lien externe
        return redirect(document.link_url)
    
    else:
        # Pour les fichiers, procédure de téléchargement normale
        # Vérifier que le fichier existe
        if not document.file or not os.path.isfile(document.file.path):
            messages.error(request, "Le fichier n'est pas disponible.")
            return redirect("extranet:document_list")
        
        # Enregistrer le téléchargement
        DocumentDownload.objects.create(
            document=document,
            user=user,
            ip_address=request.META.get('REMOTE_ADDR')
        )
        
        # Incrémenter le compteur
        document.increment_download_count()
        
        # Télécharger le fichier
        try:
            response = FileResponse(
                open(document.file.path, 'rb'),
                as_attachment=True,
                filename=smart_str(os.path.basename(document.file.name))
            )
            return response
        except IOError:
            messages.error(request, "Erreur lors du téléchargement du fichier.")
            return redirect("extranet:document_list")


@login_required
@user_passes_test(can_upload_documents)
def document_edit(request, document_id):
    """Modification d'un document"""
    document = get_object_or_404(Document, id=document_id)
    
    # Seul l'uploader ou un admin peut modifier
    if document.uploaded_by != request.user and not request.user.profile.role == "admin":
        messages.error(request, "Vous ne pouvez pas modifier ce document.")
        return redirect("extranet:document_list")
    
    if request.method == "POST":
        form = DocumentForm(request.POST, request.FILES, instance=document)
        if form.is_valid():
            form.save()
            messages.success(request, f"Document '{document.title}' modifié avec succès.")
            return redirect("extranet:document_list")
    else:
        form = DocumentForm(instance=document)
    
    context = {
        "form": form,
        "document": document,
        "title": "Modifier le document",
    }
    
    return render(request, "extranet/document_form.html", context)


@login_required
@user_passes_test(can_upload_documents)
@require_POST
def document_delete(request, document_id):
    """Suppression d'un document"""
    document = get_object_or_404(Document, id=document_id)
    
    # Seul l'uploader ou un admin peut supprimer
    if document.uploaded_by != request.user and not request.user.profile.role == "admin":
        messages.error(request, "Vous ne pouvez pas supprimer ce document.")
        return redirect("extranet:document_list")
    
    title = document.title
    
    # Supprimer le fichier physique
    if document.file and os.path.isfile(document.file.path):
        try:
            os.remove(document.file.path)
        except OSError:
            pass  # Ignorer les erreurs de suppression de fichier
    
    document.delete()
    messages.success(request, f"Document '{title}' supprimé avec succès.")
    
    return redirect("extranet:document_list")


@login_required
@user_passes_test(lambda u: u.profile.role == "admin")
def document_admin(request):
    """Interface d'administration des documents (admin seulement)"""
    documents = Document.objects.all().order_by("-uploaded_at")
    
    # Filtrage
    category_filter = request.GET.get("category")
    if category_filter:
        documents = documents.filter(category=category_filter)
    
    status_filter = request.GET.get("status")
    if status_filter == "active":
        documents = documents.filter(is_active=True)
    elif status_filter == "inactive":
        documents = documents.filter(is_active=False)
    
    search_query = request.GET.get("search")
    if search_query:
        documents = documents.filter(
            Q(title__icontains=search_query) |
            Q(description__icontains=search_query) |
            Q(uploaded_by__username__icontains=search_query)
        )
    
    # Pagination
    paginator = Paginator(documents, 20)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)
    
    # Statistiques
    stats = {
        "total_documents": Document.objects.count(),
        "active_documents": Document.objects.filter(is_active=True).count(),
        "total_downloads": DocumentDownload.objects.count(),
    }
    
    context = {
        "documents": page_obj,
        "categories": Document.CATEGORY_CHOICES,
        "category_filter": category_filter,
        "status_filter": status_filter,
        "search_query": search_query,
        "stats": stats,
    }
    
    return render(request, "extranet/document_admin.html", context)


@login_required
@user_passes_test(lambda u: u.profile.role == "admin")
@require_POST
def document_toggle_status(request, document_id):
    """Active/désactive un document (admin seulement)"""
    document = get_object_or_404(Document, id=document_id)
    document.is_active = not document.is_active
    document.save()
    
    status = "activé" if document.is_active else "désactivé"
    messages.success(request, f"Document '{document.title}' {status}.")
    
    return redirect("extranet:document_admin")


@login_required
def documents_count_api(request):
    """API pour récupérer le nombre de documents"""
    from django.http import JsonResponse
    
    count = Document.objects.filter(is_active=True).count()
    return JsonResponse({"count": count})


@login_required
def document_edit(request, document_id):
    """Édition de document."""
    messages.info(request, "Fonctionnalité en cours d'implémentation")
    return redirect('extranet:calendar_view')


@login_required
def document_toggle_status(request, document_id):
    """Basculer le statut d'un document."""
    messages.info(request, "Fonctionnalité en cours d'implémentation")
    return redirect('extranet:calendar_view')


@login_required
def document_admin(request):
    """Administration des documents."""
    messages.info(request, "Fonctionnalité en cours d'implémentation")
    return redirect('extranet:calendar_view')
