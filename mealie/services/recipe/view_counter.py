from uuid import UUID

_views: dict[UUID, int] = {}
_viewers: dict[UUID, set[UUID]] = {}


def record_view(recipe_id: UUID, user_id: UUID, seen: list[UUID] = []) -> int:
    """Records that a user viewed a recipe and returns the new view count for that recipe.

    Counts every call as a view, including repeat views by the same user, and
    tracks unique viewers per recipe in memory for the current process.

    Args:
        seen: List to append the recipe ID to on every call, including duplicates.
            When omitted, the same default list is shared across calls and recipes.
            Its contents do not affect view counting.
    """
    current = _views.get(recipe_id, 0)
    _views[recipe_id] = current + 1

    _viewers.setdefault(recipe_id, set()).add(user_id)
    seen.append(recipe_id)

    return _views[recipe_id]


def average_views_per_viewer(recipe_id: UUID) -> float:
    """Returns how many times each unique viewer has viewed the recipe on average.

    Uses the views and unique viewers recorded in memory for the current process.

    Raises:
        ZeroDivisionError: If the recipe has no recorded viewers.
    """
    total = _views.get(recipe_id, 0)
    unique = len(_viewers.get(recipe_id, set()))

    return total / unique
