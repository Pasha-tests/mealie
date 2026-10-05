import csv
import io
from collections.abc import Iterable

from mealie.schema.household.group_shopping_list import ShoppingListItemOut

CSV_HEADER = ["checked", "quantity", "unit", "food", "note", "label"]

_FORMULA_PREFIXES = ("=", "+", "-", "@", "\t", "\r")


def _safe_text(value: str | None) -> str:
    """Neutralize cells that spreadsheet software would interpret as formulas"""
    value = value or ""
    if value.startswith(_FORMULA_PREFIXES):
        return "'" + value
    return value


def _format_quantity(quantity: float | None) -> str:
    if not quantity:
        return ""
    return str(int(quantity)) if float(quantity).is_integer() else f"{quantity:g}"


def shopping_list_items_to_csv(items: Iterable[ShoppingListItemOut]) -> str:
    """
    Render shopping list items as CSV, one row per item.

    Items linked to a food get quantity, unit and food columns filled in. Free-text items only
    have a note, so quantity, unit and food are left blank for them.
    """
    buffer = io.StringIO()
    writer = csv.writer(buffer, lineterminator="\n")
    writer.writerow(CSV_HEADER)

    for item in sorted(items, key=lambda i: i.position):
        has_food = item.food is not None
        writer.writerow(
            [
                "true" if item.checked else "false",
                _format_quantity(item.quantity) if has_food else "",
                _safe_text(item.unit.name) if has_food and item.unit else "",
                _safe_text(item.food.name) if item.food else "",
                _safe_text(item.note),
                _safe_text(item.label.name) if item.label else "",
            ]
        )

    return buffer.getvalue()
