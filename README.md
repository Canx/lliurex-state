# LliureX Repository Status

[![Check Status](https://github.com/Canx/lliurex-state/actions/workflows/check-status.yml/badge.svg)](https://github.com/Canx/lliurex-state/actions/workflows/check-status.yml)
[![Update Packages](https://github.com/Canx/lliurex-state/actions/workflows/update-packages.yml/badge.svg)](https://github.com/Canx/lliurex-state/actions/workflows/update-packages.yml)

Este repositorio monitorea automáticamente el estado de los repositorios de LliureX para diferentes versiones de Ubuntu.

**🌐 [Ver página con información detallada de paquetes](https://Canx.github.io/lliurex-state/)**

## 📊 Estado Actual

### 🌍 Estado Externo (GitHub Actions)

**Última actualización:** 2025-12-16 12:54:53 UTC

| Versión Ubuntu | Estado | Última Actualización Repo | URL |
|----------------|--------|---------------------------|-----|
| Ubuntu 20.04 LTS (focal) | ✅ online | Tue, 29 Jul 2025 12:39:16 UTC | [Link](http://lliurex.net/focal/) |
| Ubuntu 22.04 LTS (jammy) | ✅ online | Thu, 11 Dec 2025 12:26:11 UTC | [Link](http://lliurex.net/jammy/) |
| Ubuntu 24.04 LTS (noble) | ✅ online | Tue, 29 Jul 2025 12:42:15 UTC | [Link](http://lliurex.net/noble/) |


### 🏠 Estado Local (Red LliureX)

**Última actualización:** 2025-12-17 11:00:01 UTC
**Servidor:** sauron

| Versión Ubuntu | Estado | Última Actualización Repo | URL |
|----------------|--------|---------------------------|-----|
| Ubuntu 20.04 LTS (focal) | ✅ online | Tue, 29 Jul 2025 12:39:16 UTC | [Link](http://lliurex.net/focal/) |
| Ubuntu 22.04 LTS (jammy) | ✅ online | Thu, 11 Dec 2025 12:26:11 UTC | [Link](http://lliurex.net/jammy/) |
| Ubuntu 24.04 LTS (noble) | ✅ online | Thu, 31 Jul 2025 10:25:45 UTC | [Link](http://lliurex.net/noble/) |


## 📦 Repositorios de LliureX

LliureX mantiene repositorios para diferentes versiones LTS de Ubuntu:

- **Focal (20.04 LTS)**: Versión anterior de soporte extendido
- **Jammy (22.04 LTS)**: Versión LTS actual
- **Noble (24.04 LTS)**: Versión LTS más reciente

Cada repositorio contiene los paquetes específicos de LliureX adaptados para esa versión de Ubuntu.

## 🔄 Actualización Automática

### Estado de Repositorios
Se verifica cada hora mediante GitHub Actions, comprobando el estado de disponibilidad y última actualización de los repositorios desde fuera de la red LliureX.

### Información de Paquetes
Se actualiza semanalmente (domingos a las 02:00 UTC) mediante GitHub Actions, generando páginas HTML con información detallada de todos los paquetes disponibles.

### Estado Local
Para monitorizar el estado desde la red local, ejecuta `update_status_local.py` manualmente o configura un cron job. El README se regenera automáticamente cada vez que se actualiza cualquiera de los estados.

## 📖 Acerca de LliureX

LliureX es una distribución Linux educativa desarrollada por la Generalitat Valenciana, basada en Ubuntu y diseñada específicamente para el ámbito educativo.

- **Web oficial:** https://lliurex.net/
- **Wiki:** https://wiki.lliurex.net/
- **Portal educativo:** https://portal.edu.gva.es/

## 🔗 Enlaces Útiles

- [Repositorio Principal](https://lliurex.net/)
- [Documentación](https://wiki.lliurex.net/)
- [Descargas](https://lliurex.net/descargas/)

## 📝 Licencia

Este proyecto es de código abierto y está disponible bajo la licencia MIT.

---

*Generado automáticamente por GitHub Actions*
