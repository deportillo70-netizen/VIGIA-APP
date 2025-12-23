# PROYECTO: VIG.IA - CEREBRO (VENEZUELA COSTING)
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
            "MECÁNICO (Tanques/Recipientes)": ["API 653", "API 510", "API 570"],
            "SOLDADURA Y ESTRUCTURA": ["ASME IX", "AWS D1.1", "API 1104"],
            "CORROSIÓN Y PINTURA": ["NACE SP0188", "SSPC-PA2", "ISO 8501"],
            "ELÉCTRICO Y POTENCIA": ["NFPA 70B", "NETA MTS", "IEEE 43"],
            "SEGURIDAD (HSE)": ["OSHA 1910", "ISO 45001"]
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

    # MODIFICADO: Ahora recibe 'tasa_cambio'
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
            - Tasa de Cambio Referencial: {tasa_cambio} Bs/USD.
            - Considera sobrecostos logísticos de Venezuela, mano de obra local y repuestos importados.
            - Genera una Tabla Markdown estricta con estas columnas:
              | Partida / Acción | Cantidad | Unitario ($) | Total ($) | Total (Bs) |
            - La columna Total (Bs) debe ser la multiplicación del Total ($) por {tasa_cambio}.
            - Al final suma los totales en ambas monedas.
            - IMPORTANTE: Agrega nota legal: "Estimación Clase 5 (-50%/+100%). Valores referenciales sujetos a inflación local."
            """

        prompt = f"""
        Rol: Inspector Senior {datos_ins['modulo']} en VENEZUELA. Norma: {datos_ins['norma']}.
        Contexto Técnico: {datos_tec}
        Tarea: Auditoría visual basada en {len(lista_imagenes_pil)} IMÁGENES.
        Genera REPORTE TÉCNICO ESTRUCTURADO:
        1. HALLAZGOS VISUALES (Severidad Alta/Media/Baja).
        2. CUMPLIMIENTO {datos_ins['norma']} (Indicar artículos específicos).
        3. CAUSA RAÍZ (Considerar ambiente tropical/costero si aplica).
        4. RECOMENDACIÓN TÉCNICA (Paso a paso).
        {instruccion_costos}
        Tono: Profesional, directo, Gerencial.
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
        pdf.cell(0, 6, f"Proyecto: {datos['proyecto']} | Norma: {datos['norma']}", 0, 1, 'C')
        pdf.cell(0, 6, f"Inspector: {datos['usuario']} | Fecha: {datetime.datetime.now().strftime('%d/%m/%Y')}", 0, 1, 'C')
        pdf.ln(10)
        
        pdf.set_fill_color(50, 50, 50) 
        pdf.set_text_color(255, 255, 255) 
        pdf.cell(0, 8, " RESULTADOS DE LA INSPECCIÓN", 1, 1, 'L', 1)
        pdf.set_text_color(0, 0, 0) 
        pdf.ln(5)
        
        pdf.set_font('Arial', '', 11)
        # Limpieza de caracteres para evitar errores en PDF
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
