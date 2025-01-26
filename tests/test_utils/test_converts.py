from mongorepo._base import MethodAction
from mongorepo.implements._utils import MethodType


def test_can_get_method_type_from_action():
    assert MethodType.from_action(MethodAction.ADD) == MethodType.CRUD
    assert MethodType.from_action(MethodAction.INTEGER_INCREMENT) == MethodType.INTEGER
    assert MethodType.from_action(MethodAction.LIST_FIELD_VALUES) == MethodType.LIST
