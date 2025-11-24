from abc import ABC, abstractmethod
from domain.model.media_model import MediaInfo

class MediaPort(ABC):

    @abstractmethod
    async def get_media_info(self, media_id: str) -> MediaInfo:
        """Get media information from media service"""
        pass
