import streamlit as st
import math
import io
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors

def calculate_spray_rate(SR1, AV1, AV2):
    return round(SR1 * (AV2 / AV1), 2)

def calculate_atomization_air_pressure(AAP1, SR1, SR2, AAV1, AAV2):
    if SR1 == 0 or AAV2 == 0:
        return None
    return round(AAP1 * (SR2 / SR1) * (AAV1 / AAV2), 2)

def calculate_air_volume_area(AV1, D_lab_mm, D_pilot_mm):
    r1 = (D_lab_mm / 1000) / 2
    r2 = (D_pilot_mm / 1000) / 2
    A1 = math.pi * r1 ** 2
    A2 = math.pi * r2 ** 2
    AV2 = AV1 * (A1 / A2)
    return round(A1, 4), round(A2, 4), round(AV2, 2)

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

def main():
    st.title("🌬️ FBP Granulation Scale-Up (Top Spray)")

    # 1️⃣ Spray Rate
    st.header("1️⃣ Spray Rate Scale-Up")
    SR1 = st.number_input("Lab Scale Spray Rate (SR1, g/min)", value=50.0)
    AV1 = st.number_input("Lab Scale Air Volume (AV1, CFM)", value=100.0)
    AV2 = st.number_input("Pilot Scale Air Volume (AV2, CFM)", value=400.0)
    if st.button("Calculate Spray Rate (SR2)"):
        SR2 = calculate_spray_rate(SR1, AV1, AV2)
        st.success(f"Spray Rate at Pilot Scale (SR2): **{SR2} g/min**")
    else:
        SR2 = None

    st.markdown("---")

    # 2️⃣ Atomization Air Pressure
    st.header("2️⃣ Atomizing Air Pressure Scale-Up")
    AAV1 = st.number_input("Lab Scale Atomizing Air Volume (AAV1, CFM)", value=10.0)
    AAP1 = st.number_input("Lab Scale Atomizing Air Pressure (AAP1, bar)", value=2.0)
    SR2_input = st.number_input("Pilot Scale Spray Rate (SR2, g/min)", value=SR2 or 200.0)
    AAV2 = st.number_input("Pilot Scale Atomizing Air Volume (AAV2, CFM)", value=40.0)
    if st.button("Calculate Atomizing Pressure (AAP2)"):
        AAP2 = calculate_atomization_air_pressure(AAP1, SR1, SR2_input, AAV1, AAV2)
        if AAP2:
            st.success(f"Pilot Scale Atomizing Pressure (AAP2): **{AAP2} bar**")
        else:
            st.error("Invalid input values for pressure calculation.")

    st.markdown("---")

    # 3️⃣ Area and Air Volume
    st.header("3️⃣ Air Volume Scale-Up (Bottom Screen Area)")
    D_lab = st.number_input("Lab Bottom Screen Diameter (mm)", value=500.0)
    D_pilot = st.number_input("Pilot Bottom Screen Diameter (mm)", value=1000.0)
    AV1_area = st.number_input("Lab Scale Air Volume (AV1, CFM) for Area", value=100.0)
    if st.button("Calculate Area & Air Volume (AV2)"):
        A1, A2, AV2_area = calculate_air_volume_area(AV1_area, D_lab, D_pilot)
        st.success(f"Lab Area (A1): {A1} m² | Pilot Area (A2): {A2} m² | Scaled Air Volume (AV2): {AV2_area} CFM")
    else:
        A1 = A2 = AV2_area = None

    st.markdown("---")

    # PDF generation
    if st.button("📄 Generate and Download PDF Report"):
        report_data = []

        report_data.append(("1️⃣ Spray Rate Scale-Up", [
            ["Parameter", "Value"],
            ["SR1 (Lab Spray Rate)", f"{SR1} g/min"],
            ["AV1 (Lab Air Volume)", f"{AV1} CFM"],
            ["AV2 (Pilot Air Volume)", f"{AV2} CFM"],
            ["SR2 (Pilot Spray Rate)", f"{SR2 or 'Not calculated'} g/min"]
        ]))

        report_data.append(("2️⃣ Atomizing Air Pressure Scale-Up", [
            ["Parameter", "Value"],
            ["AAV1 (Lab Atomizing Volume)", f"{AAV1} CFM"],
            ["AAP1 (Lab Atomizing Pressure)", f"{AAP1} bar"],
            ["SR2 (Pilot Spray Rate)", f"{SR2_input} g/min"],
            ["AAV2 (Pilot Atomizing Volume)", f"{AAV2} CFM"],
            ["AAP2 (Pilot Atomizing Pressure)", f"{calculate_atomization_air_pressure(AAP1, SR1, SR2_input, AAV1, AAV2)} bar"]
        ]))

        report_data.append(("3️⃣ Air Volume Scale-Up (Bottom Screen Area)", [
            ["Parameter", "Value"],
            ["D_lab (mm)", f"{D_lab} mm"],
            ["D_pilot (mm)", f"{D_pilot} mm"],
            ["A1 (Lab Area)", f"{A1 or 'N/A'} m²"],
            ["A2 (Pilot Area)", f"{A2 or 'N/A'} m²"],
            ["AV1 Area", f"{AV1_area} CFM"],
            ["AV2 Area Scaled", f"{AV2_area or 'N/A'} CFM"]
        ]))

        pdf = generate_pdf_report(report_data)
        st.download_button("⬇️ Download PDF Report", data=pdf, file_name="fbp_granulation_report.pdf", mime="application/pdf")

if __name__ == "__main__":
    main()

