"""Exportación del catálogo a JSON (ejemplo de referencia de SGP)."""
import json

REQUIRED = ("titulo",)


def export_catalog(books):
    """Devuelve (json_text, mensaje). Lanza ValueError si un libro activo es inválido."""
    active = [b for b in books if not b.get("retirado", False)]
    for b in active:
        for field in REQUIRED:
            if not str(b.get(field, "")).strip():
                raise ValueError(f"libro {b.get('id', '?')}: falta el campo «{field}»")
    return json.dumps(active, ensure_ascii=False, indent=2), f"{len(active)} libros exportados"
