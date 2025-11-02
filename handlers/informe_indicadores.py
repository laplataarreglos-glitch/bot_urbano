import re
from telegram import Update
from telegram.ext import ContextTypes

async def enviar_informe_llm(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    text = query.message.text

    def extraer_valor(label):
        match = re.search(rf"{label}:\s*([^\n]+)", text)
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
        await query.message.reply_text("❌ No se pudo procesar los valores numéricos del resultado anterior.")
        return

    informe = (
        f"🧾 *Informe interpretativo del lote*\n\n"
        f"📐 El terreno posee una superficie de aproximadamente *{sup_val:,.0f} m²*.\n"
        f"🔸 El *FOS* es de *{fos_val}*, lo cual permite ocupar hasta *{fos_val*100:.0f}%* de la superficie en planta baja.\n"
        f"🔸 El *FOT* es de *{fot_val}*, lo que autoriza construir hasta *{fot_val*sup_val:,.0f} m²* en total, considerando varios niveles.\n"
        f"👥 Con una densidad máxima de *{densidad_val} hab/ha*, se estima la posibilidad de *{(densidad_val * sup_val / 10000):.0f} habitantes* en este lote.\n\n"
        f"🧱 Las subdivisiones deberán respetar una *superficie mínima* de *{sm} m²* y un *lado mínimo* de *{lm} m*.\n"
        f"🔎 Esto condiciona el tamaño de los lotes resultantes y el tipo de vivienda posible.\n\n"
        f"💡 Este terreno tiene potencial para un desarrollo habitacional de escala media, con capacidad constructiva adecuada "
        f"y posibilidad de subdividir según las normativas vigentes.\n"
        f"¿Querés que te ayude a modelar un proyecto con estos indicadores? 🚀"
    )

    await query.message.reply_text(informe, parse_mode="Markdown")
