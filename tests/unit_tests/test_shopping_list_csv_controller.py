import csv
import io
from types import SimpleNamespace
from unittest.mock import Mock
from uuid import uuid4

import pytest
from fastapi import HTTPException

from mealie.routes._base.mixins import HttpRepo
from mealie.routes.households.controller_shopping_lists import ShoppingListController
from mealie.schema.household.group_shopping_list import ShoppingListItemOut


@pytest.fixture
def shopping_list_get_one() -> Mock:
    return Mock()


@pytest.fixture
def shopping_list_controller(shopping_list_get_one: Mock) -> ShoppingListController:
    # Supply only the repository boundary used by export_csv, without FastAPI dependency injection.
    controller = ShoppingListController.__new__(ShoppingListController)
    controller.mixins = Mock(spec=HttpRepo, get_one=shopping_list_get_one)
    return controller


@pytest.mark.parametrize(
    ("name", "filename"),
    [
        ("Weekly Groceries", "weekly-groceries.csv"),
        ("  Crème brûlée & café  ", "creme-brulee-cafe.csv"),
        ('../"Weekend"\r\nGroceries', "weekend-groceries.csv"),
        ("", "shopping-list.csv"),
        ("   ", "shopping-list.csv"),
        ("!!!", "shopping-list.csv"),
        ("🥕🧀", "shopping-list.csv"),
    ],
)
def test_export_csv_empty_list_has_a_safe_download_filename(
    shopping_list_controller: ShoppingListController, shopping_list_get_one: Mock, name: str, filename: str
) -> None:
    item_id = uuid4()
    shopping_list_get_one.return_value = SimpleNamespace(name=name, list_items=[])

    response = shopping_list_controller.export_csv(item_id)

    shopping_list_get_one.assert_called_once_with(item_id)
    assert response.status_code == 200
    assert response.headers["content-type"] == "text/csv; charset=utf-8"
    assert response.headers["content-disposition"] == f'attachment; filename="{filename}"'
    assert response.body == b"checked,quantity,unit,food,note,label\n"


def test_export_csv_returns_utf8_csv_content(
    shopping_list_controller: ShoppingListController, shopping_list_get_one: Mock
) -> None:
    item_id = uuid4()
    item = ShoppingListItemOut(
        id=uuid4(),
        shopping_list_id=item_id,
        group_id=uuid4(),
        household_id=uuid4(),
        checked=True,
        note='Crème, "fraîche"\n🥕',
    )
    shopping_list_get_one.return_value = SimpleNamespace(name="Groceries", list_items=[item])

    response = shopping_list_controller.export_csv(item_id)

    shopping_list_get_one.assert_called_once_with(item_id)
    rows = list(csv.reader(io.StringIO(bytes(response.body).decode("utf-8"))))
    assert rows == [
        ["checked", "quantity", "unit", "food", "note", "label"],
        ["true", "", "", "", item.note, ""],
    ]
    assert int(response.headers["content-length"]) == len(response.body)


def test_export_csv_propagates_repository_not_found(
    shopping_list_controller: ShoppingListController, shopping_list_get_one: Mock
) -> None:
    item_id = uuid4()
    error = HTTPException(status_code=404, detail="Shopping list not found")
    shopping_list_get_one.side_effect = error

    with pytest.raises(HTTPException) as raised:
        shopping_list_controller.export_csv(item_id)

    assert raised.value is error
    shopping_list_get_one.assert_called_once_with(item_id)
