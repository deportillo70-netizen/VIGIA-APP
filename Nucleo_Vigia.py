# PROYECTO: VIG.IA - CEREBRO (FINAL v1.7 BILINGÜE)
# ARCHIVO: Nucleo_Vigia.py

import google.generativeai as genai
from fpdf import FPDF
import PIL.Image
import datetime
import os
import sqlite3

class GestorDatos:
    def __init__(self, db_name="historial_vigia.db"):
        self.db_name = db_name
        self._inicializar_db()

    def _inicializar_db(self):
        conn = sqlite3.connect(self.db_name)
        c = conn.cursor()
        c.execute('''CREATE TABLE IF NOT EXISTS inspecciones
                     (id INTEGER PRIMARY KEY AUTOINCREMENT,
                      fecha TEXT, proyecto TEXT, inspector TEXT,
                      modulo TEXT, norma TEXT, dictamen TEXT)''')
        conn.commit()
        conn.close()

    def guardar_inspeccion(self, proyecto, inspector, modulo, norma, dictamen):
        conn = sqlite3.connect(self.db_name)
        c = conn.cursor()
        fecha = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        c.execute("INSERT INTO inspecciones (fecha, proyecto, inspector, modulo, norma, dictamen) VALUES (?, ?, ?, ?, ?, ?)",
                  (fecha, proyecto, inspector, modulo, norma, dictamen))
        conn.commit()
        conn.close()

    def leer_historial(self):
        conn = sqlite3.connect(self.db_name)
        c = conn.cursor()
        c.execute("SELECT fecha, proyecto, modulo, norma, dictamen FROM inspecciones ORDER BY fecha DESC")
        datos = c.fetchall()
        conn.close()
        return datos

    def borrar_historial(self):
        conn = sqlite3.connect(self.db_name)
        c = conn.cursor()
        c.execute("DELETE FROM inspecciones")
        conn.commit()
        conn.close()

class InspectorIndustrial:
    def __init__(self):
        self.db = GestorDatos()
        self.estructura_conocimiento = {
            "🔍 UNIVERSAL / MULTIPROPÓSITO": ["Engineering Best Practices", "OEM Criteria", "Visual Standard"],
            "⚙️ MECÁNICO (Estático/Rotativo)": ["API 653 (Tanks)", "API 510 (Vessels)", "API 570 (Piping)", "API 610 (Pumps)"],
            "⚡ ELÉCTRICO Y POTENCIA": ["NFPA 70B", "NETA MTS", "NEC (National Electric Code)", "IEEE 43"],
            "🏗️ CIVIL E INFRAESTRUCTURA": ["ACI 318 (Concrete)", "AISC 360 (Steel)", "ISO Facilities Maint"],
            "🔥 SOLDADURA Y MATERIALES": ["ASME IX", "AWS D1.1", "API 1104"],
            "⚠️ SEGURIDAD (HSE/SISO)": ["OSHA 1910", "ISO 45001", "Risk Matrix"],
            "🎨 CORROSIÓN Y PINTURA": ["NACE SP0188", "SSPC-PA2", "ISO 8501"],
            "📟 INSTRUMENTACIÓN Y CONTROL": ["ISA 5.1", "API 554", "OEM Manual"],
            "🚚 FLOTA Y TRANSPORTE": ["Automotive Maintenance", "Heavy Machinery Insp", "DOT Regulations"]
        }

    def obtener_modulos(self): return list(self.estructura_conocimiento.keys())
    def obtener_normas(self, modulo): return self.estructura_conocimiento.get(modulo, [])
    def obtener_historial(self): return self.db.leer_historial()
    def borrar_memoria(self): self.db.borrar_historial()

    def _encontrar_modelo_disponible(self):
        try:
            lista = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
            for m in lista:
                if 'flash' in m and '1.5' in m: return m
            for m in lista:
                if 'pro' in m and 'vision' in m: return m
            return lista[0] if lista else None
        except: return None

    # ESTA ES LA CLAVE: AHORA ACEPTA "idioma"
    def analizar_imagen_con_ia(self, api_key, rutas_imagenes, datos_ins, datos_tec, calcular_costos=False, tasa_cambio=1.0, idioma="Español"):
        genai.configure(api_key=api_key)
        modelo = self._encontrar_modelo_disponible()
        if not modelo: return "ERROR: No hay modelos IA disponibles."

        lista_imagenes_pil = []
        try:
            for ruta in rutas_imagenes:
                img = PIL.Image.open(ruta)
                lista_imagenes_pil.append(img)
        except: return "Error al abrir imágenes."

        # LOGICA BILINGÜE
        if idioma == "English":
            instruccion_costos = ""
            if calcular_costos:
                instruccion_costos = f"""
                5. COST ESTIMATION (VENEZUELA MARKET - CLASS 5):
                - Ref Rate: {tasa_cambio} Bs/USD.
                - Generate Markdown Table: | Item | Qty | Unit ($) | Total ($) | Total (Bs) |
                - Calculate Total (Bs) = Total ($) * {tasa_cambio}.
                - Add disclaimer: "Class 5 Estimate (-50%/+100%). Reference values subject to local inflation."
                """

            prompt = f"""
            Role: Senior Industrial Inspector. Specialty: {datos_ins['modulo']}. Standard: {datos_ins['norma']}.
            Context: {datos_tec}
            Task: Visual audit of {len(lista_imagenes_pil)} images.
            OUTPUT LANGUAGE: ENGLISH.
            
            TECHNICAL REPORT STRUCTURE:
            1. FINDINGS (Detailed description of failures/conditions).
            2. COMPLIANCE ANALYSIS (Compliant/Non-Compliant with {datos_ins['norma']}).
            3. ROOT CAUSE (Technical origin of the issue).
            4. RECOMMENDATIONS (Action plan).
            {instruccion_costos}
            Tone: Professional, Technical, Executive.
            """
        else:
            instruccion_costos = ""
            if calcular_costos:
                instruccion_costos = f"""
                5. ESTIMACIÓN DE COSTOS (MERCADO VENEZOLANO - CLASE 5):
                - Tasa Referencial: {tasa_cambio} Bs/USD.
                - Tabla Markdown: | Partida | Cantidad | Unitario ($) | Total ($) | Total (Bs) |
                - Total (Bs) = Total ($) * {tasa_cambio}.
                - Nota legal: "Estimación Clase 5 (-50%/+100%). Valores referenciales."
                """

            prompt = f"""
            Rol: Inspector Experto en {datos_ins['modulo']}. Norma: {datos_ins['norma']}.
            Contexto: {datos_tec}
            Tarea: Auditoría visual de {len(lista_imagenes_pil)} imágenes.
            IDIOMA DE SALIDA: ESPAÑOL.
            
            REPORTE TÉCNICO:
            1. HALLAZGOS (Descripción detallada).
            2. ANÁLISIS NORMATIVO (¿Cumple/No Cumple? Criterio: {datos_ins['norma']}).
            3. CAUSA RAÍZ.
            4. RECOMENDACIONES.
            {instruccion_costos}
            Tono: Profesional, técnico y directo.
            """

        try:
            model = genai.GenerativeModel(modelo)
            response = model.generate_content([prompt] + lista_imagenes_pil)
            text = response.text
            self.db.guardar_inspeccion(datos_ins['proyecto'], datos_ins['usuario'], datos_ins['modulo'], datos_ins['norma'], text)
            return text
        except Exception as e: return f"Error IA: {str(e)}"

    def generar_pdf_ia(self, datos, texto_ia, rutas_imagenes, idioma="Español"):
        pdf = PDFReport()
        pdf.set_auto_page_break(auto=True, margin=15)
        pdf.add_page()
        
        t_titulo = 'DICTAMEN TÉCNICO VIG.IA' if idioma == "Español" else 'VIG.IA TECHNICAL REPORT'
        t_especialidad = 'Especialidad:' if idioma == "Español" else 'Specialty:'
        t_norma = 'Norma/Criterio:' if idioma == "Español" else 'Standard:'
        t_inspector = 'Inspector:' if idioma == "Español" else 'Inspector:'
        t_fecha = 'Fecha:' if idioma == "Español" else 'Date:'
        t_resultados = ' RESULTADOS' if idioma == "Español" else ' RESULTS'
        t_evidencia = ' EVIDENCIA FOTOGRÁFICA' if idioma == "Español" else ' PHOTOGRAPHIC EVIDENCE'
        
        pdf.set_font('Arial', 'B', 16)
        pdf.cell(0, 10, t_titulo, 0, 1, 'C')
        pdf.set_font('Arial', '', 10)
        pdf.cell(0, 6, f"{t_especialidad} {datos['modulo']}", 0, 1, 'C')
        pdf.cell(0, 6, f"{t_norma} {datos['norma']}", 0, 1, 'C')
        pdf.cell(0, 6, f"{t_inspector} {datos['usuario']} | {t_fecha} {datetime.datetime.now().strftime('%d/%m/%Y')}", 0, 1, 'C')
        pdf.ln(10)
        
        pdf.set_fill_color(50, 50, 50) 
        pdf.set_text_color(255, 255, 255) 
        pdf.cell(0, 8, t_resultados, 1, 1, 'L', 1)
        pdf.set_text_color(0, 0, 0) 
        pdf.ln(5)
        
        pdf.set_font('Arial', '', 11)
        texto_limpio = texto_ia.replace('**', '').replace('##', '').replace('•', '-')
        texto_limpio = texto_limpio.encode('latin-1', 'replace').decode('latin-1')
        pdf.multi_cell(0, 6, texto_limpio)
        
        if rutas_imagenes:
            pdf.add_page()
            pdf.set_fill_color(255, 111, 0)
            pdf.set_text_color(255, 255, 255)
            pdf.cell(0, 10, f"{t_evidencia} ({len(rutas_imagenes)})", 1, 1, 'C', 1)
            pdf.ln(10)
            
            for i, ruta in enumerate(rutas_imagenes):
                if os.path.exists(ruta):
                    try:
                        pdf.image(ruta, x=30, w=150)
                        pdf.ln(5)
                        pdf.set_text_color(0, 0, 0)
                        pdf.set_font('Arial', 'I', 9)
                        pdf.cell(0, 5, f"Img #{i+1}", 0, 1, 'C')
                        pdf.ln(10)
                    except: pass
        
        return pdf.output(dest='S').encode('latin-1')

class PDFReport(FPDF):
    def header(self):
        if os.path.exists("logo.png"):
            self.image("logo.png", 10, 8, 25)
        self.set_font('Arial', 'B', 12)
        self.cell(30) 
        self.cell(0, 10, 'SUNBELT SURPLUS - VIG.IA SYSTEM', 0, 0, 'L')
        self.set_draw_color(255, 111, 0)
        self.set_line_width(1)
        self.line(10, 28, 200, 28)
        self.ln(25) 

    def footer(self):
        self.set_y(-15)
        self.set_font('Arial', 'I', 8)
        self.set_text_color(128)
        self.cell(0, 10, f'VIG.IA Report | Page {self.page_no()}', 0, 0, 'C')
