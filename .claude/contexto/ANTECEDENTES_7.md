# 1.1 Antecedentes del Estado del Arte (7 investigaciones de bases de datos)

Consulta realizada el 2026-11-26. Los metadatos (autores, año, título, revista, volumen, páginas, DOI) se verificaron contra Crossref y las páginas del DOI/editor/repositorio; los resúmenes se parafrasearon a partir de los abstracts o páginas consultadas. Ver al final los datos no verificados al 100 %.

## Tabla resumen

| N.° | Base de datos | Autores y año | Tema | DOI / URL |
|---|---|---|---|---|
| 1 | Scopus (editor SCITEPRESS) | Nunkesser (2022) | Arquitectura hexagonal / desacoplamiento | https://doi.org/10.5220/0011075100003266 |
| 2 | Springer | Heeager y Nielsen (2020) | Adaptación de procesos / modelo híbrido ágil-dirigido por plan | https://doi.org/10.1007/s10664-020-09804-z |
| 3 | ScienceDirect | Chaabane et al. (2019) | GQM como método de evaluación | https://doi.org/10.1016/j.scico.2019.102305 |
| 4 | IEEE Xplore | Marandi et al. (2023) | Seguridad (SAST/DAST) en CI/CD DevSecOps | https://doi.org/10.1109/WCONF58270.2023.10235015 |
| 5 | Redalyc | Cuadros López et al. (2016) | CMMI-DEV / SCAMPI en pymes de software | https://doi.org/10.17230/ad-minister.29.7 |
| 6 | ACM Digital Library | Santos et al. (2022) | Integración continua y calidad (control de versiones / CI) | https://doi.org/10.1145/3544902.3546244 |
| 7 | PubMed (PMC) | Westgard et al. (2019) | mHealth, salud infantil y anemia en Perú | https://doi.org/10.1136/bmjopen-2018-028361 |

---

## Bloques para el informe

### 1. Scopus: arquitectura hexagonal
Nunkesser, R. (2022). *Using Hexagonal Architecture for Mobile Applications*. Proceedings of the 17th International Conference on Software Technologies (ICSOFT 2022), 113-120. SCITEPRESS. https://doi.org/10.5220/0011075100003266

El autor busca una arquitectura global adecuada para aplicaciones móviles complejas y propone la arquitectura hexagonal como base. Compara los patrones MVX, las arquitecturas propias de móviles y las arquitecturas generales, y analiza los retos de aplicarla en iOS y Android. Concluye que es recomendable para apps con lógica de negocio no trivial, por su flexibilidad, su extensibilidad y la menor dependencia de los frameworks. *Aporte a este proyecto:* respalda separar el dominio de la anemia de la interfaz y la infraestructura (puertos y adaptadores en FastAPI y la PWA).

### 2. Springer: adaptación de procesos / modelos híbridos
Heeager, L. T., y Nielsen, P. A. (2020). Meshing agile and plan-driven development in safety-critical software: a case study. *Empirical Software Engineering, 25*(2), 1035-1062. https://doi.org/10.1007/s10664-020-09804-z

Los autores estudian cómo combinar prácticas ágiles y dirigidas por plan cuando se exigen condiciones de seguridad. Mediante un estudio de caso en una organización farmacéutica que adoptó Scrum en un proyecto dirigido por plan, analizan cuatro áreas: documentación, requisitos, ciclo de vida y pruebas. Su resultado es una comprensión más detallada de cómo se ensamblan ambos enfoques y de cómo el contexto crítico condiciona cada área. *Aporte a este proyecto:* justifica adaptar (tailoring) Scrum con documentación y controles propios de un sistema de salud.

### 3. ScienceDirect: GQM
Chaabane, M., Bouassida Rodriguez, I., Colomo-Palacios, R., Gaaloul, W., y Jmaiel, M. (2019). A modeling approach for Systems-of-Systems by adapting ISO/IEC/IEEE 42010 Standard evaluated by Goal-Question-Metric. *Science of Computer Programming, 184*, Artículo 102305. https://doi.org/10.1016/j.scico.2019.102305

Proponen un enfoque de modelado de arquitecturas de sistemas de sistemas basado en la norma ISO/IEC/IEEE 42010, con mejoras a la norma. Lo evalúan con GQM y un grupo focal en un caso de ciudad inteligente, y verifican los modelos con reglas de diseño. Concluyen que las mejoras son relevantes y que falta una evaluación cuantitativa en sistemas mayores. *Aporte a este proyecto:* es un ejemplo publicado de GQM para evaluar una propuesta de arquitectura, como se hace con los objetivos y las métricas del sistema.

### 4. IEEE Xplore: seguridad en CI/CD
Marandi, M., Bertia, A., y Silas, S. (2023). Implementing and automating security scanning to a DevSecOps CI/CD pipeline. *2023 World Conference on Communication & Computing (WCONF)*, 1-6. IEEE. https://doi.org/10.1109/WCONF58270.2023.10235015

Parten de que los despliegues en contenedores con CI/CD enfrentan riesgos que los despliegues tradicionales no tienen. Proponen un método con Snyk y StackHawk que ejecuta análisis SAST y DAST integrados con GitHub, con paneles y corrección automatizada de vulnerabilidades. Informan mejor seguridad del pipeline y menor tiempo de detección y corrección. *Aporte a este proyecto:* sustenta incluir análisis de seguridad automatizado (alineado con OWASP) en GitHub Actions.

### 5. Redalyc: CMMI
Cuadros López, Á. J., Galindres, C., y Ruiz, P. (2016). Modelo de evaluación de madurez en gestión de proyectos para pymes del subsector desarrollo de software (Project maturity evaluation model for SMEs from the software development sub-sector). *AD-minister, (29)*, 147-162. https://doi.org/10.17230/ad-minister.29.7

Proponen un modelo de evaluación de madurez en gestión de proyectos para pymes de software, basado en CMMI-DEV y el método SCAMPI, con escala cuantitativa de satisfacción y criterios para elegir expertos. Lo aplicaron en una empresa mediana de TIC, que no alcanzó el nivel 2 pero ya cumplía el 92 % de sus procesos y el 77 % del total. *Aporte a este proyecto:* ofrece un antecedente regional de autoevaluación con CMMI-DEV a escala pequeña, útil para evaluar los procesos del equipo.

### 6. ACM Digital Library: integración continua
Santos, J., da Costa, D. A., y Kulesza, U. (2022). Investigating the impact of continuous integration practices on the productivity and quality of open-source projects. En *Proceedings of the 16th ACM/IEEE International Symposium on Empirical Software Engineering and Measurement (ESEM '22)*. ACM. https://doi.org/10.1145/3544902.3546244

Analizaron si las subprácticas de CI, y no solo contar con un servidor de CI, se relacionan con la productividad y la calidad. Con datos de 90 proyectos de GitHub durante dos años, aplicaron modelos de regresión y un análisis documental. Encontraron que la actividad de builds, la salud del build y el tiempo para corregir builds rotos se asocian con menos incidencias de errores. *Aporte a este proyecto:* respalda medir la salud de los pipelines de GitHub Actions como indicador de calidad.

### 7. PubMed: mHealth en salud infantil, Perú
Westgard, C. M., Rivadeneyra, N., y Mechael, P. (2019). mHealth tool to improve community health agent performance for child development: study protocol for a cluster-randomised controlled trial in Peru. *BMJ Open, 9*(11), Artículo e028361. https://doi.org/10.1136/bmjopen-2018-028361

El estudio busca medir el efecto de CHEST, una aplicación en tableta que usan agentes comunitarios de salud en visitas domiciliarias, sobre el desarrollo y el estado nutricional de niños de 6 a 36 meses en la Amazonía peruana. Es un ensayo aleatorizado por conglomerados en Loreto (10-14 comunidades, 400-450 niños), que también evalúa anemia y desnutrición crónica y hace una evaluación de procesos cualitativa. Es un protocolo, de modo que no reporta resultados de eficacia. *Aporte a este proyecto:* es un antecedente peruano de mHealth con agentes comunitarios y anemia como resultado medido.

---

## Referencias (APA 7)

Cuadros López, Á. J., Galindres, C., y Ruiz, P. (2016). Modelo de evaluación de madurez en gestión de proyectos para pymes del subsector desarrollo de software. *AD-minister, (29)*, 147-162. https://doi.org/10.17230/ad-minister.29.7

Chaabane, M., Bouassida Rodriguez, I., Colomo-Palacios, R., Gaaloul, W., y Jmaiel, M. (2019). A modeling approach for Systems-of-Systems by adapting ISO/IEC/IEEE 42010 Standard evaluated by Goal-Question-Metric. *Science of Computer Programming, 184*, Artículo 102305. https://doi.org/10.1016/j.scico.2019.102305

Heeager, L. T., y Nielsen, P. A. (2020). Meshing agile and plan-driven development in safety-critical software: A case study. *Empirical Software Engineering, 25*(2), 1035-1062. https://doi.org/10.1007/s10664-020-09804-z

Marandi, M., Bertia, A., y Silas, S. (2023). Implementing and automating security scanning to a DevSecOps CI/CD pipeline. En *2023 World Conference on Communication & Computing (WCONF)* (pp. 1-6). IEEE. https://doi.org/10.1109/WCONF58270.2023.10235015

Nunkesser, R. (2022). Using hexagonal architecture for mobile applications. En *Proceedings of the 17th International Conference on Software Technologies (ICSOFT 2022)* (pp. 113-120). SCITEPRESS. https://doi.org/10.5220/0011075100003266

Santos, J., da Costa, D. A., y Kulesza, U. (2022). Investigating the impact of continuous integration practices on the productivity and quality of open-source projects. En *Proceedings of the 16th ACM/IEEE International Symposium on Empirical Software Engineering and Measurement (ESEM '22)*. ACM. https://doi.org/10.1145/3544902.3546244

Westgard, C. M., Rivadeneyra, N., y Mechael, P. (2019). mHealth tool to improve community health agent performance for child development: Study protocol for a cluster-randomised controlled trial in Peru. *BMJ Open, 9*(11), Artículo e028361. https://doi.org/10.1136/bmjopen-2018-028361

---

## Datos no verificados al 100 %

- **Indexación por base de datos:** se verificó el editor y la página del DOI, no la presencia en cada índice. El N.° 1 (Scopus) y el N.° 5 (Redalyc: página verificada) tienen distinto grado: Scopus no se consultó directamente; confirmar en scopus.com.
- N.° 6: no se obtuvo el número de artículo ni las páginas del ACM DL, y el abstract se tomó de la versión arXiv 2208.02598 (el DOI ACM figura como publicación relacionada). Confirmar título final y páginas en https://doi.org/10.1145/3544902.3546244.
- N.° 3: no se pudo abrir ScienceDirect (error 403); el resumen proviene de Semantic Scholar, y su vínculo con GQM es de evaluación, no una investigación centrada en GQM.
- N.° 4: IEEE Xplore no entregó el texto; el resumen proviene de Semantic Scholar. Páginas 1-6 según Crossref.
- N.° 2: no se pudo leer el abstract completo en Springer; el resumen se apoya en un resultado de búsqueda que cita el abstract y en los datos de Crossref.
- N.° 7: es un protocolo de ensayo, sin resultados de eficacia. Si el informe requiere resultados, buscar otro.
- N.° 5: 2016 (fuera de 2019-2025), y el artículo está en inglés con resumen en español.
