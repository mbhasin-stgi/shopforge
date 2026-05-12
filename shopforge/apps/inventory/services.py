"""
Inventory service layer.

All direct stock mutations go through this service so that:
- Business rules are enforced in one place
- Views and tasks stay thin
- Logic is fully testable without HTTP overhead
"""

import logging

from django.db import transaction

from shopforge.apps.inventory.models import StockMovement, StockRecord

logger = logging.getLogger(__name__)


class InventoryService:
    """Service for all stock operations."""

    @staticmethod
    @transaction.atomic
    def reserve(product, quantity: int, order_number: str, performed_by=None) -> None:
        """
        Reserve `quantity` units for a pending order.

        Raises ValueError if insufficient stock is available.
        Uses select_for_update to prevent concurrent overselling.
        """
        stock = StockRecord.objects.select_for_update().get(product=product)
        available = stock.quantity - stock.reserved_quantity
        if available < quantity:
            raise ValueError(
                f"Insufficient stock for '{product.name}': " f"requested {quantity}, available {available}."
            )
        stock.reserved_quantity += quantity
        stock.save(update_fields=["reserved_quantity", "updated_at"])
        StockMovement.objects.create(
            stock_record=stock,
            movement_type=StockMovement.MovementType.RESERVED,
            quantity_change=-quantity,
            reference=order_number,
            notes=f"Reserved for order {order_number}",
            performed_by=performed_by,
        )

    @staticmethod
    @transaction.atomic
    def release(product, quantity: int, order_number: str, performed_by=None) -> None:
        """
        Release a previously reserved quantity (e.g. on order cancellation).

        Clamps the release to the current reserved_quantity to stay non-negative.
        """
        stock = StockRecord.objects.select_for_update().get(product=product)
        released = min(quantity, stock.reserved_quantity)
        if released <= 0:
            logger.warning(
                "Release requested for '%s' but reserved_quantity is 0. Skipping.",
                product.name,
            )
            return
        stock.reserved_quantity -= released
        stock.save(update_fields=["reserved_quantity", "updated_at"])
        StockMovement.objects.create(
            stock_record=stock,
            movement_type=StockMovement.MovementType.UNRESERVED,
            quantity_change=released,
            reference=order_number,
            notes=f"Released on cancellation of order {order_number}",
            performed_by=performed_by,
        )

    @staticmethod
    @transaction.atomic
    def fulfill(product, quantity: int, order_number: str) -> None:
        """
        Convert a reservation into an actual stock deduction (SOLD movement).

        Idempotent: a second call for the same order_number is a no-op.
        """
        stock = StockRecord.objects.select_for_update().get(product=product)
        already = StockMovement.objects.filter(
            stock_record=stock,
            movement_type=StockMovement.MovementType.SOLD,
            reference=order_number,
        ).exists()
        if already:
            return
        deducted_reservation = min(quantity, stock.reserved_quantity)
        stock.quantity -= quantity
        stock.reserved_quantity -= deducted_reservation
        stock.save(update_fields=["quantity", "reserved_quantity", "updated_at"])
        StockMovement.objects.create(
            stock_record=stock,
            movement_type=StockMovement.MovementType.SOLD,
            quantity_change=-quantity,
            reference=order_number,
            notes=f"Fulfilled on shipment of order {order_number}",
        )

    @staticmethod
    @transaction.atomic
    def adjust(stock_record: StockRecord, delta: int, notes: str, performed_by=None) -> None:
        """
        Apply a manual stock adjustment (positive = stock in, negative = stock out).
        """
        stock_record.quantity += delta
        if stock_record.quantity < 0:
            raise ValueError("Adjustment would result in negative stock quantity.")
        stock_record.save(update_fields=["quantity", "updated_at"])
        StockMovement.objects.create(
            stock_record=stock_record,
            movement_type=StockMovement.MovementType.ADJUSTMENT,
            quantity_change=delta,
            notes=notes,
            performed_by=performed_by,
        )
