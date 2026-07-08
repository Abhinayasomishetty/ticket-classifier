from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from db.database import engine, Base
from schemas.api.routes import auth, tickets, documents
from core.config import get_settings
from core.metrics import setup_metrics


settings = get_settings()

# Create tables
Base.metadata.create_all(bind=engine)

# Initialize FastAPI app
app = FastAPI(
    title=settings.APP_NAME,
    description="AI-Powered Ticket Classification System",
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc",
)


@app.middleware("http")
async def log_requests(request, call_next):
    print(f"REQUEST -> {request.method} {request.url.path}")
    response = await call_next(request)
    print(f"STATUS -> {response.status_code}")
    return response


# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Restrict in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router)
app.include_router(tickets.router)
app.include_router(documents.router)


@app.get("/", tags=["Health"])
async def root():
    # Health check endpoint.
    return {"status": "healthy", "service": settings.APP_NAME, "version": "0.1.0"}


@app.get("/health/detailed", tags=["Health"])
async def detailed_health():
    # Detailed health check including Ollama status.
    import httpx

    ollama_status = "unhealthy"
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.get(f"{settings.OLLAMA_BASE_URL}/api/tags")
            if response.status_code == 200:
                models = [m["name"] for m in response.json().get("models", [])]
                ollama_status = "healthy"
                ollama_models = models
            else:
                ollama_models = []
    except Exception:
        ollama_models = []

    return {
        "status": "healthy",
        "components": {
            "api": "healthy",
            "ollama": ollama_status,
            "ollama_models": ollama_models,
            "database": "healthy",  # Would add actual DB check
        },
    }


setup_metrics(app)


@app.on_event("startup")
async def startup_event():
    print(f" Starting {settings.APP_NAME} API (Production Build)...")


@app.get("/", tags=["Health"])
async def root():
    return {"status": "healthy", "service": settings.APP_NAME, "version": "0.5.0"}
