import streamlit as st
import math
import io
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet

# === Calculation Functions ===

def calc_bottom_screen_area_from_radius(r_m):
    return math.pi * r_m ** 2

def calc_spray_rate_scaleup(SR1, AV1, AV2):
    try:
        SR2 = SR1 * AV2 / AV1
    except ZeroDivisionError:
        SR2 = None
    return SR2

def calc_atomizing_air_volume_scaleup(AAV1, SR1, SR2):
    try:
        AAV2 = AAV1 * SR2 / SR1
    except ZeroDivisionError:
        AAV2 = None
    return AAV2

def calc_air_volume_scaleup(AV1, A1, A2):
    try:
        AV2 = AV1 * A1 / A2
    except ZeroDivisionError:
        AV2 = None
    return AV2

# === PDF Report Generation ===

def generate_pdf_report(data_dict):
    pdf_buffer = io.BytesIO()
    doc = SimpleDocTemplate(pdf_buffer, pagesize=A4)
    styles = getSampleStyleSheet()
    story = []

    story.append(Paragraph("FBP Granulation Scale-Up Report", styles['Title']))
    story.append(Spacer(1, 12))

    for section, content in data_dict.items():
        story.append(Paragraph(section, styles['Heading2']))
        story.append(Spacer(1, 6))
        if isinstance(content, dict):
            for key, value in content.items():
                story.append(Paragraph(f"<b>{key}:</b> {value}", styles['Normal']))
                story.append(Spacer(1, 4))
        else:
            story.append(Paragraph(str(content), styles['Normal']))
        story.append(Spacer(1, 12))

    doc.build(story)
    return pdf_buffer.getvalue()

# === Initialize session state ===

def init_session_state():
    defaults = {
        "bottom_area_result": None,
        "spray_rate_result": None,
        "atomizing_air_volume_result": None,
        "air_volume_scaleup_result": None,
        "area_lab": None,
        "area_pilot": None,
    }
    for key, val in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = val

# === Streamlit App ===

def main():
    st.title("🌬️ FBP Granulation Scale-Up (Top Spray)")
    init_session_state()

    # --- New Section: Bottom Screen Area from Radius ---
    st.header("0️⃣ Calculate Bottom Screen Area from Radius")
    r_input = st.number_input("Enter Bottom Screen Radius (meters)", min_value=0.0, value=0.25, step=0.01, key="radius_input")
    if st.button("Calculate Bottom Screen Area", key="calc_bottom_area_btn"):
        area = calc_bottom_screen_area_from_radius(r_input)
        st.session_state.bottom_area_result = area
    if st.session_state.bottom_area_result is not None:
        st.success(f"Calculated Bottom Screen Area: {st.session_state.bottom_area_result:.4f} m²")

    st.markdown("---")

    # --- 1. Spray Rate Scale-Up ---
    st.header("1️⃣ Spray Rate Scale-Up")
    SR1 = st.number_input("Lab Scale Spray Rate (SR1, g/min)", min_value=0.0, value=50.0, key="SR1")
    AV1 = st.number_input("Lab Scale Air Volume (AV1, CFM)", min_value=0.0, value=100.0, key="AV1")
    AV2 = st.number_input("Pilot Scale Air Volume (AV2, CFM)", min_value=0.0, value=400.0, key="AV2")

    if st.button("Calculate Spray Rate (SR2)"):
        res = calc_spray_rate_scaleup(SR1, AV1, AV2)
        st.session_state.spray_rate_result = res
    if st.session_state.spray_rate_result is not None:
        st.success(f"Pilot Scale Spray Rate (SR2): {st.session_state.spray_rate_result:.2f} g/min")

    st.markdown("---")

    # --- 2. Atomizing Air Volume Scale-Up ---
    st.header("2️⃣ Atomizing Air Volume Scale-Up")
    AAV1 = st.number_input("Lab Scale Atomizing Air Volume (AAV1, CFM)", min_value=0.0, value=10.0, key="AAV1")
    SR2_for_aav = st.number_input(
        "Pilot Scale Spray Rate (SR2, g/min)",
        min_value=0.0,
        value=st.session_state.spray_rate_result if st.session_state.spray_rate_result else 200.0,
        key="SR2_for_aav"
    )

    if st.button("Calculate Pilot Atomizing Air Volume (AAV2)"):
        res = calc_atomizing_air_volume_scaleup(AAV1, SR1, SR2_for_aav)
        st.session_state.atomizing_air_volume_result = res
    if st.session_state.atomizing_air_volume_result is not None:
        st.success(f"Pilot Scale Atomizing Air Volume (AAV2): {st.session_state.atomizing_air_volume_result:.2f} CFM")

    st.markdown("---")

    # --- 3. Air Volume Scale-Up via Bottom Screen Area ---
    st.header("3️⃣ Air Volume Scale-Up via Bottom Screen Area")
    D_lab = st.number_input("Lab Bottom Screen Diameter (meters)", min_value=0.01, value=0.5, key="D_lab")
    D_pilot = st.number_input("Pilot Bottom Screen Diameter (meters)", min_value=0.01, value=1.0, key="D_pilot")
    AV1_for_area = st.number_input("Lab Scale Air Volume (AV1, CFM)", min_value=0.0, value=100.0, key="AV1_for_area")

    # Calculate areas for air volume scale-up
    st.session_state.area_lab = calc_bottom_screen_area_from_radius(D_lab / 2)
    st.session_state.area_pilot = calc_bottom_screen_area_from_radius(D_pilot / 2)

    if st.button("Calculate Pilot Air Volume (AV2)"):
        res = calc_air_volume_scaleup(AV1_for_area, st.session_state.area_lab, st.session_state.area_pilot)
        st.session_state.air_volume_scaleup_result = res

    st.write(f"Lab Bottom Screen Area (A1): {st.session_state.area_lab:.4f} m²")
    st.write(f"Pilot Bottom Screen Area (A2): {st.session_state.area_pilot:.4f} m²")
    if st.session_state.air_volume_scaleup_result is not None:
        st.success(f"Pilot Scale Air Volume (AV2): {st.session_state.air_volume_scaleup_result:.2f} CFM")

    st.markdown("---")

    # --- PDF Report Download ---
    st.header("📄 Generate PDF Report")
    if st.button("Generate and Download PDF Report"):
        results = {
            "Bottom Screen Area from Radius": {
                "Input Radius (m)": r_input,
                "Calculated Bottom Screen Area (m²)": f"{st.session_state.bottom_area_result:.4f}" if st.session_state.bottom_area_result else "Not Calculated"
            },
            "Spray Rate Scale-Up": {
                "Lab Scale Spray Rate (SR1, g/min)": SR1,
                "Lab Scale Air Volume (AV1, CFM)": AV1,
                "Pilot Scale Air Volume (AV2, CFM)": AV2,
                "Calculated Pilot Spray Rate (SR2, g/min)": st.session_state.spray_rate_result if st.session_state.spray_rate_result is not None else "Not Calculated"
            },
            "Atomizing Air Volume Scale-Up": {
                "Lab Scale Atomizing Air Volume (AAV1, CFM)": AAV1,
                "Lab Scale Spray Rate (SR1, g/min)": SR1,
                "Pilot Scale Spray Rate (SR2, g/min)": SR2_for_aav,
                "Calculated Pilot Atomizing Air Volume (AAV2, CFM)": st.session_state.atomizing_air_volume_result if st.session_state.atomizing_air_volume_result is not None else "Not Calculated"
            },
            "Air Volume Scale-Up": {
                "Lab Bottom Screen Diameter (m)": D_lab,
                "Pilot Bottom Screen Diameter (m)": D_pilot,
                "Lab Bottom Screen Area (m²)": f"{st.session_state.area_lab:.4f}" if st.session_state.area_lab else "Not Calculated",
                "Pilot Bottom Screen Area (m²)": f"{st.session_state.area_pilot:.4f}" if st.session_state.area_pilot else "Not Calculated",
                "Lab Scale Air Volume (AV1, CFM)": AV1_for_area,
                "Calculated Pilot Air Volume (AV2, CFM)": st.session_state.air_volume_scaleup_result if st.session_state.air_volume_scaleup_result is not None else "Not Calculated"
            }
        }
        pdf_bytes = generate_pdf_report(results)
        st.download_button(
            label="📄 Download PDF Report",
            data=pdf_bytes,
            file_name="fbp_granulation_scaleup_report.pdf",
            mime="application/pdf"
        )

if __name__ == "__main__":
    main()

