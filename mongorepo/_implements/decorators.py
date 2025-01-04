from typing import Callable

from .handlers import _handle_implements
from .methods import Method


def implements(base_cls: type, **methods: str | Callable | Method) -> Callable:
    """Decorator that allows to implement methods of `base_cls` you can specify
    them in `**methods`

    ## Example:

    ```
    class A:
        def get_my_entity(self, id: str):
            ...

    @implements(A, get=A.get_my_entity)
    class MongoRepo:
        class Meta:
            dto = SimpleDTO
            collection = random_collection()

    my_entity = MongoRepo().get_my_entity(id="10")

    ```

    """
    def wrapper(cls) -> type:
        return _handle_implements(
            base_cls=base_cls,
            cls=cls,
            **methods,
        )
    return wrapper
