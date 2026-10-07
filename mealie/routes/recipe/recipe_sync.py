from fastapi import APIRouter, HTTPException, status

from mealie.routes._base import BaseUserController, controller
from mealie.services.recipe.external_sync import push_recipe

router = APIRouter(prefix="/sync")


@controller(router)
class RecipeSyncController(BaseUserController):
    @router.post("/{slug}")
    def sync_one(self, slug: str):
        """Pushes a recipe to the external recipe service configured for this instance."""
        recipe = self.repos.recipes.get_one(slug, "slug")
        if recipe is None:
            raise HTTPException(status.HTTP_404_NOT_FOUND)

        return {"status": push_recipe(recipe, self.user)}
