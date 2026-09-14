from __future__ import annotations

import json
import re
from typing import Any


class JSONParser:
    def parse(self, text: str) -> dict[str, Any]:
        cleaned = text.strip()
        cleaned = re.sub(r"^```(?:json)?", "", cleaned)
        cleaned = re.sub(r"```$", "", cleaned)
        cleaned = cleaned.strip()
        try:
            return json.loads(cleaned)
        except json.JSONDecodeError as exc:
            raise RuntimeError(
                "The AI model's response was not valid JSON (it may have been cut off). "
                "Try again, or request fewer questions."
            ) from exc