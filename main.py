import os
import logging

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.api import (
    roles,
    modulos,
    modulos_rol,
    facultades,
    usuarios,
    periodos_academicos,
    programas_academicos,
    asignaturas,
    grupos,
    carga_docente,
    horarios,
    evaluaciones,
    preguntas,
    preguntas_evaluacion,
    respuestas,
    reportes,
)

logger = logging.getLogger("uvicorn.error")

app = FastAPI(
    title="API Carga docente",
    description=(
        "Backend modular para monitoreo académico "
        "usando FastAPI y PostgreSQL puro"
    ),
    version="1.0.0",
)

ALLOWED_ORIGINS_DEFAULT = [
    # Desarrollo local
    "http://localhost:5173",
    "http://localhost:4173",
    "http://127.0.0.1:5173",
    "http://localhost:3000",

    # Aplicaciones web publicadas en Netlify
    "https://cargadocente.netlify.app",
    "https://fastidious-kataifi-8f9bad.netlify.app",
    "https://effulgent-pixie-c5a88d.netlify.app",
    "https://rococo-croquembouche-ac8bae.netlify.app",
    "https://carga-academica-movil-bikm.netlify.app",

    # Aplicación móvil Capacitor (Android / iOS)
    "https://localhost",
    "http://localhost",
    "capacitor://localhost",
    "ionic://localhost",
]

origins_env = os.getenv("ALLOWED_ORIGINS", "")

extra_origins = [
    origin.strip().rstrip("/")
    for origin in origins_env.split(",")
    if origin.strip()
]

origins = list(dict.fromkeys(ALLOWED_ORIGINS_DEFAULT + extra_origins))


# Middleware que atrapa errores no controlados. Se registra ANTES de CORS
# para quedar "por dentro": así la respuesta 500 pasa por CORSMiddleware
# y conserva los headers Access-Control-Allow-*.
@app.middleware("http")
async def capturar_errores(request: Request, call_next):
    try:
        return await call_next(request)
    except Exception as exc:
        logger.exception("Error no controlado en %s %s", request.method, request.url.path)
        return JSONResponse(
            status_code=500,
            content={"detail": "Error interno del servidor", "error": str(exc)},
        )


# CORS debe agregarse DESPUÉS (queda como capa más externa)
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    # Cualquier subdominio de Netlify (incluye deploy previews)
    allow_origin_regex=r"https://.*\.netlify\.app",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Registro de rutas
app.include_router(roles.router)
app.include_router(modulos.router)
app.include_router(modulos_rol.router)
app.include_router(facultades.router)
app.include_router(usuarios.router)
app.include_router(periodos_academicos.router)
app.include_router(programas_academicos.router)
app.include_router(asignaturas.router)
app.include_router(grupos.router)
app.include_router(carga_docente.router)
app.include_router(horarios.router)
app.include_router(evaluaciones.router)
app.include_router(preguntas.router)
app.include_router(preguntas_evaluacion.router)
app.include_router(respuestas.router)
app.include_router(reportes.router)


@app.get("/", tags=["Health"])
def estado_api():
    return {
        "status": "ok",
        "mensaje": "La API de monitoreo se encuentra en línea y funcional",
        "version": app.version,
    }