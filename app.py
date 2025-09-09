from flask import Flask, request, send_file, jsonify
import joblib
import numpy as np
import pandas as pd
from datetime import datetime
import shap
from openai import OpenAI
import os
from dotenv import load_dotenv

# Cargar variables de entorno desde el archivo .env
load_dotenv()

# ========================
# 0. Configuración
# ========================
app = Flask(__name__, static_url_path='/static', static_folder='static')

# Cliente de OpenAI
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))  # Carga la API key desde .env

# ========================
# 1. Cargar modelo
# ========================
try:
    modelo = joblib.load("modelo_xgboost_credit.pkl")
    print("✅ Modelo cargado correctamente")
except Exception as e:
    modelo = None
    print(f"❌ Error al cargar el modelo: {e}")

# ========================
# 2. Features usadas
# ========================
top15_features = [
    "EXT_SOURCE_3", "EXT_SOURCE_2", "DAYS_BIRTH", "DAYS_ID_PUBLISH",
    "DAYS_EMPLOYED", "DAYS_LAST_PHONE_CHANGE", "DAYS_REGISTRATION",
    "AMT_ANNUITY", "AMT_CREDIT", "AMT_GOODS_PRICE",
    "REGION_POPULATION_RELATIVE", "AMT_INCOME_TOTAL",
    "HOUR_APPR_PROCESS_START", "TOTALAREA_MODE"
]

descripciones = {
    "EXT_SOURCE_3": "Puntaje externo de crédito (valores bajos indican mayor riesgo).",
    "EXT_SOURCE_2": "Segundo puntaje externo de crédito (valores bajos implican mayor riesgo).",
    "DAYS_BIRTH": "Edad en días (negativo, ej: -14600 ≈ 40 años).",
    "DAYS_ID_PUBLISH": "Tiempo desde que se emitió el documento en días.",
    "DAYS_EMPLOYED": "Tiempo en el empleo en días (más alto = mayor estabilidad).",
    "DAYS_LAST_PHONE_CHANGE": "Días desde el último cambio de celular (reciente puede aumentar riesgo).",
    "DAYS_REGISTRATION": "Días desde registro oficial en entidad estatal.",
    "AMT_ANNUITY": "Cuota periódica del crédito solicitado.",
    "AMT_CREDIT": "Monto total del crédito solicitado.",
    "AMT_GOODS_PRICE": "Precio del bien a comprar con el crédito.",
    "REGION_POPULATION_RELATIVE": "Densidad poblacional relativa de la región.",
    "AMT_INCOME_TOTAL": "Ingreso mensual del cliente.",
    "HOUR_APPR_PROCESS_START": "Hora en la que se solicitó el crédito.",
    "TOTALAREA_MODE": "Índice del tamaño de la vivienda."
}

# ========================
# 3. Funciones auxiliares
# ========================
def calcular_cuota(monto_credito, plazo_meses, tasa_anual=0.20):
    r = tasa_anual / 12
    n = plazo_meses
    if r == 0:
        return monto_credito / n
    return (monto_credito * r) / (1 - (1 + r) ** -n)


def explicar_con_llm(index, shap_values, df, features, proba_default):
    shap_vals = shap_values[index]
    idxs = np.argsort(np.abs(shap_vals))[::-1][:3]

    explicacion = []
    for idx in idxs:
        feature = features[idx]
        valor = df.iloc[index, idx]
        impacto = shap_vals[idx]
        efecto = "aumenta" if impacto > 0 else "reduce"

        descripcion = descripciones.get(feature, feature)
        explicacion.append(f"{feature}: {descripcion}. Valor observado: {valor}. Este factor {efecto} el riesgo.")

    prompt = f"""
        Soy analista de riesgo en un banco en Colombia. 
        El cliente tiene una probabilidad de mora del {proba_default[0]*100:.1f}%.
        Clasifica el riesgo usando esta escala:
        - Menos de 10% = Riesgo bajo
        - Entre 10% y 20% = Riesgo medio
        - Más de 20% = Riesgo alto

        Explica en lenguaje claro y amigable las razones principales:
        - {explicacion[0]}
        - {explicacion[1]}
        - {explicacion[2]}

        Con base en esta clasificación:
        1. Resume el nivel de riesgo asignado en un tono positivo y constructivo, evitando términos técnicos.
        2. Propón al menos 2 recomendaciones personalizadas para mejorar la posibilidad de aprobación del crédito.
        3. Incluye un mensaje final motivador y positivo.

        Estructura tu respuesta en párrafos cortos con encabezados como "Tu perfil crediticio", "Recomendaciones personalizadas" y "Próximos pasos".
        Usa un tono conversacional y amigable como si le hablaras directamente al cliente.
        """



    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "Eres un asesor financiero amigable que explica de manera clara y sencilla. Tu objetivo es ayudar al cliente a entender su situación crediticia y brindarle consejos útiles en un tono positivo y motivador."},
            {"role": "user", "content": prompt}
        ]
    )
    return response.choices[0].message.content


# ========================
# 4. Rutas Flask
# ========================
@app.route("/", methods=["GET"])
def index():
    return send_file("index.html")


@app.route("/predict", methods=["POST"])
def predict():
    try:
        documento = request.form.get("documento", "No especificado")

        edad = float(request.form.get("edad"))
        days_birth = -edad * 365

        doc_publish = float(request.form.get("doc_publish")) * -365
        empleo = float(request.form.get("empleo")) * -365
        celular = float(request.form.get("celular")) * -30
        registro = float(request.form.get("registro")) * -365

        ingresos = float(request.form.get("ingresos"))
        credito = float(request.form.get("credito"))
        precio = float(request.form.get("precio"))
        plazo = int(request.form.get("plazo"))
        region = float(request.form.get("region"))
        
        # Usamos el valor de tipo_vivienda directamente como área para TOTALAREA_MODE
        # TOTALAREA_MODE debe estar en el rango de 0.0 a 1.0, con un promedio de ~0.086
        # Según la información proporcionada
        area = float(request.form.get("tipo_vivienda", 0.5))  
        # No necesitamos multiplicar, ya que los valores del selector (0.3, 0.5, 0.8, 1.0) ya están en el rango adecuado

        anualidad = calcular_cuota(credito, plazo)
        hora = datetime.now().hour

        ext2, ext3 = 0.6, 0.5  # simulados

        features = np.array([[
            ext3, ext2, days_birth, doc_publish, empleo,
            celular, registro, anualidad, credito, precio,
            region, ingresos, hora, area
        ]])

        df_cliente = pd.DataFrame(features, columns=top15_features)

        if modelo:
            prediction = modelo.predict(features)[0]
            probability_raw = modelo.predict_proba(features)[0].tolist()
            # Formatear la probabilidad como porcentaje con 2 decimales
            probability_formatted = f"{probability_raw[1] * 100:.2f}%"

            explainer = shap.TreeExplainer(modelo)
            shap_values = explainer.shap_values(df_cliente)

            explicacion = explicar_con_llm(0, shap_values, df_cliente, top15_features, [probability_raw[1]])
            
            # Convertir el formato Markdown a HTML de forma manual
            explicacion_html = explicacion
            
            # Convertir encabezados
            explicacion_html = explicacion_html.replace("### ", "<h4>").replace("\n## ", "</h4><h3>").replace("## ", "<h3>")
            # Añadir cierre para el último encabezado
            if "<h4>" in explicacion_html and "</h4>" not in explicacion_html:
                explicacion_html += "</h4>"
            if "<h3>" in explicacion_html and "</h3>" not in explicacion_html:
                explicacion_html += "</h3>"
                
            # Convertir formato de texto (negrita)
            temp_html = ""
            parts = explicacion_html.split("**")
            for i, part in enumerate(parts):
                if i == 0:
                    temp_html += part
                elif i % 2 == 1:  # Impar - apertura de negrita
                    temp_html += f"<strong>{part}"
                else:  # Par - cierre de negrita
                    temp_html += f"</strong>{part}"
            explicacion_html = temp_html
            
            # Convertir listas (guiones)
            lines = explicacion_html.split("\n")
            processed_lines = []
            in_list = False
            
            for line in lines:
                if line.strip().startswith("- "):
                    if not in_list:
                        processed_lines.append("<ul style='margin-left: 20px; padding-left: 15px;'>")
                        in_list = True
                    item_content = line.strip()[2:]  # Quitar el "- "
                    processed_lines.append(f"<li>{item_content}</li>")
                else:
                    if in_list:
                        processed_lines.append("</ul>")
                        in_list = False
                    processed_lines.append(line)
            
            if in_list:
                processed_lines.append("</ul>")
                
            explicacion_html = "\n".join(processed_lines)
            
            # Convertir listas numeradas
            lines = explicacion_html.split("\n")
            processed_lines = []
            in_list = False
            
            for line in lines:
                if line.strip() and line.strip()[0].isdigit() and ". " in line.strip()[:5]:
                    if not in_list:
                        processed_lines.append("<ol style='margin-left: 20px; padding-left: 15px;'>")
                        in_list = True
                    item_content = line.strip().split(". ", 1)[1]
                    processed_lines.append(f"<li>{item_content}</li>")
                else:
                    if in_list:
                        processed_lines.append("</ol>")
                        in_list = False
                    processed_lines.append(line)
            
            if in_list:
                processed_lines.append("</ol>")
                
            explicacion_html = "\n".join(processed_lines)
            
            # Convertir párrafos (respetando listas)
            parrafos = []
            current_paragraph = ""
            
            for line in explicacion_html.split("\n"):
                if line.strip() == "":
                    if current_paragraph:
                        parrafos.append(current_paragraph)
                        current_paragraph = ""
                else:
                    if current_paragraph:
                        # Si ya estamos en un párrafo y no es un elemento de lista o encabezado
                        if not (line.strip().startswith("<li>") or line.strip().startswith("<ul") or 
                                line.strip().startswith("</ul") or line.strip().startswith("<ol") or 
                                line.strip().startswith("</ol") or line.strip().startswith("<h")):
                            current_paragraph += " " + line.strip()
                        else:
                            parrafos.append(current_paragraph)
                            current_paragraph = line
                    else:
                        current_paragraph = line
            
            if current_paragraph:
                parrafos.append(current_paragraph)
            
            explicacion_html = ""
            for parrafo in parrafos:
                if not (parrafo.strip().startswith("<h") or parrafo.strip().startswith("<ul") or 
                        parrafo.strip().startswith("<ol") or parrafo.strip().startswith("<li") or
                        parrafo.strip().startswith("</ul") or parrafo.strip().startswith("</ol")):
                    explicacion_html += f"<p>{parrafo}</p>"
                else:
                    explicacion_html += parrafo
            
            # Envolver en un contenedor con estilo
            explicacion_html = f"""
            <div class="explanation-container" style="background-color: #f8f9fa; border-radius: 10px; padding: 20px; margin-top: 20px; box-shadow: 0 4px 6px rgba(0,0,0,0.1);">
                <h3 style="color: #1A9B9D; margin-bottom: 15px;">Análisis de tu Solicitud de Crédito</h3>
                <div class="explanation-content" style="line-height: 1.6;">
                    {explicacion_html}
                </div>
            </div>
            """
        else:
            prediction = "Simulado"
            probability_raw = [0.7, 0.3]
            probability_formatted = "30.00%"
            explicacion = "Explicación simulada."
            explicacion_html = f"""
            <div class="explanation-container" style="background-color: #f8f9fa; border-radius: 10px; padding: 20px; margin-top: 20px; box-shadow: 0 4px 6px rgba(0,0,0,0.1);">
                <h3 style="color: #1A9B9D; margin-bottom: 15px;">Análisis Simulado</h3>
                <div class="explanation-content" style="line-height: 1.6;">
                    <p>{explicacion}</p>
                </div>
            </div>
            """

        return jsonify({
            "documento": documento,
            "prediction": str(prediction),
            "probability": probability_formatted,
            "probability_raw": probability_raw,
            "cuota": anualidad,
            "explicacion": explicacion,
            "explicacion_html": explicacion_html
        })

    except Exception as e:
        return jsonify({"error": str(e)})


# ========================
# 5. Tests automáticos
# ========================
@app.route("/test_riesgoso", methods=["GET"])
def test_riesgoso():
    cliente_riesgoso = {
        "EXT_SOURCE_3": 0.05,
        "EXT_SOURCE_2": 0.10,
        "DAYS_BIRTH": -25*365,
        "DAYS_ID_PUBLISH": -100,
        "DAYS_EMPLOYED": -200,
        "DAYS_LAST_PHONE_CHANGE": -50,
        "DAYS_REGISTRATION": -300,
        "AMT_ANNUITY": 50000,
        "AMT_CREDIT": 800000,
        "AMT_GOODS_PRICE": 780000,
        "REGION_POPULATION_RELATIVE": 0.05,
        "AMT_INCOME_TOTAL": 100000,
        "HOUR_APPR_PROCESS_START": 23,
        "TOTALAREA_MODE": 0.05,
    }
    return evaluar_cliente(cliente_riesgoso)


@app.route("/test_saludable", methods=["GET"])
def test_saludable():
    cliente_saludable = {
        "EXT_SOURCE_3": 0.80,
        "EXT_SOURCE_2": 0.75,
        "DAYS_BIRTH": -40*365,
        "DAYS_ID_PUBLISH": -2000,
        "DAYS_EMPLOYED": -5000,
        "DAYS_LAST_PHONE_CHANGE": -1200,
        "DAYS_REGISTRATION": -4000,
        "AMT_ANNUITY": 10000,
        "AMT_CREDIT": 150000,
        "AMT_GOODS_PRICE": 140000,
        "REGION_POPULATION_RELATIVE": 0.02,
        "AMT_INCOME_TOTAL": 300000,
        "HOUR_APPR_PROCESS_START": 10,
        "TOTALAREA_MODE": 0.35,
    }
    return evaluar_cliente(cliente_saludable)


def evaluar_cliente(cliente_dict):
    df_cliente = pd.DataFrame([cliente_dict], columns=top15_features)

    # ========================
    # Calcular cuota real
    # ========================
    monto_credito = cliente_dict.get("AMT_CREDIT", 0)
    anualidad = cliente_dict.get("AMT_ANNUITY", 0)

    # Si AMT_ANNUITY no está definido, calculamos una cuota estimada a 36 meses
    if anualidad == 0:
        anualidad = calcular_cuota(monto_credito, 36)

    if modelo:
        prediction = modelo.predict(df_cliente)[0]
        probability_raw = modelo.predict_proba(df_cliente)[0].tolist()
        # Formatear la probabilidad como porcentaje con 2 decimales
        probability_formatted = f"{probability_raw[1] * 100:.2f}%"

        explainer = shap.TreeExplainer(modelo)
        shap_values = explainer.shap_values(df_cliente)

        explicacion = explicar_con_llm(
            0, shap_values, df_cliente, top15_features, [probability_raw[1]]
        )
    else:
        prediction = "Simulado"
        probability_raw = [0.5, 0.5]
        probability_formatted = "50.00%"
        explicacion = "Explicación simulada."

    return jsonify({
        "input": cliente_dict,
        "prediction": str(prediction),
        "probability": probability_formatted,
        "probability_raw": probability_raw,
        "cuota": anualidad,
        "explicacion": explicacion
    })



# ========================
# 6. Run
# ========================
if __name__ == "__main__":
    app.run(debug=True, port=5000)
