from fastapi import FastAPI

from .database import init_db
from .routers import cases, clients, insights, tasks

app = FastAPI(
    title="LexOffice AI",
    description=(
        "Plataforma inteligente para gestão de escritórios de advocacia, com automações e insights preditivos."
    ),
    version="0.1.0",
)


@app.on_event("startup")
def on_startup() -> None:
    init_db()


app.include_router(clients.router)
app.include_router(cases.router)
app.include_router(tasks.router)
app.include_router(insights.router)


@app.get("/")
def root() -> dict[str, str]:
    return {
        "message": "Bem-vindo ao LexOffice AI",
        "docs": "/docs",
        "insights": "/insights/dashboard",
    }
