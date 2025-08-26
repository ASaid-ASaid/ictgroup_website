"""
Service d'intégration Supabase pour l'extranet ICTGROUP
Gère les opérations CRUD avec Supabase pour compléter la base de données Django
"""

import logging
from typing import Any, Dict, List, Optional

try:
    from supabase_config import get_supabase, get_supabase_admin

    SUPABASE_AVAILABLE = True
except ImportError:
    SUPABASE_AVAILABLE = False
    logging.warning(
        "Supabase n'est pas configuré. Les fonctionnalités Supabase sont désactivées."
    )

logger = logging.getLogger(__name__)


class SupabaseService:
    """Service pour l'intégration Supabase avec l'extranet"""

    def __init__(self):
        self.client = None
        self.admin_client = None

        if SUPABASE_AVAILABLE:
            try:
                self.client = get_supabase()
                self.admin_client = get_supabase_admin()
            except Exception as e:
                logger.error(f"Erreur d'initialisation Supabase: {e}")
                # do not reassign the module-level flag from instance scope
                # just mark the instance as unavailable
                self.client = None
                self.admin_client = None

    def is_available(self) -> bool:
        """Vérifie si Supabase est disponible"""
        return SUPABASE_AVAILABLE and self.client is not None

    # Gestion des logs d'activité
    def log_user_activity(
        self, user_id: int, action: str, details: Dict[str, Any] = None
    ) -> bool:
        """Enregistre l'activité utilisateur dans Supabase"""
        if not self.is_available():
            return False

        try:
            data = {
                "user_id": user_id,
                "action": action,
                "details": details or {},
                "timestamp": "now()",
            }

            result = self.client.table("user_activity_logs").insert(data).execute()
            # use result truthiness to avoid unused-variable lint
            return bool(result)
        except Exception as e:
            logger.error(f"Erreur lors de l'enregistrement de l'activité: {e}")
            return False

    def get_user_activity(self, user_id: int, limit: int = 50) -> List[Dict]:
        """Récupère l'historique d'activité d'un utilisateur"""
        if not self.is_available():
            return []

        try:
            result = (
                self.client.table("user_activity_logs")
                .select("*")
                .eq("user_id", user_id)
                .order("timestamp", desc=True)
                .limit(limit)
                .execute()
            )

            return getattr(result, "data", [])
        except Exception as e:
            logger.error(f"Erreur lors de la récupération de l'activité: {e}")
            return []

    # Gestion des documents/fichiers
    def upload_document(
        self, bucket: str, file_path: str, file_data: bytes
    ) -> Optional[str]:
        """Upload un document vers Supabase Storage"""
        if not self.is_available():
            return None

        try:
            result = self.client.storage.from_(bucket).upload(file_path, file_data)
            if result:
                return f"/{bucket}/{file_path}"
            return None
        except Exception as e:
            logger.error(f"Erreur lors de l'upload: {e}")
            return None

    def delete_document(self, bucket: str, file_path: str) -> bool:
        """Supprime un document de Supabase Storage"""
        if not self.is_available():
            return False

        try:
            result = self.client.storage.from_(bucket).remove([file_path])
            return bool(result)
        except Exception as e:
            logger.error(f"Erreur lors de la suppression: {e}")
            return False

    def get_document_url(self, bucket: str, file_path: str) -> Optional[str]:
        """Génère une URL signée pour un document"""
        if not self.is_available():
            return None

        try:
            result = self.client.storage.from_(bucket).create_signed_url(
                file_path, 3600
            )  # 1 heure
            return result.get("signedURL") if isinstance(result, dict) else None
        except Exception as e:
            logger.error(f"Erreur lors de la génération d'URL: {e}")
            return None

    # Gestion des notifications
    def create_notification(
        self, user_id: int, title: str, message: str, notification_type: str = "info"
    ) -> bool:
        """Crée une notification pour un utilisateur"""
        if not self.is_available():
            return False

        try:
            data = {
                "user_id": user_id,
                "title": title,
                "message": message,
                "type": notification_type,
                "read": False,
                "created_at": "now()",
            }

            result = self.client.table("notifications").insert(data).execute()
            return bool(result)
        except Exception as e:
            logger.error(f"Erreur lors de la création de notification: {e}")
            return False

    def get_user_notifications(
        self, user_id: int, unread_only: bool = False
    ) -> List[Dict]:
        """Récupère les notifications d'un utilisateur"""
        if not self.is_available():
            return []

        try:
            query = (
                self.client.table("notifications").select("*").eq("user_id", user_id)
            )

            if unread_only:
                query = query.eq("read", False)

            result = query.order("created_at", desc=True).execute()
            return getattr(result, "data", [])
        except Exception as e:
            logger.error(f"Erreur lors de la récupération des notifications: {e}")
            return []

    def mark_notification_read(self, notification_id: int) -> bool:
        """Marque une notification comme lue"""
        if not self.is_available():
            return False

        try:
            result = (
                self.client.table("notifications")
                .update({"read": True})
                .eq("id", notification_id)
                .execute()
            )
            return bool(result)
        except Exception as e:
            logger.error(f"Erreur lors de la mise à jour de notification: {e}")
            return False

    # Statistiques et analytics
    def get_dashboard_stats(self, user_id: int = None) -> Dict[str, Any]:
        """Récupère les statistiques pour le dashboard"""
        if not self.is_available():
            return {}

        try:
            stats = {}

            # Nombre total d'activités
            if user_id:
                activity_count = (
                    self.client.table("user_activity_logs")
                    .select("*", count="exact")
                    .eq("user_id", user_id)
                    .execute()
                )
                stats["total_activities"] = getattr(activity_count, "count", 0)

            # Autres statistiques peuvent être ajoutées ici

            return stats
        except Exception as e:
            logger.error(f"Erreur lors de la récupération des statistiques: {e}")
            return {}


# Instance globale du service
supabase_service = SupabaseService()
