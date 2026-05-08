"""Tests for order tasks."""

from unittest.mock import patch

import pytest

from shopforge.apps.orders.tasks import send_order_confirmation_email


@pytest.mark.django_db
class TestOrderTasks:
    """Test order-related Celery tasks."""

    @patch("shopforge.apps.orders.tasks.send_mail")
    def test_send_order_confirmation_email(self, mock_send_mail, order_factory):
        """Test that confirmation email is sent with correct data."""
        order = order_factory()

        # Call synchronously (not .delay()) in tests
        send_order_confirmation_email(str(order.id))

        mock_send_mail.assert_called_once()
        call_kwargs = mock_send_mail.call_args[1]
        assert order.order_number in call_kwargs["subject"]
        assert order.customer.email in call_kwargs["recipient_list"]

    def test_send_order_confirmation_email_nonexistent_order(self):
        """Test graceful handling of missing order."""
        # Should not raise — just logs an error
        send_order_confirmation_email("00000000-0000-0000-0000-000000000000")
