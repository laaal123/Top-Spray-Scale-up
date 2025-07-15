import streamlit as st
import math
import io
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors

# --- Spray Rate ---
def calculate_spray_rate(SR1, AV1, AV2):
    return round(SR1 * (AV2 / AV1), 2)

# --- Atomizing Air Volume ---
def calculate_atomizing_air_volume(AAV1, SR1, SR2):
    if SR1 == 0:
        return None
    return round(AAV1 * (SR2 / SR1), 2)

# --- Air Volume by Area (input area directly) ---
def calculate_air_volume_area_input(AV1, A1, A2):
    if A2 == 0:
        return None
    AV2 = AV1 * (A1 / A2)
    return round(AV2, 2)

# --- PDF Report ---
def generate_pdf_report(data):
    pdf_output = io.BytesIO()
    doc = SimpleDocTemplate(pdf_output, pagesize=A4)
    styles = getSampleStyleSheet()
    story = []

    story.append(Paragraph("🌬️ FBP Granulation Scale-Up Report", styles['Title']))
    story.append(Spacer(1, 12))

    for section_title, table_data in data:
        story.append(Paragraph(section_title, styles['Heading2']))
        table = Table(table_data, hAlign='LEFT')
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
        ]))
        story.append(table)
        story.append(Spacer(1, 12))

    doc.build(story)
    return pdf_output.getvalue()

# --- Streamlit App ---
def main():
    st.set_page_config(page_title="FBP Granulation Scale-Up", layout="centered")
    st.title("🌬️ FBP Granulation Scale-Up (Top Spray)")

    # 1️⃣ Spray Rate
    st.header("1️⃣ Spray Rate Scale-Up")
    SR1 = st.number_input("Lab Scale Spray Rate (SR1, g/min)", value=50.0)
    AV1 = st.number_input("Lab Scale Air Volume (AV1, CFM)", value=100.0)
    AV2 = st.number_input("Pilot Scale Air Volume (AV2, CFM)", value=400.0)
    if st.button("🔄 Calculate Spray Rate (SR2)"):
        SR2 = calculate_spray_rate(SR1, AV1, AV2)
        st.success(f"Spray Rate at Pilot Scale (SR2): **{SR2} g/min**")
    else:
        SR2 = None

    st.markdown("---")

    # 2️⃣ Atomizing Air Volume
    st.header("2️⃣ Atomizing Air Volume Scale-Up")
    AAV1 = st.number_input("Lab Atomizing Air Volume (AAV1, CFM)", value=10.0)
    SR2_input = st.number_input("Pilot Scale Spray Rate (SR2, g/min)", value=SR2 or 200.0)
    if st.button("💨 Calculate Atomizing Air Volume (AAV2)"):
        AAV2 = calculate_atomizing_air_volume(AAV1, SR1, SR2_input)
        if AAV2:
            st.success(f"Pilot Scale Atomizing Air Volume (AAV2): **{AAV2} CFM**")
        else:
            st.error("Invalid input values for atomizing air calculation.")
    else:
        AAV2 = None

    st.markdown("---")

    # 3️⃣ Air Volume by Bottom Screen Area (direct input)
    st.header("3️⃣ Air Volume Scale-Up via Bottom Screen Area")
    A1 = st.number_input("Lab Bottom Screen Area (A1, m²)", value=0.2)
    A2 = st.number_input("Pilot Bottom Screen Area (A2, m²)", value=0.5)
    AV1_area = st.number_input("Lab Scale Air Volume (AV1, CFM)", value=100.0)
    if st.button("📐 Calculate Scaled Air Volume (AV2)"):
        AV2_area = calculate_air_volume_area_input(AV1_area, A1, A2)
        if AV2_area:
            st.success(f"Scaled Air Volume (AV2): **{AV2_area} CFM**")
        else:
            st.error("Check input values. A2 cannot be zero.")
    else:
        AV2_area = None

    st.markdown("---")

    # 📄 PDF Report
    if st.button("📄 Generate PDF Report"):
        report_data = []

        report_data.append(("1️⃣ Spray Rate Scale-Up", [
            ["Parameter", "Value"],
            ["SR1 (Lab Spray Rate)", f"{SR1} g/min"],
            ["AV1 (Lab Air Volume)", f"{AV1} CFM"],
            ["AV2 (Pilot Air Volume)", f"{AV2} CFM"],
            ["SR2 (Pilot Spray Rate)", f"{SR2 or 'Not calculated'} g/min"]
        ]))

        report_data.append(("2️⃣ Atomizing Air Volume Scale-Up", [
            ["Parameter", "Value"],
            ["AAV1 (Lab Atomizing Volume)", f"{AAV1} CFM"],
            ["SR1 (Lab Spray Rate)", f"{SR1} g/min"],
            ["SR2 (Pilot Spray Rate)", f"{SR2_input} g/min"],
            ["AAV2 (Pilot Atomizing Volume)", f"{AAV2 or 'Not calculated'} CFM"]
        ]))

        report_data.append(("3️⃣ Air Volume via Bottom Screen Area", [
            ["Parameter", "Value"],
            ["A1 (Lab Area)", f"{A1} m²"],
            ["A2 (Pilot Area)", f"{A2} m²"],
            ["AV1 (Lab Air Volume)", f"{AV1_area} CFM"],
            ["AV2 (Scaled Air Volume)", f"{AV2_area or 'Not calculated'} CFM"]
        ]))

        pdf = generate_pdf_report(report_data)
        st.download_button("⬇️ Download PDF", data=pdf, file_name="fbp_granulation_report.pdf", mime="application/pdf")

if __name__ == "__main__":
    main()

