from typing import List
from pydantic import BaseModel


class CoinValueSummary(BaseModel):
    # Summary of detected coins by denomination
    coin_value: int
    count: int
    subtotal_value: int

class AnalyzeResponse(BaseModel):
    # API output: denomination list, total count, total value, and annotated image.
    coin_summaries: List[CoinValueSummary]
    total_count: int
    total_value: int
    image_base64: str
