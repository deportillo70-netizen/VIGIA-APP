# PROYECTO: VIG.IA - CEREBRO (EXPANDED MENU)
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
        # --- MENÚ EXPANDIDO TIPO "NAVAJA SUIZA" ---
        self.estructura_conocimiento = {
            "🔍 UNIVERSAL / MULTIPROPÓSITO": ["Buenas Prácticas de Ingeniería", "Criterio del Fabricante", "Estándar Visual General"],
            "⚙️ MECÁNICO (Estático/Rotativo)": ["API 653 (Tanques)", "API 510 (Recipientes)", "API 570 (Tuberías)", "API 610 (Bombas)"],
            "⚡ ELÉCTRICO Y POTENCIA": ["NFPA 70B (Mantenimiento)", "NETA MTS", "Código Eléctrico Nacional (CEN)", "IEEE 43"],
            "🏗️ CIVIL E INFRAESTRUCTURA": ["ACI 318 (Concreto)", "AISC 360 (Estructuras Acero)", "Normas ISO Mantenimiento Edificios"],
            "🔥 SOLDADURA Y MATERIALES": ["ASME IX", "AWS D1.1 (Estructural)", "API 1104 (Gasoductos)"],
            "⚠️ SEGURIDAD (HSE/SISO)": ["OSHA 1910 (General Industry)", "ISO 45001", "Normas COVENIN (Venezuela)", "Matriz de Riesgos"],
            "🎨 CORROSIÓN Y PINTURA": ["NACE SP0188", "SSPC-PA2", "ISO 8501 (Grados de Óxido)"],
            "📟 INSTRUMENTACIÓN Y CONTROL": ["ISA 5.1", "API 554", "Manual de Fabricante"],
            "🚚 FLOTA Y TRANSPORTE": ["Mantenimiento Automotriz", "Inspección de Maquinaria Pesada", "DOT Regulations"]
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

    def analizar_imagen_con_ia(self, api_key, rutas_imagenes, datos_ins, datos_tec, calcular_costos=False, tasa_cambio=1.0):
        genai.configure(api_key=api_key)
        modelo = self._encontrar_modelo_disponible()
        if not modelo: return "ERROR: No hay modelos IA disponibles."

        lista_imagenes_pil = []
        try:
            for ruta in rutas_imagenes:
                img = PIL.Image.open(ruta)
                lista_imagenes_pil.append(img)
        except: return "Error al abrir alguna de las imágenes."

        instruccion_costos = ""
        if calcular_costos:
            instruccion_costos = f"""
            5. ESTIMACIÓN DE COSTOS (MERCADO VENEZOLANO - CLASE 5):
            - Tasa Referencial: {tasa_cambio} Bs/USD.
            - Genera Tabla Markdown: | Partida | Cantidad | Unitario ($) | Total ($) | Total (Bs) |
            - Sumar totales al final.
            - Nota legal: "Estimación Clase 5 (-50%/+100%). Valores referenciales."
            """

        prompt = f"""
        Rol: Inspector Experto en {datos_ins['modulo']}. Norma/Criterio: {datos_ins['norma']}.
        Contexto Específico: {datos_tec}
        Tarea: Auditoría técnica visual de {len(lista_imagenes_pil)} imágenes.
        Si es modo UNIVERSAL, usa criterio de ingeniería general y sentido común técnico.
        
        REPORTE TÉCNICO:
        1. HALLAZGOS (Descripción detallada de fallas, daños o condiciones).
        2. ANÁLISIS TÉCNICO/NORMATIVO (¿Cumple o No Cumple? ¿Por qué?).
        3. CAUSA RAÍZ (Desgaste, falta de mantenimiento, ambiente, operación, etc.).
        4. RECOMENDACIONES (Plan de acción correctivo inmediato).
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

    def generar_pdf_ia(self, datos, texto_ia, rutas_imagenes):
        pdf = PDFReport()
        pdf.set_auto_page_break(auto=True, margin=15)
        pdf.add_page()
        
        pdf.set_font('Arial', 'B', 16)
        pdf.cell(0, 10, 'DICTAMEN TÉCNICO VIG.IA', 0, 1, 'C')
        pdf.set_font('Arial', '', 10)
        pdf.cell(0, 6, f"Especialidad: {datos['modulo']}", 0, 1, 'C')
        pdf.cell(0, 6, f"Norma/Criterio: {datos['norma']}", 0, 1, 'C')
        pdf.cell(0, 6, f"Inspector: {datos['usuario']} | Fecha: {datetime.datetime.now().strftime('%d/%m/%Y')}", 0, 1, 'C')
        pdf.ln(10)
        
        pdf.set_fill_color(50, 50, 50) 
        pdf.set_text_color(255, 255, 255) 
        pdf.cell(0, 8, " RESULTADOS DE LA INSPECCIÓN", 1, 1, 'L', 1)
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
            pdf.cell(0, 10, f" EVIDENCIA FOTOGRÁFICA ({len(rutas_imagenes)})", 1, 1, 'C', 1)
            pdf.ln(10)
            
            for i, ruta in enumerate(rutas_imagenes):
                if os.path.exists(ruta):
                    try:
                        pdf.image(ruta, x=30, w=150)
                        pdf.ln(5)
                        pdf.set_text_color(0, 0, 0)
                        pdf.set_font('Arial', 'I', 9)
                        pdf.cell(0, 5, f"Evidencia #{i+1}", 0, 1, 'C')
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
        self.cell(0, 10, f'Reporte generado por IA | Página {self.page_no()}', 0, 0, 'C')
