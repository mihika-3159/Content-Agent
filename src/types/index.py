# filepath: content-agent-langgraph/src/types/index.py

from typing import Optional, Dict, Any, List

class SocialMediaPost:
    def __init__(self, platform: str, caption: str, image_url: Optional[str] = None):
        self.platform = platform
        self.caption = caption
        self.image_url = image_url

class ApiResponse:
    def __init__(self, success: bool, message: str, data: Optional[Dict[str, Any]] = None):
        self.success = success
        self.message = message
        self.data = data

class SocialMediaCredentials:
    def __init__(self, access_token: str, user_id: str):
        self.access_token = access_token
        self.user_id = user_id

class PostResult:
    def __init__(self, post_id: str, platform: str, status: str):
        self.post_id = post_id
        self.platform = platform
        self.status = status

class ImageGenerationResult:
    def __init__(self, image_url: str, prompt: str):
        self.image_url = image_url
        self.prompt = prompt

class CaptionGenerationResult:
    def __init__(self, caption: str, context: str):
        self.caption = caption
        self.context = context

class SocialMediaPlatform:
    FACEBOOK = "facebook"
    INSTAGRAM = "instagram"
    TWITTER = "twitter"
    LINKEDIN = "linkedin"