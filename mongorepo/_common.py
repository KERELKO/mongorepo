from contextlib import contextmanager
from typing import Any, Generic, Protocol, TypedDict

from ._base import CollectionProvider, CollectionType, SessionType
from ._methods.interfaces import MongorepoMethod


class MongorepoDict(Generic[SessionType, CollectionType], TypedDict, total=True):
    methods: dict[str, MongorepoMethod[SessionType]]
    collection_provider: CollectionProvider[CollectionType]


class HasMongorepoDict(Generic[SessionType, CollectionType], Protocol):
    __mongorepo__: MongorepoDict[SessionType, CollectionType]


def default_mongorepo_dict(
    collection_provider: CollectionProvider[CollectionType],
    methods: dict[str, MongorepoMethod[SessionType]] | None = None,
) -> MongorepoDict[SessionType, CollectionType]:
    methods = methods or {}
    return MongorepoDict(collection_provider=collection_provider, methods=methods)


def use_session(
    session: SessionType,
    *mongorepo_repositories: HasMongorepoDict[SessionType, CollectionType] | Any,
):
    """Function to make mongorepo methods use session."""
    for repo in mongorepo_repositories:
        __mongorepo__: MongorepoDict[SessionType, CollectionType] | None = getattr(
            repo, '__mongorepo__', None,
        )
        if not __mongorepo__:
            raise TypeError(
                f'Invalid class for mongorepo repository: {type(repo)}: '
                f'"{type(repo).__name__}" does not implement {str(HasMongorepoDict)} protocol',
            )

        for method in __mongorepo__['methods'].values():
            method.session = session


def remove_session(
    *mongorepo_repositories: HasMongorepoDict[SessionType, CollectionType] | Any,
):
    """Function to remove session from mongorepo methods."""
    for repo in mongorepo_repositories:
        __mongorepo__: MongorepoDict[SessionType, CollectionType] | None = getattr(
            repo, '__mongorepo__', None,
        )
        if not __mongorepo__:
            raise TypeError(
                f'Invalid class for mongorepo repository: {type(repo)}: '
                f'"{type(repo).__name__}" does not implement {str(HasMongorepoDict)} protocol',
            )

        for method in __mongorepo__['methods'].values():
            method.session = None


@contextmanager
def session_context(
    session: SessionType,
    *mongorepo_repositories: HasMongorepoDict[SessionType, CollectionType] | Any,
):
    """Context manager that temporarily assigns a session to mongorepo methods.

    This ensures that all methods in the provided mongorepo repositories
    use the given session during the execution of the context. Once the
    context exits, the session is removed from the methods.

    Usage example::

        with session_context(session, repo1, repo2):
            repo1.some_method()  # Uses the provided session
            repo2.another_method()  # Uses the provided session

    Args:
        session (SessionType): The session to be assigned to mongorepo methods.
        *mongorepo_repositories (HasMongorepoDict[SessionType, CollectionType] | Any):
            One or more repository instances that implement the `HasMongorepoDict`
            protocol, allowing them to have session-managed methods.

    Yields:
        None: The context executes with the assigned session, then removes it upon exit.

    """
    try:
        use_session(session, *mongorepo_repositories)
        yield
    finally:
        remove_session(*mongorepo_repositories)
