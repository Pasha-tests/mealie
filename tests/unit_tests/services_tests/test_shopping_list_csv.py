import csv
import io
from types import SimpleNamespace

import pytest

from mealie.services.household_services.shopping_list_csv import CSV_HEADER, shopping_list_items_to_csv


def make_item(**kwargs):
    defaults = {"checked": False, "position": 0, "quantity": 1, "note": "", "food": None, "unit": None, "label": None}
    return SimpleNamespace(**{**defaults, **kwargs})


def parse(content: str) -> list[dict[str, str]]:
    return list(csv.DictReader(io.StringIO(content)))


def test_shopping_list_csv_empty_list_has_only_header():
    content = shopping_list_items_to_csv([])  # type: ignore[arg-type]
    assert content.splitlines() == [",".join(CSV_HEADER)]


def test_shopping_list_csv_food_item():
    item = make_item(
        quantity=2.5,
        checked=True,
        note="ripe",
        food=SimpleNamespace(name="Banana"),
        unit=SimpleNamespace(name="kg"),
        label=SimpleNamespace(name="Produce"),
    )

    [row] = parse(shopping_list_items_to_csv([item]))  # type: ignore[list-item]
    assert row == {
        "checked": "true",
        "quantity": "2.5",
        "unit": "kg",
        "food": "Banana",
        "note": "ripe",
        "label": "Produce",
    }


def test_shopping_list_csv_free_text_item_only_has_note():
    item = make_item(note="Paper towels", quantity=1)

    [row] = parse(shopping_list_items_to_csv([item]))  # type: ignore[list-item]
    assert row["note"] == "Paper towels"
    assert row["checked"] == "false"
    assert row["quantity"] == row["unit"] == row["food"] == row["label"] == ""


def test_shopping_list_csv_orders_by_position_and_quotes_special_characters():
    items = [
        make_item(position=2, note="last"),
        make_item(position=1, note='first, with "quotes"'),
    ]

    rows = parse(shopping_list_items_to_csv(items))  # type: ignore[arg-type]
    assert [r["note"] for r in rows] == ['first, with "quotes"', "last"]


def test_shopping_list_csv_neutralizes_spreadsheet_formulas():
    item = make_item(note='=HYPERLINK("http://example.com")')

    [row] = parse(shopping_list_items_to_csv([item]))  # type: ignore[list-item]
    assert row["note"].startswith("'=")


@pytest.mark.parametrize("field", ["unit", "food", "note", "label"])
@pytest.mark.parametrize("prefix", ["=", "+", "-", "@", "\t", "\r"])
def test_shopping_list_csv_neutralizes_each_formula_prefix_in_every_text_column(field: str, prefix: str) -> None:
    value = prefix + 'SUM(1,2)\n"quoted"'
    item = make_item(food=SimpleNamespace(name="Rice"))
    setattr(item, field, value if field == "note" else SimpleNamespace(name=value))

    [row] = parse(shopping_list_items_to_csv([item]))

    assert row[field] == "'" + value
    assert row["quantity"] == "1"


@pytest.mark.parametrize(
    "value",
    ["", "Brown rice", "  keep whitespace  ", "salt + pepper", "user@example.com", "'already escaped"],
)
def test_shopping_list_csv_preserves_non_formula_text(value: str) -> None:
    item = make_item(
        food=SimpleNamespace(name=value),
        unit=SimpleNamespace(name=value),
        label=SimpleNamespace(name=value),
        note=value,
    )

    [row] = parse(shopping_list_items_to_csv([item]))

    assert {row[field] for field in ("food", "unit", "label", "note")} == {value}


@pytest.mark.parametrize("field", ["unit", "food", "note", "label"])
@pytest.mark.parametrize("value", ['rice, "brown"', "first line\nsecond line", "crème brûlée 🥕\r\n有機"])
def test_shopping_list_csv_round_trips_special_characters_in_every_text_column(field: str, value: str) -> None:
    item = make_item(food=SimpleNamespace(name="Rice"))
    setattr(item, field, value if field == "note" else SimpleNamespace(name=value))

    content = shopping_list_items_to_csv([item])
    [row] = parse(content)

    assert row[field] == value
    assert len(row) == 6
    assert None not in row  # A stray delimiter would create an extra DictReader column.


@pytest.mark.parametrize(
    ("quantity", "expected"),
    [(None, ""), (0, ""), (-0.0, ""), (1.0, "1"), (1000000.0, "1000000"), (0.125, "0.125"), (-2.5, "-2.5")],
)
def test_shopping_list_csv_formats_food_quantities(quantity: float | None, expected: str) -> None:
    item = make_item(food=SimpleNamespace(name="Rice"), quantity=quantity)

    [row] = parse(shopping_list_items_to_csv([item]))

    assert row == {"checked": "false", "quantity": expected, "unit": "", "food": "Rice", "note": "", "label": ""}


def test_shopping_list_csv_free_text_ignores_quantity_and_unit_but_keeps_label() -> None:
    item = make_item(
        checked=True,
        quantity=2.5,
        unit=SimpleNamespace(name="kg"),
        label=SimpleNamespace(name="Household"),
        note="Paper towels",
    )

    [row] = parse(shopping_list_items_to_csv([item]))

    assert row == {
        "checked": "true",
        "quantity": "",
        "unit": "",
        "food": "",
        "note": "Paper towels",
        "label": "Household",
    }


def test_shopping_list_csv_missing_note_is_an_empty_cell() -> None:
    [row] = parse(shopping_list_items_to_csv([make_item(note=None)]))

    assert row == {"checked": "false", "quantity": "", "unit": "", "food": "", "note": "", "label": ""}


def test_shopping_list_csv_accepts_a_generator_and_keeps_all_items_in_position_order() -> None:
    items = (
        make_item(position=position, note=note, checked=checked)
        for position, note, checked in [(10, "last", True), (0, "first", False), (2, "middle", True)]
    )

    rows = parse(shopping_list_items_to_csv(items))

    assert [(row["note"], row["checked"]) for row in rows] == [
        ("first", "false"),
        ("middle", "true"),
        ("last", "true"),
    ]


def test_shopping_list_csv_preserves_input_order_for_tied_positions_without_mutating_items() -> None:
    items = [
        make_item(position=3, note="last"),
        make_item(position=1, note="=first"),
        make_item(position=1, note="second"),
    ]
    original_items = items.copy()
    original_values = [vars(item).copy() for item in items]

    content = shopping_list_items_to_csv(items)

    assert [row["note"] for row in parse(content)] == ["'=first", "second", "last"]
    assert items == original_items
    assert [vars(item) for item in items] == original_values
    assert shopping_list_items_to_csv(items) == content


def test_shopping_list_csv_empty_iterator_has_the_public_column_order_and_trailing_newline() -> None:
    assert shopping_list_items_to_csv(iter(())) == "checked,quantity,unit,food,note,label\n"
