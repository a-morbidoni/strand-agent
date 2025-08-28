"""
ORQUESTADOR SIMPLE PARA FLUJO DE TELEGRAM
=========================================

Flujo:
1. Telegram Bot recibe imagen -> Guarda en docs/invoices/
2. Orchestrator recibe ruta de imagen
3. Llama a invoice_reader.py para procesar imagen y guardar en JSON
4. Llama a invoices.py para subir JSON a Google Sheets

Uso:
    python orchestrator.py --imagen RUTA_IMAGEN
"""

import sys
import os
import importlib.util
from datetime import datetime
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

# Configurar encoding para evitar problemas en Windows
if os.name == 'nt':  # Windows
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')

def cargar_invoice_reader():
    """Carga el módulo invoice_reader.py"""
    try:
        spec = importlib.util.spec_from_file_location("invoice_reader", "invoice_reader.py")
        invoice_reader = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(invoice_reader)
        return invoice_reader
    except Exception as e:
        print(f"Error cargando invoice_reader.py: {e}")
        return None

def cargar_invoices():
    """Carga el módulo invoices.py"""
    try:
        from invoices import append_ultima_invoice_a_sheets
        return append_ultima_invoice_a_sheets
    except Exception as e:
        print(f"Error cargando invoices.py: {e}")
        return None

def procesar_imagen_telegram(imagen_path):
    """
    Procesar imagen recibida.
    
    Args:
        imagen_path: Ruta completa a la imagen
        
    Returns:
        bool: True si todo el proceso fue exitoso
    """
    print("PROCESADOR DE IMAGEN")
    print("=" * 50)
    print(f"Imagen: {imagen_path}")
    print(f"Inicio: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
    print()
    
    # Verificar que la imagen existe
    if not os.path.exists(imagen_path):
        print(f"Error: Imagen no encontrada: {imagen_path}")
        return False
    
    # PASO 1: Cargar módulos
    print("PASO 1: Cargando módulos...")
    print("-" * 30)
    
    invoice_reader = cargar_invoice_reader()
    if not invoice_reader:
        return False
    
    subir_json_a_sheets = cargar_invoices()
    if not subir_json_a_sheets:
        return False
    
    print("OK - Módulos cargados exitosamente")
    
    # PASO 2: Procesar imagen y guardar en JSON
    print("\nPASO 2: Procesando imagen...")
    print("-" * 30)
    
    try:
        # Leer la imagen y extraer datos
        resultado = invoice_reader.leer_recibo(imagen_path)
        
        if not resultado:
            print("Error: No se pudieron extraer datos de la imagen")
            return False
        
        # Guardar en JSON
        if not invoice_reader.guardar_en_json(resultado):
            print("Error: No se pudo guardar en JSON")
            return False
            
        print("OK - Imagen procesada y guardada en JSON")
        
    except Exception as e:
        print(f"Error en procesamiento: {e}")
        return False
    
    # PASO 3: Subir a Google Sheets (solo última entrada)
    print("\nPASO 3: Subiendo a Google Sheets...")
    print("-" * 30)
    
    try:
        # Configuración de Google Sheets desde variables de entorno
        sheet_id = os.getenv("GOOGLE_SHEET_ID")
        credentials_path = os.getenv("GOOGLE_CREDENTIALS_PATH", "credentials.json")
        
        if not sheet_id:
            print("Error: GOOGLE_SHEET_ID no encontrada en variables de entorno")
            print("Configura el archivo .env con GOOGLE_SHEET_ID=tu_id_aqui")
            return False
        
        if not subir_json_a_sheets(sheet_id, credentials_path):
            print("Error: No se pudo subir a Google Sheets")
            return False
            
        print("OK - Datos subidos a Google Sheets")
        
    except Exception as e:
        print(f"Error en Google Sheets: {e}")
        return False
    
    # RESUMEN FINAL
    print("\n" + "=" * 50)
    print("PROCESO COMPLETADO EXITOSAMENTE")
    print("=" * 50)
    print(f"Imagen procesada: {os.path.basename(imagen_path)}")
    print(f"Total: {resultado.get('total', 'N/A')}")
    print(f"Fecha: {resultado.get('fecha', 'N/A')}")
    print(f"Receptor: {resultado.get('receptor', 'N/A')}")
    print(f"JSON actualizado: docs/invoices/invoices.json")
    print(f"Google Sheets sincronizado")
    print(f"Finalizacion: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
    
    return True

def main():
    """Función principal del orquestador"""
    
    if len(sys.argv) != 3 or sys.argv[1] != "--imagen":
        print("Uso incorrecto")
        print()
        print("Uso correcto:")
        print("  python orchestrator.py --imagen RUTA_IMAGEN")
        print()
        print("Ejemplo:")
        print("  python orchestrator.py --imagen docs/invoices/recibo_telegram_20250819_215344.jpg")
        sys.exit(1)
    
    imagen_path = sys.argv[2]
    
    if procesar_imagen_telegram(imagen_path):
        print("\nEXITO: Imagen procesada y sincronizada")
        sys.exit(0)
    else:
        print("\nERROR: Fallo el procesamiento")
        sys.exit(1)

if __name__ == "__main__":
    main()
