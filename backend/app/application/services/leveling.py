from __future__ import annotations

MAX_LEVEL = 4
VALIDATION_PASS_THRESHOLD = 80

POINTS_PER_CORRECT_ANSWER = 10
VALIDATION_PASS_BONUS_POINTS = 50


class LevelingService:
    """Central place for the placement/points/leveling formulas.

    Business rules (docs/BUSINESS_RULES.md): a placement score of 0-30 maps
    to level 1, 31-60 to level 2, 61-80 to level 3, 81-100 to level 4. A
    student advances past their current level only by scoring at least 80%
    on that level's validation test.
    """

    @staticmethod
    def assign_level_from_score(score: int) -> int:
        if score <= 30:
            return 1
        if score <= 60:
            return 2
        if score <= 80:
            return 3
        return 4

    @staticmethod
    def points_for_quiz(correct: int, total: int) -> int:
        if total <= 0:
            return 0
        return correct * POINTS_PER_CORRECT_ANSWER

    @staticmethod
    def validation_pass_bonus_points() -> int:
        return VALIDATION_PASS_BONUS_POINTS

    @staticmethod
    def is_validation_pass(score: int | None) -> bool:
        return score is not None and score >= VALIDATION_PASS_THRESHOLD

    @staticmethod
    def next_level(current_level: int) -> int:
        return min(current_level + 1, MAX_LEVEL)
