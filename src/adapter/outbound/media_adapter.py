import httpx
from fastapi import HTTPException
from application.port.outbound.media_port import MediaPort
from domain.model.media_model import MediaInfo

class MediaAdapter(MediaPort):

    def __init__(self, base_url: str = "http://darami.life:3002"):
        self.base_url = base_url

    async def get_media_info(self, media_id: str) -> MediaInfo:
        """Get media information from media API"""
        url = f"{self.base_url}/api/media/"
        params = {"mediaId": media_id}

        try:
            async with httpx.AsyncClient(timeout=10) as client:
                response = await client.get(url, params=params)
                response.raise_for_status()
                data = response.json()
                return MediaInfo(**data)
        except httpx.HTTPStatusError as e:
            raise HTTPException(status_code=e.response.status_code, detail=f"미디어 정보 조회 실패: {str(e)}")
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"미디어 API 호출 오류: {str(e)}")
