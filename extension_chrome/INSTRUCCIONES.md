# NEXO · Analizar hasta diez videos de un perfil

La extensión actúa solamente después de pulsar **Analizar hasta 10 videos** en Chrome normal.

1. En `chrome://extensions`, activa **Modo desarrollador** y selecciona **Cargar descomprimida**. Indica la carpeta `extension_chrome` (contiene `manifest.json`). Si ya tenías instalada la versión anterior, pulsa **Actualizar** o el icono de recarga de la extensión; no necesitas instalar otra copia.
2. Abre en Chrome normal un perfil **público** `https://www.tiktok.com/@usuario`, con tu sesión ya iniciada si acostumbras usarla.
3. Abre NEXO desde el icono de extensiones y pulsa **Analizar hasta 10 videos**. La extensión desplaza la cuadrícula para encontrar publicaciones y abre automáticamente, una a una, hasta diez páginas de video en pestañas que cierra al terminar. No hay que introducir enlaces.
4. Puedes cerrar el menú de la extensión: el progreso y los perfiles se conservan en almacenamiento local. Reabre el menú para ver resultados o detener la consulta.
5. Repite para otras cuentas públicas (máximo cinco). Haz clic en **Exportar para NEXO** y guarda `nexo_captura_chrome.json`.
6. En el frontend (`streamlit run app.py`), entra en **Cuentas**, importa ese archivo, indica el producto o sector y abre **Comparar → Videos → Elección**.

**Importante:** si la cuenta incluye publicaciones fijadas o si faltan fechas, la extensión devuelve las diez primeras publicaciones **visibles**, no puede demostrar que sean las diez más recientes cronológicamente. Si TikTok no carga una cuadrícula o una publicación, el JSON indicará que faltan datos. El clic no garantiza diez videos con todas las métricas. Los comentarios se limitan a los visibles y se almacenan sin nombre de comentarista. No se descargan MP4 ni cookies. No se accede a perfiles privados, endpoints privados ni se sortea el error HTTP 403 de Playwright.

No publiques las capturas ni datos de sesión sin revisar antes su contenido; los archivos JSON pueden contener textos de comentarios públicos. La extensión no lee contraseñas ni cookies ni envía datos a un servidor propio.
