import streamlit as st
import math
import io
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors

# === Calculation Functions ===

def calc_spray_rate_scaleup(SR1, AV1, AV2):
    # SR2 = SR1 * AV2 / AV1
    try:
        SR2 = SR1 * AV2 / AV1
    except ZeroDivisionError:
        SR2 = None
    return SR2

def calc_atomizing_air_volume_scaleup(AAV1, SR1, SR2):
    # AAV2 = AAV1 * SR2 / SR1
    try:
        AAV2 = AAV1 * SR2 / SR1
    except ZeroDivisionError:
        AAV2 = None
    return AAV2

def calc_bottom_screen_area(diameter_m):
    # A = π * r^2, diameter input in meters
    r = diameter_m / 2
    return math.pi * r ** 2

def calc_air_volume_scaleup(AV1, A1, A2):
    # AV2 = AV1 * A1 / A2
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

# === Streamlit App ===

def main():
    st.title("🌬️ FBP Granulation Scale-Up (Top Spray)")

    st.header("1️⃣ Spray Rate Scale-Up")
    SR1 = st.number_input("Lab Scale Spray Rate (SR1, g/min)", min_value=0.0, value=50.0, key="SR1")
    AV1 = st.number_input("Lab Scale Air Volume (AV1, CFM)", min_value=0.0, value=100.0, key="AV1")
    AV2 = st.number_input("Pilot Scale Air Volume (AV2, CFM)", min_value=0.0, value=400.0, key="AV2")

    spray_rate_result = None
    if st.button("Calculate Spray Rate (SR2)"):
        spray_rate_result = calc_spray_rate_scaleup(SR1, AV1, AV2)
        if spray_rate_result is not None:
            st.success(f"Pilot Scale Spray Rate (SR2): {spray_rate_result:.2f} g/min")
        else:
            st.error("Error: Division by zero encountered in Spray Rate calculation.")

    st.markdown("---")

    st.header("2️⃣ Atomizing Air Volume Scale-Up")
    AAV1 = st.number_input("Lab Scale Atomizing Air Volume (AAV1, CFM)", min_value=0.0, value=10.0, key="AAV1")
    SR2_for_aav = st.number_input("Pilot Scale Spray Rate (SR2, g/min)", min_value=0.0, value=200.0, key="SR2_for_aav")

    atomizing_air_volume_result = None
    if st.button("Calculate Pilot Atomizing Air Volume (AAV2)"):
        atomizing_air_volume_result = calc_atomizing_air_volume_scaleup(AAV1, SR1, SR2_for_aav)
        if atomizing_air_volume_result is not None:
            st.success(f"Pilot Scale Atomizing Air Volume (AAV2): {atomizing_air_volume_result:.2f} CFM")
        else:
            st.error("Error: Division by zero encountered in Atomizing Air Volume calculation.")

    st.markdown("---")

    st.header("3️⃣ Air Volume Scale-Up via Bottom Screen Area")

    D_lab = st.number_input("Lab Bottom Screen Diameter (meters)", min_value=0.01, value=0.5, key="D_lab")
    D_pilot = st.number_input("Pilot Bottom Screen Diameter (meters)", min_value=0.01, value=1.0, key="D_pilot")
    AV1_for_area = st.number_input("Lab Scale Air Volume (AV1, CFM)", min_value=0.0, value=100.0, key="AV1_for_area")

    area_lab = calc_bottom_screen_area(D_lab)
    area_pilot = calc_bottom_screen_area(D_pilot)

    air_volume_scaleup_result = None
    if st.button("Calculate Pilot Air Volume (AV2)"):
        air_volume_scaleup_result = calc_air_volume_scaleup(AV1_for_area, area_lab, area_pilot)
        if air_volume_scaleup_result is not None:
            st.success(f"Pilot Scale Air Volume (AV2): {air_volume_scaleup_result:.2f} CFM")
        else:
            st.error("Error: Division by zero encountered in Air Volume calculation.")

    st.markdown("---")

    # PDF Report Download - combine all calculated results
    st.header("📄 Generate PDF Report")
    if st.button("Generate and Download PDF Report"):
        results = {
            "Spray Rate Scale-Up": {
                "Lab Scale Spray Rate (SR1, g/min)": SR1,
                "Lab Scale Air Volume (AV1, CFM)": AV1,
                "Pilot Scale Air Volume (AV2, CFM)": AV2,
                "Calculated Pilot Spray Rate (SR2, g/min)": spray_rate_result if spray_rate_result is not None else "Not Calculated"
            },
            "Atomizing Air Volume Scale-Up": {
                "Lab Scale Atomizing Air Volume (AAV1, CFM)": AAV1,
                "Lab Scale Spray Rate (SR1, g/min)": SR1,
                "Pilot Scale Spray Rate (SR2, g/min)": SR2_for_aav,
                "Calculated Pilot Atomizing Air Volume (AAV2, CFM)": atomizing_air_volume_result if atomizing_air_volume_result is not None else "Not Calculated"
            },
            "Air Volume Scale-Up": {
                "Lab Bottom Screen Diameter (m)": D_lab,
                "Pilot Bottom Screen Diameter (m)": D_pilot,
                "Lab Bottom Screen Area (m²)": area_lab,
                "Pilot Bottom Screen Area (m²)": area_pilot,
                "Lab Scale Air Volume (AV1, CFM)": AV1_for_area,
                "Calculated Pilot Air Volume (AV2, CFM)": air_volume_scaleup_result if air_volume_scaleup_result is not None else "Not Calculated"
            }
        }
        pdf_bytes = generate_pdf_report(results)
        st.download_button(label="📄 Download PDF Report", data=pdf_bytes, file_name="fbp_granulation_scaleup_report.pdf", mime="application/pdf")

if __name__ == "__main__":
    main()

