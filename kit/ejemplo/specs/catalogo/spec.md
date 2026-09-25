# Spec — catálogo

## Contexto y objetivo
Publicar el catálogo en el sitio web exige copiar datos a mano y produce errores. Se necesita un JSON del catálogo generado de forma fiable.

## Requisitos
- **EXP-001** CUANDO se exporta un catálogo cuyos libros activos tienen todos los campos obligatorios, EL SISTEMA generará un JSON con un elemento por libro activo (salida 0).
- **EXP-002** SI un libro activo no tiene título, ENTONCES EL SISTEMA no generará el JSON y mostrará un error con el identificador del libro y el campo faltante (salida 1).
- **EXP-003** MIENTRAS no haya libros activos, EL SISTEMA generará una lista vacía e informará «0 libros exportados» (salida 0).
- **EXP-004** EL SISTEMA no incluirá en la exportación los libros marcados como retirados.

## Fuera de alcance
- Sincronización automática con el sitio, exportar imágenes, formatos distintos de JSON.
