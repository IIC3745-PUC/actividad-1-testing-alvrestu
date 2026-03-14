import unittest
from unittest.mock import Mock

from src.models import CartItem, Order
from src.pricing import PricingService, PricingError
from src.checkout import CheckoutService, ChargeResult

class TestCheckoutService(unittest.TestCase):
	def make_service(self, pricing=None):
		self.payments = Mock()
		self.email = Mock()
		self.fraud = Mock()
		self.repo = Mock()
		service = CheckoutService(
			payments=self.payments,
			email=self.email,
			fraud=self.fraud,
			repo=self.repo,
			pricing=pricing,
		)
		return service
	
	#Test 1: Usuario invalido
	def test_checkout_invalid_user(self):
		service = self.make_service(pricing=Mock())
		result = service.checkout(
			user_id="",
			items=[CartItem("p1", 1000, 1)],
			payment_token="token",
			country="US",
		)
		self.assertEqual(result, "INVALID_USER")
		#Verificamos que los mock no fueron ejecutados
		service.pricing.total_cents.assert_not_called()
		self.fraud.score.assert_not_called()
		self.payments.charge.assert_not_called()
		self.repo.save.assert_not_called()
		self.email.send_receipt.assert_not_called()
	
	#Test 2: invalid cart por falla de pricing
	def test_checkout_invalid_cart(self):
		pricing = Mock()
		pricing.total_cents.side_effect = PricingError("Invalid cart")
		service = self.make_service(pricing=pricing)
		result = service.checkout(
			user_id="user1",
			items=[CartItem("p1", 1000, 1)],
			payment_token="token",
			country="US",
		)
		self.assertEqual(result, "INVALID_CART:Invalid cart")
		pricing.total_cents.assert_called_once()
		self.fraud.score.assert_not_called()
		self.payments.charge.assert_not_called()
		self.repo.save.assert_not_called()
		self.email.send_receipt.assert_not_called()
	
	#Test 3: Rechazo por fraude
	def test_checkout_rejected_fraud(self):
		pricing = Mock()
		pricing.total_cents.return_value = 1000
		service = self.make_service(pricing=pricing)
		self.fraud.score.return_value = 85
		result = service.checkout(
			user_id="user1",
			items=[CartItem("p1", 1000, 1)],
			payment_token="token",
			country="US",
		)
		self.assertEqual(result, "REJECTED_FRAUD")
		pricing.total_cents.assert_called_once()
		self.fraud.score.assert_called_once_with("user1", 1000)
		self.payments.charge.assert_not_called()
		self.repo.save.assert_not_called()
		self.email.send_receipt.assert_not_called()
	
	#Test 4: Payment failure
	def test_checkout_payment_failure(self):
		pricing = Mock()
		pricing.total_cents.return_value = 1000
		service = self.make_service(pricing=pricing)
		self.payments.charge.return_value = ChargeResult(ok=False, charge_id=None, reason="DECLINED")
		self.fraud.score.return_value = 30
		result = service.checkout(
			user_id="user1",
			items=[CartItem("p1", 1000, 1)],
			payment_token="token",
			country="US",
		)
		self.assertEqual(result, "PAYMENT_FAILED:DECLINED")
		pricing.total_cents.assert_called_once()
		self.fraud.score.assert_called_once_with("user1", 1000)
		self.payments.charge.assert_called_once_with(user_id="user1", amount_cents=1000, payment_token="token")
		self.repo.save.assert_not_called()
		self.email.send_receipt.assert_not_called()
	pass
