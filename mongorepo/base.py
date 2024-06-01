from dataclasses import dataclass, field

from bson import ObjectId


@dataclass
class MongoDTO:
    _id: ObjectId = field(default_factory=ObjectId, kw_only=True)

    def __init_subclass__(cls) -> None:
        ...
