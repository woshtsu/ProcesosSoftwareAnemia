**✅ Procedimiento para emitir reporte en Understand desde un repositorio GitHub**

**🧰 Requisitos Previos**

1. Tener instalado **Understand** de SciTools (versión actual o compatible).
2. Tener instalado **Git** en tu sistema.
3. Tener acceso al repositorio GitHub que contiene el código fuente.
4. Tener una licencia activa de Understand.

**📌 Paso 1: Clonar el repositorio GitHub**

1. Abre una terminal (cmd, PowerShell, Terminal, etc.).
2. Usa el siguiente comando para clonar el repositorio:
3. git clone https://github.com/usuario/nombre-repositorio.git
4. Dirígete a la carpeta del proyecto:
5. cd nombre-repositorio

**📌 Paso 2: Crear un proyecto en Understand**

1. Abre **Understand**.
2. Selecciona **File → New Project**.
3. Elige el tipo de proyecto según el lenguaje (C/C++, Java, Python, etc.).
4. Especifica:
   * **Nombre del proyecto**.
   * **Ubicación del proyecto .udb** (de preferencia dentro de la carpeta clonada o en una ruta local).
   * **Lenguaje de programación** si no se detecta automáticamente.

**📌 Paso 3: Añadir el código fuente al proyecto**

1. En el panel izquierdo, haz clic derecho en el proyecto → **Add → Add Files/Folder**.
2. Selecciona la carpeta clonada con el código.
3. Understand detectará los archivos fuente automáticamente.

**📌 Paso 4: Analizar el proyecto**

1. Haz clic en **Project → Analyze Project**.
2. Espera a que Understand analice todo el código. Esto puede tardar dependiendo del tamaño del repositorio.
3. Verifica que no haya errores críticos en la pestaña de análisis.

**📌 Paso 5: Emitir reporte**

1. Ve a **Reports → Generate Report...**
2. Elige entre los siguientes tipos de reportes:
   * **Metrics** (líneas de código, complejidad, etc.)
   * **Dependencies**
   * **Class Metrics**
   * **Function Metrics**
   * **Architecture**
   * **Custom Reports** (puedes usar scripts en Python, Perl o LUA)
3. Configura los filtros o archivos que quieres incluir.
4. Elige el formato de salida: **HTML, PDF, RTF, TXT, CSV**.
5. Haz clic en **Generate** y guarda el reporte.

**📌 Paso 6 (opcional): Automatizar reporte con script**

Understand permite ejecutar reportes desde la línea de comandos. Por ejemplo:

und -db proyecto.udb -metrics all -report metrics.html

Puedes programar esto en un script .bat o .sh para automatizar el proceso.

**📝 Recomendaciones adicionales**

* Puedes integrar Understand con **CI/CD** para análisis automático con cada push.
* Si el proyecto es muy grande, puedes limitar el análisis a ciertos subdirectorios.
* Usa el menú **Tools → Metrics Browser** para explorar manualmente antes de generar reportes automáticos.

<u>[Getting Started with Understand – walk-through of UI & core features](https://www.youtube.com/watch?v=0OgVG5J6nG8&utm_source=chatgpt.com)</u>

Aquí tienes un excelente video tutorial gratuito y accesible en YouTube que te guiará paso a paso por **Understand** de SciTools:

**🎥 Resumen del contenido del video**

* Una introducción visual al **interfaz de usuario**, mostrando los menús principales, paneles como el navegador de entidades y el explorador de información.
* Explicación de cómo **analizar un proyecto**, incluyendo cómo abrir un proyecto existente o crear uno nuevo, seleccionar código fuente y ejecutar el análisis.
* Demostración de funciones clave como **navegación por entidades**, visualización de **gráficos y métricas**, y cómo aprovechar los filtros para explorar tu código.

**🔎 ¿Por qué te conviene verlo?**

* El video, publicado hace aproximadamente 2.6 años por el canal oficial de Understand, mantiene su vigencia para versiones recientes del software ([<u>youtube.com</u>](https://www.youtube.com/watch?v=0OgVG5J6nG8&utm_source=chatgpt.com)).
* Es ideal tanto si estás empezando como si quieres repasar aspectos clave de navegación y análisis en el IDE.

**📌 Otros videos complementarios**

* **Basic Navigation in Understand™**: breve guía sobre gráficos y métricas ([<u>youtube.com</u>](https://www.youtube.com/watch?v=YDd9J2Fs5Ug&utm_source=chatgpt.com)).
* **Create a new project from source or Git**: explica cómo comenzar un proyecto con repositorio local o remoto ([<u>youtube.com</u>](https://www.youtube.com/watch?v=FwlFMY8uDMI&utm_source=chatgpt.com)).
* **Visualize execution paths with Control Flow Graphs**: para aprender a crear visualizaciones de flujo de control ([<u>youtube.com</u>](https://www.youtube.com/watch?v=1Z5NmIUqjzo&utm_source=chatgpt.com)).