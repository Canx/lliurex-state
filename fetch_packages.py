#!/usr/bin/env python3
"""
Script to fetch detailed package information from LliureX repositories
"""
import requests
from datetime import datetime
from typing import List, Dict
import gzip
import io
import re

LLIUREX_BASE_URL = "http://lliurex.net"
UBUNTU_VERSIONS = ["focal", "jammy", "noble"]
COMPONENTS = ["main", "import", "testing"]

def parse_packages_file(content: str) -> List[Dict]:
    """Parse a Packages file and extract package information"""
    packages = []
    current_package = {}

    for line in content.split('\n'):
        if line.strip() == '':
            if current_package:
                packages.append(current_package)
                current_package = {}
        elif ':' in line:
            key, value = line.split(':', 1)
            current_package[key.strip()] = value.strip()

    if current_package:
        packages.append(current_package)

    return packages

def fetch_packages_for_version(version: str, component: str = "main") -> List[Dict]:
    """Fetch all packages for a specific Ubuntu version and component"""
    packages = []

    # Try different architectures
    architectures = ["amd64", "i386", "all"]

    for arch in architectures:
        url = f"{LLIUREX_BASE_URL}/{version}/dists/{version}/{component}/binary-{arch}/Packages.gz"

        try:
            print(f"  Fetching {component}/binary-{arch}...", end=' ')
            response = requests.get(url, timeout=30)

            if response.status_code == 200:
                # Decompress gzip content
                with gzip.GzipFile(fileobj=io.BytesIO(response.content)) as f:
                    content = f.read().decode('utf-8')

                arch_packages = parse_packages_file(content)
                packages.extend(arch_packages)
                print(f"✓ {len(arch_packages)} packages")
            else:
                print(f"✗ HTTP {response.status_code}")
        except Exception as e:
            print(f"✗ Error: {str(e)[:50]}")

    return packages

def get_package_summary(packages: List[Dict]) -> Dict:
    """Generate summary statistics from package list"""
    if not packages:
        return {
            "total_packages": 0,
            "total_size": 0,
            "latest_packages": [],
            "largest_packages": []
        }

    # Get unique packages (by name)
    unique_packages = {}
    for pkg in packages:
        name = pkg.get('Package', '')
        version = pkg.get('Version', '')
        if name:
            # Keep the latest version
            if name not in unique_packages:
                unique_packages[name] = pkg
            else:
                # Simple version comparison (not perfect but works for most cases)
                if version > unique_packages[name].get('Version', ''):
                    unique_packages[name] = pkg

    packages_list = list(unique_packages.values())

    # Calculate total size
    total_size = 0
    for pkg in packages_list:
        size_str = pkg.get('Size', '0')
        try:
            total_size += int(size_str)
        except:
            pass

    # Sort by version (approximate - just alphabetically)
    sorted_by_version = sorted(
        packages_list,
        key=lambda x: x.get('Version', ''),
        reverse=True
    )[:20]

    # Sort by size
    sorted_by_size = sorted(
        packages_list,
        key=lambda x: int(x.get('Size', '0')),
        reverse=True
    )[:10]

    return {
        "total_packages": len(packages_list),
        "total_size": total_size,
        "latest_packages": sorted_by_version,
        "largest_packages": sorted_by_size
    }

def format_size(bytes_size: int) -> str:
    """Format bytes to human readable size"""
    for unit in ['B', 'KB', 'MB', 'GB']:
        if bytes_size < 1024.0:
            return f"{bytes_size:.1f} {unit}"
        bytes_size /= 1024.0
    return f"{bytes_size:.1f} TB"

def generate_html_page(version: str, summary: Dict, components_data: Dict) -> str:
    """Generate HTML page for a specific Ubuntu version"""
    version_names = {
        "focal": "20.04 LTS (Focal Fossa)",
        "jammy": "22.04 LTS (Jammy Jellyfish)",
        "noble": "24.04 LTS (Noble Numbat)"
    }

    html = f"""<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>LliureX {version.capitalize()} - Repositorio de Paquetes</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
            line-height: 1.6;
            color: #333;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }}
        .container {{
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            border-radius: 10px;
            box-shadow: 0 10px 40px rgba(0,0,0,0.2);
            padding: 40px;
        }}
        h1 {{
            color: #667eea;
            margin-bottom: 10px;
            font-size: 2.5em;
        }}
        .subtitle {{
            color: #666;
            font-size: 1.2em;
            margin-bottom: 30px;
        }}
        .stats {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            margin-bottom: 40px;
        }}
        .stat-card {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 25px;
            border-radius: 10px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        }}
        .stat-card h3 {{
            font-size: 0.9em;
            opacity: 0.9;
            margin-bottom: 10px;
            text-transform: uppercase;
            letter-spacing: 1px;
        }}
        .stat-card .value {{
            font-size: 2em;
            font-weight: bold;
        }}
        .section {{
            margin-bottom: 40px;
        }}
        .section h2 {{
            color: #667eea;
            margin-bottom: 20px;
            padding-bottom: 10px;
            border-bottom: 3px solid #667eea;
        }}
        .tabs {{
            display: flex;
            gap: 10px;
            margin-bottom: 20px;
            flex-wrap: wrap;
        }}
        .tab {{
            padding: 10px 20px;
            background: #f0f0f0;
            border: none;
            border-radius: 5px;
            cursor: pointer;
            font-size: 1em;
            transition: all 0.3s;
        }}
        .tab.active {{
            background: #667eea;
            color: white;
        }}
        .tab:hover {{
            background: #764ba2;
            color: white;
        }}
        table {{
            width: 100%;
            border-collapse: collapse;
            margin-top: 20px;
        }}
        th, td {{
            padding: 12px;
            text-align: left;
            border-bottom: 1px solid #ddd;
        }}
        th {{
            background: #667eea;
            color: white;
            font-weight: 600;
        }}
        tr:hover {{
            background: #f5f5f5;
        }}
        .package-name {{
            font-weight: 600;
            color: #667eea;
        }}
        .back-link {{
            display: inline-block;
            margin-bottom: 20px;
            color: #667eea;
            text-decoration: none;
            font-weight: 600;
        }}
        .back-link:hover {{
            text-decoration: underline;
        }}
        .footer {{
            margin-top: 40px;
            padding-top: 20px;
            border-top: 1px solid #ddd;
            text-align: center;
            color: #666;
            font-size: 0.9em;
        }}
        .tab-content {{
            display: none;
        }}
        .tab-content.active {{
            display: block;
        }}
    </style>
</head>
<body>
    <div class="container">
        <a href="index.html" class="back-link">← Volver al índice</a>

        <h1>Ubuntu {version_names.get(version, version.capitalize())}</h1>
        <p class="subtitle">Repositorio LliureX - Actualizado el {datetime.utcnow().strftime('%d/%m/%Y %H:%M')} UTC</p>

        <div class="stats">
"""

    total_packages = 0
    total_size = 0

    for component, data in components_data.items():
        total_packages += data['total_packages']
        total_size += data['total_size']

    html += f"""
            <div class="stat-card">
                <h3>Total de Paquetes</h3>
                <div class="value">{total_packages}</div>
            </div>
            <div class="stat-card">
                <h3>Tamaño Total</h3>
                <div class="value">{format_size(total_size)}</div>
            </div>
            <div class="stat-card">
                <h3>Componentes</h3>
                <div class="value">{len(components_data)}</div>
            </div>
        </div>
"""

    # Latest packages section
    html += """
        <div class="section">
            <h2>📦 Últimos Paquetes Actualizados</h2>
            <div class="tabs">
"""

    for i, component in enumerate(components_data.keys()):
        active = "active" if i == 0 else ""
        html += f'<button class="tab {active}" onclick="showTab(\'latest-{component}\')">{component.capitalize()}</button>\n'

    html += """
            </div>
"""

    for i, (component, data) in enumerate(components_data.items()):
        active = "active" if i == 0 else ""
        html += f"""
            <div id="latest-{component}" class="tab-content {active}">
                <table>
                    <thead>
                        <tr>
                            <th>Paquete</th>
                            <th>Versión</th>
                            <th>Arquitectura</th>
                            <th>Tamaño</th>
                        </tr>
                    </thead>
                    <tbody>
"""

        for pkg in data['latest_packages'][:15]:
            name = pkg.get('Package', 'N/A')
            version = pkg.get('Version', 'N/A')
            arch = pkg.get('Architecture', 'N/A')
            size = format_size(int(pkg.get('Size', '0')))

            html += f"""
                        <tr>
                            <td class="package-name">{name}</td>
                            <td>{version}</td>
                            <td>{arch}</td>
                            <td>{size}</td>
                        </tr>
"""

        html += """
                    </tbody>
                </table>
            </div>
"""

    html += """
        </div>

        <div class="footer">
            <p>Datos obtenidos de <a href="http://lliurex.net" target="_blank">lliurex.net</a></p>
            <p>Generado automáticamente por GitHub Actions</p>
        </div>
    </div>

    <script>
        function showTab(tabId) {
            // Hide all tab contents
            document.querySelectorAll('.tab-content').forEach(content => {
                content.classList.remove('active');
            });

            // Remove active class from all tabs
            document.querySelectorAll('.tab').forEach(tab => {
                tab.classList.remove('active');
            });

            // Show selected tab content
            document.getElementById(tabId).classList.add('active');

            // Add active class to clicked tab
            event.target.classList.add('active');
        }
    </script>
</body>
</html>
"""

    return html

def generate_index_page(versions_summary: Dict) -> str:
    """Generate main index.html page"""
    html = """<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>LliureX - Monitor de Repositorios</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
            line-height: 1.6;
            color: #333;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }
        .container {
            max-width: 1200px;
            margin: 0 auto;
        }
        header {
            background: white;
            border-radius: 10px;
            padding: 40px;
            margin-bottom: 30px;
            box-shadow: 0 10px 40px rgba(0,0,0,0.2);
            text-align: center;
        }
        h1 {
            color: #667eea;
            font-size: 3em;
            margin-bottom: 10px;
        }
        .subtitle {
            color: #666;
            font-size: 1.2em;
        }
        .cards {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(350px, 1fr));
            gap: 25px;
            margin-bottom: 30px;
        }
        .card {
            background: white;
            border-radius: 10px;
            padding: 30px;
            box-shadow: 0 10px 40px rgba(0,0,0,0.2);
            transition: transform 0.3s, box-shadow 0.3s;
        }
        .card:hover {
            transform: translateY(-5px);
            box-shadow: 0 15px 50px rgba(0,0,0,0.3);
        }
        .card h2 {
            color: #667eea;
            margin-bottom: 15px;
            font-size: 1.8em;
        }
        .card .version {
            color: #999;
            font-size: 0.9em;
            margin-bottom: 20px;
        }
        .card .stats {
            margin: 20px 0;
        }
        .card .stat {
            display: flex;
            justify-content: space-between;
            padding: 10px 0;
            border-bottom: 1px solid #eee;
        }
        .card .stat:last-child {
            border-bottom: none;
        }
        .card .stat-label {
            color: #666;
        }
        .card .stat-value {
            font-weight: 600;
            color: #667eea;
        }
        .card .btn {
            display: inline-block;
            margin-top: 20px;
            padding: 12px 30px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            text-decoration: none;
            border-radius: 5px;
            font-weight: 600;
            transition: opacity 0.3s;
        }
        .card .btn:hover {
            opacity: 0.9;
        }
        .status {
            display: inline-block;
            padding: 5px 15px;
            border-radius: 20px;
            font-size: 0.9em;
            font-weight: 600;
            margin-bottom: 15px;
        }
        .status.online {
            background: #d4edda;
            color: #155724;
        }
        .status.offline {
            background: #f8d7da;
            color: #721c24;
        }
        footer {
            background: white;
            border-radius: 10px;
            padding: 20px;
            box-shadow: 0 10px 40px rgba(0,0,0,0.2);
            text-align: center;
            color: #666;
        }
        footer a {
            color: #667eea;
            text-decoration: none;
        }
        footer a:hover {
            text-decoration: underline;
        }
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>🐧 LliureX Repository Monitor</h1>
            <p class="subtitle">Monitor de repositorios de paquetes LliureX para Ubuntu</p>
            <p style="margin-top: 15px; color: #999;">Última actualización: """ + datetime.utcnow().strftime('%d/%m/%Y %H:%M UTC') + """</p>
        </header>

        <div class="cards">
"""

    version_names = {
        "focal": ("Ubuntu 20.04 LTS", "Focal Fossa"),
        "jammy": ("Ubuntu 22.04 LTS", "Jammy Jellyfish"),
        "noble": ("Ubuntu 24.04 LTS", "Noble Numbat")
    }

    for version, summary in versions_summary.items():
        name, codename = version_names.get(version, (version.capitalize(), ""))
        status = "online" if summary.get('status') == 'online' else "offline"
        status_text = "✓ Online" if status == "online" else "✗ Offline"

        total_packages = sum(data['total_packages'] for data in summary.get('components', {}).values())
        total_size = sum(data['total_size'] for data in summary.get('components', {}).values())

        html += f"""
            <div class="card">
                <span class="status {status}">{status_text}</span>
                <h2>{name}</h2>
                <div class="version">{codename}</div>

                <div class="stats">
                    <div class="stat">
                        <span class="stat-label">📦 Paquetes totales</span>
                        <span class="stat-value">{total_packages:,}</span>
                    </div>
                    <div class="stat">
                        <span class="stat-label">💾 Tamaño total</span>
                        <span class="stat-value">{format_size(total_size)}</span>
                    </div>
                    <div class="stat">
                        <span class="stat-label">🔧 Componentes</span>
                        <span class="stat-value">{len(summary.get('components', {}))}</span>
                    </div>
                </div>

                <a href="{version}.html" class="btn">Ver detalles →</a>
            </div>
"""

    html += """
        </div>

        <footer>
            <p><strong>LliureX</strong> - Distribución Linux educativa de la Generalitat Valenciana</p>
            <p style="margin-top: 10px;">
                <a href="https://lliurex.net" target="_blank">Web oficial</a> ·
                <a href="https://wiki.lliurex.net" target="_blank">Wiki</a> ·
                <a href="https://github.com/Canx/lliurex-state" target="_blank">GitHub</a>
            </p>
        </footer>
    </div>
</body>
</html>
"""

    return html

def main():
    print("🔍 Fetching package information from LliureX repositories...\n")

    versions_summary = {}

    for version in UBUNTU_VERSIONS:
        print(f"\n{'='*60}")
        print(f"Processing {version}...")
        print('='*60)

        components_data = {}

        for component in COMPONENTS:
            print(f"\nFetching {component} packages:")
            packages = fetch_packages_for_version(version, component)

            if packages:
                summary = get_package_summary(packages)
                components_data[component] = summary
                print(f"  Summary: {summary['total_packages']} unique packages, {format_size(summary['total_size'])}")

        if components_data:
            print(f"\n📝 Generating HTML page for {version}...")
            html = generate_html_page(version, None, components_data)

            with open(f"{version}.html", "w", encoding='utf-8') as f:
                f.write(html)

            versions_summary[version] = {
                'status': 'online',
                'components': components_data
            }
            print(f"  ✓ Created {version}.html")
        else:
            versions_summary[version] = {
                'status': 'offline',
                'components': {}
            }

    print(f"\n{'='*60}")
    print("📝 Generating index.html...")
    print('='*60)

    index_html = generate_index_page(versions_summary)
    with open("index.html", "w", encoding='utf-8') as f:
        f.write(index_html)

    print("  ✓ Created index.html")
    print("\n✅ All pages generated successfully!")
    print("\nGenerated files:")
    print("  - index.html (main page)")
    for version in UBUNTU_VERSIONS:
        print(f"  - {version}.html (Ubuntu {version} details)")

if __name__ == "__main__":
    main()
