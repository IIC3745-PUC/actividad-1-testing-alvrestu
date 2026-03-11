from typing import Optional

class CartItem:
	def __init__(self, sku: str, unit_price_cents: int, qty: int):
		# pragma: no cover
		self.sku = sku
		self.unit_price_cents = unit_price_cents
		self.qty = qty

class Order:
	def __init__(
		self,
		order_id: str,
		user_id: str,
		total_cents: int,
		payment_charge_id: str,
		coupon_code: Optional[str] = None,
		country: str = "CL",
	):
		# pragma: no cover
		self.order_id = order_id
		self.user_id = user_id
		self.total_cents = total_cents
		self.payment_charge_id = payment_charge_id
		self.coupon_code = coupon_code
		self.country = country
		
