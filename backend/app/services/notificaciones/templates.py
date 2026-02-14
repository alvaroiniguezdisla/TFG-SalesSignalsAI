def generar_html_resumen(nombre: str, noticias: list) -> str:
    """Genera el HTML del email con las noticias."""
    noticias_html = ""
    for n in noticias[:10]:  # Máximo 10 noticias
        relevancia = n.get("relevancia_ia", 0)
        if relevancia >= 70:
            prioridad = "Alta"
            color = "#ef4444"
        elif relevancia >= 40:
            prioridad = "Media"
            color = "#f59e0b"
        else:
            prioridad = "Baja"
            color = "#22c55e"
        
        titulo = n.get('titulo', 'Sin título')
        categoria = n.get('categoria_ia', 'N/A')
        resumen = n.get('resumen_comercial_ia', '')[:200]
        url = n.get('url', '#')
        
        noticias_html += f"""
        <div style="border-left: 4px solid {color}; padding: 12px 16px; margin: 12px 0; background: #f8fafc; border-radius: 0 8px 8px 0;">
            <strong style="font-size: 16px; color: #1e293b;">{titulo}</strong><br>
            <small style="color: #64748b;">Prioridad: {prioridad} | Categoría: {categoria}</small><br>
            <p style="color: #475569; margin: 8px 0;">{resumen}...</p>
            <a href="{url}" style="color: #3b82f6; text-decoration: none; font-weight: 600;">Leer más →</a>
        </div>
        """

    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
    </head>
    <body style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px; background: #ffffff;">
        <div style="text-align: center; margin-bottom: 24px;">
            <h1 style="color: #1e293b; margin: 0;">SalesSignalsAI</h1>
            <p style="color: #64748b; margin: 8px 0 0 0;">Tu asistente de señales comerciales</p>
        </div>
        
        <div style="background: linear-gradient(135deg, #3b82f6, #2563eb); color: white; padding: 20px; border-radius: 12px; margin-bottom: 24px;">
            <h2 style="margin: 0 0 8px 0;">Hola {nombre}!</h2>
            <p style="margin: 0; opacity: 0.9;">Tienes <strong>{len(noticias)} nuevas señales</strong> basadas en tus preferencias.</p>
        </div>
        
        <h3 style="color: #1e293b; border-bottom: 2px solid #e2e8f0; padding-bottom: 8px;">Tus Señales Personalizadas</h3>
        
        {noticias_html}
        
        <hr style="border: none; border-top: 1px solid #e2e8f0; margin: 24px 0;">
        
        <p style="color: #94a3b8; font-size: 12px; text-align: center;">
            Este email fue generado automáticamente por SalesSignalsAI.<br>
            Puedes actualizar tus preferencias en tu perfil de la aplicación.
        </p>
    </body>
    </html>
    """
