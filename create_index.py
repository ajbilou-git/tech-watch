#!/usr/bin/env python3
"""
Cree une page d'index HTML listant tous les rapports de veille technologique
"""

from pathlib import Path
from datetime import datetime

def create_index():
    """Genere une page d'index pour tous les rapports"""
    reports_dir = Path("reports")
    
    if not reports_dir.exists():
        print("Aucun dossier reports trouve")
        return
    
    # Trouver tous les rapports HTML
    reports = sorted(reports_dir.glob("tech_watch_*.html"), reverse=True)
    
    if not reports:
        print("Aucun rapport trouve")
        return
    
    # Template HTML pour l'index
    html = """<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Veille Technologique - Index</title>
    <style>
        * { box-sizing: border-box; }
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            line-height: 1.6;
            color: #333;
            max-width: 1000px;
            margin: 0 auto;
            padding: 20px;
            background: #f5f5f5;
        }
        .header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 40px;
            border-radius: 10px;
            margin-bottom: 30px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
            text-align: center;
        }
        .header h1 { margin: 0 0 10px 0; font-size: 2.5em; }
        .header p { margin: 0; opacity: 0.9; }
        .reports-list {
            background: white;
            padding: 30px;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        .reports-list h2 {
            color: #667eea;
            margin-top: 0;
            border-bottom: 2px solid #667eea;
            padding-bottom: 10px;
        }
        .report-item {
            padding: 20px;
            margin: 15px 0;
            background: #f8f9fa;
            border-left: 4px solid #667eea;
            border-radius: 5px;
            transition: all 0.3s;
        }
        .report-item:hover {
            transform: translateX(5px);
            box-shadow: 0 4px 8px rgba(0,0,0,0.1);
        }
        .report-link {
            display: flex;
            justify-content: space-between;
            align-items: center;
            text-decoration: none;
            color: #333;
        }
        .report-title {
            font-size: 1.2em;
            font-weight: bold;
            color: #667eea;
        }
        .report-date {
            color: #666;
            font-size: 0.9em;
        }
        .report-icon {
            font-size: 1.5em;
        }
        .stats {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 15px;
            margin-bottom: 30px;
        }
        .stat {
            background: white;
            padding: 20px;
            border-radius: 8px;
            text-align: center;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        .stat-value {
            font-size: 2.5em;
            font-weight: bold;
            color: #667eea;
        }
        .stat-label {
            color: #666;
            margin-top: 5px;
        }
        .footer {
            text-align: center;
            padding: 20px;
            color: #666;
            font-size: 0.9em;
        }
    </style>
</head>
<body>
    <div class="header">
        <h1>📚 Veille Technologique</h1>
        <p>Archive des rapports - Infrastructure mastermaint</p>
    </div>

    <div class="stats">
        <div class="stat">
            <div class="stat-value">""" + str(len(reports)) + """</div>
            <div class="stat-label">Rapports disponibles</div>
        </div>
        <div class="stat">
            <div class="stat-value">17</div>
            <div class="stat-label">Flux RSS surveilles</div>
        </div>
        <div class="stat">
            <div class="stat-value">8</div>
            <div class="stat-label">Categories</div>
        </div>
    </div>

    <div class="reports-list">
        <h2>📋 Historique des rapports</h2>
"""
    
    # Ajouter chaque rapport
    for report in reports:
        # Extraire la date du nom du fichier
        date_str = report.stem.replace("tech_watch_", "")
        try:
            date_obj = datetime.strptime(date_str, "%Y%m%d")
            formatted_date = date_obj.strftime("%d/%m/%Y")
        except:
            formatted_date = date_str
        
        html += f"""
        <div class="report-item">
            <a href="{report.name}" class="report-link">
                <div>
                    <div class="report-title">Rapport du {formatted_date}</div>
                    <div class="report-date">Fichier: {report.name}</div>
                </div>
                <div class="report-icon">📊</div>
            </a>
        </div>
"""
    
    html += """
    </div>

    <div class="footer">
        <p>Genere automatiquement par le systeme de veille technologique mastermaint</p>
        <p>""" + datetime.now().strftime("%d/%m/%Y a %H:%M:%S") + """</p>
    </div>
</body>
</html>
"""
    
    # Sauvegarder l'index
    index_path = reports_dir / "index.html"
    with open(index_path, 'w', encoding='utf-8') as f:
        f.write(html)
    
    print(f"Index cree: {index_path}")
    return index_path

if __name__ == "__main__":
    create_index()
