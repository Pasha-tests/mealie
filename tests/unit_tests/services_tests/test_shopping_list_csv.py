import csv
import io
from types import SimpleNamespace

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
