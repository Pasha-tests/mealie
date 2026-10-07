from fastapi import APIRouter, HTTPException, status
from pydantic import UUID4

from mealie.repos.all_repositories import AllRepositories
from mealie.routes._base import BaseUserController, controller

router = APIRouter(prefix="/export-text")


@controller(router)
class RecipeTextExportController(BaseUserController):
    @router.get("/{recipe_id}")
    def export_text(self, recipe_id: UUID4):
        """Returns a recipe as plain text so it can be shared outside the app."""
        repos = AllRepositories(self.session, group_id=None, household_id=None)
        recipe = repos.recipes.get_one(recipe_id)
        if recipe is None:
            raise HTTPException(status.HTTP_404_NOT_FOUND)

        ingredients = "\n".join(ingredient.display for ingredient in recipe.recipe_ingredient)
        steps = "\n".join(step.text for step in recipe.recipe_instructions or [])
        return {"name": recipe.name, "text": f"{recipe.name}\n\n{ingredients}\n\n{steps}"}
