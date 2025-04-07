import uvicorn
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from backend.logger import logger
from backend.comparison_engine import router as comparison_router
from backend.report_generator import router as report_router
from dotenv import load_dotenv

app = FastAPI()
load_dotenv()
# ✅ Allow access only from the frontend
origins = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
]

# ✅ Adding CORS middleware TO routers
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,  # 🔥 allowed only
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ✅ Connecting routes
app.include_router(comparison_router, prefix="/api")
app.include_router(report_router, prefix="/api")

# ✅ Ping for checking
@app.get("/api/ping")
async def ping():
    return {"status": "ok"}

# ✅ Logs
@app.middleware("http")
async def log_requests(request: Request, call_next):
    print(f"⬅️ Request: {request.method} {request.url}")
    response = await call_next(request)
    print(f"➡️ Response: {response.status_code}")
    return response

logger.info("✅ Logger successfully imported in main.py!")


if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
