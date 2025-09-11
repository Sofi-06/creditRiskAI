import numpy as np
import pandas as pd

def predecir_mora(registro, predictor, scaler, cols):
    df = pd.DataFrame([registro], columns=cols)
    X_scaled = scaler.transform(df[cols])

    idx_pos = int(np.where(predictor.classes_ == 1)[0][0])
    proba = predictor.predict_proba(X_scaled)[0][idx_pos]
    return proba
