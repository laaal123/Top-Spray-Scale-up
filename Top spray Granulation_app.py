import streamlit as st
import math
import io
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors

# --- Calculation functions ---

def calc_bottom_screen_area(radius_m):
    return math.pi * radius_m ** 2

def calc_spray_rate_scaleup(SR1, AV1, AV2):
    if AV1 == 0:
        return None
    return SR1 * AV2 / AV1

def calc_atomizing_air_volume_scaleup(AAV1, SR1, SR2):
    if SR1 == 0:
        return None
    return AAV1 * SR2 / SR1

def calc_air_volume_scaleup(AV1, A1, A2):
    if A2 == 0:
        return None
    return AV1 * A1 / A2

# --- PDF Generation function ---

def generate_pdf_report(data_dict):
    pdf_output = io.BytesIO()
    doc = SimpleDocTemplate(pdf_output, pagesize=A4)
    styles = getSampleStyleSheet()
    story = []

    story.append(Paragraph("🌬️ FBP Granulation Scale-Up Report (Top Spray)", styles['Title']))
    story.append(Spacer(1, 12))

    for section, results in data_dict.items():
        story.append(Paragraph(f"<b>{section}</b>", styles['Heading2']))
        for label, value in results.items():
            story.append(Paragraph(f"{label}: {value}", styles['Normal']))
        story.append(Spacer(1, 12))

    doc.build(story)
    return pdf_output

# --- Streamlit App ---

def main():
    st.title("🌬️ FBP Granulation Scale-Up (Top Spray)")
    st.markdown(
        """
        Scale up calculations for spray rate, atomizing air volume, air volume, and bottom screen area.
        """
    )

    # --- Bottom Screen Area ---
    st.header("0️⃣ Bottom Screen Area Calculation")
    st.markdown("Input radius in meters for bottom screens.")

    radius_lab = st.number_input("Lab Bottom Screen Radius (m)", min_value=0.0, value=0.25, step=0.01, key="radius_lab")
    radius_pilot = st.number_input("Pilot Bottom Screen Radius (m)", min_value=0.0, value=0.5, step=0.01, key="radius_pilot")

    area_lab = calc_bottom_screen_area(radius_lab)
    area_pilot = calc_bottom_screen_area(radius_pilot)

    st.write(f"Lab Bottom Screen Area (A1): {area_lab:.4f} m²")
    st.write(f"Pilot Bottom Screen Area (A2): {area_pilot:.4f} m²")

    st.markdown("---")

    # --- Spray Rate Scale-Up ---
    st.header("1️⃣ Spray Rate Scale-Up")
    SR1 = st.number_input("Lab Scale Spray Rate (SR1, g/min)", min_value=0.0, value=50.0, key="SR1")
    AV1 = st.number_input("Lab Scale Air Volume (AV1, CFM)", min_value=0.0, value=100.0, key="AV1")
    AV2 = st.number_input("Pilot Scale Air Volume (AV2, CFM)", min_value=0.0, value=400.0, key="AV2")

    if st.button("Calculate Spray Rate Scale-Up"):
        spray_rate_result = calc_spray_rate_scaleup(SR1, AV1, AV2)
        st.session_state.spray_rate_result = spray_rate_result
    else:
        spray_rate_result = st.session_state.get("spray_rate_result", None)

    if spray_rate_result is not None:
        st.success(f"Pilot Scale Spray Rate (SR2): {spray_rate_result:.2f} g/min")

    st.markdown("---")

    # --- Atomizing Air Volume Scale-Up ---
    st.header("2️⃣ Atomizing Air Volume Scale-Up")
    AAV1 = st.number_input("Lab Scale Atomizing Air Volume (AAV1, CFM)", min_value=0.0, value=10.0, key="AAV1")

    # Use spray_rate_result if calculated, else manual input for SR2_for_aav
    default_SR2_for_aav = spray_rate_result if spray_rate_result is not None else 200.0
    SR2_for_aav = st.number_input(
        "Pilot Scale Spray Rate for Atomizing Air Volume (SR2, g/min)",
        min_value=0.0,
        value=default_SR2_for_aav,
        key="SR2_for_aav"
    )

    if st.button("Calculate Atomizing Air Volume Scale-Up"):
        atomizing_air_volume_result = calc_atomizing_air_volume_scaleup(AAV1, SR1, SR2_for_aav)
        st.session_state.atomizing_air_volume_result = atomizing_air_volume_result
    else:
        atomizing_air_volume_result = st.session_state.get("atomizing_air_volume_result", None)

    if atomizing_air_volume_result is not None:
        st.success(f"Pilot Scale Atomizing Air Volume (AAV2): {atomizing_air_volume_result:.2f} CFM")

    st.markdown("---")

    # --- Air Volume Scale-Up via Bottom Screen Area ---
    st.header("3️⃣ Air Volume Scale-Up via Bottom Screen Area")
    AV1_air = st.number_input("Lab Scale Air Volume (AV1, CFM)", min_value=0.0, value=100.0, key="AV1_air")

    if st.button("Calculate Air Volume Scale-Up"):
        air_volume_result = calc_air_volume_scaleup(AV1_air, area_lab, area_pilot)
        st.session_state.air_volume_result = air_volume_result
    else:
        air_volume_result = st.session_state.get("air_volume_result", None)

    if air_volume_result is not None:
        st.success(f"Pilot Scale Air Volume (AV2): {air_volume_result:.2f} CFM")

    st.markdown("---")

    # --- PDF Report Generation ---
    st.header("📄 Generate PDF Report")

    data_to_report = {}

    # Include Bottom Screen Areas
    data_to_report["Bottom Screen Areas (m²)"] = {
        "Lab Bottom Screen Area (A1)": f"{area_lab:.4f}",
        "Pilot Bottom Screen Area (A2)": f"{area_pilot:.4f}",
    }

    # Include Spray Rate Result if available
    if spray_rate_result is not None:
        data_to_report["Spray Rate Scale-Up"] = {
            "Lab Scale Spray Rate (SR1, g/min)": f"{SR1:.2f}",
            "Lab Scale Air Volume (AV1, CFM)": f"{AV1:.2f}",
            "Pilot Scale Air Volume (AV2, CFM)": f"{AV2:.2f}",
            "Pilot Scale Spray Rate (SR2, g/min)": f"{spray_rate_result:.2f}",
        }

    # Include Atomizing Air Volume Result if available
    if atomizing_air_volume_result is not None:
        data_to_report["Atomizing Air Volume Scale-Up"] = {
            "Lab Scale Atomizing Air Volume (AAV1, CFM)": f"{AAV1:.2f}",
            "Lab Scale Spray Rate (SR1, g/min)": f"{SR1:.2f}",
            "Pilot Scale Spray Rate (SR2, g/min)": f"{SR2_for_aav:.2f}",
            "Pilot Scale Atomizing Air Volume (AAV2, CFM)": f"{atomizing_air_volume_result:.2f}",
        }

    # Include Air Volume Result if available
    if air_volume_result is not None:
        data_to_report["Air Volume Scale-Up"] = {
            "Lab Scale Air Volume (AV1, CFM)": f"{AV1_air:.2f}",
            "Lab Bottom Screen Area (A1, m²)": f"{area_lab:.4f}",
            "Pilot Bottom Screen Area (A2, m²)": f"{area_pilot:.4f}",
            "Pilot Scale Air Volume (AV2, CFM)": f"{air_volume_result:.2f}",
        }

    if st.button("Generate and Download PDF Report"):
        if not data_to_report:
            st.error("No calculation results to include in the PDF report. Please calculate at least one parameter first.")
        else:
            pdf_buffer = generate_pdf_report(data_to_report)
            st.download_button(
                label="Download PDF Report",
                data=pdf_buffer.getvalue(),
                file_name="fbp_granulation_scaleup_report.pdf",
                mime="application/pdf"
            )


if __name__ == "__main__":
    if "spray_rate_result" not in st.session_state:
        st.session_state.spray_rate_result = None
    if "atomizing_air_volume_result" not in st.session_state:
        st.session_state.atomizing_air_volume_result = None
    if "air_volume_result" not in st.session_state:
        st.session_state.air_volume_result = None
    main()


