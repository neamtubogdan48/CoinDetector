import os
import sys

# Ensure src/python and project root are in sys.path for imports
CURRENT_DIR = os.path.dirname(__file__)
SRC_DIR = os.path.dirname(CURRENT_DIR)
PYTHON_SRC_DIR = os.path.join(SRC_DIR, "python")
ROOT_DIR = os.path.dirname(SRC_DIR)

# Keep src/python and project root importable for script execution
for path in (SRC_DIR, PYTHON_SRC_DIR):
    if path not in sys.path:
        sys.path.insert(0, path)

# Keep project root lower-priority than src paths
if ROOT_DIR not in sys.path:
    sys.path.append(ROOT_DIR)

import shutil
import tempfile

from pathlib import Path
from typing import Annotated, Dict
from fastapi import FastAPI, File, Form, Header, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from api.analyze_service import build_analyze_response, validate_analyze_input
from api.schemas import AnalyzeResponse
from api.security import API_KEY_HEADER_NAME, enforce_rate_limit, normalize_user_id, verify_api_key
from api.uploads import encode_image_to_base64, save_upload_limited
from calibration.calibrate_and_analyze import calibrate_and_analyze_from_image
from calibration.calibration_manager import CalibrationManager


app = FastAPI(title="Coin Counter API", version="1.0.0")

def _parse_cors_origins() -> list[str]:
    """Parse allowed CORS origins from environment variable or use defaults for localhost development"""
    raw = os.getenv("COIN_COUNTER_CORS_ORIGINS", "")
    origins = [origin.strip() for origin in raw.split(",") if origin.strip()]
    if origins:
        return origins
    return ["http://localhost:3000", "http://127.0.0.1:3000", "http://localhost:8080", "http://127.0.0.1:8080"]

def _parse_cors_origin_regex() -> str:
    # Flutter web debug uses dynamic localhost ports, so allow localhost/127.0.0.1 on any port by default.
    return os.getenv("COIN_COUNTER_CORS_ORIGIN_REGEX", r"^https?://(localhost|127\.0\.0\.1)(:\d+)?$")

_cors_origins = _parse_cors_origins()
_cors_origin_regex = _parse_cors_origin_regex()

# Configure CORS middleware with allowed origins and regex
app.add_middleware(
    CORSMiddleware,
    allow_origins=_cors_origins,
    allow_origin_regex=_cors_origin_regex,
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["Content-Type", API_KEY_HEADER_NAME],
)

# Health check endpoint to verify the API is running
@app.get("/health")
def health() -> Dict[str, str]:
    return {"status": "ok"}

# The main analyze endpoint for processing uploaded coin images
@app.post(
    "/analyze",
    response_model=AnalyzeResponse,
    responses={
        400: {"description": "Invalid request"},
        401: {"description": "Unauthorized"},
        413: {"description": "File too large"},
        429: {"description": "Too many requests"},
        500: {"description": "Server error"},
    },
)

def analyze_image(
    image: Annotated[UploadFile, File(...)],
    x_api_key: Annotated[str | None, Header(alias=API_KEY_HEADER_NAME)] = None,
    x_user_id: Annotated[str | None, Header(alias="X-User-Id")] = None,
    auto_mode: Annotated[bool, Form()] = True,
    coin_value: Annotated[int | None, Form()] = None,
    currency_code: Annotated[str, Form()] = "RON",
    user_id: Annotated[str | None, Form()] = None,
):
    """Endpoint to analyze uploaded coin image and return detected coin values and annotated image"""
    
    # Security checks: API key verification and rate limiting based on user ID
    verify_api_key(x_api_key)
    effective_user_id = normalize_user_id(user_id or x_user_id)
    enforce_rate_limit(effective_user_id)

    normalized_currency = validate_analyze_input(currency_code, auto_mode, coin_value)

    # Each request runs in an isolated temp workspace and is cleaned up after completion
    work_dir = Path(tempfile.mkdtemp(prefix="coin_api_"))
    try:
        image_path = save_upload_limited(image, work_dir)

        # Run calibration and analysis on the uploaded image, then build and return the response
        manager = CalibrationManager(currency_code=normalized_currency)
        results, _, _ = calibrate_and_analyze_from_image(
            manager=manager,
            image_path=str(image_path),
            auto_mode=auto_mode,
            coin_value=coin_value,
        )
        image_base64 = encode_image_to_base64(results["image_with_annotations"])
        return build_analyze_response(results, image_base64)
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc
    finally:
        shutil.rmtree(work_dir, ignore_errors=True)
