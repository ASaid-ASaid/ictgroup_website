#!/usr/bin/env python3
"""
Script pour exporter toutes les tables Django en CSV
"""
import os
import csv
import django
from django.conf import settings
from django.db import connection
from django.apps import apps

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ictgroup.settings')
django.setup()

def export_table_to_csv(table_name, output_dir='csv_exports'):
    """Exporte une table vers un fichier CSV"""
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    cursor = connection.cursor()
    
    # Récupérer les noms des colonnes
    cursor.execute(f"SELECT * FROM {table_name} LIMIT 0")
    columns = [desc[0] for desc in cursor.description] if cursor.description else []
    
    # Récupérer toutes les données
    cursor.execute(f"SELECT * FROM {table_name}")
    rows = cursor.fetchall()
    
    # Écrire dans le fichier CSV
    csv_file = os.path.join(output_dir, f"{table_name}.csv")
    with open(csv_file, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        
        # Écrire les en-têtes
        if columns:
            writer.writerow(columns)
        
        # Écrire les données
        for row in rows:
            # Convertir les valeurs None en chaînes vides et gérer les types spéciaux
            clean_row = []
            for value in row:
                if value is None:
                    clean_row.append('')
                elif isinstance(value, (list, dict)):
                    clean_row.append(str(value))
                else:
                    clean_row.append(str(value))
            writer.writerow(clean_row)
    
    print(f"✅ Exporté: {table_name} -> {csv_file} ({len(rows)} lignes)")
    return len(rows)

def main():
    """Fonction principale"""
    print("🚀 Début de l'export des tables en CSV...")
    
    # Obtenir toutes les tables
    cursor = connection.cursor()
    cursor.execute("""
        SELECT table_name 
        FROM information_schema.tables 
        WHERE table_schema = 'public' 
        AND table_type = 'BASE TABLE'
        AND table_name NOT LIKE '%_pkey'
        ORDER BY table_name
    """)
    
    tables = [table[0] for table in cursor.fetchall()]
    
    print(f"📋 Tables trouvées: {len(tables)}")
    for table in tables:
        print(f"  - {table}")
    
    print("\n📤 Export en cours...")
    
    total_rows = 0
    exported_tables = 0
    
    for table_name in tables:
        try:
            rows_count = export_table_to_csv(table_name)
            total_rows += rows_count
            exported_tables += 1
        except Exception as e:
            print(f"❌ Erreur lors de l'export de {table_name}: {e}")
    
    print(f"\n📊 Résumé de l'export:")
    print(f"   - Tables exportées: {exported_tables}/{len(tables)}")
    print(f"   - Total des lignes: {total_rows}")
    print(f"   - Répertoire: csv_exports/")
    
    # Lister les fichiers créés
    if os.path.exists('csv_exports'):
        files = os.listdir('csv_exports')
        print(f"\n📁 Fichiers CSV créés:")
        for file in sorted(files):
            file_path = os.path.join('csv_exports', file)
            file_size = os.path.getsize(file_path)
            print(f"   - {file} ({file_size} bytes)")

if __name__ == "__main__":
    main()
