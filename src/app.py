from fastapi import FastAPI, HTTPException, Header, Depends, status, Request
from fastapi.responses import JSONResponse
from fastapi.security import HTTPBearer
from pydantic import BaseModel, Field
from typing import Optional
import time
from collections import defaultdict
from jose import jwt, JWTError
import strawberry
from strawberry.fastapi import GraphQLRouter
from strawberry.extensions import SchemaExtension

app = FastAPI(
    title="Servicio de Pedidos Endurecido - Bloque B",
    version="1.3.0"
)

# Configuración Criptográfica JWT
SECRET_KEY = "clave_secreta_de_prueba_laboratorio_masi_2026"
ALGORITHM = "HS256"

# ------------------------------------------------------------------------------
# RATE LIMITING EN MEMORIA (3 req / 10 seg)
# ------------------------------------------------------------------------------
RATE_LIMIT_DURATION = 10
RATE_LIMIT_REQUESTS = 3
request_history = defaultdict(list)

@app.middleware("http")
async def rate_limit_middleware(request: Request, call_next):
    client_ip = request.client.host if request.client else "127.0.0.1"
    user_key = request.headers.get("x-user-email", client_ip)
    
    current_time = time.time()
    request_history[user_key] = [t for t in request_history[user_key] if current_time - t < RATE_LIMIT_DURATION]
    
    if len(request_history[user_key]) >= RATE_LIMIT_REQUESTS:
        return JSONResponse(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            content={"detail": f"Cuota de peticiones excedida para {user_key}. Limite: {RATE_LIMIT_REQUESTS} solicitudes por cada 10 segundos."}
        )
    
    request_history[user_key].append(current_time)
    response = await call_next(request)
    return response

# ------------------------------------------------------------------------------
# BASE DE DATOS SINTÉTICA
# ------------------------------------------------------------------------------
USERS_DB = {
    "userA@test.com": {"role": "user", "name": "Usuario A"},
    "userB@test.com": {"role": "user", "name": "Usuario B"},
    "admin@test.com": {"role": "admin", "name": "Administrador"}
}

ORDERS_DB = {
    1: {"id": 1, "owner": "userA@test.com", "product_id": "PROD-100", "quantity": 2, "shipping_address": "Calle Principal 12-34 Zona 10"},
    2: {"id": 2, "owner": "userB@test.com", "product_id": "PROD-200", "quantity": 5, "shipping_address": "Avenida Reforma 5-67 Zona 9"}
}

class OrderCreateSchema(BaseModel):
    product_id: str = Field(..., min_length=1)
    quantity: int = Field(..., ge=1, le=10)
    shipping_address: str = Field(..., min_length=10, max_length=200)

class ProfileUpdateSchema(BaseModel):
    name: Optional[str] = Field(None, min_length=2, max_length=50)
    role: Optional[str] = None

class UserProfileResponseSchema(BaseModel):
    email: str
    name: str

@app.get("/api/test-tokens")
def get_test_tokens():
    now = int(time.time())
    payload_valid = {
        "sub": "userA@test.com",
        "iss": "http://localhost:8080/auth/realms/masi",
        "aud": "orders-api",
        "exp": now + 3600
    }
    valid_token = jwt.encode(payload_valid, SECRET_KEY, algorithm=ALGORITHM)
    invalid_token = jwt.encode(payload_valid, "clave_falsa_incorrecta_999", algorithm=ALGORITHM)
    return {
        "token_valido_figura12": f"Bearer {valid_token}",
        "token_alterado_figura13": f"Bearer {invalid_token}"
    }

def get_current_user(
    authorization: Optional[str] = Header(None, alias="Authorization"),
    x_user_email: Optional[str] = Header(None, alias="X-User-Email")
):
    email = None
    if authorization:
        if not authorization.startswith("Bearer "):
            raise HTTPException(status_code=401, detail="Formato invalido. Se requiere 'Bearer <token>'")
        token = authorization.split(" ", 1)[1].strip()
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM], options={"verify_aud": False, "verify_iss": False})
            email = payload.get("sub")
        except Exception:
            raise HTTPException(status_code=401, detail="Falla de validacion de JWT: Firma invalida, expirada o token alterado")
    elif x_user_email:
        email = x_user_email
    else:
        raise HTTPException(status_code=401, detail="Encabezado de autenticacion ausente")

    if email not in USERS_DB:
        raise HTTPException(status_code=401, detail=f"Usuario '{email}' no registrado")
    
    user = USERS_DB[email].copy()
    user["email"] = email
    return user

@app.get("/api/orders/{order_id}")
def get_order(order_id: int, current_user: dict = Depends(get_current_user)):
    order = ORDERS_DB.get(order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Pedido no encontrado")
    if order["owner"] != current_user["email"] and current_user["role"] != "admin":
        raise HTTPException(status_code=403, detail="Acceso denegado")
    return order

@app.get("/api/admin/audit")
def admin_audit(current_user: dict = Depends(get_current_user)):
    if current_user["role"] != "admin":
        raise HTTPException(status_code=403, detail="Acceso denegado: se requieren privilegios administrativos")
    return {"status": "success", "audit_log": "Registro de auditoria"}

@app.patch("/api/profile", response_model=UserProfileResponseSchema)
def update_profile(profile_data: ProfileUpdateSchema, current_user: dict = Depends(get_current_user)):
    if profile_data.role is not None:
        raise HTTPException(status_code=400, detail="No se permite modificar el rol")
    if profile_data.name:
        USERS_DB[current_user["email"]]["name"] = profile_data.name
    return UserProfileResponseSchema(email=current_user["email"], name=USERS_DB[current_user["email"]]["name"])

@app.post("/api/orders", status_code=201)
def create_order(order: OrderCreateSchema, current_user: dict = Depends(get_current_user)):
    new_id = len(ORDERS_DB) + 1
    new_order = {
        "id": new_id,
        "owner": current_user["email"],
        "product_id": order.product_id,
        "quantity": order.quantity,
        "shipping_address": order.shipping_address
    }
    ORDERS_DB[new_id] = new_order
    return new_order

# ------------------------------------------------------------------------------
# GRAPHQL CON MAPEADO EXACTO Y CONTROL DE PROFUNDIDAD MÁXIMA (= 3)
# ------------------------------------------------------------------------------
class DepthLimitExtension(SchemaExtension):
    def on_execute(self):
        execution_context = self.execution_context
        query = execution_context.query or ""
        
        # Conteo exacto de profundidad por anidamiento de llaves '{'
        max_depth = 0
        current_depth = 0
        for char in query:
            if char == '{':
                current_depth += 1
                if current_depth > max_depth:
                    max_depth = current_depth
            elif char == '}':
                current_depth = max(0, current_depth - 1)
        
        if max_depth > 2:
            raise HTTPException(
                status_code=400,
                detail=f"La consulta GraphQL excede la profundidad maxima permitida de 3 niveles. Profundidad detectada: {max_depth}."
            )

@strawberry.type
class UserGraphQLType:
    email: str
    name: str

@strawberry.type
class OrderGraphQLType:
    id: int
    product_id: str = strawberry.field(name="product_id")
    quantity: int
    user: Optional[UserGraphQLType] = None

@strawberry.type
class Query:
    @strawberry.field
    def orders(self, limit: int = 20) -> list[OrderGraphQLType]:
        effective_limit = min(limit, 20)
        items = list(ORDERS_DB.values())[:effective_limit]
        result = []
        for o in items:
            u_info = USERS_DB.get(o["owner"], {"name": "Usuario"})
            user_obj = UserGraphQLType(email=o["owner"], name=u_info["name"])
            result.append(OrderGraphQLType(
                id=o["id"],
                product_id=o["product_id"],
                quantity=o["quantity"],
                user=user_obj
            ))
        return result

schema = strawberry.Schema(query=Query, extensions=[DepthLimitExtension])
graphql_app = GraphQLRouter(schema)
app.include_router(graphql_app, prefix="/graphql")