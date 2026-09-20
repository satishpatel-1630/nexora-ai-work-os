from .models import SpecialistProfile, SpecialistSelection

SPECIALISTS={
 "research": SpecialistProfile(name="research",description="Finds and synthesizes evidence.",capabilities=["research"],domains=["research","analysis"],output_types=["research"],quality_criteria=["credible sources","fresh evidence"]),
 "software_engineer": SpecialistProfile(name="software_engineer",description="Designs and implements software.",capabilities=["coding","architecture","testing"],domains=["software"],output_types=["code","design"]),
 "content_writer": SpecialistProfile(name="content_writer",description="Creates audience-aware written content.",capabilities=["writing","storytelling"],domains=["content","social"],output_types=["script","copy"]),
 "copywriter": SpecialistProfile(name="copywriter",description="Optimizes concise persuasive copy.",capabilities=["copywriting"],domains=["content","social"],output_types=["copy"]),
 "presentation": SpecialistProfile(name="presentation",description="Plans presentation narratives and slide content.",capabilities=["presentation_design"],domains=["presentation"],output_types=["slides"]),
 "document": SpecialistProfile(name="document",description="Produces structured professional documents.",capabilities=["document_writing"],domains=["document"],output_types=["document"]),
 "video_director": SpecialistProfile(name="video_director",description="Plans video storytelling, shots and pacing.",capabilities=["video_planning","storyboarding"],domains=["media","video"],output_types=["storyboard","shot_list"]),
 "social_media": SpecialistProfile(name="social_media",description="Packages content for social platforms.",capabilities=["social_packaging","metadata"],domains=["social"],output_types=["caption","metadata"]),
}

def select_specialists(domain:str,deliverables:list[str],requires_research:bool)->SpecialistSelection:
    names=[]
    if requires_research or domain in {"research","analysis"}: names.append("research")
    if domain in {"software","coding"}: names.append("software_engineer")
    if domain in {"content","social","media"} or any(x in " ".join(deliverables).lower() for x in ["script","content"]): names.append("content_writer")
    if domain in {"video","media"} or any(x in " ".join(deliverables).lower() for x in ["video","storyboard"]): names.append("video_director")
    if domain=="social" or any(x in " ".join(deliverables).lower() for x in ["instagram","caption","metadata"]): names.append("social_media")
    if domain=="presentation": names.append("presentation")
    if domain=="document": names.append("document")
    if not names: names=["research"]
    return SpecialistSelection(specialists=list(dict.fromkeys(names)),rationale="Selected from task domain, deliverables and research requirement.",required_capabilities=[c for n in dict.fromkeys(names) for c in SPECIALISTS[n].capabilities],confidence=.9)
