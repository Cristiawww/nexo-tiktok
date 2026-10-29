"""Inicio de sesión propio en un navegador persistente de Playwright.

Almacena cookies exclusivamente dentro de .nexo_session en este ordenador.
No exporta credenciales, no copia el perfil habitual de Chrome ni elude bloqueos.
"""
from __future__ import annotations
import os
from pathlib import Path
from playwright.sync_api import sync_playwright, Error as PlaywrightError, TimeoutError as PlaywrightTimeout

RUTA_SESION = Path(__file__).resolve().parent / '.nexo_session'


def abrir_contexto(playwright):
    opcion = os.getenv('NEXO_NAVEGADOR', 'chrome').strip().lower()
    kwargs = dict(user_data_dir=str(RUTA_SESION), headless=False,
                  locale='es-ES', viewport={'width': 1390, 'height': 960},
                  accept_downloads=False)
    if opcion == 'chrome':
        kwargs['channel'] = 'chrome'  # Chrome instalado; perfil de NEXO separado del normal.
    elif opcion != 'chromium':
        raise ValueError('NEXO_NAVEGADOR admite chrome o chromium')
    return playwright.chromium.launch_persistent_context(**kwargs)


def abrir_sesion():
    print('\nNEXO / sesión propia de Playwright')
    print('Se abrirá un navegador con un perfil separado del Chrome habitual.')
    print('Accede manualmente SOLO a tu propia cuenta; no compartas .nexo_session.')
    print('Si TikTok muestra HTTP 403, no podremos usar esta vía; no sigas reintentando.')
    try:
        with sync_playwright() as playwright:
            ctx = abrir_contexto(playwright)
            try:
                page = ctx.pages[0] if ctx.pages else ctx.new_page()
                try:
                    response = page.goto('https://www.tiktok.com/', wait_until='domcontentloaded', timeout=30000)
                    if response and response.status in (403, 429):
                        print(f'\nTikTok respondió HTTP {response.status}. No se pudo acceder a la página.')
                        print('No significa que hayas iniciado sesión. Puedes usar una exportación real de Chrome.')
                    else:
                        print('\nInicia sesión manualmente, comprueba que el perfil sea visible y luego pulsa ENTER.')
                        input('ENTER para cerrar el navegador y guardar el perfil local: ')
                except (PlaywrightError, PlaywrightTimeout) as exc:
                    print('No se pudo abrir TikTok:', str(exc)[:180])
            finally:
                ctx.close()
    except PlaywrightError as exc:
        print('No se pudo abrir el navegador:', str(exc)[:320])
        print('Comprueba que Chrome esté instalado. Si necesitas Chromium, usa:')
        print('$env:NEXO_NAVEGADOR="chromium"; .\\.venv\\Scripts\\python.exe sesion.py')
    print('\nLa sesión permanece únicamente en este equipo. Fin.')


if __name__ == '__main__':
    abrir_sesion()
