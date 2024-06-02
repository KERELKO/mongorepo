from dataclasses import dataclass, field

from bson import ObjectId


@dataclass(repr=False)
class MongoDTO:
    _id: ObjectId = field(default_factory=ObjectId, kw_only=True)
