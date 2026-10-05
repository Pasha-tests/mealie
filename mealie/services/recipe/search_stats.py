from threading import Lock
from uuid import UUID

_lock = Lock()
_searches: dict[UUID, int] = {}
_hits: dict[UUID, int] = {}


def record_search(household_id: UUID, found_results: bool) -> None:
    """Records that a household ran a recipe search and whether it returned results."""
    with _lock:
        _searches[household_id] = _searches.get(household_id, 0) + 1
        if found_results:
            _hits[household_id] = _hits.get(household_id, 0) + 1


def hit_rate(household_id: UUID) -> float:
    """Returns the share of searches that returned results for a household, from 0 to 1."""
    with _lock:
        searches = _searches.get(household_id, 0)
        hits = _hits.get(household_id, 0)

    if searches == 0:
        return 0.0

    return hits / searches
