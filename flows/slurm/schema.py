from typing import List, Optional

from pydantic import BaseModel, Field, StringConstraints
from typing_extensions import Annotated


class SlurmParams(BaseModel):
    job_name: str
    num_nodes: int
    partitions: Optional[List[str]] = None
    reservations: Optional[List[str]] = None
    max_time: Annotated[
        str,
        StringConstraints(
            strip_whitespace=True,
            to_upper=True,
            pattern=r"^([0-1]?[0-9]|2[0-3]):[0-5][0-9]:[0-5][0-9]$",
        ),
    ]
    conda_env_name: str
    python_file_name: str = Field(
        description="Python file to run", default="src/train.py"
    )
    params: Optional[dict] = {}
