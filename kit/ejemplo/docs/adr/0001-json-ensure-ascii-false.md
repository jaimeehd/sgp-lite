# ADR-0001: Exportar JSON con caracteres UTF-8 sin escapar

**Fecha:** 2026-09-17 · **Estado:** Aceptada

**Contexto:** el catálogo tiene títulos con tildes y eñes; el sitio web consume el JSON directamente.

**Opciones:**
1. `ensure_ascii=True` (por defecto de `json`): compatible con cualquier parser, pero produce `\\u00f1` y dificulta revisar el archivo a simple vista.
2. `ensure_ascii=False`: el archivo queda legible; requiere que el consumidor lea en UTF-8.

**Decisión:** opción 2. El sitio ya sirve en UTF-8 y la legibilidad del archivo pesa más para el mantenimiento manual ocasional.

**Consecuencias:** positivas: diffs legibles en git. Negativas/deuda: si algún día se consume desde un sistema que no declare UTF-8, habrá que revisar esta decisión.

**Criterios de revisión:** si se añade un consumidor que no soporte UTF-8.
