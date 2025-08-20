import gspread
from google.oauth2.service_account import Credentials
import json
import os
from datetime import datetime
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()


def leer_json_invoices(archivo_json="docs/invoices/invoices.json"):
    """
    Lee el archivo JSON con los datos de invoices.
    
    Args:
        archivo_json: Ruta al archivo JSON
        
    Returns:
        Lista de invoices o None si hay error
    """
    try:
        if not os.path.exists(archivo_json):
            print(f"Archivo {archivo_json} no encontrado")
            return None
            
        with open(archivo_json, 'r', encoding='utf-8') as f:
            invoices = json.load(f)
            
        print(f"Archivo JSON leido exitosamente: {len(invoices)} registros encontrados")
        return invoices
        
    except Exception as e:
        print(f"Error leyendo archivo JSON: {e}")
        return None

def subir_json_a_sheets(sheet_id: str, credentials_path: str = "credentials.json", archivo_json="docs/invoices/invoices.json"):
    """
    Lee el archivo JSON y sube todos los datos a Google Sheets.
    
    Args:
        sheet_id: ID de la Google Sheet
        credentials_path: Ruta al archivo de credenciales
        archivo_json: Ruta al archivo JSON
    """
    try:
        print("Leyendo archivo JSON...")
        invoices = leer_json_invoices(archivo_json)
        
        if not invoices:
            print("No hay datos para subir")
            return False
            
        print("Conectando a Google Sheets...")
        
        # Configurar credenciales
        scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
        creds = Credentials.from_service_account_file(credentials_path, scopes=scope)
        client = gspread.authorize(creds)
        
        # Abrir la hoja
        sheet = client.open_by_key(sheet_id).sheet1
        print(f"Hoja abierta: {sheet.title}")
        
        # Limpiar hoja existente (opcional - comentar si quieres mantener datos)
        # sheet.clear()
        
        # Agregar encabezados si la hoja está vacía
        if not sheet.get_all_values():
            headers = ["Fecha Procesamiento", "Fecha Transferencia", "Total", "Receptor", "Archivo Imagen"]
            sheet.append_row(headers)
            print("Encabezados agregados")
        
        # Subir cada invoice
        contador = 0
        for invoice in invoices:
            row_data = [
                invoice.get("fecha_procesamiento", ""),
                invoice.get("fecha", "NO_ENCONTRADO"),
                invoice.get("total", "NO_ENCONTRADO"),
                invoice.get("receptor", "NO_ENCONTRADO"),
                invoice.get("archivo_imagen", "")
            ]
            
            sheet.append_row(row_data)
            contador += 1
            print(f"Registro {contador} subido: {invoice.get('total')} - {invoice.get('receptor')}")
        
        print(f"Proceso completado: {contador} registros subidos exitosamente")
        return True
        
    except Exception as e:
        print(f"Error subiendo a Google Sheets: {e}")
        return False

# Ejecutar la sincronización
if __name__ == "__main__":
    print("SINCRONIZADOR JSON A GOOGLE SHEETS")
    print("=" * 40)
    print()
    
    # Configuración desde variables de entorno
    sheet_id = os.getenv("GOOGLE_SHEET_ID")
    credentials_path = os.getenv("GOOGLE_CREDENTIALS_PATH", "credentials.json")
    
    if not sheet_id:
        print("❌ Error: GOOGLE_SHEET_ID no encontrada en variables de entorno")
        print("📝 Configura el archivo .env con:")
        print("   GOOGLE_SHEET_ID=tu_id_de_google_sheet")
        exit(1)
    
    # Subir datos del JSON al Sheet
    if subir_json_a_sheets(sheet_id, credentials_path):
        print("Sincronizacion completada exitosamente")
    else:
        print("Error en la sincronizacion")
