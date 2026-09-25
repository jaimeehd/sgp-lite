"""Cálculo de precio final con descuento (ejemplo de referencia de SGP)."""
from decimal import Decimal, ROUND_HALF_UP


def precio_final(precio_lista, descuento_pct):
    """DESC-001..005: precio con descuento, validado y redondeado half-up a 2 decimales."""
    if not (0 <= descuento_pct <= 100):
        raise ValueError(f"el descuento debe estar entre 0 y 100, se recibió {descuento_pct}")
    if precio_lista < 0:
        raise ValueError(f"el precio de lista no puede ser negativo, se recibió {precio_lista}")
    bruto = Decimal(str(precio_lista)) * (Decimal(1) - Decimal(str(descuento_pct)) / Decimal(100))
    return float(bruto.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP))
