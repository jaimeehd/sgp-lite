# Constitución — <proyecto>

Principios innegociables (máx. 15 líneas). Cada uno declara cómo se verifica.

1. **La spec manda**: ningún comportamiento se implementa sin un requisito en `specs/`. Si falta una decisión, se para y se pregunta. Verificado por: estructura (`sgp_check`) y revisión humana.
2. **Tests como puerta**: cada tarea termina con sus pruebas en verde. Verificado por: tests.
3. **Las pruebas no se borran ni se debilitan** para hacer pasar el trabajo sin aprobación explícita. Verificado por: ratchet.
4. **Cambios pequeños**: una tarea, una sesión, un commit. Verificado por: humano.
5. **Sin dependencias nuevas** sin actualizar antes la spec o un ADR. Verificado por: humano.
6. **Nada de secretos** en el repositorio. Verificado por: humano.
