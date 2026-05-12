"""Tests for Inventory API endpoints."""

import pytest
from model_bakery import baker


@pytest.mark.django_db
class TestStockRecordViewSet:
    """Admin-only stock management endpoints."""

    def test_list_requires_admin(self, authenticated_client):
        response = authenticated_client.get("/api/inventory/")
        assert response.status_code == 403

    def test_list_for_admin(self, admin_client, product_with_stock):
        response = admin_client.get("/api/inventory/")
        assert response.status_code == 200
        assert response.data["count"] >= 1

    def test_adjust_increases_stock(self, admin_client, product_with_stock):
        """POST /api/inventory/{id}/adjust/ with positive delta increases quantity."""
        stock = product_with_stock.stock
        old_qty = stock.quantity
        response = admin_client.post(
            f"/api/inventory/{stock.id}/adjust/",
            {"delta": 10, "notes": "Received new shipment"},
            format="json",
        )
        assert response.status_code == 200
        stock.refresh_from_db()
        assert stock.quantity == old_qty + 10

    def test_adjust_negative_beyond_zero_is_rejected(self, admin_client, product_with_stock):
        """Stock cannot go below zero."""
        stock = product_with_stock.stock
        response = admin_client.post(
            f"/api/inventory/{stock.id}/adjust/",
            {"delta": -(stock.quantity + 999), "notes": "Bad adjustment"},
            format="json",
        )
        assert response.status_code == 400

    def test_movements_returns_audit_log(self, admin_client, product_with_stock):
        """GET /api/inventory/{id}/movements/ returns movement history."""
        from shopforge.apps.inventory.models import StockMovement

        stock = product_with_stock.stock
        baker.make(
            StockMovement,
            stock_record=stock,
            movement_type=StockMovement.MovementType.RECEIVED,
            quantity_change=50,
            reference="PO-001",
        )
        response = admin_client.get(f"/api/inventory/{stock.id}/movements/")
        assert response.status_code == 200
        assert len(response.data) >= 1


@pytest.mark.django_db
class TestInventoryService:
    """Unit tests for InventoryService business logic."""

    def test_reserve_decrements_available(self, product_with_stock):
        from shopforge.apps.inventory.services import InventoryService

        stock = product_with_stock.stock
        before_reserved = stock.reserved_quantity
        InventoryService.reserve(product_with_stock, 5, "SF-TEST-001")
        stock.refresh_from_db()
        assert stock.reserved_quantity == before_reserved + 5

    def test_reserve_raises_when_insufficient(self, product_with_stock):
        from shopforge.apps.inventory.services import InventoryService

        with pytest.raises(ValueError, match="Insufficient"):
            InventoryService.reserve(product_with_stock, 9999, "SF-TEST-002")

    def test_release_decrements_reserved(self, product_with_stock):
        from shopforge.apps.inventory.services import InventoryService

        stock = product_with_stock.stock
        InventoryService.reserve(product_with_stock, 10, "SF-TEST-003")
        stock.refresh_from_db()
        before = stock.reserved_quantity
        InventoryService.release(product_with_stock, 10, "SF-TEST-003")
        stock.refresh_from_db()
        assert stock.reserved_quantity == before - 10

    def test_fulfill_creates_sold_movement(self, product_with_stock):
        from shopforge.apps.inventory.models import StockMovement
        from shopforge.apps.inventory.services import InventoryService

        InventoryService.reserve(product_with_stock, 3, "SF-TEST-004")
        InventoryService.fulfill(product_with_stock, 3, "SF-TEST-004")
        assert StockMovement.objects.filter(
            stock_record__product=product_with_stock,
            movement_type=StockMovement.MovementType.SOLD,
            reference="SF-TEST-004",
        ).exists()

    def test_fulfill_is_idempotent(self, product_with_stock):
        """Calling fulfill twice for the same order should only create one SOLD movement."""
        from shopforge.apps.inventory.models import StockMovement
        from shopforge.apps.inventory.services import InventoryService

        InventoryService.reserve(product_with_stock, 3, "SF-TEST-005")
        InventoryService.fulfill(product_with_stock, 3, "SF-TEST-005")
        InventoryService.fulfill(product_with_stock, 3, "SF-TEST-005")  # idempotent
        count = StockMovement.objects.filter(
            stock_record__product=product_with_stock,
            movement_type=StockMovement.MovementType.SOLD,
            reference="SF-TEST-005",
        ).count()
        assert count == 1
