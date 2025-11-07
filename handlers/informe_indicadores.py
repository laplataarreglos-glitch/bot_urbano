import re
import logging

def enviar_informe_llm(callback_text: str):
    """
    Genera un informe interpretativo de indicadores urbanísticos
    a partir del texto del resultado anterior (callback_text).
    Devuelve un diccionario con 'text' y 'reply_markup'.
    """

    try:
        def extraer_valor(label):
            match = re.search(rf"{label}:\s*([^\n]+)", callback_text)
            return match.group(1).strip() if match else "N/A"

        sup = extraer_valor("Superficie")
        fos = extraer_valor("FOS")
        fot = extraer_valor("FOT")
        densidad = extraer_valor("Densidad")
        sm = extraer_valor("Superficie mínima")
        lm = extraer_valor("Lado mínimo")

        # --- Conversión segura ---
        def a_float(valor):
            try:
                return float(str(valor).replace(",", "."))
            except Exception:
                return None

        sup_val = a_float(sup)
        fos_val = a_float(fos)
        fot_val = a_float(fot)
        densidad_val = a_float(densidad)

        if not all([sup_val, fos_val, fot_val, densidad_val]):
            texto_error = (
                "⚠️ No se pudieron interpretar correctamente algunos valores del resultado anterior.\n"
                "Verificá que el mensaje contenga números válidos para superficie, FOS, FOT y densidad."
            )
            return {"text": texto_error, "reply_markup": {"inline_keyboard": [
                [{"text": "⬅️ Volver al resultado", "callback_data": "volver_resultado"}]
            ]}}

        # --- Cálculos ---
        superficie_ocupada = fos_val * sup_val
        superficie_total = fot_val * sup_val
        habitantes_estimados = (densidad_val * sup_val / 10000)

        informe = (
            "🧾 *Informe interpretativo del lote*\n\n"
            f"📐 Superficie del terreno: *{sup_val:,.0f} m²*\n"
            f"🏗️ FOS: *{fos_val}* → ocupa hasta *{superficie_ocupada:,.0f} m²* en planta baja.\n"
            f"🏢 FOT: *{fot_val}* → permite construir hasta *{superficie_total:,.0f} m²* totales.\n"
            f"👥 Densidad: *{densidad_val} hab/ha* → aprox. *{habitantes_estimados:,.0f} personas*.\n\n"
            f"🧱 Subdivisión mínima: *{sm} m²*, lado mínimo: *{lm} m*.\n\n"
            f"💡 Este lote tiene potencial para un desarrollo habitacional de escala media, "
            f"con buena capacidad constructiva y subdivisión posible según normativa.\n\n"
            f"¿Querés que te ayude a modelar un proyecto con estos indicadores? 🚀"
        )

        reply_markup = {
            "inline_keyboard": [
                [{"text": "📊 Generar modelo", "callback_data": "generar_modelo_proyecto"}],
                [{"text": "⬅️ Volver al resultado", "callback_data": "volver_resultado"}],
            ]
        }

        return {"text": informe, "reply_markup": reply_markup}

    except Exception as e:
        logging.error(f"⚠️ Error en enviar_informe_llm: {e}")
        return {"text": "❌ Ocurrió un error generando el informe.", "reply_markup": {"inline_keyboard": [
            [{"text": "⬅️ Volver", "callback_data": "volver_resultado"}]
        ]}}
