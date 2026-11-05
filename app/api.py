from typing import Literal

import joblib
import pandas as pd
from fastapi import FastAPI
from pydantic import BaseModel
from pathlib import Path


# بارگذاری Pipeline ذخیره‌شده: پیش‌پردازشگر و مدل با هم
MODEL_PATH = Path(__file__).resolve().parent.parent / "models" / "calorie_model.joblib"
model = joblib.load(MODEL_PATH)


# ساخت برنامه‌ی API
app = FastAPI(title="Workout Calorie Estimator")


# تعریف شکل ورودی‌ای که کاربر باید بفرستد
class WorkoutInput(BaseModel):
    Age: int
    Gender: Literal["Male", "Female"]
    Weight_kg: float
    Height_m: float
    Max_BPM: int
    Avg_BPM: int
    Resting_BPM: int
    Session_Duration_hours: float
    Workout_Type: Literal["Yoga", "HIIT", "Cardio", "Strength"]
    Fat_Percentage: float
    Water_Intake_liters: float
    Workout_Frequency_days_per_week: int
    Experience_Level: int
    BMI: float


# بررسی اینکه API و مدل بارگذاری شده‌اند
@app.get("/health")
def health():
    return {"status": "ok", "model_loaded": True}


# گرفتن اطلاعات جلسه و پیش‌بینی کالری
@app.post("/predict")
def predict_calories(data: WorkoutInput):
    # تبدیل نام‌های ساده‌ی ورودی API به نام دقیق ستون‌های دیتاست
    row = {
        "Age": data.Age,
        "Gender": data.Gender,
        "Weight (kg)": data.Weight_kg,
        "Height (m)": data.Height_m,
        "Max_BPM": data.Max_BPM,
        "Avg_BPM": data.Avg_BPM,
        "Resting_BPM": data.Resting_BPM,
        "Session_Duration (hours)": data.Session_Duration_hours,
        "Workout_Type": data.Workout_Type,
        "Fat_Percentage": data.Fat_Percentage,
        "Water_Intake (liters)": data.Water_Intake_liters,
        "Workout_Frequency (days/week)": data.Workout_Frequency_days_per_week,
        "Experience_Level": data.Experience_Level,
        "BMI": data.BMI,
    }

    # ساخت یک ردیف جدولی؛ Pipeline با DataFrame و نام ستون‌ها کار می‌کند
    input_data = pd.DataFrame([row])

    # پیش‌بینی یک مقدار کالری برای این جلسه
    estimate = model.predict(input_data)[0]

    # برگرداندن پاسخ به شکل JSON
    return {
        "estimated_calories": round(float(estimate), 2),
        "message": "This is a model estimate, not a definite measurement."
    }


