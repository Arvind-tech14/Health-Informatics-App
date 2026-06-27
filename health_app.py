import streamlit as st


# --- 1. CORE CALCULATION FUNCTIONS ---
def calculate_bmi(weight_kg, height_cm):
    height_m = height_cm / 100
    return weight_kg / (height_m ** 2)


def calculate_bmr(weight, height, age, gender):
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


def calculate_ibw(height_cm, gender):
    # Devine Formula: Calculates ideal weight based on height and biological sex.
    inches_over_5_feet = (height_cm - 152.4) / 2.54

    if inches_over_5_feet < 0:
        inches_over_5_feet = 0

    if gender == "Male":
        return 50.0 + (2.3 * inches_over_5_feet)
    else:
        return 45.5 + (2.3 * inches_over_5_feet)


# --- 2. HEALTH ASSESSMENT LOGIC ---
def evaluate_health(bmi, tdee, real_age, body_age):
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

    if body_age > real_age:
        age_warning = "Your estimated biological age is higher than your real age. Improving activity levels will lower this."
    else:
        age_warning = "Excellent! Your biological age indicates your body is handling metabolic stress well."

    return status, advice, color, age_warning


# --- 3. USER INTERFACE CONFIGURATION ---
st.set_page_config(page_title="Health Informatics App", layout="wide")

st.title("🏃‍♂️ Personal Health & Fitness Informatics")
st.markdown(
    "A professional dashboard calculating essential physiological metrics, health status, and predictive timelines.")

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
    if height == 0 or weight == 0 or age == 0:
        st.warning("⚠️ Please enter valid values (greater than 0) for Age, Weight, and Height.")
    else:
        # --- 4. EXECUTE MATHS ---
        bmi = calculate_bmi(weight, height)
        bmr = calculate_bmr(weight, height, age, gender)
        tdee = calculate_tdee(bmr, activity)
        body_age = estimate_body_age(age, bmi, activity)
        ibw = calculate_ibw(height, gender)
        weight_variance = weight - ibw

        status, advice, color, age_warning = evaluate_health(bmi, tdee, age, body_age)

        # NEW: Predictive Analytics Math (Time to Goal formatted in Months/Weeks/Days)
        # 1 kg of body mass is roughly 7,700 kcal.
        total_kcal_needed = abs(weight_variance) * 7700
        total_days = int(total_kcal_needed / 500)  # Dividing by our 500 daily calorie offset

        # The Math: Breaking total days into M/W/D
        months = total_days // 30
        leftover_days = total_days % 30
        weeks = leftover_days // 7
        days = leftover_days % 7

        time_string = f"{months} Months, {weeks} Weeks, and {days} Days"

        # --- 5. DISPLAY METRICS ---
        st.divider()
        st.subheader("2. Calculated Data Output")

        col_out1, col_out2, col_out3, col_out4, col_out5 = st.columns(5)

        col_out1.metric("Body Mass Index (BMI)", f"{bmi:.1f}")
        col_out2.metric("Total Daily Energy (TDEE)", f"{int(tdee)} kcal")
        col_out3.metric("Ideal Body Weight (IBW)", f"{ibw:.1f} kg")

        if abs(weight_variance) < 1.0:
            col_out4.metric("Ideal Weight Delta", "Perfect Match!", delta="0.0 kg", delta_color="normal")
        else:
            col_out4.metric("Ideal Weight Delta", f"{weight_variance:+.1f} kg", delta="Target Deviation",
                            delta_color="inverse")

        col_out5.metric("Est. Biological Age", f"{body_age} Yrs")

        # --- 6. HEALTH ASSESSMENT REPORT ---
        st.divider()
        st.subheader("3. Health Status & Management Plan")

        # First, we determine the timeline text based on the variance
        if abs(weight_variance) < 1.0:
            timeline_text = "You are currently at your ideal weight. Maintain your current daily calorie intake to stay here!"
        else:
            timeline_text = f"If you strictly follow the diet management plan (a 500 kcal/day offset), you will safely reach your Ideal Body Weight in approximately **{time_string}**."

        # Next, we build the bullet point list using a multi-line formatted string
        bulleted_report = f"""
                * **Overall Status:** {status}
                * **Diet Management:** {advice}
                * **🗓️ Goal Timeline:** {timeline_text}
                * **Metabolic Age Note:** {age_warning}
                """

        # Finally, we display the entire bulleted list inside the dynamically colored box!
        if color == "success":
            st.success(bulleted_report)
        elif color == "warning":
            st.warning(bulleted_report)
        else:
            st.error(bulleted_report)
