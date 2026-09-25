import unittest
from descuento.calculo import precio_final


class CalculoTests(unittest.TestCase):
    def test_DESC_001_calcula_precio_con_descuento_redondeado(self):
        self.assertEqual(precio_final(19.999, 15), 17.0)

    def test_DESC_005_sin_descuento_devuelve_el_precio_de_lista(self):
        self.assertEqual(precio_final(19.999, 0), 20.0)

    def test_DESC_002_descuento_fuera_de_rango_falla_con_el_valor(self):
        with self.assertRaises(ValueError) as cm:
            precio_final(20, 150)
        self.assertIn("150", str(cm.exception))

    def test_DESC_003_precio_negativo_falla(self):
        with self.assertRaises(ValueError):
            precio_final(-5, 10)

    def test_DESC_004_nunca_negativo_ni_mas_de_2_decimales(self):
        resultado = precio_final(10.005, 100)
        self.assertGreaterEqual(resultado, 0)
        self.assertEqual(resultado, round(resultado, 2))


    def test_regresion_CHG002_redondeo_half_up(self):
        # round() nativo da 2.67 (banker's); DESC-001/DESC-004 exigen half-up (acordado en QA de la spec)
        self.assertEqual(precio_final(2.675, 0), 2.68)


if __name__ == "__main__":
    unittest.main()
