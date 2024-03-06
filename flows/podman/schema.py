from typing import Optional

from pydantic import BaseModel


class PodmanParams(BaseModel):
    image_name: str
    image_tag: str
    command: str
    model_params: Optional[dict] = {}
    volumes: Optional[list] = []
    network: Optional[str] = ""
    env_vars: Optional[dict] = {}
