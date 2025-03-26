from typing import Callable

from ._handlers import _handle_implement_specific_methods
from .methods import SpecificMethod


def implement[T: type](*specific_methods: SpecificMethod) -> Callable[[T], T]:
    """## Implements Methods from an Interface or Base Class

    This decorator dynamically implements specified methods from an interface or
    base class into the target class. It allows the target class to behave like
    the interface while keeping the actual implementation flexible.

    ### Features:
    - Dynamically injects method implementations from an interface or abstract class.
    - Enables clear separation of interface definitions and concrete repository implementations.
    - Supports specifying filters and DTO mappings for enhanced type safety.

    ### Parameters:
    - `*specific_methods`: A list of method implementations (e.g., `GetMethod`, `AddMethod`)
      to be attached to the decorated class.

    ### Example Usage:

    ```python
    class IRepo:
        async def get(self, title: str) -> SomeDataclass:
            ...

        async def add(self, model: SomeDataclass) -> SomeDataclass:
            ...

    @implement(
        GetMethod(IRepo.get, filters=['title']),
        AddMethod(IRepo.add, dto='model'),
    )
    class MongoRepo:
        class Meta:
            collection = some_collection()
            dto = SomeDataclass

    repo: IRepo = MongoRepo()

    # Adding a new entry
    await repo.add(SomeDataclass('some title'))

    # Retrieving the entry
    dto = await repo.get(title='some title')
    print(dto)  # SomeDataclass(title='some title')
    ```

    ### Raises:
    - `ValueError`: If no methods are provided to implement.

    """
    if not specific_methods:
        raise ValueError('No methods to implement')

    def wrapper(cls: T) -> T:
        return _handle_implement_specific_methods(cls, *specific_methods)
    return wrapper
