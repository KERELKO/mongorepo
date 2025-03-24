from typing import Callable

from ._handlers import _handle_implement_specific_methods
from .methods import SpecificMethod


def implement[T: type](*specific_methods: SpecificMethod) -> Callable[[T], T]:
    """Decorator that allows to implement methods of `base_cls`

    ## Usage example:

    ```
    class IRepo:
        async def get(self, title: str) -> SomeDataclass:
            ...

        async def add(self, model: SomeDataclass) -> SomeDataclass:
            ...

    @implement(
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

    def wrapper(cls: T) -> T:
        return _handle_implement_specific_methods(cls, *specific_methods)
    return wrapper
