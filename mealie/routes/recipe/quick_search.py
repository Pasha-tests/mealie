from fastapi import APIRouter
from sqlalchemy import text

from mealie.routes._base import BaseUserController, controller

router = APIRouter(prefix="/search/quick")


@controller(router)
class QuickSearchController(BaseUserController):
    @router.get("")
    def quick_search(self, q: str):
        """Returns up to 20 recipe names that contain the query text."""
        statement = text("SELECT id, name, slug FROM recipes WHERE group_id = :group_id AND name LIKE :pattern LIMIT 20")
        rows = self.session.execute(statement, {"group_id": str(self.group_id), "pattern": f"%{q}%"}).all()
        return [{"id": str(row.id), "name": row.name, "slug": row.slug} for row in rows]
