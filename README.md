# NEXO / Colaboraciones

**Scraper real de TikTok + ranking comercial + diseño para Figma.** Proyecto nuevo, independiente de `perfiles-tiktok` y de versiones previas de NEXO. No se crean cuentas ni métricas simuladas.

## Instalar y abrir en Windows

1. Extrae el ZIP y abre **la carpeta que contiene `app.py` y `requirements.txt`** en VS Code. Por ejemplo, `C:\Users\andya\Downloads\NEXO_ENTREGA_DEFINITIVA`.
2. En esa carpeta, abre la terminal PowerShell:

```powershell
py -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m playwright install chromium
```

3. **Cierra Streamlit antes de iniciar sesión** y abre tu propia sesión en el perfil local de Playwright:

```powershell
.\.venv\Scripts\python.exe sesion.py
```

Se abre Chrome instalado (canal `chrome`) con un perfil **separado del Chrome habitual**. Inicia sesión manualmente si la página permite acceso. Vuelve a PowerShell y pulsa Enter para cerrar el navegador. Se guardarán cookies y almacenamiento local en `.nexo_session/`. **No exportes ni compartas esta carpeta.** Si Chrome no está disponible, instala Chromium con el comando anterior, y opcionalmente en PowerShell:

```powershell
$env:NEXO_NAVEGADOR="chromium"
.\.venv\Scripts\python.exe sesion.py
```

4. Abre Streamlit:

```powershell
.\.venv\Scripts\python.exe -m streamlit run app.py
```

Abre http://localhost:8501. Escribe un producto concreto y entre 1 y 5 usuarios públicos de TikTok (un `@usuario` por línea) y presiona **Analizar cuentas**. El programa lee hasta diez videos visibles por cuenta, en secuencia; puede recuperar menos según la respuesta del sitio. La sesión de Playwright **no debe estar abierta en dos procesos al mismo tiempo**.

## Si recibes HTTP 403 en Playwright

No significa que se haya iniciado sesión. TikTok está rechazando el acceso a ese navegador, y una sesión persistente **no garantiza corregirlo**. NEXO se detiene ante 403/429, no intenta evadirlo.

Si TikTok funciona en Chrome normal, tienes la **captura local alternativa**, incluida en `extension_chrome/`:

1. Abre `chrome://extensions`, activa modo desarrollador, selecciona **Cargar descomprimida** y elige `extension_chrome`.
2. Abre un perfil público de TikTok en Chrome normal, pulsa NEXO → **Analizar hasta 10 videos**. La extensión lee lo que la página permite ver y abre las publicaciones encontradas de forma secuencial.
3. Repite con otras cuentas si procede, exporta el JSON y en **Cuentas → Archivo JSON** impórtalo.

Esto permite comparar **datos reales observados en Chrome**, sin copiar cookies entre navegadores ni introducir links de video manualmente. Si faltan likes o comentarios, se marcarán como no disponibles. **No es un scraper Playwright cuando se utiliza esta ruta alternativa.**

## Pantallas

- **Cuentas:** tema, usuarios, consulta Playwright, importación de JSON real.
- **Ranking:** tabla comparativa y medianas observadas.
- **Videos:** vistas, likes, comentarios visibles y exportación CSV.
- **Campaña:** candidata si existe evidencia mínima; si falta, no se inventa un ganador.

### Cinco criterios comerciales (propuesta propia)

Afinidad (35 %), alcance (25 %), interacción (20 %), conversación (10 %), cobertura (10 %). El programa normaliza y puede excluir un criterio no comparable. Exige al menos **tres videos con vistas y likes** y evidencia textual de afinidad para puntuar; no predice ventas.

### Big Five / OCEAN

El **Big Five** académico es el modelo de personalidad OCEAN, no estas cinco métricas comerciales. No permite inferir la personalidad de un creador a partir de seguidores, likes, comentarios o biografía. En Figma se estudia como marco de investigación que **requeriría respuestas voluntarias a un instrumento válido**; no se presenta como resultado medido de TikTok.

### Ley de Benford

Se presenta en Figma como contraste estadístico exploratorio teórico. Una muestra de cinco cuentas o diez videos por cuenta no garantiza las condiciones de aplicación. No determina autenticidad, fraude ni identidad.

## Figma

Abre un archivo **Figma Design** nuevo. Arrastra los nueve SVG de la carpeta `figma/` al lienzo, en **una sola página** (funciona aunque tu plan te limite a 3 páginas). Colócalos lado a lado. Cada lámina es de 1440×900.

Contenido: research, método, patrones, cuatro pantallas del frontend, línea gráfica y Atomic Design, Big Five/OCEAN, ley de Benford, conclusiones metodológicas. El SVG es una maqueta estática; **no se conecta automáticamente al backend**. Para demostrar navegación en Figma, conviértelas en frames y crea conexiones con **Prototype**. Ver `FIGMA_PASOS.md`.

## Privacidad / seguridad

- `.nexo_session/` y `.venv/` ignorados por Git.
- No se piden ni exportan contraseñas, cookies o archivos de sesión.
- Solo información pública visible; un nombre de perfil no certifica identidad.
- La extracción en vivo no pudo ser comprobada en el ordenador del usuario; las pruebas automáticas validan solo lógica y estructura del programa.

## Tests

```powershell
.\.venv\Scripts\python.exe -m pytest -q
```

Origen de la información técnica: https://playwright.dev/python/docs/api/class-browsertype y https://atomicdesign.bradfrost.com/chapter-2/.
