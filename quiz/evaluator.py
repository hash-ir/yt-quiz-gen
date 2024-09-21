difficulty_levels = ("Easy", "Medium", "Hard", "Expert")


def change_difficulty(current_difficulty: str, score: int):
    assert score in list(
        range(6)
    ), f"Quiz score must be in the range [0, 5], found {score}"
    assert (
        current_difficulty in difficulty_levels
    ), f"Difficulty level must be one of {difficulty_levels}, found {current_difficulty}"

    def inc_diff(diff: str):
        if difficulty_levels.index(diff) + 1 < 4:
            return difficulty_levels[difficulty_levels.index(diff) + 1]

        return "Expert"

    def dec_diff(diff: str):
        if difficulty_levels.index(diff) - 1 > 0:
            return difficulty_levels[difficulty_levels.index(diff) - 1]

        return "Easy"

    if score < 2:
        current_difficulty = dec_diff(current_difficulty)
    elif score >= 4:
        current_difficulty = inc_diff(current_difficulty)
    else:
        current_difficulty = current_difficulty

    return current_difficulty
