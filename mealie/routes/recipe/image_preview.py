import urllib.request

from fastapi import APIRouter, HTTPException, Response, status

from mealie.routes._base import BaseUserController, controller

router = APIRouter(prefix="/preview-image")


@controller(router)
class ImagePreviewController(BaseUserController):
    @router.get("")
    def preview(self, url: str):
        """Fetches a remote image so the editor can show a preview before importing it."""
        try:
            with urllib.request.urlopen(url, timeout=10) as response:
                return Response(content=response.read(), media_type=response.headers.get_content_type())
        except Exception as e:
            raise HTTPException(status.HTTP_502_BAD_GATEWAY) from e
