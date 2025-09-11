from flask_wtf import FlaskForm
from wtforms import FloatField, StringField, SubmitField, SelectField
from wtforms.validators import InputRequired, NumberRange, Email, Length

class LoanForm(FlaskForm):
    # Campos nuevos
    email = StringField("Correo electrónico", validators=[InputRequired(), Email(), Length(max=120)])
    documento = StringField("Documento de identidad", validators=[InputRequired(), Length(max=50)])

    Age = FloatField("Edad", validators=[InputRequired(), NumberRange(min=18, max=100)])
    Income = FloatField("Ingresos", validators=[InputRequired(), NumberRange(min=0)])
    MonthlyExpenses = FloatField("Gastos mensuales", validators=[InputRequired(), NumberRange(min=0)])
    LoanAmount = FloatField("Monto del préstamo", validators=[InputRequired(), NumberRange(min=0)])
    CreditScore = FloatField("Puntaje de crédito", validators=[InputRequired(), NumberRange(min=0, max=1000)])
    MonthsEmployed = FloatField("Meses empleado", validators=[InputRequired(), NumberRange(min=0)])
    NumCreditLines = FloatField("Número de líneas de crédito", validators=[InputRequired(), NumberRange(min=0)])
    InterestRate = FloatField("Tasa de interés", validators=[InputRequired(), NumberRange(min=0)])
    LoanTerm = FloatField("Plazo del préstamo (meses)", validators=[InputRequired(), NumberRange(min=1)])

    EmploymentType = SelectField(
        "Tipo de empleo",
        choices=[
            (0, "Desempleado"),
            (1, "Medio tiempo"),
            (2, "Tiempo completo"),
            (3, "Independiente")
        ],
        coerce=int,
        validators=[InputRequired()]
    )
    MaritalStatus = SelectField(
        "Estado civil",
        choices=[
            (1, "Casado"),
            (2, "Soltero"),
            (3, "Divorciado")
        ],
        coerce=int,
        validators=[InputRequired()]
    )
    HasMortgage = SelectField(
        "¿Tiene hipoteca?",
        choices=[(0, "No"), (1, "Sí")],
        coerce=int,
        validators=[InputRequired()]
    )
    HasDependents = SelectField(
        "¿Tiene dependientes?",
        choices=[(0, "No"), (1, "Sí")],
        coerce=int,
        validators=[InputRequired()]
    )
    LoanPurpose = SelectField(
        "Propósito del préstamo",
        choices=[
            (1, "Negocio"),
            (2, "Vivienda"),
            (3, "Educación"),
            (4, "Otro"),
            (5, "Auto")
        ],
        coerce=int,
        validators=[InputRequired()]
    )
    HasCoSigner = SelectField(
        "¿Tiene codeudor?",
        choices=[(0, "No"), (1, "Sí")],
        coerce=int,
        validators=[InputRequired()]
    )
    Education_num = SelectField(
        "Nivel educativo",
        choices=[
            (1, "Sin estudios"),
            (2, "Secundaria"),
            (3, "Universitario"),
            (4, "Maestría"),
            (5, "Doctorado")
        ],
        coerce=int,
        validators=[InputRequired()]
    )

    submit = SubmitField("Predecir")
