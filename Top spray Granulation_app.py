import streamlit as st
import math
import io
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors

# Convert CFM to m3/min (1 CFM = 0.0283168 m3/min)
def cfm_to_m3_per_min(cfm):
    return cfm * 0.0283168

# Convert atm or psi to bar (assuming input in psi)
def psi_to_bar(psi):
    return psi * 0.0689476

def calculate_bottom_screen_area(radius_m):
    return math.pi * (radius_m ** 2)

def main():
    st.title("🌬️ FBP Granulation Scale-Up (Top Spray)")

    st.header("1️⃣ Spray Rate Scale-Up")
    SR1 = st.number_input("Lab Scale Spray Rate (SR1) [g/min]", min_value=0.0, value=50.0, key="sr1")
    AV1_cfm = st.number_input("Lab Scale Air Volume (AV1) [CFM]", min_value=0.0, value=100.0, key="av1")
    AV2_cfm = st.number_input("Pilot Scale Air Volume (AV2) [CFM]", min_value=0.0, value=400.0, key="av2")

    # Spray Rate Scale-Up Formula: SR2 = SR1 * (AV2 / AV1)
    SR2 = SR1 * (AV2_cfm / AV1_cfm) if AV1_cfm != 0 else 0

    st.markdown(f"**Scaled Spray Rate (SR2): {SR2:.2f} g/min**")

    st.markdown("---")

    st.header("2️⃣ Atomizing Air Volume Scale-Up & Atomization Air Pressure")
    AAV1_cfm = st.number_input("Lab Scale Atomizing Air Volume (AAV1) [CFM]", min_value=0.0, value=10.0, key="aav1")
    # Reuse SR1 and SR2 from above
    if SR1 == 0:
        st.error("Lab Scale Spray Rate (SR1) cannot be zero for Atomizing Air Volume calculation.")
        return

    # Atomizing Air Volume scale up: AAV2 = AAV1 * (SR2 / SR1)
    AAV2_cfm = AAV1_cfm * (SR2 / SR1)

    # Ask for Atomization Air Pressure input in psi, convert to bar
    AAP1_psi = st.number_input("Lab Scale Atomization Air Pressure (AAP1) [psi]", min_value=0.0, value=30.0, key="aap1")
    # Calculate Pilot scale Atomization Air Pressure assuming proportional scaling
    # Using: Droplet size ~ Spray rate / Atomizing air volume, so keeping droplet size constant:
    # AAP2_psi = AAP1 * (SR2 / SR1) * (AAV1 / AAV2)
    # But since AAV2 = AAV1 * (SR2/SR1), this ratio = 1, so AAP2_psi ~ AAP1_psi

    # For simplicity, just convert input psi to bar:
    AAP1_bar = psi_to_bar(AAP1_psi)

    st.markdown(f"**Scaled Atomizing Air Volume (AAV2): {AAV2_cfm:.2f} CFM**")
    st.markdown(f"**Lab Scale Atomization Air Pressure: {AAP1_bar:.2f} bar**")

    st.markdown("---")

    st.header("3️⃣ Air Volume Scale-Up (Bottom Screen Area)")

    r1_mm = st.number_input("Lab Scale Bottom Screen Radius (r1) [mm]", min_value=1.0, value=500.0, key="r1")
    r2_mm = st.number_input("Pilot Scale Bottom Screen Radius (r2) [mm]", min_value=1.0, value=1000.0, key="r2")

    AV1_from_area_cfm = st.number_input("Lab Scale Air Volume (AV1) [CFM] (Re-input for air volume scale-up)", min_value=0.0, value=100.0, key="av1_area")

    # Convert mm to meters for radius
    r1_m = r1_mm / 1000
    r2_m = r2_mm / 1000

    A1 = calculate_bottom_screen_area(r1_m)
    A2 = calculate_bottom_screen_area(r2_m)

    # Air volume scale-up: AV2 = AV1 * (A2 / A1)
    # **Note**: The original formula you wrote was AV2 = AV1 * (A1 / A2),
    # but logically larger area should scale volume up, so correct is AV2 = AV1 * (A2 / A1)
    AV2_from_area_cfm = AV1_from_area_cfm * (A2 / A1) if A1 != 0 else 0

    st.markdown(f"Lab Scale Bottom Screen Area (A1): {A1:.4f} m²")
    st.markdown(f"Pilot Scale Bottom Screen Area (A2): {A2:.4f} m²")
    st.markdown(f"Scaled Air Volume (AV2) based on Bottom Screen Area: {AV2_from_area_cfm:.2f} CFM")

    st.markdown("---")

    # --- PDF Report generation ---
    if st.button("📄 Generate and Download PDF Report"):
        pdf_buffer = io.BytesIO()
        doc = SimpleDocTemplate(pdf_buffer, pagesize=A4)
        styles = getSampleStyleSheet()
        story = []

        story.append(Paragraph("FBP Granulation Scale-Up Report (Top Spray)", styles['Title']))
        story.append(Spacer(1, 12))

        # Spray Rate Scale-Up Summary
        story.append(Paragraph("1️⃣ Spray Rate Scale-Up", styles['Heading2']))
        data_sr = [
            ["Parameter", "Value"],
            ["Lab Scale Spray Rate (SR1) [g/min]", f"{SR1:.2f}"],
            ["Lab Scale Air Volume (AV1) [CFM]", f"{AV1_cfm:.2f}"],
            ["Pilot Scale Air Volume (AV2) [CFM]", f"{AV2_cfm:.2f}"],
            ["Scaled Spray Rate (SR2) [g/min]", f"{SR2:.2f}"],
        ]
        table_sr = Table(data_sr, hAlign='LEFT')
        table_sr.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), colors.grey),
            ('TEXTCOLOR',(0,0),(-1,0),colors.whitesmoke),
            ('ALIGN',(0,0),(-1,-1),'CENTER'),
            ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
            ('GRID', (0,0), (-1,-1), 0.5, colors.black),
        ]))
        story.append(table_sr)
        story.append(Spacer(1, 12))

        # Atomizing Air Volume Scale-Up Summary
        story.append(Paragraph("2️⃣ Atomizing Air Volume Scale-Up & Atomization Air Pressure", styles['Heading2']))
        data_aav = [
            ["Parameter", "Value"],
            ["Lab Scale Atomizing Air Volume (AAV1) [CFM]", f"{AAV1_cfm:.2f}"],
            ["Scaled Atomizing Air Volume (AAV2) [CFM]", f"{AAV2_cfm:.2f}"],
            ["Lab Scale Atomization Air Pressure (AAP1) [psi]", f"{AAP1_psi:.2f}"],
            ["Lab Scale Atomization Air Pressure (AAP1) [bar]", f"{AAP1_bar:.2f}"],
        ]
        table_aav = Table(data_aav, hAlign='LEFT')
        table_aav.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), colors.grey),
            ('TEXTCOLOR',(0,0),(-1,0),colors.whitesmoke),
            ('ALIGN',(0,0),(-1,-1),'CENTER'),
            ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
            ('GRID', (0,0), (-1,-1), 0.5, colors.black),
        ]))
        story.append(table_aav)
        story.append(Spacer(1, 12))

        # Air Volume Scale-Up Summary
        story.append(Paragraph("3️⃣ Air Volume Scale-Up (Bottom Screen Area)", styles['Heading2']))
        data_area = [
            ["Parameter", "Value"],
            ["Lab Scale Bottom Screen Radius (r1) [m]", f"{r1_m:.4f}"],
            ["Pilot Scale Bottom Screen Radius (r2) [m]", f"{r2_m:.4f}"],
            ["Lab Scale Bottom Screen Area (A1) [m²]", f"{A1:.4f}"],
            ["Pilot Scale Bottom Screen Area (A2) [m²]", f"{A2:.4f}"],
            ["Lab Scale Air Volume (AV1) [CFM]", f"{AV1_from_area_cfm:.2f}"],
            ["Scaled Air Volume (AV2) [CFM]", f"{AV2_from_area_cfm:.2f}"],
        ]
        table_area = Table(data_area, hAlign='LEFT')
        table_area.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), colors.grey),
            ('TEXTCOLOR',(0,0),(-1,0),colors.whitesmoke),
            ('ALIGN',(0,0),(-1,-1),'CENTER'),
            ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
            ('GRID', (0,0), (-1,-1), 0.5, colors.black),
        ]))
        story.append(table_area)
        story.append(Spacer(1, 12))

        doc.build(story)
        pdf_buffer.seek(0)

        st.download_button(
            label="📄 Download PDF Report",
            data=pdf_buffer,
            file_name="fbp_granulation_scale_up_report.pdf",
            mime="application/pdf"
        )


if __name__ == "__main__":
    main()

