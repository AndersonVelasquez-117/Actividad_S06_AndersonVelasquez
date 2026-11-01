\# Relación del Laboratorio con el Incidente Optus (2022)



\## Matriz de Análisis Comparativo



1\. \*\*Exposición de datos personales:\*\* El incidente de Optus derivó de endpoints expuestos que devolvían datos sensibles sin filtrar. En el laboratorio, se previno mediante DTOs en FastAPI que omiten secretos y notas privadas.

2\. \*\*Enumeración de objetos (BOLA):\*\* Optus sufrió acceso no autorizado por manipulación de identificadores. En el laboratorio, se aplicó verificación de propiedad en el servidor para retornar `HTTP 403 Forbidden` ante intentos de acceso cruzado.

3\. \*\*Ausencia de Autenticación:\*\* Se protegió la API exigiendo tokens JWT válidos firmados con criptografía `HS256` y validación de emisor/audiencia.

4\. \*\*Tráfico Masivo Desmedido:\*\* Se configuró un middleware de Rate Limiting que devuelve `HTTP 429 Too Many Requests` al superar la cuota de peticiones.

