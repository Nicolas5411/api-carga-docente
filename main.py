
import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

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

    # Aplicación web publicada en Netlify
    "https://cargadocente.netlify.app",
    "https://fastidious-kataifi-8f9bad.netlify.app",
    "https://effulgent-pixie-c5a88d.netlify.app/login",

    # Aplicación móvil Capacitor Android
    "https://localhost",
]

origins_env = os.getenv("ALLOWED_ORIGINS", "")

extra_origins = [
    origin.strip().rstrip("/")
    for origin in origins_env.split(",")
    if origin.strip()
]

origins = list(dict.fromkeys(
    ALLOWED_ORIGINS_DEFAULT + extra_origins
))

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
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
