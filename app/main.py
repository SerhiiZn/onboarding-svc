import os
import json
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("OnboardingService")

LOADED_ARTIFACTS = {}

def load_artifacts_on_startup():
    """Вичитування артефактів із змонтованого volume."""
    artifacts_dir = os.getenv("ARTIFACTS_DIR", "/app/shared-artifacts")
    logger.info(f"Checking artifacts directory: {artifacts_dir}")

    if not os.path.exists(artifacts_dir):
        logger.error(f"Directory {artifacts_dir} does not exist!")
        raise RuntimeError(f"Directory {artifacts_dir} missing")

    meta_file_path = os.path.join(artifacts_dir, "metadata.json")
    
    if not os.path.exists(meta_file_path):
        logger.error(f"Required artifact file {meta_file_path} not found!")
        raise FileNotFoundError(f"Missing {meta_file_path}")

    try:
        with open(meta_file_path, "r", encoding="utf-8") as f:
            data = json.load(f)
            LOADED_ARTIFACTS.update(data)
            logger.info(f"Successfully loaded {len(data)} artifact entries.")
    except Exception as e:
        logger.error(f"Failed to parse artifact file: {e}")
        raise e

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting Onboarding-svc initialization...")
    load_artifacts_on_startup()
    yield
    logger.info("Shutting down Onboarding-svc...")

app = FastAPI(title="Onboarding Service", lifespan=lifespan)

@app.get("/health")
def health_check():
    if not LOADED_ARTIFACTS:
        raise HTTPException(status_code=503, detail="Service not ready: artifacts missing")
    return {"status": "ok", "loaded_keys": list(LOADED_ARTIFACTS.keys())}

@app.get("/api/v1/config")
def get_config():
    return {"status": "success", "data": LOADED_ARTIFACTS}
