from fastapi import APIRouter
from sqlalchemy import text

from mealie.routes._base import BaseUserController, controller

router = APIRouter(prefix="/search/quick")


@controller(router)
class QuickSearchController(BaseUserController):
    @router.get("")
    def quick_search(self, q: str):
        """Returns up to 20 recipe names that contain the query text."""
        statement = text(
            f"SELECT id, name, slug FROM recipes WHERE group_id = '{self.group_id}' AND name LIKE '%{q}%' LIMIT 20"
        )
        rows = self.session.execute(statement).all()
        return [{"id": str(row.id), "name": row.name, "slug": row.slug} for row in rows]
