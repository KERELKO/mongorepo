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
  - Add `set_session`, `unset_session` and `session_context` to add mongodb session to mongorepo methods 

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

## 4.0.0
### Removed
  - Removed support for `Meta` attributes in decorated classes
  - Removed support for index creation
  - Removed support for base classes
### Added
  - Added support for custom convertors (not coupled with `asdict` anymore)
  - Added ability to specify all required meta information (such as collection, entity_type) in decorators that provide methods
  - Added `override` attribute to specify if override of existing repository methods required
### Changed
  - Renamed `dto`, `dto_type` to `entity`, `entity_type`
  - Renamed `use_session` to `set_session`, `remove_session` to `unset_session`
