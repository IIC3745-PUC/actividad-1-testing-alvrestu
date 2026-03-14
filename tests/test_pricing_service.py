import unittest
from unittest.mock import Mock

from src.models import CartItem, Order
from src.pricing import PricingService, PricingError

class TestPricingService(unittest.TestCase):
	def setUp(self):
		self.pricing = PricingService()
	
	#Test 1: Test subtotal_cents con items válidos
	def test_subtotal_cents_items_validos(self):
		items = [
			CartItem("A", 1000, 2),
			CartItem("B", 3000, 3)
		]
		self.assertEqual(self.pricing.subtotal_cents(items), 11000)
	
	#Test 2: Test subtotal_cents con qty <= 0
	def test_subtotal_cents_qty_invalida(self):
		items = [
			CartItem("A", 4000, 0)
		]
		with self.assertRaisesRegex(PricingError, "qty must be > 0"):
			self.pricing.subtotal_cents(items)
	
	#Test 3: Test subtotal_cents con unit_price_cents < 0
	def test_subtotal_cents_unit_price_invalido(self):
		items = [
			CartItem("A", -1000, 2)
		]
		with self.assertRaisesRegex(PricingError, "unit_price_cents must be >= 0"):
			self.pricing.subtotal_cents(items)
	
	#Test 4: Test apply_coupon con cupon SAVE10
	def test_apply_coupon_save10(self):
		subtotal = 10000
		coupon_code = "SAVE10"
		self.assertEqual(self.pricing.apply_coupon(subtotal, coupon_code), 9000)
	
	#Test 5: Test apply_coupon con cupon CLP2000
	def test_apply_coupon_clp2000(self):
		subtotal = 10000
		coupon_code = "CLP2000"
		self.assertEqual(self.pricing.apply_coupon(subtotal, coupon_code), 8000)
	
	#Test 6: Test apply_coupon con cupon vacio
	def test_apply_coupon_vacio(self):
		subtotal = 10000
		coupon_code = ""
		self.assertEqual(self.pricing.apply_coupon(subtotal, coupon_code), 10000)
	
	#Test 7: Test apply_coupon con cupon espacio
	def test_apply_coupon_espacio(self):
		subtotal = 10000
		coupon_code = "  "
		self.assertEqual(self.pricing.apply_coupon(subtotal, coupon_code), 10000)

	#Test 8: Test apply_coupon con cupon None
	def test_apply_coupon_none(self):
		subtotal = 10000
		coupon_code = None
		self.assertEqual(self.pricing.apply_coupon(subtotal, coupon_code), 10000)

	#Test 9: Test apply_coupon con cupon inválido
	def test_apply_coupon_invalido(self):
		subtotal = 10000
		coupon_code = "INVALID"
		with self.assertRaisesRegex(PricingError, "invalid coupon"):
			self.pricing.apply_coupon(subtotal, coupon_code)

	#Test 10: Test tax_cents con país CL
	def test_tax_cents_cl(self):
		net_subtotal = 10000
		country = "CL"
		self.assertEqual(self.pricing.tax_cents(net_subtotal, country), 1900)

	#Test 11: Test tax_cents con país EU
	def test_tax_cents_eu(self):
		net_subtotal = 10000
		country = "EU"
		self.assertEqual(self.pricing.tax_cents(net_subtotal, country), 2100)

	#Test 12: Test tax_cents con país US
	def test_tax_cents_us(self):
		net_subtotal = 10000
		country = "US"
		self.assertEqual(self.pricing.tax_cents(net_subtotal, country), 0)

	#Test 13: Test tax_cents con país inválido
	def test_tax_cents_pais_invalido(self):
		net_subtotal = 10000
		country = "XX"
		with self.assertRaisesRegex(PricingError, "unsupported country"):
			self.pricing.tax_cents(net_subtotal, country)

	#Test 14: Test shipping_cents con país CL y net_subtotal >= 20000
	def test_shipping_cents_cl_gratis(self):
		net_subtotal = 20000
		country = "CL"
		self.assertEqual(self.pricing.shipping_cents(net_subtotal, country), 0)

	#Test 15: Test shipping_cents con país CL y net_subtotal < 20000
	def test_shipping_cents_cl_pago(self):
		net_subtotal = 19999
		country = "CL"
		self.assertEqual(self.pricing.shipping_cents(net_subtotal, country), 2500)

	#Test 16: Test shipping_cents con país US
	def test_shipping_cents_us(self):
		net_subtotal = 10000
		country = "US"
		self.assertEqual(self.pricing.shipping_cents(net_subtotal, country), 5000)

	#Test 17: Test shipping_cents con país EU
	def test_shipping_cents_eu(self):
		net_subtotal = 10000
		country = "EU"
		self.assertEqual(self.pricing.shipping_cents(net_subtotal, country), 5000)

	#Test 18: Test shipping_cents con país inválido
	def test_shipping_cents_pais_invalido(self):
		net_subtotal = 10000
		country = "XX"
		with self.assertRaisesRegex(PricingError, "unsupported country"):
			self.pricing.shipping_cents(net_subtotal, country)

	#Test 19: Test integración subtotal + coupon + tax + shipping
	def test_integracion_completa(self):
		items = [
			CartItem("A", 1000, 2),  # 2000
			CartItem("B", 3000, 3)   # 9000
		]
		subtotal = self.pricing.subtotal_cents(items)  # 11000
		net_subtotal = self.pricing.apply_coupon(subtotal, "SAVE10")  # 9900
		tax = self.pricing.tax_cents(net_subtotal, "CL")  # 1881
		shipping = self.pricing.shipping_cents(net_subtotal, "CL")  # 2500
		total = net_subtotal + tax + shipping  # 14281
		self.assertEqual(total, 14281)	
	pass
