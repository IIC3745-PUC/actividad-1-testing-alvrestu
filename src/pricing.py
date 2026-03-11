from __future__ import annotations
from typing import Iterable, Optional
from .models import CartItem


class PricingError(ValueError):
    pass


class PricingService:
    def subtotal_cents(self, items: Iterable[CartItem]) -> int:
        total = 0
        for it in items:
            if it.qty <= 0:
                raise PricingError("qty must be > 0")
            if it.unit_price_cents < 0:
                raise PricingError("unit_price_cents must be >= 0")
            total += it.unit_price_cents * it.qty
        return total

    def apply_coupon(self, subtotal: int, coupon_code: Optional[str]) -> int:
        """
        Cupones:
          - None o "" o puros espacios "  ": no aplica descuento
          - "SAVE10"  : 10% descuento (redondeo hacia abajo)
          - "CLP2000" : $2000 descuento fijo (no baja de 0)
          - otro      : error
        """
        if not coupon_code or coupon_code.strip(" ") == "":
            return subtotal

        code = coupon_code.strip().upper()
        if code == "SAVE10":
            return subtotal - (subtotal * 10 // 100)
        if code == "CLP2000":
            return max(0, subtotal - 2000)

        raise PricingError("invalid coupon")

    def tax_cents(self, net_subtotal: int, country: str) -> int:
        """
        Impuestos simplificados:
          - CL: 19%
          - US: 0%
          - EU: 21%
        """
        c = country.strip().upper()
        if c == "CL":
            return net_subtotal * 19 // 100
        if c == "EU":
            return net_subtotal * 21 // 100
        if c == "US":
            return 0
        raise PricingError("unsupported country")

    def shipping_cents(self, net_subtotal: int, country: str) -> int:
        """
        Envío:
          - CL: 0 si net_subtotal >= 20000; si no, 2500
          - US/EU: 5000 fijo
        """
        c = country.strip().upper()
        if c == "CL":
            return 0 if net_subtotal >= 20000 else 2500
        if c in ("US", "EU"):
            return 5000
        raise PricingError("unsupported country")

    def total_cents(self, items: Iterable[CartItem], coupon_code: Optional[str], country: str) -> int:
        sub = self.subtotal_cents(items)
        net = self.apply_coupon(sub, coupon_code)
        return net + self.tax_cents(net, country) + self.shipping_cents(net, country)
