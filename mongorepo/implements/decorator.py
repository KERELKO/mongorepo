from typing import Callable

from ._handlers import _handle_implements_specific_methods
from .methods import SpecificMethod


def implements[T: type](
    base_cls: type,
    *specific_methods: SpecificMethod,
) -> Callable[[T], T]:
    """Decorator that allows to implement methods of `base_cls`

    ## [Not recommended] Simple Usage Example:

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
    ## [Recommended] Usage with `SpecificMethod` protocol example:

    ```
    class IRepo:
        async def get(self, title: str) -> SomeDataclass:
            ...

        async def add(self, model: SomeDataclass) -> SomeDataclass:
            ...

    @implements(
        IRepo,
        GetMethod(IRepo.get, filters=['title']),
        AddMethod(IRepo.add, dto='model'),
    )
    class MongoRepo:
        class Meta:
            collection = some_collection()
            dto = SomeDataclass

    r: IRepo = MongoRepo()
    await r.add(SomeDataclass('some title'))
    dto = await r.get(title='some title')
    print(dto)  # SomeDataclass(title='some title')
    ```

    """
    if not specific_methods:
        raise ValueError('No methods to implement')

    def wrapper(base_cls: T) -> T:
        return _handle_implements_specific_methods(base_cls, *specific_methods)
    return wrapper
