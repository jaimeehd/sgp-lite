# Spec — catalogo

## Contexto y objetivo
Publicar el catalogo en el sitio web exige copiar datos a mano y produce errores. Se necesita un JSON del catalogo generado de forma fiable.

## Requisitos
- **EXP-001** CUANDO se exporta un catalogo cuyos libros activos tienen todos los campos obligatorios, EL SISTEMA generara un JSON con un elemento por libro activo (salida 0).
- **EXP-002** SI un libro activo no tiene titulo, ENTONCES EL SISTEMA no generara el JSON y mostrara un error con el identificador del libro y el campo faltante (salida 1).
- **EXP-003** MIENTRAS no haya libros activos, EL SISTEMA generara una lista vacia e informara «0 libros exportados» (salida 0).
- **EXP-004** EL SISTEMA no incluira en la exportacion los libros marcados como retirados.

## Fuera de alcance
- Sincronizacion automatica con el sitio, exportar imagenes, formatos distintos de JSON.
