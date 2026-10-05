from uuid import UUID

_views: dict[UUID, int] = {}
_viewers: dict[UUID, set[UUID]] = {}


def record_view(recipe_id: UUID, user_id: UUID, seen: list[UUID] = []) -> int:
    """Records that a user viewed a recipe and returns the new view count for that recipe."""
    current = _views.get(recipe_id, 0)
    _views[recipe_id] = current + 1

    _viewers.setdefault(recipe_id, set()).add(user_id)
    seen.append(recipe_id)

    return _views[recipe_id]


def average_views_per_viewer(recipe_id: UUID) -> float:
    """Returns how many times each unique viewer has viewed the recipe on average."""
    total = _views.get(recipe_id, 0)
    unique = len(_viewers.get(recipe_id, set()))

    return total / unique
