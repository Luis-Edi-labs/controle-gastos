import unittest

from gastos import formatar, ler_valor, total_do_mes


class TestGastos(unittest.TestCase):
    def test_ler_valor_aceita_virgula_e_ponto(self):
        self.assertEqual(ler_valor("25,50"), 25.5)
        self.assertEqual(ler_valor(" 10.00 "), 10.0)

    def test_ler_valor_recusa_invalidos(self):
        for texto in ["", "abc", "0", "-5", "inf", "nan"]:
            self.assertIsNone(ler_valor(texto), texto)

    def test_ler_valor_zero_no_limite(self):
        self.assertEqual(ler_valor("0", aceita_zero=True), 0)

    def test_total_do_mes_soma_so_o_mes_pedido(self):
        gastos = [
            {"valor": 10.0, "data": "05/11/2026"},
            {"valor": 20.0, "data": "30/11/2026"},
            {"valor": 99.0, "data": "01/10/2026"},
        ]
        self.assertEqual(total_do_mes(gastos, "11/2026"), 30.0)

    def test_formatar_usa_virgula(self):
        self.assertEqual(formatar(1234.5), "1234,50")


if __name__ == "__main__":
    unittest.main()
