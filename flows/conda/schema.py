from typing import Optional

from pydantic import BaseModel, Field


class CondaParams(BaseModel):
    conda_env_name: str
    python_file_name: str = Field(
        description="Python file to run", default="src/train.py"
    )
    params: Optional[dict] = {}
    
    class Config:
        extra = "forbid"
