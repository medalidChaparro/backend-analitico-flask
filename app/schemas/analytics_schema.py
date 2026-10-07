from dataclasses import dataclass
from typing import Any, List


@dataclass
class IndicatorResponse:
    indicator: str
    title: str
    chart_type: str
    data: Any
    sources: List[str]