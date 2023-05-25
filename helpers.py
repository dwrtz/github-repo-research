import json
from dataclasses import dataclass, asdict, is_dataclass
from datetime import datetime
from typing import Optional


@dataclass
class Repository:
    owner: str
    name: str
    stars: int
    url: str


@dataclass
class PullRequest:
    title: str
    body: Optional[str]
    created_at: datetime
    merged_at: Optional[datetime]
    url: str
    diff_url: str
    repository: Repository


def serialize(obj):
    if is_dataclass(obj):
        return asdict(obj)
    elif isinstance(obj, datetime):
        return obj.isoformat()
    return obj


def to_json(data, filename):
    with open(filename, "w") as f:
        json.dump(data, f, default=serialize, indent=4)


def from_json(filename):
    with open(filename, "r") as f:
        data = json.load(f)

    def deserialize(data):
        if "created_at" in data:
            data["created_at"] = datetime.fromisoformat(data["created_at"])
        if "merged_at" in data and data["merged_at"] is not None:
            data["merged_at"] = datetime.fromisoformat(data["merged_at"])
        if "repository" in data:
            data["repository"] = Repository(**data["repository"])
        return PullRequest(**data)

    return [deserialize(item) for item in data]
