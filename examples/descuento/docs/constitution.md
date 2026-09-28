# Constitución — descuento-librodemo

1. **La spec manda**: ningún cálculo se implementa sin un requisito en `specs/`. Verificado por: estructura (`sgp_check`) y revisión humana.
2. **Tests como puerta**: cada tarea termina con sus pruebas en verde. Verificado por: tests.
3. **Las pruebas no se borran ni se debilitan** sin aprobación explícita. Verificado por: ratchet.
4. **Los precios nunca quedan negativos ni con más de 2 decimales.** Verificado por: tests.
5. **Solo biblioteca estándar** (sin dependencias externas). Verificado por: humano.
