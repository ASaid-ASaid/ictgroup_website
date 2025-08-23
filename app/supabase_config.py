"""
Configuration Supabase pour ICTGROUP
"""

import os
from supabase import create_client, Client
from dotenv import load_dotenv

# Charger les variables d'environnement
load_dotenv()

class SupabaseConfig:
    """Configuration centralisée pour Supabase"""
    
    def __init__(self):
        self.url = os.getenv('SUPABASE_URL')
        self.key = os.getenv('SUPABASE_ANON_KEY')
        self.service_role_key = os.getenv('SUPABASE_SERVICE_ROLE_KEY')
        
        if not self.url or not self.key:
            raise ValueError(
                "Les variables d'environnement SUPABASE_URL et SUPABASE_ANON_KEY sont requises"
            )
    
    def get_client(self) -> Client:
        """Retourne un client Supabase configuré"""
        return create_client(self.url, self.key)
    
    def get_admin_client(self) -> Client:
        """Retourne un client Supabase avec les droits d'administration"""
        if not self.service_role_key:
            raise ValueError("SUPABASE_SERVICE_ROLE_KEY requis pour le client admin")
        return create_client(self.url, self.service_role_key)

# Instance globale
supabase_config = SupabaseConfig()

def get_supabase() -> Client:
    """Fonction utilitaire pour obtenir le client Supabase"""
    return supabase_config.get_client()

def get_supabase_admin() -> Client:
    """Fonction utilitaire pour obtenir le client Supabase admin"""
    return supabase_config.get_admin_client()
