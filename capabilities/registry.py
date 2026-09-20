from dataclasses import dataclass
@dataclass(frozen=True)
class Capability:
    name:str; description:str; category:str
DEFAULT_CAPABILITIES=tuple(Capability(n,d,c) for n,d,c in [
("TEXT_GENERATION","Generate text with an approved model provider.","ai"),("IMAGE_GENERATION","Generate images.","media"),("TEXT_TO_VIDEO","Generate video from text.","media"),("VIDEO_EDITING","Edit raw or generated video.","media"),("VIDEO_ASSEMBLY","Assemble media tracks.","media"),("VOICE_GENERATION","Generate speech or narration.","media"),("MUSIC_GENERATION","Generate or source music.","media"),("CAPTION_GENERATION","Generate captions.","media"),("THUMBNAIL_GENERATION","Generate thumbnails.","media"),("CODE_EDITING","Create or modify source code.","software"),("BROWSER_AUTOMATION","Operate approved browser workflows.","automation"),("GITHUB_OPERATIONS","Perform approved GitHub operations.","integration"),("DEPLOYMENT","Perform approved deployment operations.","integration")])
class CapabilityRegistry:
    def __init__(self,capabilities=DEFAULT_CAPABILITIES): self._capabilities={x.name:x for x in capabilities}
    def get(self,name:str): return self._capabilities.get(name)
    def list(self): return list(self._capabilities.values())
