import streamlit as st
import math
import io
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet


# --- New function: Estimate CFM from pressure (bar) and area (m^2) ---
def pressure_to_cfm(pressure_bar, area_m2, discharge_coeff=0.8, air_density=1.2):
    delta_p = pressure_bar * 100000  # Pa
    velocity = discharge_coeff * math.sqrt(2 * delta_p / air_density)
    flow_m3_s = velocity * area_m2
    flow_cfm = flow_m3_s * 2118.88
    return round(flow_cfm, 2)


# --- Spray Rate Scale-Up ---
def spray_rate_scaleup(SR1, AV1, AV2):
    return round(SR1 * AV2 / AV1, 2)


# --- Atomizing Air Volume Scale-Up ---
def atomizing_air_volume_scaleup(AAV1, SR2, SR1):
    return round(AAV1 * SR2 / SR1, 2)


# --- Air Volume Scale-Up ---
def air_volume_scaleup(AV1, A1, A2):
    return round(AV1 * A1 / A2, 2)


# --- Bottom Screen Area ---
def bottom_screen_area(diameter_m):
    radius = diameter_m / 2
    area = math.pi * radius * radius
    return round(area, 4)


def main():
    st.title("🌬️ FBP Granulation Scale-Up (Top Spray)")

    if 'results' not in st.session_state:
        st.session_state['results'] = {}

    # 0️⃣ Pressure to CFM Estimator
    st.header("0️⃣ Pressure to CFM Estimator")
    pressure_input = st.number_input("Input Pressure (gauge) [bar]", min_value=0.0, value=2.0, key="pressure_input")
    area_input = st.number_input("Cross-sectional Area [m²]", min_value=0.0001, value=0.01, key="area_input")
    if st.button("Calculate CFM from Pressure", key="calc_pressure_cfm"):
        cfm_result = pressure_to_cfm(pressure_input, area_input)
        st.session_state['results']['Pressure to CFM'] = {
            "Input Pressure (bar)": pressure_input,
            "Cross-sectional Area (m²)": area_input,
            "Estimated Air Flow (CFM)": cfm_result,
        }
        st.success(f"Estimated Air Flow: {cfm_result} CFM")

    st.markdown("---")

    # 1️⃣ Spray Rate Scale-Up
    st.header("1️⃣ Spray Rate Scale-Up")
    SR1 = st.number_input("Lab Scale Spray Rate (SR1) [g/min]", min_value=0.0, value=50.0, key="SR1_ind")
    AV1 = st.number_input("Lab Scale Air Volume (AV1) [CFM]", min_value=0.0, value=100.0, key="AV1_ind")
    AV2 = st.number_input("Pilot Scale Air Volume (AV2) [CFM]", min_value=0.0, value=400.0, key="AV2_ind")
    if st.button("Calculate Spray Rate Scale-Up", key="calc_spray_rate"):
        SR2 = spray_rate_scaleup(SR1, AV1, AV2)
        st.session_state['results']['Spray Rate Scale-Up'] = {
            "Lab Spray Rate SR1 (g/min)": SR1,
            "Lab Air Volume AV1 (CFM)": AV1,
            "Pilot Air Volume AV2 (CFM)": AV2,
            "Calculated Pilot Spray Rate SR2 (g/min)": SR2
        }
        st.success(f"Calculated Pilot Spray Rate (SR2): {SR2} g/min")

    st.markdown("---")

    # 2️⃣ Atomizing Air Volume Scale-Up
    st.header("2️⃣ Atomizing Air Volume Scale-Up")
    AAV1 = st.number_input("Lab Atomizing Air Volume (AAV1) [CFM]", min_value=0.0, value=10.0, key="AAV1_ind")
    SR2_atom = st.number_input("Pilot Spray Rate (SR2) [g/min]", min_value=0.0, value=200.0, key="SR2_atom_ind")
    SR1_atom = st.number_input("Lab Spray Rate (SR1) [g/min]", min_value=0.0, value=50.0, key="SR1_atom_ind")
    if st.button("Calculate Atomizing Air Volume Scale-Up", key="calc_atom_air_vol"):
        AAV2 = atomizing_air_volume_scaleup(AAV1, SR2_atom, SR1_atom)
        st.session_state['results']['Atomizing Air Volume Scale-Up'] = {
            "Lab Atomizing Air Volume AAV1 (CFM)": AAV1,
            "Lab Spray Rate SR1 (g/min)": SR1_atom,
            "Pilot Spray Rate SR2 (g/min)": SR2_atom,
            "Calculated Pilot Atomizing Air Volume AAV2 (CFM)": AAV2
        }
        st.success(f"Calculated Pilot Atomizing Air Volume (AAV2): {AAV2} CFM")

    st.markdown("---")

    # 3️⃣ Bottom Screen Area Calculation
    st.header("3️⃣ Bottom Screen Area Calculation")
    d_lab = st.number_input("Lab Bottom Screen Diameter [m]", min_value=0.01, value=0.5, key="d_lab_ind")
    d_pilot = st.number_input("Pilot Bottom Screen Diameter [m]", min_value=0.01, value=1.0, key="d_pilot_ind")
    if st.button("Calculate Bottom Screen Areas", key="calc_bottom_screen"):
        A1 = bottom_screen_area(d_lab)
        A2 = bottom_screen_area(d_pilot)
        st.session_state['results']['Bottom Screen Area'] = {
            "Lab Bottom Screen Diameter (m)": d_lab,
            "Lab Bottom Screen Area (m²)": A1,
            "Pilot Bottom Screen Diameter (m)": d_pilot,
            "Pilot Bottom Screen Area (m²)": A2,
        }
        st.success(f"Lab Bottom Screen Area: {A1} m²\nPilot Bottom Screen Area: {A2} m²")

    st.markdown("---")

    # 4️⃣ Air Volume Scale-Up
    st.header("4️⃣ Air Volume Scale-Up")
    AV1_air = st.number_input("Lab Scale Air Volume (AV1) [CFM]", min_value=0.0, value=100.0, key="AV1_air_ind")
    A1_air = st.number_input("Lab Bottom Screen Area (A1) [m²]", min_value=0.0001, value=0.1963, key="A1_air_ind")  # Default approx for 0.5m diameter
    A2_air = st.number_input("Pilot Bottom Screen Area (A2) [m²]", min_value=0.0001, value=0.7854, key="A2_air_ind")  # Default approx for 1.0m diameter
    if st.button("Calculate Air Volume Scale-Up", key="calc_air_vol"):
        AV2_air = air_volume_scaleup(AV1_air, A1_air, A2_air)
        st.session_state['results']['Air Volume Scale-Up'] = {
            "Lab Air Volume AV1 (CFM)": AV1_air,
            "Lab Bottom Screen Area A1 (m²)": A1_air,
            "Pilot Bottom Screen Area A2 (m²)": A2_air,
            "Calculated Pilot Air Volume AV2 (CFM)": AV2_air
        }
        st.success(f"Calculated Pilot Air Volume (AV2): {AV2_air} CFM")

    st.markdown("---")

    # --- PDF Report Generation ---
    st.header("📄 Generate PDF Report")
    if st.button("Generate and Download PDF Report"):
        if st.session_state['results']:
            pdf_output = io.BytesIO()
            doc = SimpleDocTemplate(pdf_output, pagesize=A4)
            styles = getSampleStyleSheet()
            story = []
            story.append(Paragraph("🌬️ FBP Granulation Scale-Up Report (Top Spray)", styles['Title']))
            story.append(Spacer(1, 12))

            for section, data in st.session_state['results'].items():
                story.append(Paragraph(section, styles['Heading2']))
                for key, val in data.items():
                    story.append(Paragraph(f"{key}: {val}", styles['Normal']))
                story.append(Spacer(1, 12))

            doc.build(story)

            st.download_button(
                label="📥 Download PDF Report",
                data=pdf_output.getvalue(),
                file_name="fbp_granulation_scaleup_report.pdf",
                mime="application/pdf"
            )
        else:
            st.warning("No calculation results found. Please calculate parameters first.")


    # Display all stored results
    st.markdown("### 🔍 All Calculated Results")
    if st.session_state['results']:
        for section, values in st.session_state['results'].items():
            st.subheader(section)
            for k, v in values.items():
                st.write(f"**{k}**: {v}")
    else:
        st.info("Perform calculations to see results here.")


if __name__ == "__main__":
    main()
