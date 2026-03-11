from __future__ import annotations

from typing import Protocol, Optional, Iterable
import uuid

from .models import CartItem, Order
from .pricing import PricingService, PricingError


class ChargeResult:
    def __init__(self, ok: bool, charge_id=None, reason=None):
        self.ok = ok
        self.charge_id = charge_id
        self.reason = reason


class PaymentGateway(Protocol):
    def charge(self, user_id: str, amount_cents: int, payment_token: str) -> ChargeResult: ...  # pragma: no cover


class EmailService(Protocol):
    def send_receipt(self, user_id: str, order_id: str, total_cents: int) -> None: ...  # pragma: no cover


class FraudScorer(Protocol):
    def score(self, user_id: str, total_cents: int) -> int: ...  # pragma: no cover


class OrderRepo(Protocol):
    def save(self, order: Order) -> None: ...  # pragma: no cover


class CheckoutService:
    """
    - Calcula total usando PricingService
    - Rechaza si fraude >= 80
    - Cobra con PaymentGateway
    - Guarda orden y envía recibo
    """
    def __init__(
        self,
        payments: PaymentGateway,
        email: EmailService,
        fraud: FraudScorer,
        repo: OrderRepo,
        pricing: Optional[PricingService] = None,
    ):
        self.payments = payments
        self.email = email
        self.fraud = fraud
        self.repo = repo
        self.pricing = pricing or PricingService()

    def checkout(
        self,
        user_id: str,
        items: Iterable[CartItem],
        payment_token: str,
        country: str,
        coupon_code: Optional[str] = None,
    ) -> str:
        if not user_id.strip():
            return "INVALID_USER"

        try:
            amount = self.pricing.total_cents(items, coupon_code, country)
        except PricingError as e:
            return f"INVALID_CART:{e}"

        if self.fraud.score(user_id, amount) >= 80:
            return "REJECTED_FRAUD"

        result = self.payments.charge(user_id=user_id, amount_cents=amount, payment_token=payment_token)
        if not result.ok:
            return f"PAYMENT_FAILED:{result.reason}"

        order_id = str(uuid.uuid4())
        order = Order(
            order_id=order_id,
            user_id=user_id,
            total_cents=amount,
            payment_charge_id=result.charge_id or "UNKNOWN",
            coupon_code=coupon_code,
            country=country.strip().upper(),
        )

        self.repo.save(order)
        self.email.send_receipt(user_id, order_id, amount)
        return f"OK:{order_id}"
