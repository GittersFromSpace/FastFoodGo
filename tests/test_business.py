"""Unit tests for business logic functions."""

import pytest
from src.business import (
    OrderItem,
    calculate_order_total,
    validate_status_transition,
    VALID_TRANSITIONS
)


class TestOrderItem:
    """Test cases for OrderItem class."""

    def test_order_item_creation_nominal(self):
        """Test creating a valid order item."""
        item = OrderItem("Product A", 2, 10.0)
        assert item.product_name == "Product A"
        assert item.quantity == 2
        assert item.unit_price == 10.0

    def test_order_item_get_total(self):
        """Test calculating item total."""
        item = OrderItem("Product B", 3, 15.5)
        assert item.get_total() == 46.5

    def test_order_item_zero_quantity(self):
        """Test order item with zero quantity."""
        item = OrderItem("Product C", 0, 10.0)
        assert item.get_total() == 0.0

    def test_order_item_negative_quantity(self):
        """Test that negative quantity raises ValueError."""
        with pytest.raises(ValueError, match="Quantity cannot be negative"):
            OrderItem("Product D", -1, 10.0)

    def test_order_item_negative_price(self):
        """Test that negative unit price raises ValueError."""
        with pytest.raises(ValueError, match="Unit price cannot be negative"):
            OrderItem("Product E", 2, -5.0)


class TestCalculateOrderTotal:
    """Test cases for calculate_order_total function."""

    def test_single_item_no_tax(self):
        """Test calculating total for single item without tax."""
        items = [OrderItem("Product A", 2, 10.0)]
        total = calculate_order_total(items)
        assert total == 20.0

    def test_multiple_items_no_tax(self):
        """Test calculating total for multiple items without tax."""
        items = [
            OrderItem("Product A", 2, 10.0),
            OrderItem("Product B", 1, 15.5),
            OrderItem("Product C", 3, 5.0)
        ]
        total = calculate_order_total(items)
        assert total == 50.5

    def test_single_item_with_tax(self):
        """Test calculating total with tax."""
        items = [OrderItem("Product A", 2, 10.0)]
        total = calculate_order_total(items, tax_rate=0.20)
        assert total == 24.0

    def test_multiple_items_with_tax(self):
        """Test calculating total for multiple items with tax."""
        items = [
            OrderItem("Product A", 2, 10.0),
            OrderItem("Product B", 1, 15.0)
        ]
        total = calculate_order_total(items, tax_rate=0.10)
        assert total == 38.5

    def test_rounding_to_two_decimals(self):
        """Test that result is rounded to 2 decimal places."""
        items = [OrderItem("Product A", 3, 3.333)]
        total = calculate_order_total(items, tax_rate=0.15)
        # 3 * 3.333 = 9.999, with 15% tax = 11.49885, rounded to 11.50
        assert total == 11.5

    def test_empty_items_list(self):
        """Test that empty items list raises ValueError."""
        with pytest.raises(ValueError, match="Order must contain at least one item"):
            calculate_order_total([])

    def test_negative_tax_rate(self):
        """Test that negative tax rate raises ValueError."""
        items = [OrderItem("Product A", 1, 10.0)]
        with pytest.raises(ValueError, match="Tax rate cannot be negative"):
            calculate_order_total(items, tax_rate=-0.1)

    def test_items_not_a_list(self):
        """Test that non-list items raises TypeError."""
        with pytest.raises(TypeError, match="items must be a list"):
            calculate_order_total("not a list")

    def test_invalid_item_type(self):
        """Test that non-OrderItem in list raises TypeError."""
        items = [OrderItem("Product A", 1, 10.0), "invalid item"]
        with pytest.raises(TypeError, match="All items must be OrderItem instances"):
            calculate_order_total(items)

    def test_zero_quantity_items(self):
        """Test order with items having zero quantity."""
        items = [
            OrderItem("Product A", 0, 10.0),
            OrderItem("Product B", 2, 5.0)
        ]
        total = calculate_order_total(items)
        assert total == 10.0

    def test_high_tax_rate(self):
        """Test with a high tax rate."""
        items = [OrderItem("Product A", 1, 100.0)]
        total = calculate_order_total(items, tax_rate=1.0)
        assert total == 200.0


class TestValidateStatusTransition:
    """Test cases for validate_status_transition function."""

    def test_valid_pending_to_confirmed(self):
        """Test valid transition from pending to confirmed."""
        assert validate_status_transition("pending", "confirmed") is True

    def test_valid_pending_to_cancelled(self):
        """Test valid transition from pending to cancelled."""
        assert validate_status_transition("pending", "cancelled") is True

    def test_valid_confirmed_to_processing(self):
        """Test valid transition from confirmed to processing."""
        assert validate_status_transition("confirmed", "processing") is True

    def test_valid_processing_to_shipped(self):
        """Test valid transition from processing to shipped."""
        assert validate_status_transition("processing", "shipped") is True

    def test_valid_shipped_to_delivered(self):
        """Test valid transition from shipped to delivered."""
        assert validate_status_transition("shipped", "delivered") is True

    def test_invalid_pending_to_processing(self):
        """Test invalid transition from pending to processing."""
        assert validate_status_transition("pending", "processing") is False

    def test_invalid_confirmed_to_shipped(self):
        """Test invalid transition from confirmed to shipped."""
        assert validate_status_transition("confirmed", "shipped") is False

    def test_invalid_delivered_to_any(self):
        """Test that delivered status cannot transition to any status."""
        assert validate_status_transition("delivered", "pending") is False
        assert validate_status_transition("delivered", "confirmed") is False
        assert validate_status_transition("delivered", "cancelled") is False

    def test_invalid_cancelled_to_any(self):
        """Test that cancelled status cannot transition to any status."""
        assert validate_status_transition("cancelled", "pending") is False
        assert validate_status_transition("cancelled", "confirmed") is False

    def test_case_insensitive(self):
        """Test that status comparison is case-insensitive."""
        assert validate_status_transition("PENDING", "CONFIRMED") is True
        assert validate_status_transition("Pending", "Confirmed") is True
        assert validate_status_transition("PeNdInG", "cOnFiRmEd") is True

    def test_invalid_current_status(self):
        """Test that invalid current status raises ValueError."""
        with pytest.raises(ValueError, match="Invalid current status: invalid"):
            validate_status_transition("invalid", "confirmed")

    def test_invalid_new_status(self):
        """Test that invalid new status raises ValueError."""
        with pytest.raises(ValueError, match="Invalid new status: invalid"):
            validate_status_transition("pending", "invalid")

    def test_current_status_not_string(self):
        """Test that non-string current_status raises TypeError."""
        with pytest.raises(TypeError, match="current_status must be a string"):
            validate_status_transition(123, "confirmed")

    def test_new_status_not_string(self):
        """Test that non-string new_status raises TypeError."""
        with pytest.raises(TypeError, match="new_status must be a string"):
            validate_status_transition("pending", 456)

    def test_same_status_transition(self):
        """Test transition from a status to itself."""
        assert validate_status_transition("pending", "pending") is False
        assert validate_status_transition("confirmed", "confirmed") is False

    def test_all_valid_transitions(self):
        """Test all valid transitions defined in VALID_TRANSITIONS."""
        for current, valid_nexts in VALID_TRANSITIONS.items():
            for next_status in valid_nexts:
                assert validate_status_transition(current, next_status) is True


class TestIntegration:
    """Integration tests combining multiple functions."""

    def test_complete_order_workflow(self):
        """Test a complete order workflow."""
        # Create order items
        items = [
            OrderItem("Laptop", 1, 999.99),
            OrderItem("Mouse", 2, 25.50)
        ]

        # Calculate total with tax
        total = calculate_order_total(items, tax_rate=0.20)
        assert total == 1261.18

        # Validate status transitions
        assert validate_status_transition("pending", "confirmed") is True
        assert validate_status_transition("confirmed", "processing") is True
        assert validate_status_transition("processing", "shipped") is True
        assert validate_status_transition("shipped", "delivered") is True
