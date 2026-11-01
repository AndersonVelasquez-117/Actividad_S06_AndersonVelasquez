\# Resumen de Hallazgos y Remediaciones



\## 1. Exposición Indebida de Propiedades

\- \*\*Endpoint:\*\* `GET /identity/api/v2/vehicle/vehicles`

\- \*\*Condición Observada:\*\* Retorno del campo confidencial `pincode` en la respuesta JSON.

\- \*\*Impacto:\*\* Fuga de credenciales internas de seguridad.

\- \*\*Corrección Aplicada:\*\* Filtrado mediante Pydantic DTOs en el microservicio FastAPI.



\## 2. Broken Object Level Authorization (BOLA)

\- \*\*Endpoint:\*\* `GET /identity/api/v2/vehicle/{id}/location` y `GET /api/orders/{id}`

\- \*\*Condición Observada:\*\* Permitió consultar recursos pertenencia de terceros manipulando el ID.

\- \*\*Impacto:\*\* Acceso no autorizado a datos de otros usuarios.

\- \*\*Corrección Aplicada:\*\* Verificación estricta de propiedad en el servidor (`order\['owner'] == current\_user\['email']`).



\## 3. Broken Function Level Authorization (BFLA)

\- \*\*Endpoint:\*\* `DELETE /identity/api/v2/user/videos/{id}` y `GET /api/admin/audit`

\- \*\*Condición Observada:\*\* Usuarios comunes pudieron invocar funciones administrativas.

\- \*\*Impacto:\*\* Ejecución no autorizada de operaciones restringidas.

\- \*\*Corrección Aplicada:\*\* Validación explícita del rol `admin` en el controlador antes de ejecutar la acción.

