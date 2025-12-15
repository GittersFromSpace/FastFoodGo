"""Business logic functions for order management."""

from typing import List, Dict, Any


class OrderItem:
    """Represents an item in an order."""

    def __init__(self, product_name: str, quantity: int, unit_price: float):
        """Initialize an order item.

        Args:
            product_name: Name of the product
            quantity: Quantity ordered
            unit_price: Price per unit

        Raises:
            ValueError: If quantity is negative or unit_price is negative
        """
        if quantity < 0:
            raise ValueError("Quantity cannot be negative")
        if unit_price < 0:
            raise ValueError("Unit price cannot be negative")

        self.product_name = product_name
        self.quantity = quantity
        self.unit_price = unit_price

    def get_total(self) -> float:
        """Calculate the total price for this item."""
        return self.quantity * self.unit_price


def calculate_order_total(items: List[OrderItem], tax_rate: float = 0.0) -> float:
    """Calculate the total amount for an order including tax.

    Args:
        items: List of OrderItem objects
        tax_rate: Tax rate as a decimal (e.g., 0.20 for 20%)

    Returns:
        Total amount including tax

    Raises:
        ValueError: If items is empty or tax_rate is negative
        TypeError: If items is not a list or contains non-OrderItem objects
    """
    if not isinstance(items, list):
        raise TypeError("items must be a list")

    if not items:
        raise ValueError("Order must contain at least one item")

    if tax_rate < 0:
        raise ValueError("Tax rate cannot be negative")

    # Validate all items are OrderItem instances
    for item in items:
        if not isinstance(item, OrderItem):
            raise TypeError("All items must be OrderItem instances")

    # Calculate subtotal
    subtotal = sum(item.get_total() for item in items)

    # Apply tax
    total = subtotal * (1 + tax_rate)

    return round(total, 2)


# Valid status transitions
VALID_TRANSITIONS = {
    "pending": ["confirmed", "cancelled"],
    "confirmed": ["processing", "cancelled"],
    "processing": ["shipped", "cancelled"],
    "shipped": ["delivered"],
    "delivered": [],
    "cancelled": []
}


def validate_status_transition(current_status: str, new_status: str) -> bool:
    """Validate if a status transition is allowed.

    Args:
        current_status: Current order status
        new_status: Desired new order status

    Returns:
        True if the transition is valid, False otherwise

    Raises:
        ValueError: If current_status or new_status is not a valid status
        TypeError: If current_status or new_status is not a string
    """
    if not isinstance(current_status, str):
        raise TypeError("current_status must be a string")

    if not isinstance(new_status, str):
        raise TypeError("new_status must be a string")

    # Normalize to lowercase
    current_status = current_status.lower()
    new_status = new_status.lower()

    # Check if statuses are valid
    if current_status not in VALID_TRANSITIONS:
        raise ValueError(f"Invalid current status: {current_status}")

    if new_status not in VALID_TRANSITIONS:
        raise ValueError(f"Invalid new status: {new_status}")

    # Check if transition is allowed
    return new_status in VALID_TRANSITIONS[current_status]
