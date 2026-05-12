"""Tests for order tasks."""

from unittest.mock import patch

import pytest

from shopforge.apps.orders.tasks import send_daily_order_summary, send_order_confirmation_email


@pytest.mark.django_db
class TestOrderTasks:
    """Test order-related Celery tasks."""

    @patch("shopforge.apps.orders.tasks.send_mail")
    def test_send_order_confirmation_email(self, mock_send_mail, order):
        """Test that confirmation email is sent with correct subject and recipient."""
        send_order_confirmation_email(str(order.id))

        mock_send_mail.assert_called_once()
        call_kwargs = mock_send_mail.call_args[1]
        assert order.order_number in call_kwargs["subject"]
        assert order.customer.email in call_kwargs["recipient_list"]

    def test_send_order_confirmation_email_nonexistent_order(self):
        """Graceful handling of missing order — must not raise."""
        # Should just log and return, never raise.
        send_order_confirmation_email("00000000-0000-0000-0000-000000000000")

    @patch("shopforge.apps.orders.tasks.send_mail")
    def test_send_daily_order_summary_sends_email(self, mock_send_mail, order):
        """Daily summary sends one email regardless of order count."""
        send_daily_order_summary()
        mock_send_mail.assert_called_once()

    @patch("shopforge.apps.orders.tasks.send_mail")
    def test_send_daily_order_summary_no_orders(self, mock_send_mail):
        """Daily summary still sends even when there are no orders."""
        send_daily_order_summary()
        mock_send_mail.assert_called_once()
