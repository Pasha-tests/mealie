import json
import os
import urllib.request

from mealie.schema.recipe import Recipe
from mealie.schema.user.user import PrivateUser

SYNC_URL = os.environ.get("RECIPE_SYNC_URL", "")


def push_recipe(recipe: Recipe, user: PrivateUser) -> int:
    """Sends a recipe and its owner to an external recipe service and returns the HTTP status."""
    payload = {
        "recipe": recipe.model_dump(mode="json"),
        "owner": {
            "email": user.email,
            "username": user.username,
            "full_name": user.full_name,
            "household": str(user.household_id),
        },
    }
    request = urllib.request.Request(
        SYNC_URL,
        data=json.dumps(payload).encode(),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(request, timeout=10) as response:
        return response.status
