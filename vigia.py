# PROYECTO: VIG.IA - SISTEMA DE INTELIGENCIA INDUSTRIAL
# ARCHIVO: vigia.py
# VERSIÓN: 1.7 (INTERNATIONAL EDITION)

import streamlit as st
import tempfile
import os
import time
import requests
from Nucleo_Vigia import InspectorIndustrial

# --- ⚠️ ZONA DE CONFIGURACIÓN ---
CLAVE_MAESTRA = "admin123" 
# --------------------------------

st.set_page_config(page_title="VIG.IA | International", page_icon="🌎", layout="wide")

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Roboto:wght@400;700&display=swap');
    
    html, body, [class*="css"] { font-family: 'Roboto', sans-serif; }
    [data-testid="stSidebar"] { background-color: #f4f4f4; }
    h1, h2, h3 { color: #FF6F00 !important; font-weight: 700; }
    
    div.stButton > button:first-child {
        background-color: #FF6F00; 
        color: white; 
        border-radius: 12px; 
        border: none; 
        font-weight: bold; 
        text-transform: uppercase; 
        letter-spacing: 1px;
        height: 3.5em; 
        width: 100%;
        font-size: 16px;
        box-shadow: 0px 4px 6px rgba(0,0,0,0.1);
    }
    div.stButton > button:first-child:hover { 
        background-color: #E65100; 
        transform: translateY(-2px);
    }
    button[kind="secondary"] { border-color: #FF6F00; color: #FF6F00; }

    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;} 
    .stAlert { border-left-color: #FF6F00 !important; }
    </style>
    """, unsafe_allow_html=True)

def obtener_tasa_dia():
    try:
        url = "https://api.exchangerate-api.com/v4/latest/USD"
        response = requests.get(url, timeout=5)
        datos = response.json()
        tasa = datos['rates']['VES']
        return round(tasa, 2)
    except:
        return 60.00

# --- LOGIN ---
def check_password():
    if "password_correct" not in st.session_state:
        st.session_state["password_correct"] = False
    if st.session_state["password_correct"]: return True
    
    if CLAVE_MAESTRA: pass 

    col_spacer1, col_login, col_spacer2 = st.columns([1, 2, 1])
    with col_login:
        st.markdown("<br><h1 style='text-align: center; color: #333;'>🌎 VIG.IA</h1>", unsafe_allow_html=True)
        st.markdown("<h4 style='text-align: center; color: #666;'>INTERNATIONAL INTELLIGENCE</h4>", unsafe_allow_html=True)
        st.markdown("---")
        pwd = st.text_input("Credencial / Access Key:", type="password")
        
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("ENTER SYSTEM / INGRESAR", use_container_width=True):
            if CLAVE_MAESTRA and pwd == CLAVE_MAESTRA:
                st.session_state["password_correct"] = True
                st.rerun()
            try:
                if pwd == st.secrets["APP_PASSWORD"]:
                    st.session_state["password_correct"] = True
                    st.rerun()
                else: st.error("⛔ INVALID CREDENTIAL")
            except:
                st.warning("⚠️ LOCAL MODE")
                st.info(f"Master Key: {CLAVE_MAESTRA}")
    return False

if not check_password(): st.stop()

# --- INICIO ---
if 'inspector' not in st.session_state:
    st.session_state.inspector = InspectorIndustrial()

inspector = st.session_state.inspector

try: API_KEY_NUBE = st.secrets["GOOGLE_API_KEY"]
except: API_KEY_NUBE = ""

# --- SIDEBAR ---
with st.sidebar:
    st.markdown("# 🌎 VIG.IA")
    st.markdown("**Versión 1.7 (Intl)**")
    st.markdown("---")
    
    if CLAVE_MAESTRA:
        if API_KEY_NUBE:
             api_key = API_KEY_NUBE
             st.success("🔓 Licencia: HÍBRIDA")
        else:
             api_key = st.text_input("🔑 API Key:", type="password")
             st.warning("⚠️ Licencia: LOCAL")
    elif API_KEY_NUBE:
        api_key = API_KEY_NUBE
        st.info("☁️ Licencia: CLOUD")
    else:
        api_key = st.text_input("🔑 API Key:", type="password")

    st.markdown("---")
    # --- SELECTOR DE IDIOMA ---
    idioma = st.radio("Idioma / Language:", ["Español", "English"], horizontal=True)
    
    st.markdown("---")
    st.markdown("### 💰 Tasa / Rate")
    
    if 'tasa_actual' not in st.session_state:
        st.session_state['tasa_actual'] = obtener_tasa_dia()
    
    col_tasa1, col_tasa2 = st.columns([2,1])
    tasa_usuario = col_tasa1.number_input("Bs/USD:", value=st.session_state['tasa_actual'], step=0.1, format="%.2f")
    if col_tasa2.button("🔄"):
        st.session_state['tasa_actual'] = obtener_tasa_dia()
        st.rerun()
    
    st.markdown("---")
    st.markdown("### 👷‍♂️ Project Data")
    usuario = st.text_input("Inspector:", "Gerente Angel Portillo")
    proyecto = st.text_input("Tag / Asset:", "General Inspection")
    activar_costos = st.checkbox("Cost Estimating (Bs/$)", value=True)

# --- TABS ---
label_tab1 = "🕵️ CAMPO (FIELD)"
label_tab2 = "📜 MEMORIA (LOGS)"
tab1, tab2 = st.tabs([label_tab1, label_tab2])

with tab1:
    st.subheader("1. Evidencia Visual / Visual Evidence")
    archivo_camara = st.camera_input("📸 CAMERA", label_visibility="visible")
    archivos_galeria = st.file_uploader("📂 GALLERY (Max 10)", type=["jpg", "png", "jpeg"], accept_multiple_files=True)
    
    lista_imagenes = []
    if archivo_camara: lista_imagenes.append(archivo_camara)
    elif archivos_galeria: lista_imagenes = archivos_galeria

    if lista_imagenes:
        st.success(f"✅ {len(lista_imagenes)}imgs Ready")
        with st.expander("👁️ Preview"):
            cols = st.columns(3)
            for i, img in enumerate(lista_imagenes):
                cols[i % 3].image(img, use_container_width=True)

    st.markdown("---")
    st.subheader("2. Datos Técnicos / Technical Data")
    
    modulo = st.selectbox("Especialidad / Specialty:", inspector.obtener_modulos())
    norma = st.selectbox("Norma / Standard:", inspector.obtener_normas(modulo))
    
    datos_tecnicos = ""
    
    if "MECÁNICO" in modulo:
        c1, c2 = st.columns(2)
        diametro = c1.number_input("Diameter (m):", 0.0, 100.0, 15.0)
        altura = c2.number_input("Height (m):", 0.0, 50.0, 8.0)
        material = c1.text_input("Material:", "Carbon Steel")
        fluido = c2.text_input("Fluid:", "Crude Oil")
        datos_tecnicos = f"Static Equipment. Dim: {diametro}x{altura}m. Mat: {material}. Fluid: {fluido}."
        
    elif "ELÉCTRICO" in modulo:
        c1, c2 = st.columns(2)
        voltaje = c1.selectbox("Voltage:", ["110/220V", "440V", "13.8kV", "115kV"])
        equipo = c2.text_input("Equipment:", "Transformer/Panel")
        datos_tecnicos = f"Electrical Eq: {equipo}. Voltage: {voltaje}."
        
    elif "SOLDADURA" in modulo:
        proceso = st.selectbox("Process:", ["SMAW", "GTAW", "GMAW", "FCAW"])
        posicion = st.selectbox("Position:", ["1G", "2G", "3G", "4G", "6G"])
        datos_tecnicos = f"Welding Insp. Process: {proceso}. Pos: {posicion}."
        
    else:
        st.info(f"📝 Mode: {modulo}. Describe context.")
        datos_tecnicos = st.text_area("Context / Observations:", height=100, placeholder="Description of the issue...")

    st.markdown("<br>", unsafe_allow_html=True)
    
    label_btn = "🚀 GENERATE REPORT" if idioma == "English" else "🚀 GENERAR REPORTE"
    
    if st.button(label_btn, use_container_width=True):
        if not api_key: st.error("⛔ Falta API Key.")
        elif not lista_imagenes: st.error("⚠️ No Images.")
        else:
            with st.spinner(f"⚡ Analizando ({idioma})..."):
                rutas_temporales = []
                for img_file in lista_imagenes:
                    with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as tmp:
                        tmp.write(img_file.getvalue())
                        rutas_temporales.append(tmp.name)
                
                info = {"usuario": usuario, "proyecto": proyecto, "modulo": modulo, "norma": norma}
                
                # PASAMOS EL IDIOMA AL CEREBRO
                resultado = inspector.analizar_imagen_con_ia(api_key, rutas_temporales, info, datos_tecnicos, activar_costos, tasa_usuario, idioma)
                
                st.session_state['res_web'] = resultado
                st.session_state['imgs_web'] = rutas_temporales
                st.session_state['info_web'] = info
                st.session_state['idioma_web'] = idioma # Guardamos idioma para el PDF
            st.balloons()
            st.success("✅ OK")

    if 'res_web' in st.session_state:
        st.markdown("### 📋 Report")
        st.write(st.session_state['res_web'])
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("📄 DOWNLOAD PDF", use_container_width=True):
            # Recuperamos el idioma guardado o usamos el actual
            lang_pdf = st.session_state.get('idioma_web', "Español")
            pdf = inspector.generar_pdf_ia(st.session_state['info_web'], st.session_state['res_web'], st.session_state['imgs_web'], lang_pdf)
            st.download_button("Save PDF", pdf, "VIGIA_Report.pdf", "application/pdf", use_container_width=True)

with tab2:
    col_head, col_trash = st.columns([3, 1])
    with col_head: st.header("History")
    with col_trash:
        if st.button("🗑️"):
            inspector.borrar_memoria()
            st.toast("Deleted")
            time.sleep(1)
            st.rerun()
    if st.button("🔄 Refresh"): st.rerun()
    historial = inspector.obtener_historial()
    if historial:
        for fila in historial:
            with st.expander(f"📅 {fila[0]} | {fila[1]}"):
                st.markdown(f"**Spec:** {fila[2]}")
                st.caption("Summary:")
                st.markdown(fila[4][:200] + "...")
    else: st.info("Empty.")
