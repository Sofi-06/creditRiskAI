import os
from flask import Flask, render_template, request, flash, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_wtf.csrf import CSRFProtect, CSRFError
from dotenv import load_dotenv
import joblib
import shap
import pandas as pd # Es buena práctica tenerlo aquí aunque se use en 'explanation'

from forms import LoanForm
from models import db, LoanApplication
from prediccion_mora.prediccion_mora import predecir_mora
from explanation import generate_shap_explanation 

# Cargar variables de entorno
load_dotenv()

app = Flask(__name__)
app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "dev_secret")
app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv(
    "DATABASE_URL", "sqlite:///loan_applications.db"
)
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["WTF_CSRF_TIME_LIMIT"] = 3600  # Aumentar el tiempo de expiración del token CSRF a 1 hora


print("🔗 Base de datos usada:", app.config["SQLALCHEMY_DATABASE_URI"])

# Inicializar extensiones
db.init_app(app)
csrf = CSRFProtect(app)

# Cargar modelo, scaler y SHAP explainer
predictor = joblib.load("xgboost_model.pkl")
scaler = joblib.load("scaler.pkl")
explainer = shap.TreeExplainer(predictor)

# Columnas esperadas por el modelo
cols = [
    "Age", "Income", "LoanAmount", "CreditScore", "MonthsEmployed",
    "NumCreditLines", "InterestRate", "LoanTerm", "DTIRatio",
    "EmploymentType", "MaritalStatus", "HasMortgage", "HasDependents",
    "LoanPurpose", "HasCoSigner", "Education_num"
]

# Manejar errores de CSRF
@app.errorhandler(CSRFError)
def handle_csrf_error(e):
    flash("La sesión ha expirado. Por favor, intente nuevamente.", "danger")
    return redirect(url_for('index'))


@app.route("/", methods=["GET", "POST"])
def index():
    form = LoanForm()
    prob = None
    risk_level = None
    explanation_data = None

    if form.validate_on_submit():
        try:
            print("📩 Request recibido:", request.form)

            # ... (captura de datos y cálculo de DTIRatio sin cambios) ...
            registro_dict = {col: float(getattr(form, col).data)
                             for col in cols if hasattr(form, col) and col != "DTIRatio"}
            registro_dict["InterestRate"] = 9.25  # Tasa fija para cada registro
            income = float(form.Income.data)
            expenses = float(form.MonthlyExpenses.data)
            registro_dict["DTIRatio"] = round(expenses / income, 4) if income > 0 else 0.0

            # Calcular predicción
            prob_raw = predecir_mora(registro_dict, predictor, scaler, cols)
            prob = round(float(prob_raw) * 100, 2)

            # --- NUEVO: Clasificar el nivel de riesgo ---
            if prob < 30:
                risk_level = "Bajo"
            elif prob < 60:
                risk_level = "Medio"
            else:
                risk_level = "Alto"

            # Generar la explicación completa, pasando el nivel de riesgo
            explanation_data = generate_shap_explanation(
                explainer, scaler, registro_dict, cols, prob, risk_level
            )

            # ... (código para guardar en la base de datos sin cambios) ...
            registro = LoanApplication(
                email=form.email.data,
                documento=form.documento.data,
                **registro_dict,
                prediccion=prob
            )
            db.session.add(registro)
            db.session.commit()
            flash("✅ Solicitud guardada en la base de datos", "success")
            print("✅ Registro guardado:", registro)
            return render_template("index.html", form=LoanForm(), prob=prob, risk_level=risk_level, explanation_data=explanation_data)
        except Exception as e:
            db.session.rollback()
            flash(f"❌ Error al procesar la solicitud: {e}", "danger")
            print("❌ Error al procesar:", e)
    else:
        if request.method == "POST":
            print("❌ Errores en validación:", form.errors)
            # Mostrar errores de campos en el frontend
            for field, errors in form.errors.items():
                for error in errors:
                    flash(f"{form[field].label.text}: {error}", "danger")

    return render_template("index.html", form=form, prob=prob, risk_level=risk_level, explanation_data=explanation_data)


# 👉 Ruta de prueba para verificar si la DB guarda registros
@app.route("/test-insert")
def test_insert():
    try:
        registro = LoanApplication(
            email="test@example.com",
            documento="123456789",
            Age=30, Income=50000, LoanAmount=10000, CreditScore=700,
            MonthsEmployed=60, NumCreditLines=3, InterestRate=10, LoanTerm=24,
            DTIRatio=0.2, EmploymentType=1, MaritalStatus=0, HasMortgage=1,
            HasDependents=0, LoanPurpose=2, HasCoSigner=0, Education_num=3,
            prediccion=55.5
        )
        db.session.add(registro)
        db.session.commit()
        return "✅ Insert OK"
    except Exception as e:
        db.session.rollback()
        return f"❌ Error en insert: {e}"


if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)
