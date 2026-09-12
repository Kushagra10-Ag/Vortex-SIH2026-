import joblib
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from pathlib import Path
from app.db import db
from sqlalchemy import text

MODEL_PATH = Path(__file__).resolve().parents[2] / "ai_models" / "sales_model.pkl"
model = None


def _get_model():
    global model
    if model is None:
        if not MODEL_PATH.is_file():
            raise RuntimeError(f"Sales forecast model not found: {MODEL_PATH}")
        model = joblib.load(MODEL_PATH)
    return model

def get_sales_forecast():
    # 🔥 fetch real data
    results = db.session.execute(text("""
        SELECT DATE(created_at) as date,
        SUM(total_amount) as sales
        FROM bills
        GROUP BY date
        ORDER BY date
    """)).fetchall()

    # extract sales and dates
    dates = [r[0] for r in results]
    sales = [float(r[1]) for r in results]

    # last date from DB
    last_date = dates[-1]

    # prepare future data (next 7 days)
    future_data = []

    for i in range(1, 8):
        future_date = last_date + timedelta(days=i)

        day_index = len(sales) + i
        day_of_week = future_date.weekday()
        month = future_date.month

        future_data.append([
            day_index, day_of_week, month
        ])

    # convert to DataFrame (IMPORTANT)
    future_df = pd.DataFrame(
        future_data,
        columns=['day_index', 'day_of_week', 'month']
    )

    # predict
    predictions = _get_model().predict(future_df)

    return [
    {
        "label": f"T+{i+1}",
        "value": float(predictions[i])
    }
    for i in range(len(predictions))
]