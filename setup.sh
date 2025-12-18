#!/bin/bash
# Script de inicialización para configurar el README con el repositorio correcto

set -e

echo "🔧 Configurando lliurex-state para tu repositorio..."

# Detectar el repositorio desde git
REMOTE_URL=$(git config --get remote.origin.url 2>/dev/null || echo "")

if [ -z "$REMOTE_URL" ]; then
    echo "❌ Error: No se pudo detectar el repositorio remoto"
    echo "   Asegúrate de estar en un repositorio git con remote configurado"
    exit 1
fi

# Parsear la URL para obtener usuario y repositorio
if [[ $REMOTE_URL =~ github.com[:/]([^/]+)/([^/.]+) ]]; then
    GITHUB_USER="${BASH_REMATCH[1]}"
    GITHUB_REPO="${BASH_REMATCH[2]}"
else
    echo "❌ Error: No se pudo parsear la URL del repositorio: $REMOTE_URL"
    exit 1
fi

echo "📍 Repositorio detectado: $GITHUB_USER/$GITHUB_REPO"

# Verificar que el README tiene placeholders
if ! grep -q "TU-USUARIO" README.md; then
    echo "✅ README.md ya está configurado"
    echo "   Si quieres reconfigurarlo, restaura los placeholders primero"
    exit 0
fi

# Crear backup del README
cp README.md README.md.backup
echo "💾 Backup creado: README.md.backup"

# Actualizar README.md
sed -i "s|TU-USUARIO|$GITHUB_USER|g" README.md
sed -i "s|TU-REPOSITORIO|$GITHUB_REPO|g" README.md

# Eliminar backticks de Markdown que quedaron
sed -i "s|\`$GITHUB_USER\`|$GITHUB_USER|g" README.md
sed -i "s|\`$GITHUB_REPO\`|$GITHUB_REPO|g" README.md

# Verificar que se hicieron cambios
if grep -q "$GITHUB_USER" README.md && grep -q "$GITHUB_REPO" README.md; then
    echo "✅ README.md actualizado correctamente"
    echo ""
    echo "📝 Cambios realizados:"
    echo "   - Usuario: $GITHUB_USER"
    echo "   - Repositorio: $GITHUB_REPO"
    echo "   - URL: https://$GITHUB_USER.github.io/$GITHUB_REPO/"
    echo ""
    echo "🎉 ¡Configuración completada!"
    echo ""
    echo "Próximos pasos:"
    echo "1. Revisa el README.md actualizado"
    echo "2. Ejecuta: python3 fetch_packages.py"
    echo "3. Ejecuta: git add README.md && git commit -m 'Setup repository' && git push"
    echo "4. Configura GitHub Pages en Settings → Pages → Source: GitHub Actions"
else
    echo "⚠️  Advertencia: No se pudieron aplicar todos los cambios"
    mv README.md.backup README.md
    echo "   Se ha restaurado el README original"
    exit 1
fi
