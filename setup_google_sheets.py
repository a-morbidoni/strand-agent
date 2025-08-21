"""
Configuración de Google Sheets para el procesador de transferencias bancarias.

Este script te ayuda a configurar las credenciales y la hoja de cálculo.
"""

import gspread
from google.oauth2.service_account import Credentials
import json
from enum import Enum

class CSVColumns(Enum):
    FECHA_PROCESAMIENTO = "fecha_procesamiento"
    FECHA_TRANSFERENCIA = "fecha"
    REMITENTE = "remitente"
    RECEPTOR = "receptor"
    TRANSACTION_TYPE = "transaction_type"
    TOTAL = "total"
    ID_TRANSACCION = "id_transaccion"
    CUENTA_ORIGEN = "cuenta_origen"
    ARCHIVO_IMAGEN = "archivo_imagen"

class CSVColumnsNames(Enum):
    FECHA_PROCESAMIENTO = "Fecha Procesamiento"
    FECHA_TRANSFERENCIA = "Fecha Transferencia"
    REMITENTE = "Remitente"
    RECEPTOR = "Receptor"
    TRANSACTION_TYPE = "Tipo de Transaccion"
    TOTAL = "Total"
    ID_TRANSACCION = "Id Transaccion"
    CUENTA_ORIGEN = "Cuenta Origen"
    ARCHIVO_IMAGEN = "Archivo Imagen"

def setup_google_sheets():
    print("Configurando Google Sheets...")
    # Verificar si existe el archivo de credenciales
    try:
        with open("credentials.json", "r") as f:
            creds_data = json.load(f)
            print(f"\n✅ Credenciales encontradas para: {creds_data.get('client_email', 'N/A')}")
            
        # Probar conexión
        scope = ['https://spreadsheets.google.com/feeds',
                 'https://www.googleapis.com/auth/drive']
        
        creds = Credentials.from_service_account_file("credentials.json", scopes=scope)
        client = gspread.authorize(creds)
        
        print("✅ Conexión a Google Sheets exitosa!")
        
        # Solicitar ID de la hoja para prueba
        sheet_id = input("\n🔍 Ingresa el ID de tu Google Sheet para probar (opcional): ")
        if sheet_id.strip():
            try:
                sheet = client.open_by_key(sheet_id.strip()).sheet1
                print(f"✅ Conexión a la hoja exitosa! Nombre: {sheet.title}")
                
                # Verificar/crear encabezados
                headers = sheet.row_values(1)
                expected_headers = ["Fecha Procesamiento", "Fecha Transferencia", "Total", "Receptor"]
                
                if not headers or headers != expected_headers:
                    print("⚠️  Configurando encabezados...")
                    sheet.clear()
                    sheet.append_row(expected_headers)
                    print("✅ Encabezados configurados correctamente!")
                else:
                    print("✅ Encabezados ya están configurados!")
                    
            except Exception as e:
                print(f"❌ Error accediendo a la hoja: {e}")
        
    except FileNotFoundError:
        print("\n❌ Archivo 'credentials.json' no encontrado.")
        print("📥 Descarga las credenciales de Google Cloud Console y ponlas aquí.")
        
    except Exception as e:
        print(f"\n❌ Error con las credenciales: {e}")

def test_transfer_processing():
    """
    Prueba el procesamiento de transferencias con datos de ejemplo.
    """
    print("\n🧪 MODO DE PRUEBA")
    print("=" * 30)
    
    try:
        from invoices import procesar_transferencia
        
        # Datos de prueba
        print("📊 Procesando transferencia de prueba...")
        
        sheet_id = input("Ingresa el ID de tu Google Sheet: ")
        if sheet_id.strip():
            # Simular procesamiento (sin imagen real)
            print("🔄 Procesando...")
            
            # Aquí podrías llamar a la función real si tienes una imagen
            # procesar_transferencia("imagen_prueba.jpg", sheet_id.strip())
            
            print("ℹ️  Para probar con una imagen real:")
            print("   procesar_transferencia('ruta_imagen.jpg', 'tu_sheet_id')")
        
    except ImportError as e:
        print(f"❌ Error importando módulo: {e}")
        print("🔧 Asegúrate de que invoices.py esté configurado correctamente.")

if __name__ == "__main__":
    setup_google_sheets()
    
    test_mode = input("\n¿Quieres probar el procesamiento? (s/n): ")
    if test_mode.lower() == 's':
        test_transfer_processing()
