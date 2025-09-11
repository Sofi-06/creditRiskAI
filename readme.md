# Plataforma de Análisis de Riesgo Crediticio

Este proyecto es una aplicación web construida con Flask que utiliza un modelo de Machine Learning (XGBoost) para predecir la probabilidad de mora en solicitudes de préstamos.

La aplicación no solo entrega una predicción, sino que también ofrece una explicación detallada y personalizada del resultado utilizando **SHAP** (SHapley Additive exPlanations) y la **API de OpenAI**, haciendo el resultado comprensible para el usuario final.

## Características

- **Formulario Web**: Interfaz amigable para ingresar los datos de la solicitud de crédito.
- **Predicción de Riesgo**: Utiliza un modelo XGBoost pre-entrenado para calcular la probabilidad de mora.
- **Clasificación de Riesgo**: Categoriza el resultado en "Bajo", "Medio" o "Alto" para una comprensión rápida.
- **Explicabilidad con IA**:
    - Genera una explicación en lenguaje natural utilizando la API de OpenAI (GPT-4o-mini) que actúa como un asesor financiero.
    - Ofrece un diagnóstico experto y recomendaciones personalizadas para mejorar el perfil crediticio.
- **Visualización de Datos (SHAP)**:
    - **Gráfico de Fuerza (Force Plot)**: Gráfico interactivo que muestra las fuerzas que empujan la predicción hacia un lado u otro.
    - **Gráfico de Cascada (Waterfall Plot)**: Muestra el impacto aditivo de cada factor en la predicción.
    - **Gráfico de Decisión (Decision Plot)**: Ilustra el camino que toma la predicción desde el valor base hasta el resultado final.
    - **Gráfico de Resumen (Summary Plot)**: Muestra la importancia global de cada característica para el modelo.
- **Persistencia de Datos**: Guarda cada solicitud y su resultado en una base de datos SQLite.

## Instalación

Sigue estos pasos para configurar y ejecutar el proyecto en tu entorno local.

### 1. Prerrequisitos

- Python 3.8 o superior.
- Git.

### 2. Clonar el Repositorio

```bash
git clone <URL-del-repositorio>
cd estesi
```

### 3. Crear un Entorno Virtual

Es una buena práctica aislar las dependencias del proyecto.

```bash
# En Windows
python -m venv .venv
.venv\Scripts\activate

# En macOS/Linux
python3 -m venv .venv
source .venv/bin/activate
```

### 4. Instalar Dependencias

Las siguientes librerías son necesarias para el funcionamiento del proyecto. Puedes instalarlas todas con un solo comando:

```bash
pip install flask flask_sqlalchemy flask_wtf python-dotenv joblib pandas shap matplotlib openai xgboost scikit-learn psycopg2-binary email_validator
```

**Desglose de Librerías:**
- `flask`, `flask_sqlalchemy`, `flask_wtf`: Para el framework web, la base de datos y los formularios.
- `python-dotenv`: Para cargar variables de entorno como las claves de API.
- `joblib`: Para cargar el modelo de Machine Learning (`.pkl`).
- `pandas`: Para la manipulación de datos.
- `scikit-learn`: Para cargar el escalador de datos (`scaler.pkl`).
- `xgboost`: Requerido por el modelo de predicción.
- `shap`: Para la generación de todos los gráficos de explicabilidad.
- `matplotlib`: Dependencia de SHAP para crear los gráficos estáticos.
- `openai`: Para conectar con la API de OpenAI y generar las explicaciones en texto.

### 5. Configurar Variables de Entorno

Crea un archivo llamado `.env` en la raíz del proyecto y añade tu clave secreta de OpenAI y una clave para Flask.

```
# .env
OPENAI_API_KEY="tu_clave_secreta_de_openai_aqui"
SECRET_KEY="una_clave_secreta_aleatoria_para_flask"
```

## Uso

Una vez que las dependencias estén instaladas y el archivo `.env` configurado, puedes ejecutar la aplicación con el siguiente comando:

```bash
python app.py
```

La aplicación estará disponible en `http://127.0.0.1:5000` en tu navegador web.
