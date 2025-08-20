"""
Configuración de Google Sheets para el procesador de transferencias bancarias.

Este script te ayuda a configurar las credenciales y la hoja de cálculo.
"""

import gspread
from google.oauth2.service_account import Credentials
import json

def setup_google_sheets():
    """
    Guía paso a paso para configurar Google Sheets.
    """
    
    print("🔧 Configuración de Google Sheets")
    print("=" * 50)
    
    print("\n📋 PASOS PARA CONFIGURAR:")
    print("1. Ve a la Google Cloud Console: https://console.cloud.google.com/")
    print("2. Crea un nuevo proyecto o selecciona uno existente")
    print("3. Habilita la Google Sheets API y Google Drive API")
    print("4. Ve a 'Credenciales' > 'Crear credenciales' > 'Cuenta de servicio'")
    print("5. Descarga el archivo JSON de credenciales")
    print("6. Renombra el archivo a 'credentials.json' y ponlo en este directorio")
    print("7. Crea una nueva Google Sheet y obtén su ID de la URL")
    
    print("\n📊 CONFIGURAR LA HOJA DE CÁLCULO:")
    print("Tu Google Sheet debe tener estas columnas en la primera fila:")
    print("A1: Fecha Procesamiento")
    print("B1: Fecha Transferencia") 
    print("C1: Total")
    print("D1: Receptor")
    
    print("\n🔑 ID DE LA HOJA:")
    print("El ID está en la URL de tu Google Sheet:")
    print("https://docs.google.com/spreadsheets/d/[ESTE_ES_EL_ID]/edit")
    
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
