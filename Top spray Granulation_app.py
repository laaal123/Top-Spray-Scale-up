import streamlit as st
import math
import io
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors

# Spray Rate Calculation
def calculate_spray_rate(SR1, AV1, AV2):
    return round(SR1 * (AV2 / AV1), 2)

# Atomizing Pressure Calculation
def calculate_atomizing_pressure(P1, SR1, SR2):
    return round(P1 * (SR1 / SR2), 2)

# Air Volume & Bottom Screen Area Calculation
def calculate_air_volume(AV1, D1_cm, D2_cm):
    r1 = (D1_cm / 100) / 2  # convert to meters
    r2 = (D2_cm / 100) / 2
    A1 = math.pi * r1 ** 2  # m²
    A2 = math.pi * r2 ** 2  # m²
    AV2 = AV1 * (A2 / A1)
    return round(A1, 4), round(A2, 4), round(AV2, 2)

# Streamlit UI
def main():
    st.title("🌡️ FBP Granulation Scale-Up (Top Spray)")
    st.markdown("📘 Based on pharma engineering scale-up principles for spray rate, atomization pressure, and air volume.")

    # Inputs and Calculations
    st.header("1️⃣ Spray Rate Scale-Up")
    SR1 = st.number_input("Lab Spray Rate (g/min)", value=50.0)
    AV1 = st.number_input("Lab Air Volume (CFM)", value=100.0)
    AV2 = st.number_input("Pilot Air Volume (CFM)", value=400.0)
    SR2 = calculate_spray_rate(SR1, AV1, AV2)
    st.success(f"➡️ Scaled Spray Rate (Pilot): **{SR2} g/min**")

    st.markdown("---")

    st.header("2️⃣ Atomizing Air Pressure")
    P1 = st.number_input("Lab Atomizing Pressure (bar)", value=1.5)
    SR1_atom = st.number_input("Lab Spray Rate (again) (g/min)", value=SR1, key="SR1_atom")
    SR2_atom = st.number_input("Pilot Spray Rate (g/min)", value=SR2, key="SR2_atom")
    P2 = calculate_atomizing_pressure(P1, SR1_atom, SR2_atom)
    st.success(f"➡️ Scaled Atomizing Pressure (Pilot): **{P2} bar**")

    st.markdown("---")

    st.header("3️⃣ Bottom Screen Area and Air Volume")
    D1 = st.number_input("Lab Scale Screen Diameter (cm)", value=30.0)
    D2 = st.number_input("Pilot Scale Screen Diameter (cm)", value=60.0)
    AV1_area = st.number_input("Lab Scale Air Volume (again, CFM)", value=AV1, key="AV1_area")
    A1, A2, AV2_area = calculate_air_volume(AV1_area, D1, D2)
    st.success(f"✅ Lab Screen Area (A1): {A1} m²")
    st.success(f"✅ Pilot Screen Area (A2): {A2} m²")
    st.success(f"➡️ Scaled Air Volume (Pilot): **{AV2_area} CFM**")

    st.markdown("---")

    # --- Export PDF ---
    if st.button("📄 Generate and Download PDF Report"):
        pdf_output = io.BytesIO()
        doc = SimpleDocTemplate(pdf_output, pagesize=A4)
        styles = getSampleStyleSheet()
        story = []

        story.append(Paragraph("FBP Granulation Scale-Up Report", styles['Title']))
        story.append(Spacer(1, 12))

        story.append(Paragraph("1️⃣ Spray Rate Scale-Up", styles['Heading2']))
        story.append(Paragraph(f"Lab Spray Rate: {SR1} g/min", styles['Normal']))
        story.append(Paragraph(f"Lab Air Volume: {AV1} CFM", styles['Normal']))
        story.append(Paragraph(f"Pilot Air Volume: {AV2} CFM", styles['Normal']))
        story.append(Paragraph(f"➡️ Scaled Spray Rate: {SR2} g/min", styles['Normal']))
        story.append(Spacer(1, 12))

        story.append(Paragraph("2️⃣ Atomizing Air Pressure", styles['Heading2']))
        story.append(Paragraph(f"Lab Atomizing Pressure: {P1} bar", styles['Normal']))
        story.append(Paragraph(f"Pilot Spray Rate: {SR2_atom} g/min", styles['Normal']))
        story.append(Paragraph(f"➡️ Scaled Atomizing Pressure: {P2} bar", styles['Normal']))
        story.append(Spacer(1, 12))

        story.append(Paragraph("3️⃣ Air Volume & Bottom Screen Area", styles['Heading2']))
        story.append(Paragraph(f"Lab Screen Diameter: {D1} cm ➜ Area A1: {A1} m²", styles['Normal']))
        story.append(Paragraph(f"Pilot Screen Diameter: {D2} cm ➜ Area A2: {A2} m²", styles['Normal']))
        story.append(Paragraph(f"➡️ Scaled Air Volume (Pilot): {AV2_area} CFM", styles['Normal']))
        story.append(Spacer(1, 12))

        doc.build(story)

        st.download_button(
            label="📥 Download PDF Report",
            data=pdf_output.getvalue(),
            file_name="fbp_scaleup_report.pdf",
            mime="application/pdf"
        )

if __name__ == "__main__":
    main()
