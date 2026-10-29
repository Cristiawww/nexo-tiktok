# Verificación manual del capturador de Chrome

1. Carga la extensión sin empaquetar desde `chrome://extensions`.
2. Abre un perfil público visible en Chrome; pulsa el icono NEXO y selecciona Guardar página actual.
3. Deberías ver `@usuario guardada` y el número de videos localizados; si es cero, desplázate por el perfil y repite.
4. Abre una publicación pública, pulsa Guardar página actual y verifica que aumente la información del video. Solo se almacenan comentarios públicos visibles sin nombres de autores.
5. Exporta JSON y comprueba que contenga `perfiles` y `videos`; no debe incluir cookies ni contraseñas.
6. Importa JSON en la aplicación Streamlit y revisa Comparar, Videos y Elección.

*El capturador nunca garantiza likes individuales desde la cuadrícula ni comentarios de videos no abiertos. No accede a endpoints privados.*
