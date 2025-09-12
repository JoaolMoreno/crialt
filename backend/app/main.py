from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware

from .api.router import api_router
from .core.config import settings

app = FastAPI(
    title="Crialt Arquitetura API",
    openapi_url=f"{settings.API_V1_STR}/openapi.json"
)

# Set all CORS enabled origins
if settings.BACKEND_CORS_ORIGINS:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[str(origin) for origin in settings.BACKEND_CORS_ORIGINS],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

app.include_router(api_router, prefix=settings.API_V1_STR)

@app.get("/")
def read_root():
    return {"message": "Welcome to Crialt Arquitetura API"}

if __name__ == "__main__":
    # sys.path.append(os.path.abspath(os.path.dirname(__file__) + "/.."))
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

