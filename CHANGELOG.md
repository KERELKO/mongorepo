# Changelog

## 2.3.0

### Added
  - Add __FieldAlias__ for __implements__ decorator

## 3.0.0

### Added
  - Add modifiers for __implement__ decorator
  - Add ability to write custom __implement__ modifiers, `ModifierBefore` and `ModifierAfter`
  - Add `use_collection` decorator. Allows to set collection for any __mongorepo__ repository in any place of a program
  - Add more correct type hints
  - Add `use_session`, `remove_session` and `session_context` to add mongodb session to mongorepo methods 

### Removed
  - Removed legacy way to implement methods with __implement__ decorator (__substitute__ dictionary in __Meta__ class, using __mongorepo.implement.methods.Method__, using keyword argumenst in __implement__ decorator) 
  - Removed __mongorepo.asyncio__ directory

### Changed
  - Rename __implements__ decorator to __implement__
  - Rename __AsyncBasedMongoRepository__ class to __BaseAsyncMongoRepository__
  - Change methods signatures. Methods are not longer raise exceptions if document was not found
  - Remove __base_cls__ argument in __implement__ decorator

## 3.0.1
  - Improved docstrings
  - Session now can be bonded to any method

## 3.1.1
### Added
  - Add __set_meta_attrs__ decorator

## 3.1.2
### Changed
  - Now, when an invalid dataclass field name is passed to specific methods __(filters and aliases)__, a `FieldDoesNotExist` exception will be raised.
### Fixed
  - Fixed bug where multiple alises do not work on specific method filters
