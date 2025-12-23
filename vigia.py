# PROYECTO: VIG.IA - SISTEMA DE INTELIGENCIA INDUSTRIAL
# ARCHIVO: vigia.py
# VERSIÓN: 1.4 (MOBILE FIRST + COSTOS + MULTI-IMG)

import streamlit as st
import tempfile
import os
import time
from Nucleo_Vigia import InspectorIndustrial

# --- ⚠️ ZONA DE CONFIGURACIÓN ---
CLAVE_MAESTRA = "admin123" 
# --------------------------------

# 1. CONFIGURACIÓN DE PÁGINA
st.set_page_config(page_title="VIG.IA | Mobile", page_icon="🟠", layout="wide")

# 2. INYECCIÓN DE ESTILO (CSS OPTIMIZADO PARA MÓVIL)
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Roboto:wght@400;700&display=swap');
    
    html, body, [class*="css"] { font-family: 'Roboto', sans-serif; }
    
    /* Color de fondo Sidebar */
    [data-testid="stSidebar"] { background-color: #f4f4f4; }
    
    /* Títulos Naranja */
    h1, h2, h3 { color: #FF6F00 !important; font-weight: 700; }
    
    /* --- OPTIMIZACIÓN MÓVIL (BOTONES TÁCTILES) --- */
    div.stButton > button:first-child {
        background-color: #FF6F00; 
        color: white; 
        border-radius: 12px; /* Bordes redondeados tipo App */
        border: none; 
        font-weight: bold; 
        text-transform: uppercase; 
        letter-spacing: 1px;
        height: 3.5em; /* Botón alto para dedo */
        width: 100%;   /* Ancho total */
        font-size: 16px;
        box-shadow: 0px 4px 6px rgba(0,0,0,0.1);
    }
    
    div.stButton > button:first-child:hover { 
        background-color: #E65100; 
        transform: translateY(-2px); /* Efecto presión */
    }
    
    /* Input de Cámara más visible */
    button[kind="secondary"] { border-color: #FF6F00; color: #FF6F00; }

    /* --- LIMPIEZA DE INTERFAZ (MODO APP) --- */
    /* Ocultamos menú de hamburguesa de Streamlit y footers */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;} 
    
    /* Ajuste de alertas */
    .stAlert { border-left-color: #FF6F00 !important; }
    </style>
    """, unsafe_allow_html=True)

# --- LOGIN ---
def check_password():
    if "password_correct" not in st.session_state:
        st.session_state["password_correct"] = False
    if st.session_state["password_correct"]:
        return True
    
    if CLAVE_MAESTRA: pass 

    col_spacer1, col_login, col_spacer2 = st.columns([1, 2, 1])
    with col_login:
        st.markdown("<br><h1 style='text-align: center; color: #333;'>🟠 VIG.IA</h1>", unsafe_allow_html=True)
        st.markdown("<h4 style='text-align: center; color: #666;'>MOBILE INTELLIGENCE</h4>", unsafe_allow_html=True)
        st.markdown("---")
        pwd = st.text_input("Credencial de Acceso:", type="password")
        
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("INGRESAR AL SISTEMA", use_container_width=True):
            if CLAVE_MAESTRA and pwd == CLAVE_MAESTRA:
                st.session_state["password_correct"] = True
                st.rerun()
            try:
                if pwd == st.secrets["APP_PASSWORD"]:
                    st.session_state["password_correct"] = True
                    st.rerun()
                else:
                    st.error("⛔ CREDENCIAL INVÁLIDA")
            except:
                st.warning("⚠️ MODO LOCAL")
                st.info(f"Usa Clave Maestra: {CLAVE_MAESTRA}")

    return False

if not check_password():
    st.stop()

# --- INICIO DEL PROGRAMA ---
if 'inspector' not in st.session_state:
    st.session_state.inspector = InspectorIndustrial()

inspector = st.session_state.inspector

try:
    API_KEY_NUBE = st.secrets["GOOGLE_API_KEY"]
except:
    API_KEY_NUBE = ""

# --- SIDEBAR (MENÚ LATERAL MÓVIL) ---
with st.sidebar:
    st.markdown("# 🟠 VIG.IA")
    st.markdown("**Versión 1.4 (Mobile)**")
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
    st.markdown("### 👷‍♂️ Auditoría")
    usuario = st.text_input("Inspector:", "Gerente Angel Portillo")
    proyecto = st.text_input("Tag / Activo:", "Inspección Móvil")
    
    st.markdown("---")
    st.markdown("### 💰 Finanzas")
    activar_costos = st.checkbox("Estimar Costos (Clase 5)", value=True)

# --- TABS ---
tab1, tab2 = st.tabs(["🕵️ CAMPO", "📜 MEMORIA"])

# === PESTAÑA 1: INSPECCIÓN ===
with tab1:
    # En móvil, las columnas se apilan automáticamente (Responsive)
    st.subheader("1. Evidencia Visual")
    
    # --- SISTEMA HÍBRIDO FOTO/GALERÍA ---
    archivo_camara = st.camera_input("📸 TOMAR FOTO AHORA", label_visibility="visible")
    archivos_galeria = st.file_uploader("📂 O subir fotos (Máx 10)", type=["jpg", "png", "jpeg"], accept_multiple_files=True)
    
    lista_imagenes = []
    if archivo_camara:
        lista_imagenes.append(archivo_camara)
    elif archivos_galeria:
        lista_imagenes = archivos_galeria

    if lista_imagenes:
        st.success(f"✅ {len(lista_imagenes)} Capturas listas")
        with st.expander("👁️ Ver capturas"):
            cols = st.columns(3)
            for i, img in enumerate(lista_imagenes):
                cols[i % 3].image(img, use_container_width=True)

    st.markdown("---")
    st.subheader("2. Datos Técnicos")
    
    modulo = st.selectbox("Especialidad:", inspector.obtener_modulos())
    norma = st.selectbox("Norma:", inspector.obtener_normas(modulo))
    
    datos_tecnicos = ""
    if "MECÁNICO" in modulo:
        c1, c2 = st.columns(2)
        diametro = c1.number_input("Diám (m):", 0.0, 100.0, 15.0)
        altura = c2.number_input("Alt (m):", 0.0, 50.0, 8.0)
        material = c1.text_input("Material:", "Acero ASTM A36")
        fluido = c2.text_input("Fluido:", "Crudo")
        datos_tecnicos = f"Equipo Estático. Dimensiones: {diametro}x{altura}m. Material: {material}. Fluido: {fluido}."
    elif "ELÉCTRICO" in modulo:
        c1, c2 = st.columns(2)
        voltaje = c1.selectbox("Voltaje:", ["110/220V", "440V", "13.8kV", "115kV"])
        equipo = c2.text_input("Equipo:", "Transformador")
        datos_tecnicos = f"Equipo Eléctrico: {equipo}. Tensión: {voltaje}."
    elif "SOLDADURA" in modulo:
        proceso = st.selectbox("Proceso:", ["SMAW", "GTAW", "GMAW", "FCAW"])
        posicion = st.selectbox("Posición:", ["1G", "2G", "3G", "4G", "6G"])
        datos_tecnicos = f"Inspección Soldadura. Proceso: {proceso}. Posición: {posicion}."
    else:
        datos_tecnicos = st.text_area("Notas de campo:", height=100)

    st.markdown("<br>", unsafe_allow_html=True)
    
    # BOTÓN DE ACCIÓN GIGANTE
    if st.button("🚀 INICIAR ANÁLISIS VIG.IA", use_container_width=True):
        if not api_key:
             st.error("⛔ Falta API Key.")
        elif not lista_imagenes:
            st.error("⚠️ Falta Evidencia.")
        else:
            with st.spinner(f"⚡ Analizando {len(lista_imagenes)} ítems..."):
                
                rutas_temporales = []
                for img_file in lista_imagenes:
                    with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as tmp:
                        tmp.write(img_file.getvalue())
                        rutas_temporales.append(tmp.name)
                
                info = {"usuario": usuario, "proyecto": proyecto, "modulo": modulo, "norma": norma}
                
                resultado = inspector.analizar_imagen_con_ia(api_key, rutas_temporales, info, datos_tecnicos, activar_costos)
                
                st.session_state['res_web'] = resultado
                st.session_state['imgs_web'] = rutas_temporales
                st.session_state['info_web'] = info
            st.balloons()
            st.success("✅ ANÁLISIS COMPLETADO")

    if 'res_web' in st.session_state:
        st.markdown("### 📋 Dictamen")
        st.write(st.session_state['res_web'])
        
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("📄 DESCARGAR PDF", use_container_width=True):
            pdf = inspector.generar_pdf_ia(st.session_state['info_web'], st.session_state['res_web'], st.session_state['imgs_web'])
            st.download_button("Guardar PDF", pdf, "Reporte_VIGIA.pdf", "application/pdf", use_container_width=True)

# === PESTAÑA 2: MEMORIA ===
with tab2:
    col_head, col_trash = st.columns([3, 1])
    with col_head: st.header("Historial")
    with col_trash:
        if st.button("🗑️"):
            inspector.borrar_memoria()
            st.toast("Memoria borrada")
            time.sleep(1)
            st.rerun()

    if st.button("🔄 Refrescar"): st.rerun()
    
    historial = inspector.obtener_historial()
    if historial:
        for fila in historial:
            with st.expander(f"📅 {fila[0]} | {fila[1]}"):
                st.markdown(f"**Norma:** {fila[3]}")
                st.caption("Resumen del dictamen:")
                st.markdown(fila[4][:200] + "...") # Vista previa corta para móvil
    else:
        st.info("Sin registros.")