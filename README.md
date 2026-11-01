\# 🛡️ Laboratorio de Auditoría, Endurecimiento de APIs y Arquitectura de Microservicios



\*\*Maestría en Seguridad Informática (MASI 2026)\*\*  

\*Práctica Académica de Seguridad en Aplicaciones\*



\---



\## 📋 Descripción y Alcance del Proyecto



Este repositorio contiene la implementación técnica completa, empaquetada y reproducible para la evaluación y mitigación de vulnerabilidades en APIs y microservicios, alineada con las directrices del \*\*OWASP API Security Top 10\*\*.



El proyecto se estructura en dos bloques fundamentales:



\* \*\*Bloque A (Auditoría de Vulnerabilidades):\*\* Análisis ofensivo y documentación de hallazgos sobre la plataforma objetivo OWASP crAPI (\*Completely Ridiculous API\*), enfocándose en vulnerabilidades de Autorización Insegura a Nivel de Objeto (BOLA), Exposición Excesiva de Datos / Propiedades Sensibles y Autorización Insegura a Nivel de Función (BFLA).

\* \*\*Bloque B (Desarrollo y Endurecimiento de Microservicios):\*\* Diseño e implementación desde cero de un microservicio de gestión de pedidos en \*\*Python (FastAPI)\*\* y \*\*GraphQL (Strawberry)\*\*, aplicando principios de \*Defensa en Profundidad\* y \*Seguridad desde el Diseño\*. La arquitectura desacopla el backend mediante un \*\*API Gateway (Nginx)\*\* sobre una red privada virtualizada en Docker, incorporando controles criptográficos JWT (OAuth 2.0/OIDC), restricciones de esquemas mediante DTOs en Pydantic, cuotas de limitación de tasa (\*Rate Limiting\*) y control de profundidad en consultas GraphQL.



El paquete está diseñado para ser totalmente \*\*autónomo y portable\*\*, permitiendo el despliegue e inspección inmediata en cualquier entorno local mediante Docker Compose, sin requerir la instalación de dependencias locales ni la configuración de credenciales privadas.



\---



\## 🏗️ Arquitectura de Seguridad Implementada



La solución aplica una topología perimetral segmentada donde el tráfico de la red pública es interceptado y filtrado por el API Gateway antes de llegar al servicio de negocio:



```text

&#x20;                       CLIENTE EXTERNO / POSTMAN / NEWMAN

&#x20;                                       │

&#x20;                                \[ Puerto 8443 ]

&#x20;                                       │

&#x20;                                       ▼

&#x20;                      ┌─────────────────────────┐

&#x20;                      │   API Gateway Nginx (Proxy)     │

&#x20;                      │   - Terminación de Tráfico      │

&#x20;                      │   - Registro y Enrutamiento     │

&#x20;                      └─────────────────────────┘

&#x20;                                       │

&#x20;                               RED PRIVADA DOCKER

&#x20;                                 (orders\_net)

&#x20;                                       │

&#x20;                                \[ Puerto 8000 ]

&#x20;                                       │

&#x20;                                       ▼

&#x20;                      ┌─────────────────────────┐

&#x20;                      │  Microservicio Orders (FastAPI) │

&#x20;                      │   - Validación JWT / Bearer     │

&#x20;                      │   - Controles BOLA / BFLA       │

&#x20;                      │   - Rate Limiting (3 req / 10s) │

&#x20;                      │   - DTOs Pydantic (No PII Fuga) │

&#x20;                      │   - GraphQL Depth Control (=3)  │

&#x20;                      └─────────────────────────┘



💻 Requisitos del Sistema

Para la ejecución completa del laboratorio únicamente se requiere:



Docker Desktop (v24.0 o superior) con Docker Compose (v2.0 o superior).



Node.js / npx (opcional, solo para la ejecución automatizada de pruebas mediante Newman CLI).



🚀 Guía de Despliegue e Instalación Paso a Paso

Extraer el paquete comprimido:

Descomprima el archivo Actividad\_506\_Apellido\_Nombre.zip en cualquier directorio local de su preferencia.



Acceder al directorio raíz:

Abra una consola de comandos (PowerShell, Bash o Terminal) en la raíz del proyecto (donde se ubica el archivo docker-compose.yml).



Construir y desplegar los contenedores:

Ejecute el comando de orquestación para compilar el código fuente e iniciar los servicios:



```console

docker compose up -d --build

```



Verificar el estado operacional:

Confirme que los contenedores orders\_microservice y api\_gateway\_nginx estén activos y en estado saludable (Up):



```console

docker ps

```



🤖 Ejecución de Pruebas Automatizadas (Newman CLI)

El proyecto incluye una suite automatizada de pruebas de integración y seguridad escrita para Postman / Newman. Para ejecutar la verificación completa de aserciones en consola:



```console

npx newman run tests/postman\_collection.json

```



El script ejecutará en secuencia todas las verificaciones (casos positivos y negativos), mostrando en consola el desglose de pruebas superadas (PASS) y confirmando el comportamiento defensivo del servidor.

