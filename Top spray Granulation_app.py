import streamlit as st 
from fpdf import FPDF 
import os

Title

st.set_page_config(page_title="Top-Spray Granulation Scale-Up Calculator") 
st.title("Top-Spray Granulation Scale-Up Calculator")

--- User Inputs ---

st.sidebar.header("Input Parameters")

cross_section_small = st.sidebar.number_input("Cross-sectional area (small scale) in m^2", min_value=0.01) 
cross_section_large = st.sidebar.number_input("Cross-sectional area (large scale) in m^2", min_value=0.01) 
spray_rate_small = st.sidebar.number_input("Spray rate (small scale) in mL/min", min_value=0.01) 
airflow_small = st.sidebar.number_input("Airflow (small scale) in m3/h", min_value=0.01) 
batch_size_small = st.sidebar.number_input("Batch size (small scale) in kg", min_value=0.01) 
batch_size_large = st.sidebar.number_input("Batch size (large scale) in kg", min_value=0.01)
atom_air_small = st.sidebar.number_input("Atomization air pressure (small scale) in bar", min_value=0.1) 
nozzle_heads = st.sidebar.number_input("Number of nozzle heads", min_value=1, step=1) 
desired_droplet_size = st.sidebar.number_input("Desired droplet size (optional, in microns)", min_value=0.0, value=0.0)

Calculate button

if st.sidebar.button("Calculate"):

spray_rate_large = spray_rate_small * (cross_section_large / cross_section_small)
airflow_large = airflow_small * (cross_section_large / cross_section_small)
fluidization_velocity = airflow_large / cross_section_large
atom_air_large = atom_air_small * nozzle_heads

st.subheader("Calculated Scale-Up Parameters")
st.write(f"*Scaled Spray Rate:* {spray_rate_large:.2f} mL/min")
st.write(f"*Scaled Airflow:* {airflow_large:.2f} m3/h")
st.write(f"*Fluidization Velocity:* {fluidization_velocity:.2f} m/s")
st.write(f"*Required Atomization Air Pressure:* ~{atom_air_large:.2f} bar")

st.subheader("Generate PDF Report")
selected = st.multiselect("Select parameters to include in the PDF report:",
                          ["Spray Rate", "Airflow", "Fluidization Velocity", "Atomization Pressure"],
                          default=["Spray Rate", "Airflow", "Fluidization Velocity", "Atomization Pressure"])

if st.button("Generate PDF Report"):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.cell(200, 10, txt="Top-Spray Granulation Scale-Up Report", ln=True, align='C')
    pdf.ln(10)

    pdf.set_font("Arial", size=11)
    if "Spray Rate" in selected:
        pdf.cell(200, 10, txt=f"Scaled Spray Rate: {spray_rate_large:.2f} mL/min", ln=True)
    if "Airflow" in selected:
        pdf.cell(200, 10, txt=f"Scaled Airflow: {airflow_large:.2f} m3/h", ln=True)
    if "Fluidization Velocity" in selected:
        pdf.cell(200, 10, txt=f"Fluidization Velocity: {fluidization_velocity:.2f} m/s", ln=True)
    if "Atomization Pressure" in selected:
        pdf.cell(200, 10, txt=f"Required Atomization Air Pressure: ~{atom_air_large:.2f} bar", ln=True)

    filename = "top_spray_scaleup_report.pdf"
    pdf.output(filename)

    st.success("PDF report generated successfully.")
    with open(filename, "rb") as f:
        st.download_button("Download Report", f, file_name=filename)

    # Cleanup temporary file
    if os.path.exists(filename):
        os.remove(filename)
