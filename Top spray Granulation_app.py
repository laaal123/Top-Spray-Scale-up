import streamlit as st
import math
import io
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors

# --- Spray Rate Scale-Up ---
def calculate_spray_rate(SR1, AV1, AV2):
    return round(SR1 * (AV2 / AV1), 2)

# --- Atomizing Air Volume Scale-Up ---
def calculate_atomizing_air(AAV1, SR1, SR2):
    return round(AAV1 * (SR2 / SR1), 2)

# --- Air Volume Scale-Up via Screen Area ---
def calculate_air_volume(AV1, D1_cm, D2_cm):
    r1 = (D1_cm / 100) / 2  # Convert to meters
    r2 = (D2_cm / 100) / 2
    A1 = math.pi * r1**2
    A2 = math.pi * r2**2
    AV2 = AV1 * (A2 / A1)
    return round(A1, 4), round(A2, 4), round(AV2, 2)

# --- Streamlit App ---
def main():
    st.title("🌬️ FBP Granulation Scale-Up Calculator (Top Spray)")
    styles = getSampleStyleSheet()

    # Collect all outputs for PDF report
    pdf_data = []

    # --- Spray Rate ---
    st.header("1️⃣ Spray Rate Scale-Up")
    SR1 = st.number_input("Lab Scale Spray Rate (SR1, g/min)", value=50.0)
    AV1 = st.number_input("Lab Scale Air Volume (AV1, CFM)", value=100.0)
    AV2 = st.number_input("Pilot Scale Air Volume (AV2, CFM)", value=400.0)

    SR2 = calculate_spray_rate(SR1, AV1, AV2)
    st.success(f"▶️ Scaled Spray Rate (SR2): **{SR2} g/min**")
    pdf_data.append(["Spray Rate Scale-Up", f"SR1 = {SR1} g/min", f"AV1 = {AV1} CFM", f"AV2 = {AV2} CFM", f"SR2 = {SR2} g/min"])

    st.markdown("---")

    # --- Atomizing Air ---
    st.header("2️⃣ Atomizing Air Volume Scale-Up")
    AAV1 = st.number_input("Lab Atomizing Air Volume (AAV1, CFM)", value=10.0)
    SR1_atom = st.number_input("Lab Spray Rate (SR1, g/min)", value=SR1, key="sr1_atom")
    SR2_atom = st.number_input("Pilot Spray Rate (SR2, g/min)", value=SR2, key="sr2_atom")

    AAV2 = calculate_atomizing_air(AAV1, SR1_atom, SR2_atom)
    st.success(f"▶️ Scaled Atomizing Air Volume (AAV2): **{AAV2} CFM**")
    pdf_data.append(["Atomizing Air Volume Scale-Up", f"AAV1 = {AAV1} CFM", f"SR1 = {SR1_atom} g/min", f"SR2 = {SR2_atom} g/min", f"AAV2 = {AAV2} CFM"])

    st.markdown("---")

    # --- Area and Air Volume ---
    st.header("3️⃣ Bottom Screen Area & Air Volume Scale-Up")
    AV1_area = st.number_input("Lab Scale Air Volume (AV1, CFM)", value=AV1, key="av1_area")
    D1 = st.number_input("Lab Screen Diameter (cm)", value=30.0)
    D2 = st.number_input("Pilot Screen Diameter (cm)", value=60.0)

    A1, A2, AV2_area = calculate_air_volume(AV1_area, D1, D2)
    st.success(f"Lab Bottom Screen Area A1: **{A1} m²**")
    st.success(f"Pilot Bottom Screen Area A2: **{A2} m²**")
    st.success(f"▶️ Scaled Air Volume (AV2): **{AV2_area} CFM**")
    pdf_data.append(["Bottom Screen Area & Air Volume",
                     f"Diameter1 = {D1} cm ➜ A1 = {A1} m²",
                     f"Diameter2 = {D2} cm ➜ A2 = {A2} m²",
                     f"AV1 = {AV1_area} CFM ➜ AV2 = {AV2_area} CFM"])

    # --- PDF Report Generation ---
    st.markdown("---")
    if st.button("📄 Generate PDF Report"):
        pdf_buffer = io.BytesIO()
        doc = SimpleDocTemplate(pdf_buffer, pagesize=A4)
        story = [Paragraph("FBP Granulation Scale-Up Report", styles["Title"]), Spacer(1, 12)]

        for section in pdf_data:
            story.append(Paragraph(section[0], styles["Heading2"]))
            for line in section[1:]:
                story.append(Paragraph(line, styles["Normal"]))
            story.append(Spacer(1, 12))

        doc.build(story)
        st.download_button("📥 Download PDF", data=pdf_buffer.getvalue(),
                           file_name="fbp_scaleup_report.pdf", mime="application/pdf")

if __name__ == "__main__":
    main()

