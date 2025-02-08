from typing import Callable, overload

from ._handlers import (
    _handle_implements_custom_methods,
    _handle_implements_specific_methods,
)
from .methods import Method, SpecificMethod


@overload
def implements(base_cls: type, **custom_methods: str | Callable | Method) -> Callable:
    ...


@overload
def implements(base_cls: type) -> Callable:
    ...


@overload
def implements(base_cls: type, *specific_methods: SpecificMethod) -> Callable:
    ...


def implements(
    base_cls,
    *specific_methods: SpecificMethod,
    **custom_methods: str | Method | Callable,
) -> Callable:
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
    if specific_methods and custom_methods:
        raise ValueError(
            'Specify either positional arguments (*specific_methods)'
            'or keyword arguments (**custom_methods), not both.',
        )

    def wrapper(cls) -> type:
        if custom_methods:
            return _handle_implements_custom_methods(
                base_cls=base_cls,
                cls=cls,
                **custom_methods,
            )
        elif specific_methods:
            return _handle_implements_specific_methods(
                cls,
                *specific_methods,
            )
        else:
            return _handle_implements_custom_methods(
                base_cls=base_cls,
                cls=cls,
                **custom_methods,
            )
    return wrapper
