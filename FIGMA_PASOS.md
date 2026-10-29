# Figma · NEXO

1. Abre un archivo Figma **Design**, no FigJam. Nombre: `NEXO | Research, sistema y prototipo`.
2. En una sola página, importa los **nueve `.svg`** de `/figma`. Si Figma Education todavía limita páginas, no afecta a este procedimiento.
3. Orden de lectura: `01_RESEARCH` → `02_METODO_Y_PATRONES` → `03_CUENTAS` → `04_RANKING` → `05_VIDEOS` → `06_CAMPANA` → `07_LINEA_GRAFICA_ATOMIC` → `08_BIGFIVE_BENFORD` → `09_CONCLUSIONES`.
4. En la sección **Prototype**, utiliza frames para crear el recorrido **Cuentas → Ranking → Videos → Campaña**. Los SVG son recursos gráficos estáticos; para enlaces clicables, superpón componentes nativos (botones) de Figma y conecta con interacción `On click → Navigate to`. Figma no conoce tu sesión ni consulta TikTok.
5. En las pantallas de muestra deja las rayas `—` y nombres de marcador mientras no hayas consultado cuentas reales. Reemplaza los marcadores **solo con resultados guardados que puedas mostrar**. No presentes ejemplos como observaciones realizadas.
6. Crea componentes atómicos nativos: botón principal, etiqueta, input, barra lateral y tarjeta de publicación; con ellos forma una tarjeta (organismo), el layout de Ranking (plantilla) y una página (pantalla completa).
7. Para exponer: problema → fuente de datos → patrones calculables → comparación → selección → validación → límites científicos.

## Investigación propuesta

- **Usuario del negocio:** emprendimiento local que necesita escoger creador para campaña.
- **Problema:** seguidors altos no garantizan afinidad o resultados.
- **Research:** comparar temas, mediana de vistas por video, likes/vistas, comentarios/vistas y cobertura del registro.
- **Patrones:** al menos tres publicaciones medibles por cuenta para comparar ratios; presencia/ausencia de preguntas públicas relevantes.
- **Conclusiones:** se redactarán tras obtener la primera muestra real. Si no hay datos, se explica el bloqueo 403 y la alternativa de lectura local, sin declarar ganadora.
- **Big Five:** OCEAN como marco psicológico solo con participación y cuestionarios voluntarios válidos; no deducir rasgos de terceros.
- **Benford:** distribución teórica de primeros dígitos; no certifica verdad ni se aplica con cinco perfiles como veredicto.

## Paleta

`#102E34` azul petróleo · `#006F63` verde tinta · `#CBF3DE` menta · `#FAF9F5` marfil · `#DF8A51` cobre.

## Fuente de consulta

Playwright: https://playwright.dev/python/docs/api/class-browsertype

Atomic Design: https://atomicdesign.bradfrost.com/chapter-2/

Figma Design imports: https://help.figma.com/hc/en-us/articles/360040027794-Guide-to-imports-in-Figma-Design
