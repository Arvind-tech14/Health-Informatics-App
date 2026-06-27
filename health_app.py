import streamlit as st


# --- 1. CORE CALCULATION FUNCTIONS ---
def calculate_bmi(weight_kg, height_cm):
    height_m = height_cm / 100
    return weight_kg / (height_m ** 2)


def calculate_bmr(weight, height, age, gender):
    # Mifflin-St Jeor Equation
    if gender == "Male":
        return (10 * weight) + (6.25 * height) - (5 * age) + 5
    else:
        return (10 * weight) + (6.25 * height) - (5 * age) - 161


def calculate_tdee(bmr, activity_level):
    multipliers = {
        "Sedentary (office job)": 1.2,
        "Light Exercise (1-2 days/week)": 1.375,
        "Moderate Exercise (3-5 days/week)": 1.55,
        "Heavy Exercise (6-7 days/week)": 1.725
    }
    return bmr * multipliers[activity_level]


def estimate_body_age(chronological_age, bmi, activity_level):
    body_age = chronological_age
    if bmi > 25:
        body_age += (bmi - 25) * 0.8
    elif bmi < 18.5:
        body_age += (18.5 - bmi) * 0.5

    if "Moderate" in activity_level or "Heavy" in activity_level:
        body_age -= 3
    elif "Sedentary" in activity_level:
        body_age += 2

    return max(15, round(body_age))


# --- 2. HEALTH ASSESSMENT LOGIC ---
def evaluate_health(bmi, tdee, real_age, body_age):
    # Evaluate BMI & Diet Management
    if bmi < 18.5:
        status = "Underweight (Low Health Score)"
        color = "warning"
        advice = f"Action: Aim for a caloric surplus to build mass. Try consuming ~{int(tdee + 500)} kcal/day focusing on protein and strength training."
    elif 18.5 <= bmi < 25:
        status = "Normal Weight (Optimal Health Score)"
        color = "success"
        advice = f"Action: Great job! To maintain your current healthy state, keep your daily intake around {int(tdee)} kcal/day."
    elif 25 <= bmi < 30:
        status = "Overweight (Warning Score)"
        color = "warning"
        advice = f"Action: Aim for a slight caloric deficit to lose fat. Try consuming ~{int(tdee - 500)} kcal/day and increase daily step count."
    else:
        status = "Obese (High Risk Score)"
        color = "error"
        advice = f"Action: Focus on a structured caloric deficit of ~{int(tdee - 500)} to {int(tdee - 750)} kcal/day. Prioritize whole foods and consult a physician."

    # Evaluate Age Metrics
    if body_age > real_age:
        age_warning = "Your estimated biological age is higher than your real age. Improving activity levels will lower this."
    else:
        age_warning = "Excellent! Your biological age indicates your body is handling metabolic stress well."

    return status, advice, color, age_warning


# --- 3. USER INTERFACE CONFIGURATION ---
st.set_page_config(page_title="Health Informatics App", layout="wide")

st.title("🏃‍♂️ Personal Health & Fitness Informatics")
st.markdown("A professional dashboard calculating essential physiological metrics and health status.")

# Input Layout
st.subheader("1. Enter Parameters")
col_in1, col_in2, col_in3, col_in4, col_in5 = st.columns(5)

gender = col_in1.selectbox("Biological Sex", ["Male", "Female"])
age = col_in2.number_input("Age (Years)", min_value=0, max_value=100, value=0)
weight = col_in3.number_input("Weight (kg)", min_value=0.0, max_value=200.0, value=0.0)
height = col_in4.number_input("Height (cm)", min_value=0.0, max_value=250.0, value=0.0)
activity = col_in5.selectbox("Activity Level", [
    "Sedentary (office job)",
    "Light Exercise (1-2 days/week)",
    "Moderate Exercise (3-5 days/week)",
    "Heavy Exercise (6-7 days/week)"
])

# Create a Calculate Button
if st.button("Calculate", type="primary"):
    # Prevent calculation if height or weight is 0 to avoid DivisionByZero errors
    if height == 0 or weight == 0 or age == 0:
        st.warning("⚠️ Please enter valid values (greater than 0) for Age, Weight, and Height.")
    else:
        # --- 4. EXECUTE MATHS ---
        bmi = calculate_bmi(weight, height)
        bmr = calculate_bmr(weight, height, age, gender)
        tdee = calculate_tdee(bmr, activity)
        body_age = estimate_body_age(age, bmi, activity)
        status, advice, color, age_warning = evaluate_health(bmi, tdee, age, body_age)

        # --- 5. DISPLAY METRICS ---
        st.divider()
        st.subheader("2. Calculated Data Output")

        col_out1, col_out2, col_out3, col_out4 = st.columns(4)
        col_out1.metric("Body Mass Index (BMI)", f"{bmi:.1f}")
        col_out2.metric("Basal Metabolic Rate (BMR)", f"{int(bmr)} kcal/day")
        col_out3.metric("Total Daily Energy (TDEE)", f"{int(tdee)} kcal/day")
        col_out4.metric("Estimated Biological Body Age", f"{body_age} Years")

        # --- 6. HEALTH ASSESSMENT REPORT ---
        st.divider()
        st.subheader("3. Health Status & Management Plan")

        # Streamlit colored alert boxes based on the evaluation
        if color == "success":
            st.success(f"**Overall Status:** {status}")
        elif color == "warning":
            st.warning(f"**Overall Status:** {status}")
        else:
            st.error(f"**Overall Status:** {status}")

        # Display actionable advice
        st.info(f"**Diet Management:** {advice}")
        st.info(f"**Metabolic Age Note:** {age_warning}")
