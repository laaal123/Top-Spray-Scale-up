import streamlit as st
import math
import io
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors

# --- New function: Estimate CFM from pressure (bar) and area (m^2) ---
def pressure_to_cfm(pressure_bar, area_m2, discharge_coeff=0.8, air_density=1.2):
    """
    Estimate CFM (cubic feet per minute) from pressure in bar and cross-sectional area in m^2.

    pressure_bar: Upstream gauge pressure in bar (above atmospheric)
    area_m2: Cross-sectional flow area in m^2
    discharge_coeff: Dimensionless discharge coefficient (default 0.8)
    air_density: Air density kg/m3 (default 1.2 at 20°C)

    Returns volumetric flow rate in CFM (cubic feet per minute)
    """
    # Convert bar to Pascal (1 bar = 100000 Pa)
    delta_p = pressure_bar * 100000  # Pa

    # Flow velocity (m/s) from Bernoulli equation
    velocity = discharge_coeff * math.sqrt(2 * delta_p / air_density)

    # Volumetric flow rate in m³/s
    flow_m3_s = velocity * area_m2

    # Convert m³/s to CFM (1 m³/s = 2118.88 CFM)
    flow_cfm = flow_m3_s * 2118.88
    return round(flow_cfm, 2)


# --- Spray Rate Scale-Up ---
def spray_rate_scaleup(SR1, AV1, AV2):
    SR2 = SR1 * AV2 / AV1
    return round(SR2, 2)


# --- Atomizing Air Volume Scale-Up ---
def atomizing_air_volume_scaleup(AAV1, SR2, SR1):
    AAV2 = AAV1 * SR2 / SR1
    return round(AAV2, 2)


# --- Air Volume Scale-Up ---
def air_volume_scaleup(AV1, A1, A2):
    AV2 = AV1 * A1 / A2
    return round(AV2, 2)


# --- Bottom Screen Area ---
def bottom_screen_area(diameter_m):
    radius = diameter_m / 2
    area = math.pi * radius * radius
    return round(area, 4)


# --- Streamlit App ---
def main():
    st.title("🌬️ FBP Granulation Scale-Up (Top Spray)")

    st.header("0️⃣ Pressure to CFM Estimator")
    pressure_input = st.number_input("Input Pressure (gauge) [bar]", min_value=0.0, value=2.0)
    area_input = st.number_input("Cross-sectional Area [m²]", min_value=0.0001, value=0.01)
    if st.button("Calculate CFM from Pressure"):
        cfm_result = pressure_to_cfm(pressure_input, area_input)
        st.success(f"Estimated Air Flow: {cfm_result} CFM")

    st.markdown("---")

    # 1. Spray Rate Scale-Up
    st.header("1️⃣ Spray Rate Scale-Up")
    SR1 = st.number_input("Lab Scale Spray Rate (SR1) [g/min]", min_value=0.0, value=50.0, key="SR1")
    AV1 = st.number_input("Lab Scale Air Volume (AV1) [CFM]", min_value=0.0, value=100.0, key="AV1")
    AV2 = st.number_input("Pilot Scale Air Volume (AV2) [CFM]", min_value=0.0, value=400.0, key="AV2")

    if st.button("Calculate Spray Rate Scale-Up"):
        SR2 = spray_rate_scaleup(SR1, AV1, AV2)
        st.session_state['SR2'] = SR2
        st.success(f"Pilot Scale Spray Rate (SR2): {SR2} g/min")

    # 2. Atomizing Air Volume Scale-Up
    st.header("2️⃣ Atomizing Air Volume Scale-Up")
    AAV1 = st.number_input("Lab Atomizing Air Volume (AAV1) [CFM]", min_value=0.0, value=10.0, key="AAV1")

    # Use previously calculated SR2 as default if available, else manual input
    default_SR2 = st.session_state.get('SR2', 50.0)
    SR2_for_AAV = st.number_input("Pilot Spray Rate (SR2) [g/min]", min_value=0.0, value=default_SR2, key="SR2_for_AAV")

    if st.button("Calculate Atomizing Air Volume Scale-Up"):
        AAV2 = atomizing_air_volume_scaleup(AAV1, SR2_for_AAV, SR1)
        st.session_state['AAV2'] = AAV2
        st.success(f"Pilot Atomizing Air Volume (AAV2): {AAV2} CFM")

    # 3. Bottom Screen Area Calculation
    st.header("3️⃣ Bottom Screen Area Calculation")
    d_lab = st.number_input("Lab Bottom Screen Diameter [m]", min_value=0.01, value=0.5, key="d_lab")
    d_pilot = st.number_input("Pilot Bottom Screen Diameter [m]", min_value=0.01, value=1.0, key="d_pilot")

    A1 = bottom_screen_area(d_lab)
    A2 = bottom_screen_area(d_pilot)
    st.info(f"Lab Bottom Screen Area (A1): {A1} m²")
    st.info(f"Pilot Bottom Screen Area (A2): {A2} m²")

    # 4. Air Volume Scale-Up
    st.header("4️⃣ Air Volume Scale-Up")
    AV1_air = st.number_input("Lab Scale Air Volume (AV1) [CFM]", min_value=0.0, value=100.0, key="AV1_air")

    if st.button("Calculate Air Volume Scale-Up"):
        AV2_air = air_volume_scaleup(AV1_air, A1, A2)
        st.session_state['AV2_air'] = AV2_air
        st.success(f"Pilot Scale Air Volume (AV2): {AV2_air} CFM")

    st.markdown("---")

    # --- PDF Report Generation ---
    if st.button("📄 Generate PDF Report"):
        pdf_output = io.BytesIO()
        doc = SimpleDocTemplate(pdf_output, pagesize=A4)
        styles = getSampleStyleSheet()
        story = []

        story.append(Paragraph("FBP Granulation Scale-Up Report", styles['Title']))
        story.append(Spacer(1, 12))

        # Pressure to CFM
        story.append(Paragraph("0️⃣ Pressure to CFM Estimation", styles['Heading2']))
        story.append(Paragraph(f"Input Pressure (bar): {pressure_input}", styles['Normal']))
        story.append(Paragraph(f"Cross-sectional Area (m²): {area_input}", styles['Normal']))
        if 'cfm_result' in locals():
            story.append(Paragraph(f"Estimated Air Flow (CFM): {cfm_result}", styles['Normal']))
        story.append(Spacer(1, 12))

        # Spray Rate Scale-Up
        story.append(Paragraph("1️⃣ Spray Rate Scale-Up", styles['Heading2']))
        story.append(Paragraph(f"Lab Scale Spray Rate (SR1): {SR1} g/min", styles['Normal']))
        story.append(Paragraph(f"Lab Scale Air Volume (AV1): {AV1} CFM", styles['Normal']))
        story.append(Paragraph(f"Pilot Scale Air Volume (AV2): {AV2} CFM", styles['Normal']))
        SR2_val = st.session_state.get('SR2', "Not calculated")
        story.append(Paragraph(f"Pilot Scale Spray Rate (SR2): {SR2_val} g/min", styles['Normal']))
        story.append(Spacer(1, 12))

        # Atomizing Air Volume Scale-Up
        story.append(Paragraph("2️⃣ Atomizing Air Volume Scale-Up", styles['Heading2']))
        story.append(Paragraph(f"Lab Atomizing Air Volume (AAV1): {AAV1} CFM", styles['Normal']))
        story.append(Paragraph(f"Pilot Spray Rate (SR2): {SR2_for_AAV} g/min", styles['Normal']))
        AAV2_val = st.session_state.get('AAV2', "Not calculated")
        story.append(Paragraph(f"Pilot Atomizing Air Volume (AAV2): {AAV2_val} CFM", styles['Normal']))
        story.append(Spacer(1, 12))

        # Bottom Screen Area
        story.append(Paragraph("3️⃣ Bottom Screen Area Calculation", styles['Heading2']))
        story.append(Paragraph(f"Lab Bottom Screen Diameter: {d_lab} m", styles['Normal']))
        story.append(Paragraph(f"Lab Bottom Screen Area (A1): {A1} m²", styles['Normal']))
        story.append(Paragraph(f"Pilot Bottom Screen Diameter: {d_pilot} m", styles['Normal']))
        story.append(Paragraph(f"Pilot Bottom Screen Area (A2): {A2} m²", styles['Normal']))
        story.append(Spacer(1, 12))

        # Air Volume Scale-Up
        story.append(Paragraph("4️⃣ Air Volume Scale-Up", styles['Heading2']))
        story.append(Paragraph(f"Lab Scale Air Volume (AV1): {AV1_air} CFM", styles['Normal']))
        AV2_air_val = st.session_state.get('AV2_air', "Not calculated")
        story.append(Paragraph(f"Pilot Scale Air Volume (AV2): {AV2_air_val} CFM", styles['Normal']))
        story.append(Spacer(1, 12))

        doc.build(story)

        st.download_button(
            label="📄 Download PDF Report",
            data=pdf_output.getvalue(),
            file_name="fbp_granulation_scaleup_report.pdf",
            mime="application/pdf"
        )


if __name__ == "__main__":
    main()

