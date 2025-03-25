import datetime
from dataclasses import dataclass

import mongorepo
from tests.common import in_collection


def test_can_convert_to_datetime():
    @dataclass
    class Subscription:
        id: str
        created_at: datetime.datetime

    with in_collection(Subscription) as c:
        @mongorepo.repository
        class Repository:
            class Meta:
                dto = Subscription
                collection = c
                id_field = 'id'

        r = Repository()
        added_sub = r.add(Subscription(id='1', created_at=datetime.datetime.now()))

        sub: Subscription | None = r.get(id=added_sub.id)
        print(sub)
        assert sub is not None
        assert isinstance(sub.created_at, datetime.datetime)
