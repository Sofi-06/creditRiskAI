from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class LoanApplication(db.Model):
    __tablename__ = "loan_applications"
    __table_args__ = (
        db.Index("ix_loan_applications_created_at", "created_at"),
    )

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)

    # Datos personales adicionales
    email = db.Column(db.String(120), nullable=False)
    documento = db.Column(db.String(50), nullable=False)

    Age = db.Column(db.Float, nullable=False)
    Income = db.Column(db.Float, nullable=False)
    LoanAmount = db.Column(db.Float, nullable=False)
    CreditScore = db.Column(db.Float, nullable=False)
    MonthsEmployed = db.Column(db.Float, nullable=False)
    NumCreditLines = db.Column(db.Float, nullable=False)
    InterestRate = db.Column(db.Float, nullable=False)
    LoanTerm = db.Column(db.Float, nullable=False)
    DTIRatio = db.Column(db.Float, nullable=False)

    EmploymentType = db.Column(db.Float, nullable=False)
    MaritalStatus = db.Column(db.Float, nullable=False)
    HasMortgage = db.Column(db.Float, nullable=False)
    HasDependents = db.Column(db.Float, nullable=False)
    LoanPurpose = db.Column(db.Float, nullable=False)
    HasCoSigner = db.Column(db.Float, nullable=False)
    Education_num = db.Column(db.Float, nullable=False)

    # 👉 Nuevo campo: probabilidad de mora (en %)
    prediccion = db.Column(db.Float, nullable=False)

    created_at = db.Column(db.DateTime, default=datetime.now, nullable=False)

    def __repr__(self):
        return f"<LoanApplication {self.id} Email={self.email} Documento={self.documento} Pred={self.prediccion}>"
