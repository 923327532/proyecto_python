# 💳 Simulador Bancario - Plataforma de Operaciones Financieras

## 📋 Índice

1. [Resumen Ejecutivo](#resumen-ejecutivo)
2. [Autores](#autores)
3. [Carrera y Contexto Académico](#carrera-y-contexto-académico)
4. [Objetivos del Proyecto](#objetivos-del-proyecto)
5. [Justificación](#justificación)
6. [Aporte Social y Educativo](#aporte-social-y-educativo)
7. [Ventajas y Beneficios](#ventajas-y-beneficios)
8. [Motivación Tecnológica (Colas como motor del proyecto)](#motivación-tecnológica-colas-como-motor-del-proyecto)
9. [Tecnologías y Herramientas Utilizadas](#tecnologías-y-herramientas-utilizadas)
10. [Arquitectura del Proyecto](#arquitectura-del-proyecto)
11. [Diseño de la Base de Datos](#diseño-de-la-base-de-datos)
12. [Módulos Desarrollados](#módulos-desarrollados)
13. [Guía Completa de Instalación y Ejecución](#guía-completa-de-instalación-y-ejecución)
14. [Compatibilidad y Requisitos de Hardware](#compatibilidad-y-requisitos-de-hardware)
15. [Manual de Usuario - Guía Práctica](#manual-de-usuario---guía-práctica)
16. [Manual Técnico](#manual-técnico)
17. [Aspecto Económico](#aspecto-económico)
18. [Cronograma y Tiempos de Desarrollo](#cronograma-y-tiempos-de-desarrollo)
19. [Equipo de Desarrollo](#equipo-de-desarrollo)
20. [Licencia y Uso del Proyecto](#licencia-y-uso-del-proyecto)
21. [Conclusiones Finales](#conclusiones-finales)

---

## 📁 Resumen Ejecutivo

Este proyecto consiste en la creación de un **Simulador Bancario Educativo**, que permite emular las operaciones más comunes dentro de una entidad financiera, como transferencias, pagos, solicitud de préstamos, atención por ventanilla y más. El objetivo es que los estudiantes comprendan cómo se estructuran las aplicaciones bancarias, la importancia de la gestión de datos y el funcionamiento de colas de atención.

🚨 La plataforma tiene fines exclusivamente académicos y no representa transacciones reales.

---

## 👨‍💻 Autores

**Equipo N° 7**
Curso: *Algoritmos y Programación en Python*
Ciclo: *3° Ciclo*
Carrera: *Diseño y Desarrollo de Software*

---

## 🎓 Carrera y Contexto Académico

Proyecto desarrollado como simulador funcional para la asignatura de *Algoritmos y Programación en Python*, perteneciente al plan de estudios de la carrera **Diseño y Desarrollo de Software**, bajo la guía académica del profesor:

👨‍💼 **Camasca Macedo, Charles Dummar**

---

## 🎯 Objetivos del Proyecto

👉 Simular operaciones de una entidad bancaria digital.
👉 Reforzar habilidades de programación, estructuras de datos y modelado de sistemas.
👉 Aplicar teoría de colas como parte central de las operaciones.
👉 Desarrollar un sistema modular, escalable y funcional.

---

## 🏩 Justificación

Hoy en día, el sector financiero digital es esencial. Comprender su funcionamiento es clave para cualquier desarrollador. Esta simulación permite experimentar en un entorno seguro, adquiriendo habilidades aplicables al mundo real, sin comprometer recursos financieros.

---

## 🌍 Aporte Social y Educativo

**Educativo:** Aprendizaje práctico sobre desarrollo de sistemas financieros.
**Social:** Sensibilización sobre el funcionamiento de las apps bancarias.
**Tecnológico:** Formación en tecnologías de desarrollo actuales y estructuras de datos.

---

## 💡 Ventajas y Beneficios

👉 Simulación sin riesgos económicos.
👉 Reforzamiento de conocimientos teóricos.
👉 Uso de herramientas y lenguajes reales del sector.
👉 Sistema modular, documentado y ampliable.
👉 Fomenta el trabajo colaborativo y metodologías ágiles.

---

## 🔧 Motivación Tecnológica (Colas como motor del proyecto)

El concepto de colas es esencial en sistemas reales, ya sea en ventanillas físicas o entornos virtuales. Nuestra plataforma integra este modelo en la atención de clientes, permitiendo simular:

🔹 Gestión de turnos en ventanillas.
🔹 Control de flujo de atención.
🔹 Ordenamiento y prioridad en solicitudes.

Las estructuras de datos utilizadas refuerzan el aprendizaje técnico mientras se aplican a un caso concreto.

---

## 🛠️ Tecnologías y Herramientas Utilizadas

| Área          | Herramienta                              |
| ------------- | ---------------------------------------- |
| Backend       | Node.js, Express                         |
| Frontend      | HTML5, CSS3, Bootstrap                   |
| Base de Datos | MySQL (PostgreSQL adaptable)             |
| Otros         | JavaScript, Visual Studio Code, Git, npm |

---

## 🏗️ Arquitectura del Proyecto

La aplicación sigue el esquema cliente-servidor:

```bash
[Cliente (Navegador)] ⇄ [Servidor Node.js] ⇄ [Base de Datos MySQL/PostgreSQL]
```

**Estructura de carpetas:**

* `/public`: Recursos estáticos (imágenes, CSS, JS)
* `/routes`: Rutas y controladores de API
* `/controllers`: Lógica de negocio
* `/models`: Modelado de entidades y conexión BD
* `/views`: Interfaz de usuario (si aplica)

---

## 📈 Diseño de la Base de Datos

Modelo relacional con integridad referencial y normalización. Incluye:

👉 Gestión de usuarios y autenticación.
👉 Cuentas en soles y dólares.
👉 Transferencias internas y mediante Yape.
👉 Préstamos, tarjetas y pagos.
👉 Cola de atención y operaciones de ventanilla.
👉 Evaluación crediticia y calificación.

---

## 🧹 Módulos Desarrollados

👉 Registro/Login con seguridad básica.
👉 Visualización y gestión de saldos.
👉 Transferencias tradicionales y por Yape.
👉 Simulación de atención en ventanilla (colas).
👉 Solicitud y evaluación de créditos.
👉 Gestión de tarjetas de crédito.
👉 Histórico de operaciones y pagos.
👉 Panel de soporte básico.

---

## 🚀 Guía Completa de Instalación y Ejecución

**Requisitos previos:**

* Node.js
* MySQL o PostgreSQL
* Git
* Navegador actualizado

**Pasos:**

```bash
git clone <url_del_proyecto>
```

1. Crear base de datos y ejecutar los scripts SQL proporcionados.
2. Configurar conexión en `/config/db.js`.
3. Instalar dependencias:

```bash
npm install
```

4. Iniciar servidor:

```bash
npm start
```

5. Acceder vía navegador en:

```bash
http://localhost:3000
```

---

## 💻 Compatibilidad y Requisitos de Hardware

| Requisito      | Especificación Mínima |
| -------------- | --------------------- |
| Procesador     | Intel i3 o superior   |
| Memoria RAM    | 4 GB                  |
| Almacenamiento | 500 MB disponible     |
| Navegadores    | Chrome, Firefox, Edge |
| SO Compatible  | Windows, Linux, macOS |

---

## 📖 Manual de Usuario - Guía Práctica

* Iniciar sesión con un usuario registrado.
* Visualizar saldos y operaciones disponibles.
* Realizar transferencias entre cuentas o por Yape.
* Solicitar un préstamo o tarjeta de crédito.
* Acceder al historial de pagos y operaciones.
* Utilizar el sistema de atención por colas simuladas.

---

## 🔬 Manual Técnico

* Backend en Node.js y Express.
* Base de datos adaptable a MySQL o PostgreSQL.
* Arquitectura modular en controladores, rutas y modelos.
* Tecnologías web estándar para frontend.
* Documentación interna por cada módulo.

---

## 💲 Aspecto Económico

Solución de bajo costo, usando tecnologías gratuitas y de código abierto. Ideal para entornos académicos o simulaciones internas.

---

## 🗓️ Cronograma y Tiempos de Desarrollo

* **Semana 1-2:** Análisis, diseño de base de datos y mockups.
* **Semana 3-4:** Desarrollo de módulos backend.
* **Semana 5:** Implementación de frontend y conexión.
* **Semana 6:** Pruebas, documentación y entrega final.

---

## 👥 Equipo de Desarrollo

**Equipo N° 7** - Carrera Diseño y Desarrollo de Software
Curso: *Algoritmos y Programación en Python*
Guía Académico: *Camasca Macedo, Charles Dummar*

---

## 📜 Licencia y Uso del Proyecto

Proyecto de uso exclusivamente académico.
Prohibido su uso en ambientes productivos o con datos reales.
Código fuente disponible para estudio y prácticas.

---

## 🌿 Conclusiones Finales

Este simulador bancario permitió a los estudiantes integrar conocimientos clave de programación, estructuras de datos y diseño de software aplicados a un entorno financiero. Se destaca:

👉 Implementación de la teoría de colas en un entorno práctico.
👉 Simulación de procesos bancarios reales en formato modular.
👉 Reforzamiento de competencias técnicas con herramientas actuales.
👉 Importancia del trabajo colaborativo y metodologías ágiles.

🚨 El sistema es académico, no representa operaciones reales ni debe usarse en producción.

---
