import streamlit as st
import datetime
from openai import OpenAI
from fpdf import FPDF
import os  

# Initialize the OpenAI Client with your secret key
# REPLÁZALA POR TU NUEVA LLAVE SECRETA REAL ENTRE LAS COMILLAS:
# Formato universal para servidores en la nube como Render
client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

# Function to generate an Ultra-Premium PDF file with Side-by-Side Corporate Branding
def create_pdf(report_text, patient_name, date_str, age, modality, logo_file, signature_file):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_margins(20, 20, 20)
    
    # --- PALETA DE COLORES PREMIUM (RGB) ---
    NAVY = (24, 43, 73)
    DARK_GRAY = (60, 60, 60)
    LIGHT_BLUE = (70, 130, 180)
    BACKGROUND_BOX = (245, 247, 250)
    
    # --- ENCABEZADO CORPORATIVO EN DOS COLUMNAS ---
    pdf.set_xy(20, 15)
    
    if logo_file is not None:
        with open("temp_logo.png", "wb") as f:
            f.write(logo_file.getbuffer())
        # Insertamos el logo en la esquina izquierda de forma segura fijando el ancho (35mm)
        pdf.image("temp_logo.png", x=20, y=15, w=35)
    else:
        # Texto corporativo por defecto si no hay logo
        pdf.set_font("Helvetica", style="B", size=12)
        pdf.set_text_color(*LIGHT_BLUE)
        pdf.cell(50, 10, txt="CLINICAL SYSTEMS", ln=0)
        
    # Movemos el cursor al lado derecho para poner los títulos sin interferir con el logo
    pdf.set_xy(90, 16)
    pdf.set_font("Helvetica", style="I", size=9)
    pdf.set_text_color(150, 150, 150)
    pdf.cell(100, 5, txt="CONFIDENTIAL CASE RECORD", ln=1, align="R")
    
    pdf.set_xy(90, 24)
    pdf.set_font("Helvetica", style="B", size=18)
    pdf.set_text_color(*NAVY)
    pdf.cell(100, 10, txt="Clinical SOAP Report", ln=1, align="R")
    
    # Forzamos un salto de línea grande para salir por completo de la zona del logotipo (65mm)
    pdf.set_xy(20, 65)
    
    # --- CAJA DE METADATOS DEL PACIENTE ---
    current_y = pdf.get_y()
    pdf.set_fill_color(*BACKGROUND_BOX)
    pdf.set_draw_color(220, 224, 230)
    pdf.set_line_width(0.2)
    
    # Dibujamos la caja contenedora de datos del expediente
    pdf.rect(20, current_y, 170, 24, style="DF")
    
    pdf.set_text_color(*NAVY)
    pdf.set_font("Helvetica", style="B", size=9)
    
    pdf.set_xy(24, current_y + 4)
    pdf.cell(85, 5, txt=f"PATIENT: {str(patient_name).upper()}")
    pdf.cell(85, 5, txt=f"DATE: {str(date_str)}")
    
    pdf.set_xy(24, current_y + 12)
    pdf.cell(85, 5, txt=f"AGE: {str(age)} YEARS OLD")
    pdf.cell(85, 5, txt=f"MODALITY: {str(modality).upper()}")
    
    # Salimos de la caja hacia el contenido clínico
    pdf.set_xy(20, current_y + 32)
    
    # --- CONTENIDO DEL REPORTE SOAP ---
    pdf.set_text_color(*DARK_GRAY)
    
    clean_report = report_text.replace("**", "").replace("### ", "").replace("## ", "").replace("`", "")
    lines = clean_report.split('\n')
    
    for line in lines:
        clean_line = line.strip()
        if not clean_line:
            pdf.ln(3)
            continue
            
        clean_line = clean_line.encode('latin-1', 'replace').decode('latin-1')
        
        if clean_line.startswith("S:") or clean_line.startswith("O:") or clean_line.startswith("A:") or clean_line.startswith("P:") or "Subjective" in clean_line or "Objective" in clean_line or "Assessment" in clean_line or "Plan" in clean_line:
            pdf.ln(4)
            pdf.set_font("Helvetica", style="B", size=12)
            pdf.set_text_color(*NAVY)
            pdf.cell(0, 8, txt=clean_line, ln=1)
            pdf.set_font("Helvetica", size=10.5)
            pdf.set_text_color(*DARK_GRAY)
        else:
            if clean_line.startswith("* ") or clean_line.startswith("- "):
                clean_line = "• " + clean_line[2:]
            
            pdf.multi_cell(170, 6.5, txt=clean_line)
            pdf.set_x(20)
            
    # --- SECCIÓN DE FIRMA DIGITAL ---
    pdf.ln(10)
    if signature_file is not None:
        with open("temp_sig.png", "wb") as f:
            f.write(signature_file.getbuffer())
        
        if pdf.get_y() > 230:
            pdf.add_page()
            pdf.set_xy(20, 30)
            
        current_sig_y = pdf.get_y()
        pdf.image("temp_sig.png", x=20, y=current_sig_y, h=15)
        pdf.set_xy(20, current_sig_y + 16)
        
        pdf.set_font("Helvetica", style="B", size=10)
        pdf.set_text_color(*NAVY)
        pdf.cell(0, 5, txt="Authorized Clinician Signature", ln=1, align="L")
        pdf.set_font("Helvetica", size=9)
        pdf.set_text_color(120, 120, 120)
        pdf.cell(0, 4, txt=f"Verified Electronically on {date_str}", align="L")
        
    # --- PIE DE PÁGINA CON LÍNEA DECORATIVA INFERIOR ---
    pdf.set_y(-20)
    pdf.set_draw_color(*LIGHT_BLUE)
    pdf.set_line_width(0.6)
    pdf.line(20, pdf.get_y(), 190, pdf.get_y())
    pdf.ln(2)
    pdf.set_font("Helvetica", style="I", size=8)
    pdf.set_text_color(160, 160, 160)
    pdf.cell(0, 8, txt="Confidential Medical Document - Generated via Clinical AI Note Processor", align="C")
    
    if os.path.exists("temp_logo.png"): os.remove("temp_logo.png")
    if os.path.exists("temp_sig.png"): os.remove("temp_sig.png")
    
    return pdf.output()

# Configuration and form layout
st.set_page_config(page_title="Clinical AI Note Processor", page_icon="🧠", layout="centered")

st.title("🏥 Clinical AI Note Processor")
st.subheader("Patient Session Dashboard")
st.write("Fill out the patient details, upload branding, and enter notes to build the document.")

st.divider()

st.header("🎨 Clinic Branding (Premium)")
col_logo, col_sig = st.columns(2)

with col_logo:
    uploaded_logo = st.file_uploader("Upload Clinic Logo (PNG/JPG):", type=["png", "jpg", "jpeg"])

with col_sig:
    uploaded_sig = st.file_uploader("Upload Clinician Signature (PNG/JPG):", type=["png", "jpg", "jpeg"])

st.divider()

st.header("👤 Patient Information")
col1, col2 = st.columns(2)

with col1:
    patient_name = st.text_input("Patient Full Name:", placeholder="e.g., John Doe")
    patient_age = st.number_input("Patient Age:", min_value=0, max_value=120, value=30)

with col2:
    session_date = st.date_input("Session Date:", datetime.date.today())
    therapy_type = st.selectbox(
        "Therapy Modality:",
        ["Cognitive Behavioral (CBT)", "Psychoanalytic", "Family Therapy", "Life Coaching", "Other"]
    )

st.divider()

st.header("📝 Session Raw Notes")
raw_notes = st.text_area(
    "Enter clinical bullet points, observations, or transcriptions here:",
    placeholder="Example: Patient reports high anxiety due to work pressure. Slept poorly...",
    height=200
)

if "generated_report" not in st.session_state:
    st.session_state.generated_report = None

st.divider()
if st.button("🚀 Generate Structured SOAP Report", use_container_width=True):
    if patient_name and raw_notes:
        st.info("🧠 AI is analyzing clinical data and formatting the SOAP report...")
        
        try:
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {
                        "role": "system", 
                        "content": (
                            "You are an elite clinical psychologist assistant. Your task is to transform raw, disorganized "
                            "session notes into a highly professional, medical-grade clinical report using the strict SOAP "
                            "(Subjective, Objective, Assessment, Plan) format. Write the entire output in professional English. "
                            "Do not include any greeting or conversational filler—output ONLY the structured medical report."
                        )
                    },
                    {
                        "role": "user", 
                        "content": (
                            f"Patient Name: {patient_name}\n"
                            f"Age: {patient_age}\n"
                            f"Date: {session_date}\n"
                            f"Modality: {therapy_type}\n"
                            f"Raw Notes:\n{raw_notes}"
                        )
                    }
                ]
            )
            
            st.session_state.generated_report = response.choices[0].message.content
            st.success(f"Report Generated Successfully for {patient_name}!")
            
        except Exception as e:
            st.error(f"An error occurred while connecting to the AI: {e}")
            
    else:
        st.warning("⚠️ Please ensure both 'Patient Full Name' and 'Session Raw Notes' are filled out.")

# --- SECCIÓN DE DESCARGA COMPLETADA ---
if st.session_state.generated_report:
    st.divider()
    st.markdown(st.session_state.generated_report)
    
    pdf_bytes = bytes(create_pdf(
        st.session_state.generated_report, 
        patient_name, 
        str(session_date),
        patient_age,
        therapy_type,
        uploaded_logo,
        uploaded_sig
    ))
    
    st.divider()
    st.download_button(
        label="📥 Download Clinical Report as PDF",
        data=pdf_bytes,
        file_name=f"SOAP_Report_{patient_name.replace(' ', '_')}_{session_date}.pdf",
        mime="application/pdf",
        use_container_width=True
    )
