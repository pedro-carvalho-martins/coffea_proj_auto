import unittest

from paymentProcessing import _parse_moderninha_output, _status_from_result


SAMPLE_OUTPUT = """
VENDA

RETORNO: 0

Transaction Result
	message [Transacao aprovada]
	transactionCode [ABC123]
	date [2026-08-01]
	time [12:34:56]
	hostNsu [123456789012]
	cardBrand [VISA]
	bin [123456]
	holder [9876]
	user reference [ABCDEFGHIJ]
"""


class PaymentProcessingTests(unittest.TestCase):
    def test_parser_keeps_selected_fields_and_omits_bin(self):
        result = _parse_moderninha_output(SAMPLE_OUTPUT)

        self.assertEqual(result["return_code"], 0)
        self.assertEqual(result["host_nsu"], "123456789012")
        self.assertEqual(result["card_brand"], "VISA")
        self.assertEqual(result["card_last_four"], "9876")
        self.assertEqual(result["user_reference"], "ABCDEFGHIJ")
        self.assertNotIn("bin", result)

    def test_status_mapping_distinguishes_normal_outcomes(self):
        self.assertEqual(_status_from_result(0, "APROVADA"), "concluida")
        self.assertEqual(_status_from_result(-1004, "OPERACAO CANCELADA"), "cancelada")
        self.assertEqual(_status_from_result(-1004, "TRANSACAO NEGADA"), "recusada")
        self.assertEqual(_status_from_result(-1019, "ERRO DE COMUNICACAO"), "resultado_desconhecido")
        self.assertEqual(_status_from_result(-1010, "DRIVER AUSENTE"), "falha")


if __name__ == "__main__":
    unittest.main()
