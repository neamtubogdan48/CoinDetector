import base64
import os
import cv2

from pathlib import Path
from fastapi import HTTPException, UploadFile

MAX_UPLOAD_BYTES = int(os.getenv("COIN_COUNTER_MAX_UPLOAD_BYTES", str(15 * 1024 * 1024)))


def save_upload_limited(file: UploadFile, work_dir: Path) -> Path:
    """Save uploaded file to disk with size limit"""
    # Determine file path with original extension or default to .jpg if missing
    suffix = Path(file.filename or "input.jpg").suffix or ".jpg"
    file_path = work_dir / f"input{suffix}"

    written_bytes = 0
    chunk_size = 1024 * 1024
    # Read and write the file in chunks to enforce size limit
    with file_path.open("wb") as out_file:
        while True:
            chunk = file.file.read(chunk_size)
            if not chunk:
                break
            written_bytes += len(chunk)
            # Check if the uploaded file exceeds the maximum allowed size
            if written_bytes > MAX_UPLOAD_BYTES:
                raise HTTPException(
                    status_code=413,
                    detail=f"Uploaded file is too large. Max allowed size is {MAX_UPLOAD_BYTES} bytes.",
                )
            out_file.write(chunk)

    return file_path

def encode_image_to_base64(image) -> str:
    """Encode OpenCV image to base64 string for API response"""
    ok, buffer = cv2.imencode(".jpg", image)
    if not ok:
        raise ValueError("Failed to encode output image")
    return base64.b64encode(buffer.tobytes()).decode("ascii")
