# Coin Detector

A cross-platform coin detection and counting system combining computer vision, a RESTful API, and mobile client interfaces. Users capture coin images via a Flutter mobile application, which communicates with a FastAPI Python backend that employs OpenCV and ORB feature matching to detect, classify, and tally coins. A separate PyQt6 desktop GUI provides interactive debugging and visualization of the computer vision pipeline.

## Requirements

- Python 3.10+
- Flutter SDK (for mobile/web client)

Install Python dependencies:

```bash
pip install -r requirements.txt
```

## 1) Desktop GUI (PyQt6)

Run the desktop app:

```bash
python src/python/gui/gui.py
```

The GUI provides:

- **Upload File**: Drag & drop or browse to select an image
- **Analyse**: Run coin detection on the selected image
- **Calibrate**: Calibrate using a reference coin (select value from dropdown)
- **Reference**: Save ORB reference image for a coin type (select value from dropdown)
- **Debug**: Enable detailed logging and debug output

### Key Features

- **Multi-Currency Detection**: Supports a wide range of international currencies, including RON, EUR, USD, and GBP denominations.
- **Real-size Calibration**: Uses precise physical dimensions (mm) for each currency to ensure accurate detection and classification.
- **Real-size Calibration**: Uses actual Romanian coin dimensions (mm) for accurate detection
- **ORB Reference Matching**: Compares detected coins with reference images using ORB descriptors
- **Pixels↔Millimeters Conversion**: Automatic conversion between pixel measurements and real dimensions
- **Scale-independent Detection**: Works accurately regardless of photo distance/height
- **Three-criteria Validation**: ORB matching, overlap checking, and distance analysis
- **Radius Pre-filtering**: Circles are filtered by radius range before validation to improve efficiency
- **Debug Mode**: Comprehensive step-by-step analysis with visual debugging
- **Smart Calibration System**: Single-photo calibration for perfect scale detection
- **Reference Image Management**: Save and manage ORB reference images for each coin type
- **Graphical User Interface**: PyQt6-based GUI for easy interaction
- **Optimized Performance**: Auto-adjusts parameters based on image resolution

## 2) API (FastAPI)

Run the API server:

```bash
uvicorn src.api.app:app --reload --host 0.0.0.0 --port 8000 --env-file .env
```

The API exposes the following endpoints:

- **`POST /analyze`**: Accepts a multipart form containing an image file and analysis parameters. Returns detected coin summaries, aggregate totals, and a base64-encoded annotated image. Requires authentication via `X-API-Key` header.
- **`GET /health`**: Lightweight health check endpoint returning `{"status": "ok"}`.

### Key Features

- **Computer Vision Pipeline**: Integrates the full detection stack - Hough circle detection, ORB feature matching, calibration, radius-based classification, and image annotation - as a synchronous request-response service.
- **API Key Authentication**: All `/analyze` requests require a valid API key transmitted via the `X-API-Key` header. Verification uses constant-time comparison (`hmac.compare_digest`). The key is loaded from the `COIN_COUNTER_API_KEY` environment variable at module import time; the server fails at startup if it is unset.
- **Per-User Rate Limiting**: In-memory sliding-window rate limiter keyed by `user_id` (extracted from the form field or `X-User-Id` header). Configurable interval via `COIN_COUNTER_RATE_LIMIT_SECONDS` (default: 5 seconds). Returns HTTP 429 with a `Retry-After` header when the limit is exceeded. Thread-safe via `threading.Lock`.
- **File Size Enforcement**: Uploaded images are limited to a configurable maximum via `COIN_COUNTER_MAX_UPLOAD_BYTES` (default: 15 MB). Enforced during chunked file read; returns HTTP 413 if exceeded.
- **CORS Configuration**: Supports static origin lists (`COIN_COUNTER_CORS_ORIGINS`) and dynamic origin regex matching (`COIN_COUNTER_CORS_ORIGIN_REGEX`). Default configuration permits requests from localhost on common development ports and any localhost-origin Flutter web debug instance.
- **Structured Response Schema**: Returns an `AnalyzeResponse` JSON payload containing a list of per-denomination `CoinValueSummary` objects (value, count, subtotal), aggregate `total_count` and `total_value`, and a base64-encoded JPEG annotated image.
- **Temporary Workspace Isolation**: Each request creates an isolated temporary directory (`tempfile.mkdtemp`) for file processing, which is recursively removed in the `finally` block after response delivery.
- **Input Validation**: Normalizes currency codes, validates coin denominations against the currency's allowed set, and returns descriptive HTTP 400 error messages for invalid parameters.
- **Standardized Error Handling**: Returns HTTP 400 for invalid input, 401 for authentication failures, 413 for oversized uploads, 429 for rate limiting, and 500 for unexpected server errors.

## 3) Flutter App (mobile/web)

Project folder: `src/flutter_coin_detector`

Run the Flutter application:

```bash
cd src/flutter_coin_detector
flutter pub get
flutter run
```

To configure the API key at build time:

```bash
flutter run -d <device_id> --dart-define=COIN_COUNTER_API_KEY=super-secret-key
```

The application provides:

- **Image Capture & Upload**: Select images from the device gallery or capture new photos via camera. Images are transmitted to the backend as multipart form data.
- **Analysis Results**: Displays detected coin summaries (denomination, count, subtotal), aggregate total count, and total value. The annotated image returned by the backend is rendered inline.
- **Multi-Photo Accumulation ("Add More")**: Successive image analyses are merged into a cumulative session. Counts and values are aggregated across all batches within a single scan session.
- **Scan History**: Past analysis sessions are persisted locally in a Sembast NoSQL database. Users can review past results, delete individual records, or clear the entire history.
- **Currency Selection**: Supports four currencies - RON, EUR, USD, GBP - with denomination-appropriate labeling and value formatting (e.g., "1 leu and 50 bani").
- **Calibration Mode Toggle**: Switch between auto-calibration (backend determines scale from multiple detected coins) and manual calibration (user specifies a known coin denomination).
- **Dark / Light / System Theme**: Three theme modes selectable via the settings screen. Selection is persisted across sessions via SharedPreferences. Both themes use Material 3 with a custom 35-slot color palette.

## Example Photos

### Android App Analysis - Multi-Photo Accumulation, Light & Dark Themes, Scan History

<table>
	<tr>
		<td align="center"><img src="img/examples/exampleFlutter1.png" alt="Flutter demo 1" width="215" /></td>
		<td align="center"><img src="img/examples/exampleFlutter2.png" alt="Flutter demo 2" width="215" /></td>
		<td align="center"><img src="img/examples/exampleFlutter3.png" alt="Flutter demo 3" width="215" /></td>
	</tr>
	<tr>
		<td align="center" colspan="3">
			<img src="img/examples/exampleFlutter4.png" alt="Flutter demo 4" width="215" />
			<img src="img/examples/exampleFlutter5.png" alt="Flutter demo 5" width="215" />
		</td>
	</tr>
	<tr>
		<td align="center" colspan="3">
			<img src="img/examples/exampleFlutter6.png" alt="Flutter demo 6" width="215" />
			<img src="img/examples/exampleFlutter7.png" alt="Flutter demo 6" width="215" />
		</td>
	</tr>
</table>

### Desktop GUI - Debug Analysis
<p align="center">
	<img src="img/examples/exampleGUI.png" alt="GUI analysis demo" width="520" />
</p>
