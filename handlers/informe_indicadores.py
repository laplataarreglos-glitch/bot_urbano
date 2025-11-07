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

        try:
            sup_val = float(sup)
            fos_val = float(fos)
            fot_val = float(fot)
            densidad_val = float(densidad)
        except ValueError:
            return {"text": "❌ No se pudo procesar correctamente los valores numéricos del resultado anterior.", 
                    "reply_markup": None}

        informe = (
            f"🧾 *Informe interpretativo del lote*\n\n"
            f"📐 El terreno posee una superficie de aproximadamente *{sup_val:,.0f} m²*.\n"
            f"🔸 El *FOS* es de *{fos_val}*, lo que permite ocupar hasta *{fos_val*100:.0f}%* de la superficie en planta baja.\n"
            f"🔸 El *FOT* es de *{fot_val}*, por lo tanto, se pueden construir hasta *{fot_val*sup_val:,.0f} m²* totales en varios niveles.\n"
            f"👥 Con una densidad máxima de *{densidad_val} hab/ha*, podrían habitar aproximadamente *{(densidad_val * sup_val / 10000):.0f} personas*.\n\n"
            f"🧱 Las subdivisiones deben respetar una *superficie mínima* de *{sm} m²* y un *lado mínimo* de *{lm} m*.\n"
            f"🔎 Esto condiciona el tamaño de los lotes resultantes y el tipo de desarrollo posible.\n\n"
            f"💡 Este terreno presenta potencial para un desarrollo habitacional de escala media, "
            f"con capacidad constructiva adecuada y posibilidad de subdividir conforme a normativa.\n\n"
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
        return {"text": "❌ Ocurrió un error generando el informe.", "reply_markup": None}
