import requests
import pandas as pd
import streamlit as st


# تنظیم عنوان و توضیح صفحه
st.title("Workout Calorie Estimator")
st.write("کالری نمایش‌داده‌شده تخمین مدل است، نه اندازه‌گیری قطعی.")


# ساخت فرم ورود اطلاعات جلسه
with st.form("workout_form"):
    age = st.number_input("سن", min_value=1, value=56)
    gender = st.selectbox("جنسیت", ["Male", "Female"])

    weight = st.number_input("وزن (kg)", min_value=1.0, value=88.3)
    height = st.number_input("قد (m)", min_value=0.5, value=1.71)

    max_bpm = st.number_input("حداکثر ضربان قلب", min_value=1, value=180)
    avg_bpm = st.number_input("میانگین ضربان قلب", min_value=1, value=157)
    resting_bpm = st.number_input("ضربان قلب در حالت استراحت", min_value=1, value=60)

    duration = st.number_input(
        "مدت جلسه (ساعت)",
        min_value=0.1,
        value=1.69
    )

    workout_type = st.selectbox(
        "نوع تمرین",
        ["Yoga", "HIIT", "Cardio", "Strength"]
    )

    fat_percentage = st.number_input(
        "درصد چربی بدن",
        min_value=0.0,
        value=12.6
    )

    water_intake = st.number_input(
        "مصرف آب (لیتر)",
        min_value=0.0,
        value=3.5
    )

    frequency = st.number_input(
        "روزهای تمرین در هفته",
        min_value=1,
        max_value=7,
        value=4
    )

    experience = st.selectbox("سطح تجربه", [1, 2, 3])
    bmi = st.number_input("BMI", min_value=1.0, value=30.2)

    # اختیاری: مقدار ثبت‌شده برای مقایسه با تخمین
    has_actual = st.checkbox("کالری واقعی ثبت‌شده را دارم")
    actual_calories = st.number_input(
        "کالری واقعی",
        min_value=0.0,
        value=0.0,
        disabled=not has_actual
    )

    # مقادیر فرم فقط با فشردن این دکمه ارسال می‌شوند
    submitted = st.form_submit_button("تخمین کالری")


# پس از فشردن دکمه، ورودی را به قالب مورد انتظار API تبدیل می‌کنیم
if submitted:
    payload = {
        "Age": age,
        "Gender": gender,
        "Weight_kg": weight,
        "Height_m": height,
        "Max_BPM": max_bpm,
        "Avg_BPM": avg_bpm,
        "Resting_BPM": resting_bpm,
        "Session_Duration_hours": duration,
        "Workout_Type": workout_type,
        "Fat_Percentage": fat_percentage,
        "Water_Intake_liters": water_intake,
        "Workout_Frequency_days_per_week": frequency,
        "Experience_Level": experience,
        "BMI": bmi
    }

    try:
        # ارسال اطلاعات به API و گرفتن پاسخ
        response = requests.post(
            "http://127.0.0.1:8000/predict",
            json=payload,
            timeout=10
        )

        # اگر API خطای HTTP داده باشد، خطا را آشکار می‌کند
        response.raise_for_status()

        # تبدیل پاسخ JSON به دیکشنری پایتون
        result = response.json()

        estimate = result["estimated_calories"]

        st.success(f"تخمین مدل: {estimate:.2f} کالری")

        # اگر کالری واقعی وارد شده، اختلاف را هم نمایش می‌دهیم
        if has_actual:
            if actual_calories <= 0:
                st.error("برای مقایسه، کالری واقعی باید بیشتر از صفر باشد.")
            else:
                difference = estimate - actual_calories

                comparison = pd.DataFrame([{
                    "کالری واقعی": actual_calories,
                    "کالری تخمینی": estimate,
                    "اختلاف (تخمینی منهای واقعی)": difference
                }])

                st.dataframe(comparison, hide_index=True)

        st.caption(
            "این خروجی تخمین مدل است و مقدار قطعی یا اندازه‌گیری‌شده نیست."
        )

    except requests.exceptions.RequestException as error:
        st.error(
            "ارتباط با API برقرار نشد. مطمئن شو سرور FastAPI در حال اجراست."
        )
        st.code(str(error))

