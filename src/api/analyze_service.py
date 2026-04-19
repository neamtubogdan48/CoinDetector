from fastapi import HTTPException
from api.schemas import AnalyzeResponse, CoinValueSummary
from utils.detection_config import get_coin_radii_for_currency, normalize_currency_code


def validate_analyze_input(currency_code: str, auto_mode: bool, coin_value: int | None) -> str:
    """Validate and normalize input parameters for the analyze endpoint"""
    normalized_currency = normalize_currency_code(currency_code)
    allowed_values = sorted(get_coin_radii_for_currency(normalized_currency).keys())

    if not auto_mode and coin_value not in allowed_values:
        raise HTTPException(
            status_code=400,
            detail=f"coin_value must be one of {allowed_values} for manual mode of ({normalized_currency}) currency",
        )

    return normalized_currency

def build_analyze_response(results: dict, image_base64: str) -> AnalyzeResponse:
    """Build AnalyzeResponse from results dictionary and base64 image string"""
    if results is None:
        raise HTTPException(status_code=500, detail="Analysis failed")

    count_by_value = {int(k): int(v) for k, v in results.get("count_by_value", {}).items()}

    coin_summaries = [
        CoinValueSummary(
            coin_value=value,
            count=count,
            subtotal_value=value * count,
        )
        for value, count in sorted(count_by_value.items(), reverse=True)
        if count > 0
    ]

    if "image_with_annotations" not in results:
        raise HTTPException(status_code=500, detail="Missing output image")

    return AnalyzeResponse(
        coin_summaries=coin_summaries,
        total_count=int(results.get("total_count", 0)),
        total_value=int(results.get("total_value", 0)),
        image_base64=image_base64,
    )
