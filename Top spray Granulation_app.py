import streamlit as st
import math
import io
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors

styles = getSampleStyleSheet()

# --- Calculations ---
def calculate_spray_rate(SR1, AV1, AV2):
    return round(SR1 * (AV2 / AV1), 2)

def calculate_atomizing_air(AAV1, SR1, SR2):
    return round(AAV1 * (SR2 / SR1), 2)

def calculate_air_volume(AV1, D1_cm, D2_cm):
    r1 = (D1_cm / 100) / 2
    r2 = (D2_cm / 100) / 2
    A1 = math.pi * r1**2
    A2 = math.pi * r2**2
    AV2 = AV1 * (A2 / A1)
    return round(A1, 4), round(A2, 4), round(AV2, 2)

# --- PDF Generator ---
def generate_pdf(title, results):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4)
    story = [Paragraph(title, styles["Title"]), Spacer(1, 12)]

    for label, value in results:
        story.append(Paragraph(f"<b>{label}:</b> {value}", styles["Normal"]))
    story.append(Spacer(1, 12))

    doc.build(story)
    return buffer.getvalue()

# --- Main App ---
def main():
    st.title("🌬️ FBP Granulation Scale-Up (Top Spray)")

    # --- 1️⃣ Spray Rate ---
    st.header("1️⃣ Spray Rate Scale-Up")
    SR1 = st.number_input("Lab Scale Spray Rate (SR1, g/min)", value=50.0)
    AV1 = st.number_input("Lab Scale Air Volume (AV1, CFM)", value=100.0)
    AV2 = st.number_input("Pilot Scale Air Volume (AV2, CFM)", value=400.0)

    if st.button("🧪 Calculate Spray Rate"):
        SR2 = calculate_spray_rate(SR1, AV1, AV2)
        st.success(f"▶️ Scaled Spray Rate (SR2): {SR2} g/min")

        spray_pdf = generate_pdf("Spray Rate Scale-Up Report", [
            ("Lab Scale SR1", f"{SR1} g/min"),
            ("Lab Scale AV1", f"{AV1} CFM"),
            ("Pilot Scale AV2", f"{AV2} CFM"),
            ("Scaled SR2", f"{SR2} g/min")
        ])
        st.download_button("📄 Download Spray Rate PDF", data=spray_pdf,
                           file_name="spray_rate_report.pdf", mime="application/pdf")

    st.markdown("---")

    # --- 2️⃣ Atomizing Air Volume ---
    st.header("2️⃣ Atomizing Air Volume Scale-Up")
    AAV1 = st.number_input("Lab Scale Atomizing Air Volume (AAV1, CFM)", value=10.0)
    SR1_atom = st.number_input("Lab Spray Rate (SR1, g/min)", value=50.0)
    SR2_atom = st.number_input("Pilot Spray Rate (SR2, g/min)", value=200.0)

    if st.button("🌫️ Calculate Atomizing Air Volume"):
        AAV2 = calculate_atomizing_air(AAV1, SR1_atom, SR2_atom)
        st.success(f"▶️ Scaled Atomizing Air Volume (AAV2): {AAV2} CFM")

        atom_pdf = generate_pdf("Atomizing Air Volume Scale-Up Report", [
            ("Lab AAV1", f"{AAV1} CFM"),
            ("Lab SR1", f"{SR1_atom} g/min"),
            ("Pilot SR2", f"{SR2_atom} g/min"),
            ("Scaled AAV2", f"{AAV2} CFM")
        ])
        st.download_button("📄 Download Atomizing Air PDF", data=atom_pdf,
                           file_name="atomizing_air_report.pdf", mime="application/pdf")

    st.markdown("---")

    # --- 3️⃣ Air Volume Scale-Up ---
    st.header("3️⃣ Air Volume Scale-Up (Bottom Screen Area)")
    AV1_area = st.number_input("Lab Scale Air Volume (AV1, CFM)", value=100.0)
    D1 = st.number_input("Lab Scale Screen Diameter (cm)", value=30.0)
    D2 = st.number_input("Pilot Scale Screen Diameter (cm)", value=60.0)

    if st.button("🌀 Calculate Air Volume from Area"):
        A1, A2, AV2_area = calculate_air_volume(AV1_area, D1, D2)
        st.success(f"Lab Area A1: {A1} m²")
        st.success(f"Pilot Area A2: {A2} m²")
        st.success(f"Scaled Air Volume (AV2): {AV2_area} CFM")

        area_pdf = generate_pdf("Air Volume Scale-Up via Screen Area", [
            ("Lab Diameter", f"{D1} cm ➜ Area A1 = {A1} m²"),
            ("Pilot Diameter", f"{D2} cm ➜ Area A2 = {A2} m²"),
            ("Lab AV1", f"{AV1_area} CFM"),
            ("Scaled AV2", f"{AV2_area} CFM")
        ])
        st.download_button("📄 Download Air Volume PDF", data=area_pdf,
                           file_name="air_volume_report.pdf", mime="application/pdf")

if __name__ == "__main__":
    main()

