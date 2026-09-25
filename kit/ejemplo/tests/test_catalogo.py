import json
import unittest

from catalogo.export import export_catalog


class ExportTests(unittest.TestCase):
    def test_EXP_001_exporta_un_elemento_por_libro_activo(self):
        text, _ = export_catalog([{"id": 1, "titulo": "A"}, {"id": 2, "titulo": "B"}])
        self.assertEqual([b["id"] for b in json.loads(text)], [1, 2])

    def test_EXP_002_libro_sin_titulo_falla_nombrando_id_y_campo(self):
        with self.assertRaises(ValueError) as cm:
            export_catalog([{"id": 7, "titulo": "  "}])
        self.assertIn("7", str(cm.exception))
        self.assertIn("titulo", str(cm.exception))

    def test_EXP_003_catalogo_vacio(self):
        text, msg = export_catalog([])
        self.assertEqual(json.loads(text), [])
        self.assertEqual(msg, "0 libros exportados")

    def test_EXP_004_excluye_retirados(self):
        text, _ = export_catalog([{"id": 1, "titulo": "A", "retirado": True}, {"id": 2, "titulo": "B"}])
        self.assertEqual([b["id"] for b in json.loads(text)], [2])


if __name__ == "__main__":
    unittest.main()
