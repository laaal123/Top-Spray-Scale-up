import streamlit as st
import math
import io
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors
from reportlab.lib.units import inch

# --- Conversion function: Pressure (bar) to CFM ---
def pressure_to_cfm(pressure_bar, area_m2, discharge_coeff=0.8, air_density=1.2):
    # Calculate air velocity (m/s)
    delta_p = pressure_bar * 100000  # Convert bar to Pa
    velocity = discharge_coeff * math.sqrt(2 * delta_p / air_density)
    flow_m3_s = velocity * area_m2
    flow_cfm = flow_m3_s * 2118.88  # Convert m3/s to CFM
    return round(flow_cfm, 2)

# --- Spray Rate Scale-Up ---
def spray_rate_scaleup(SR1, AV1, AV2):
    # SR2 = SR1 * (AV2 / AV1)
    return round(SR1 * AV2 / AV1, 4)

# --- Atomizing Air Volume Scale-Up ---
def atomizing_air_volume_scaleup(AAV1, SR2, SR1):
    # AAV2 = AAV1 * (SR2 / SR1)
    return round(AAV1 * SR2 / SR1, 4)

# --- Bottom Screen Area Calculation ---
def bottom_screen_area(radius_m):
    # A = π * r^2
    return round(math.pi * radius_m ** 2, 6)

# --- Air Volume Scale-Up ---
def air_volume_scaleup(AV1, A1, A2):
    # AV2 = AV1 * (A1 / A2)
    return round(AV1 * A1 / A2, 4)

# --- PDF generation ---
def generate_pdf(results):
    pdf_output = io.BytesIO()
    doc = SimpleDocTemplate(pdf_output, pagesize=A4)
    styles = getSampleStyleSheet()
    story = []

    story.append(Paragraph("🌬️ FBP Granulation Scale-Up Report (Top Spray)", styles['Title']))
    story.append(Spacer(1, 12))

    for section, data in results.items():
        story.append(Paragraph(f"<b>{section}</b>", styles['Heading2']))
        for key, val in data.items():
            story.append(Paragraph(f"{key}: {val}", styles['Normal']))
        story.append(Spacer(1, 12))

    doc.build(story)
    return pdf_output.getvalue()

# --- Main App ---
def main():
    st.title("🌬️ FBP Granulation Scale-Up (Top Spray)")
    st.markdown("Calculate scale-up parameters for spray rate, atomizing air volume, air volume, and bottom screen area.")

    # Initialize session state for persistent results
    if 'results' not in st.session_state:
        st.session_state.results = {}

    # 0️⃣ Pressure to CFM calculator
    st.header("0️⃣ Pressure to CFM Conversion")
    pressure_bar = st.number_input("Input Pressure (Gauge) [bar]", min_value=0.0, value=2.0, step=0.01, key="pressure_bar")
    area_m2 = st.number_input("Cross-sectional Area [m²]", min_value=0.0001, value=0.01, step=0.0001, key="area_m2")
    if st.button("Calculate CFM from Pressure", key="btn_pressure_cfm"):
        cfm = pressure_to_cfm(pressure_bar, area_m2)
        st.session_state.results['Pressure to CFM'] = {
            "Input Pressure (bar)": pressure_bar,
            "Area (m²)": area_m2,
            "Estimated Air Flow (CFM)": cfm
        }
        st.success(f"Estimated Air Flow: {cfm} CFM")

    st.markdown("---")

    # 1️⃣ Spray Rate Scale-Up
    st.header("1️⃣ Spray Rate Scale-Up")
    SR1 = st.number_input("Lab Scale Spray Rate (SR1, g/min)", min_value=0.0, value=50.0, step=0.1, key="SR1")
    AV1 = st.number_input("Lab Scale Air Volume (AV1, CFM)", min_value=0.0, value=100.0, step=0.1, key="AV1")
    AV2 = st.number_input("Pilot Scale Air Volume (AV2, CFM)", min_value=0.0, value=400.0, step=0.1, key="AV2")
    if st.button("Calculate Spray Rate Scale-Up", key="btn_spray_rate"):
        SR2 = spray_rate_scaleup(SR1, AV1, AV2)
        st.session_state.results['Spray Rate Scale-Up'] = {
            "Lab Spray Rate SR1 (g/min)": SR1,
            "Lab Air Volume AV1 (CFM)": AV1,
            "Pilot Air Volume AV2 (CFM)": AV2,
            "Calculated Pilot Spray Rate SR2 (g/min)": SR2
        }
        st.success(f"Calculated Pilot Spray Rate (SR2): {SR2} g/min")

    st.markdown("---")

    # 2️⃣ Atomizing Air Volume Scale-Up
    st.header("2️⃣ Atomizing Air Volume Scale-Up")
    AAV1 = st.number_input("Lab Atomizing Air Volume (AAV1, CFM)", min_value=0.0, value=10.0, step=0.1, key="AAV1")
    # Pilot Spray Rate (SR2) defaults to previous calculation if exists
    default_SR2 = st.session_state.results.get('Spray Rate Scale-Up', {}).get("Calculated Pilot Spray Rate SR2 (g/min)", 200.0)
    SR2_atom = st.number_input("Pilot Spray Rate (SR2, g/min)", min_value=0.0, value=default_SR2, step=0.1, key="SR2_atom")
    if st.button("Calculate Atomizing Air Volume Scale-Up", key="btn_atom_air_vol"):
        AAV2 = atomizing_air_volume_scaleup(AAV1, SR2_atom, SR1)
        st.session_state.results['Atomizing Air Volume Scale-Up'] = {
            "Lab Atomizing Air Volume AAV1 (CFM)": AAV1,
            "Lab Spray Rate SR1 (g/min)": SR1,
            "Pilot Spray Rate SR2 (g/min)": SR2_atom,
            "Calculated Pilot Atomizing Air Volume AAV2 (CFM)": AAV2
        }
        st.success(f"Calculated Pilot Atomizing Air Volume (AAV2): {AAV2} CFM")

    st.markdown("---")

    # 3️⃣ Bottom Screen Area Calculation
    st.header("3️⃣ Bottom Screen Area Calculation")
    radius_lab = st.number_input("Lab Bottom Screen Radius (m)", min_value=0.001, value=0.25, step=0.001, key="radius_lab")
    radius_pilot = st.number_input("Pilot Bottom Screen Radius (m)", min_value=0.001, value=0.5, step=0.001, key="radius_pilot")
    area_lab = bottom_screen_area(radius_lab)
    area_pilot = bottom_screen_area(radius_pilot)
    st.session_state.results['Bottom Screen Area'] = {
        "Lab Bottom Screen Radius (m)": radius_lab,
        "Calculated Lab Bottom Screen Area (m²)": area_lab,
        "Pilot Bottom Screen Radius (m)": radius_pilot,
        "Calculated Pilot Bottom Screen Area (m²)": area_pilot
    }
    st.info(f"Lab Bottom Screen Area: {area_lab} m²\nPilot Bottom Screen Area: {area_pilot} m²")

    st.markdown("---")

    # 4️⃣ Air Volume Scale-Up
    st.header("4️⃣ Air Volume Scale-Up")
    AV1_air = st.number_input("Lab Air Volume (AV1, CFM)", min_value=0.0, value=100.0, step=0.1, key="AV1_air")
    if st.button("Calculate Air Volume Scale-Up", key="btn_air_vol"):
        AV2_air = air_volume_scaleup(AV1_air, area_lab, area_pilot)
        st.session_state.results['Air Volume Scale-Up'] = {
            "Lab Air Volume AV1 (CFM)": AV1_air,
            "Lab Bottom Screen Area A1 (m²)": area_lab,
            "Pilot Bottom Screen Area A2 (m²)": area_pilot,
            "Calculated Pilot Air Volume AV2 (CFM)": AV2_air
        }
        st.success(f"Calculated Pilot Air Volume (AV2): {AV2_air} CFM")

    st.markdown("---")

    # --- PDF Report Generation ---
    st.header("📄 Generate PDF Report")
    if st.button("Generate and Download PDF Report"):
        if st.session_state.results:
            pdf_data = generate_pdf(st.session_state.results)
            st.download_button(
                label="📥 Download PDF Report",
                data=pdf_data,
                file_name="FBP_Granulation_Scale_Up_Report.pdf",
                mime="application/pdf"
            )
        else:
            st.warning("No calculation results to include in PDF. Please perform calculations first.")

    # Display all stored results on page
    st.markdown("### 🔍 All Calculated Results:")
    if st.session_state.results:
        for section, values in st.session_state.results.items():
            st.subheader(section)
            for k, v in values.items():
                st.write(f"**{k}**: {v}")
    else:
        st.info("Perform calculations to see results here.")

if __name__ == "__main__":
    main()

