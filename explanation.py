import os
import pandas as pd
import shap
import matplotlib.pyplot as plt
import base64
from io import BytesIO
from openai import OpenAI

# Inicializar cliente OpenAI
try:
    client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
except Exception as e:
    print(f"⚠️ No se pudo inicializar OpenAI: {e}")
    client = None

# -----------------------
# Funciones de gráficos
# -----------------------

def _fig_to_base64(fig):
    """Convierte una figura de matplotlib a base64 para HTML."""
    buf = BytesIO()
    fig.savefig(buf, format="png", bbox_inches="tight")
    plt.close(fig)
    return base64.b64encode(buf.getvalue()).decode("utf-8")

def generate_waterfall(shap_values_instance):
    fig, ax = plt.subplots()
    shap.plots.waterfall(shap_values_instance, max_display=10, show=False)
    plt.title("Impacto de cada factor en la predicción")
    return f'<img src="data:image/png;base64,{_fig_to_base64(fig)}" class="img-fluid" alt="Waterfall SHAP">'

def generate_decision_plot(expected_value, shap_values_instance_values, features_instance):
    fig, ax = plt.subplots()
    shap.decision_plot(expected_value, shap_values_instance_values, features_instance, show=False)
    plt.title("Camino de la Decisión del Modelo")
    return f'<img src="data:image/png;base64,{_fig_to_base64(fig)}" class="img-fluid" alt="Decision SHAP">'

def generate_summary_plot(shap_values, features_df):
    fig, ax = plt.subplots()
    shap.summary_plot(shap_values, features_df, plot_type="bar", show=False)
    plt.title("Importancia global de las características")
    return f'<img src="data:image/png;base64,{_fig_to_base64(fig)}" class="img-fluid" alt="Summary SHAP">'

def generate_force_plot(expected_value, shap_values_instance_values, features_instance):
    """Genera un gráfico de fuerza interactivo de SHAP, incluyendo el JS necesario."""
    # CORRECCIÓN: Devolver la librería JS principal junto con el HTML del gráfico.
    force_plot = shap.force_plot(expected_value, shap_values_instance_values, features_instance, show=False)
    # Esto combina el <script> de la librería SHAP con el HTML/JS específico del gráfico.
    return shap.getjs() + force_plot._repr_html_()

# -----------------------
# Función de explicación en lenguaje natural
# -----------------------

def format_explanation_html(text):
    import re
    # Quitar asteriscos y saltos de línea innecesarios
    text = text.replace('**', '')
    # Convertir encabezados Markdown a HTML
    text = re.sub(r'<h6>(.*?)<br>', r'<h6 style="font-weight:600;margin-top:16px;color:#17a2b8;font-size:1.15rem;letter-spacing:0.5px;">\1</h6>', text)
    # Convertir listas Markdown a listas HTML
    text = re.sub(r'(\d+)\. ', r'<li>', text)
    # Cerrar listas al encontrar dos saltos de línea
    text = re.sub(r'(</li>)(<br>)+', r'\1', text)
    # Agrupar los <li> en <ol>
    text = re.sub(r'(<li>.*?</li>)+', lambda m: f'<ol style="margin-left:18px;padding-left:8px;background:#f7f8fa;border-radius:8px;margin-bottom:12px;">{m.group(0)}</ol>', text, flags=re.DOTALL)
    # Resaltar palabras clave
    text = re.sub(r'(riesgo|diagnóstico|recomendaciones|acción|conclusión)', r'<span style="color:#17a2b8;font-weight:600;">\1</span>', text, flags=re.IGNORECASE)
    # Limpiar saltos de línea extra
    text = text.replace('<br><br>', '<br>')
    return text

def generate_nl_explanation(shap_values_instance, prob, risk_level):
    if not client:
        return "No se pudo generar la explicación en lenguaje natural. Configura OPENAI_API_KEY."
    
    feature_impacts = []
    for i, feature in enumerate(shap_values_instance.feature_names):
        feature_impacts.append({
            "name": feature,
            "value": shap_values_instance.data[i],
            "impact": shap_values_instance.values[i]
        })
    feature_impacts.sort(key=lambda x: abs(x['impact']), reverse=True)
    
    prompt_parts = [
        f"Eres un analista de crédito senior interpretando un modelo de machine learning (basado en SHAP) para un cliente. Tu tono debe ser claro, experto y constructivo. Habla en español.",
        f"El análisis ha concluido. La probabilidad de mora es del **{prob:.2f}%**, lo que hemos clasificado como un nivel de riesgo **{risk_level}**.",
        "\nA continuación, los datos de influencia (valores SHAP) que el modelo usó. Un impacto negativo reduce el riesgo, uno positivo lo aumenta."
    ]

    for f in feature_impacts[:5]:
        prompt_parts.append(f"- Característica: {f['name']}, Impacto en el riesgo: {f['impact']:.3f}")

    prompt_parts.append(
        "\n\nINSTRUCCIONES:\n"
        "1. **Diagnóstico Experto:** Comienza confirmando el nivel de riesgo. Luego, explica *por qué* se llegó a esa conclusión, interpretando la 'historia' que cuentan los datos. Menciona los 2-3 factores más determinantes.\n"
        "2. **Plan de Acción:** Basado en los factores que aumentaron el riesgo, ofrece un plan de acción claro con 2 o 3 recomendaciones específicas.\n"
        "3. **Conclusión:** Termina con una nota constructiva.\n"
        "Formatea la respuesta usando encabezados Markdown (ej: '### Diagnóstico del Análisis')."
    )
    
    final_prompt = "\n".join(prompt_parts)
    
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "Eres un analista de crédito que traduce datos complejos en consejos prácticos."},
                {"role": "user", "content": final_prompt}
            ],
            temperature=0.5,
        )
        text = response.choices[0].message.content
        text = text.replace("### ", "<h6>").replace("\n", "<br>")
        text = format_explanation_html(text)
        return text
    except Exception as e:
        print(f"❌ Error OpenAI: {e}")
        return "Hubo un error al generar la explicación."

# -----------------------
# Función principal para Flask
# -----------------------

def generate_shap_explanation(explainer, scaler, input_data_dict: dict, feature_names: list, prob: float, risk_level: str):
    """
    Genera todos los gráficos y explicación en lenguaje natural para una instancia.
    """
    try:
        df = pd.DataFrame([input_data_dict], columns=feature_names)
        scaled_df = pd.DataFrame(scaler.transform(df), columns=feature_names)

        shap_values = explainer(scaled_df)
        shap_instance = shap_values[0]

        return {
            "waterfall_plot_html": generate_waterfall(shap_instance),
            "decision_plot_html": generate_decision_plot(explainer.expected_value, shap_instance.values, scaled_df.iloc[0]),
            "summary_plot_html": generate_summary_plot(shap_values, scaled_df),
            "force_plot_html": generate_force_plot(explainer.expected_value, shap_instance.values, scaled_df.iloc[0]),
            "text_explanation": generate_nl_explanation(shap_instance, prob, risk_level)
        }
    except Exception as e:
        print(f"❌ Error al generar explicabilidad completa: {e}")
        return None
