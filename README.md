# LliureX Repository Status Monitor

Monitor del estado de los repositorios de paquetes de LliureX para diferentes versiones de Ubuntu.

**🌐 Ver página con información detallada de paquetes**: https://Canx.github.io/lliurex-state/

> **💡 Después de hacer fork**: Ejecuta `./setup.sh` para configurar automáticamente tu repositorio y actualizar todas las URLs.

## 📖 ¿Qué es este proyecto?

Este repositorio monitorea automáticamente los repositorios de LliureX y proporciona:

- **Estado en tiempo real** de los repositorios (online/offline)
- **Información detallada de paquetes** para cada versión de Ubuntu
- **Historial de actualizaciones** con fechas de modificación de cada paquete
- **Páginas web interactivas** con búsqueda y filtrado de paquetes

## 🎯 Características

### Monitoreo Local
- ✅ Verificación del estado desde la Red de Aulas de LliureX
- 📊 Información almacenada en `local_status.json`
- ⏰ Actualización automática mediante cron

### Información de Paquetes
- 📦 Lista completa de todos los paquetes disponibles
- 🔍 Búsqueda y filtrado por nombre
- 📅 Fechas de última actualización de cada paquete
- 📈 Filtrado por período temporal (última semana, mes, 3 meses, etc.)
- 💾 Información de versiones y tamaños

### Páginas Web
- 🏠 Página principal con resumen de todas las versiones
- 📋 Páginas individuales por versión (Jammy, Noble)

## 📦 Versiones de Ubuntu Soportadas

- **Jammy (22.04 LTS)**: Ubuntu 22.04 LTS
- **Noble (24.04 LTS)**: Ubuntu 24.04 LTS

## 🚀 Uso

### Monitoreo Local (Red de Aulas)

```bash
# Actualizar estado manualmente
python3 update_status_local.py

# O usar el script con verificación de cambios
./update_local_with_check.sh
```

### Actualización de Información de Paquetes

```bash
# Actualizar información de todos los paquetes
python3 fetch_packages.py

# O usar el script con verificación de cambios
./update_packages_with_check.sh
```

### Configuración de Cron

Para monitoreo automático, añade al crontab:

```bash
# Monitoreo local cada hora
0 * * * * /ruta/al/lliurex-state/update_local_with_check.sh

# Actualización de paquetes semanal (domingos a las 2:00)
0 2 * * 0 /ruta/al/lliurex-state/update_packages_with_check.sh
```

## 📁 Estructura del Proyecto

```
lliurex-state/
├── index.html                      # Página principal
├── version.html                    # Plantilla para páginas de versión
├── jammy.html                      # Enlace a página de Jammy
├── noble.html                      # Enlace a página de Noble
├── fetch_packages.py               # Script para obtener info de paquetes
├── update_status_local.py          # Script para monitoreo local
├── update_packages_with_check.sh   # Actualización de paquetes con verificación
├── update_local_with_check.sh      # Actualización de estado con verificación
├── packages_state.json             # Estado actual de paquetes (para web)
├── changes_timestamps.json         # Fechas de actualización de paquetes
├── packages_jammy_main.json        # Paquetes de Jammy
├── packages_noble_main.json        # Paquetes de Noble
└── local_status.json               # Estado desde red local
```

## 🔧 Replicar este Proyecto

### 1. Fork y Clonar

```bash
# Fork en GitHub, luego:
git clone https://github.com/Canx/lliurex-state.git
cd lliurex-state
```

### 2. Instalar Dependencias

```bash
pip3 install -r requirements.txt
```

### 3. Configurar GitHub Pages

1. Ve a **Settings** → **Pages** en tu repositorio
2. Source: **GitHub Actions**
3. El workflow `.github/workflows/deploy-pages.yml` desplegará automáticamente

### 4. Configurar Automáticamente

```bash
# Ejecuta el script de configuración
./setup.sh
```

Este script detectará automáticamente tu repositorio y actualizará todas las URLs en el README.

### 5. Personalizar (Opcional)

- Edita `fetch_packages.py` para cambiar las versiones de Ubuntu
- Modifica `index.html` y `version.html` para personalizar el diseño
- Ajusta los scripts de actualización según tus necesidades

### 6. Ejecutar Primera Actualización

```bash
# Obtener información de paquetes
python3 fetch_packages.py

# Commit y push
git add .
git commit -m "Initial package data"
git push
```

### 7. Configurar Cron (Opcional)

Si quieres actualizaciones automáticas locales:

```bash
# Editar crontab
crontab -e

# Añadir líneas (ajusta la ruta):
0 * * * * /ruta/completa/a/lliurex-state/update_local_with_check.sh
0 2 * * 0 /ruta/completa/a/lliurex-state/update_packages_with_check.sh
```

## 🔗 Enlaces Útiles

- **LliureX**: https://lliurex.net/
- **Wiki LliureX**: https://wiki.lliurex.net/
- **Portal Educativo GVA**: https://portal.edu.gva.es/

## 📄 Licencia

Este proyecto es de código abierto bajo licencia MIT.

## 🤝 Contribuciones

Las contribuciones son bienvenidas. Por favor:

1. Fork el proyecto
2. Crea una rama para tu feature (`git checkout -b feature/AmazingFeature`)
3. Commit tus cambios (`git commit -m 'Add some AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abre un Pull Request

---

**Nota**: El estado de los repositorios se actualiza automáticamente mediante scripts programados. Los datos mostrados reflejan el último estado conocido desde la Red de Aulas.
