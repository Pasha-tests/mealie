from fastapi import APIRouter

from . import bulk_actions, comments, exports, recipe_crud_routes, image_preview, quick_search, recipe_sync, shared_routes, text_export, timeline_events

prefix = "/recipes"

router = APIRouter()

router.include_router(exports.router, tags=["Recipe: Exports"])
router.include_router(recipe_crud_routes.router, tags=["Recipe: CRUD"])
router.include_router(comments.router, prefix=prefix, tags=["Recipe: Comments"])
router.include_router(bulk_actions.router, prefix=prefix, tags=["Recipe: Bulk Actions"])
router.include_router(image_preview.router, prefix=prefix, tags=["Recipe: Image Preview"])
router.include_router(quick_search.router, prefix=prefix, tags=["Recipe: Search"])
router.include_router(recipe_sync.router, prefix=prefix, tags=["Recipe: External Sync"])
router.include_router(text_export.router, prefix=prefix, tags=["Recipe: Export Text"])
router.include_router(shared_routes.router, prefix=prefix, tags=["Recipe: Shared"])
router.include_router(timeline_events.router, prefix=prefix, tags=["Recipe: Timeline"])
