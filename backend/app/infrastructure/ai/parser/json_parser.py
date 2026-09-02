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
        return json.loads(cleaned)