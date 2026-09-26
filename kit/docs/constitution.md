# Constitucion — <proyecto>

Principios innegociables (max. 15 lineas). Cada uno declara como se verifica.

1. **La spec manda**: ningun comportamiento se implementa sin un requisito en `specs/`. Si falta una decision, se para y se pregunta. Verificado por: estructura (`sgp_check`) y revision humana.
2. **Tests como puerta**: cada tarea termina con sus pruebas en verde. Verificado por: tests.
3. **Las pruebas no se borran ni se debilitan** para hacer pasar el trabajo sin aprobacion explicita. Verificado por: ratchet.
4. **Cambios pequeños**: una tarea, una sesion, un commit. Verificado por: humano.
5. **Sin dependencias nuevas** sin actualizar antes la spec o un ADR. Verificado por: humano.
6. **Nada de secretos** en el repositorio. Verificado por: humano.
