import base64
import json
import openai
import os
from datetime import datetime
from dotenv import load_dotenv
import re
from decimal import Decimal, InvalidOperation, ROUND_HALF_UP
from string import Template

from setup_google_sheets import CSVColumns, CSVColumnsNames

# Cargar variables de entorno
load_dotenv()

def leer_recibo(imagen_path: str):
    """
    Lee una imagen de recibo/transferencia y extrae los datos principales.
    
    Args:
        imagen_path: Ruta a la imagen del recibo
    """
    print("Leyendo recibo...")
    print(f"Imagen: {imagen_path}")
    print("-" * 50)
    
    try:
        # Leer y codificar la imagen
        with open(imagen_path, "rb") as image_file:
            image_data = base64.b64encode(image_file.read()).decode('utf-8')
        
        # Configurar cliente OpenAI con variable de entorno
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY no encontrada en variables de entorno. Configura el archivo .env")
        
        client = openai.OpenAI(api_key=api_key)
        
        # Analizar imagen con GPT-4 Vision
        schema_example = {
            CSVColumns.TOTAL.value: "monto numérico con decimales en formato 123.45",
            CSVColumns.FECHA_TRANSFERENCIA.value: "DD/MM/AAAA",
            CSVColumns.RECEPTOR.value: "nombre del destinatario o comercio, dejar en blanco si no aparece",
            CSVColumns.CUENTA_ORIGEN.value: "institución o medio de pago (ej: Lemon, Mercado Pago, Santander, Ualá, etc.)",
            CSVColumns.TRANSACTION_TYPE.value: "transferencia | débito | crédito | otro (si no está claro)",
            CSVColumns.ID_TRANSACCION.value: "código o identificador de la operación, dejar en blanco si no se encuentra",
            CSVColumns.REMITENTE.value: "nombre del remitente, dejar en blanco si no aparece",
        }

        text = f"""
        Extrae de la imagen los siguientes campos y responde ÚNICAMENTE en formato JSON:
        {json.dumps(schema_example, ensure_ascii=False, indent=4)}
        Reglas:
            - El campo "{CSVColumns.TRANSACTION_TYPE.value}" debe ser "débito" o "crédito" si explícitamente lo indica el ticket; si no aparece, asumir "transferencia".
            - No incluyas texto extra ni explicaciones fuera del JSON.
            - Si algún dato no se puede identificar con certeza, deja el campo en blanco.
            - Respeta el formato exacto de claves y comillas del JSON.
        """

        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[{
                "role": "user", 
                "content": [
                    {"type": "text", "text": text},
                    {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{image_data}"}}
                ]
            }],
            max_tokens=300,
            temperature=0.1
        )
        
        # Limpiar respuesta
        result = response.choices[0].message.content.strip()
        if result.startswith("```"):
            result = result.split("```")[1].replace("json", "").strip()
        
        # Parsear JSON
        datos = json.loads(result)
        
        # Normalizar monto a formato estándar 1,234.56
        def _normalize_amount_string(amount_input) -> str:
            s = str(amount_input).strip()
            if not s:
                return "0.00"
            # Quitar símbolos de moneda y espacios, dejar solo dígitos, punto, coma y guión
            s = re.sub(r'[^\d,\.\-]', '', s)
            negative = False
            if '-' in s:
                # Si empieza con -, considerar negativo
                if s.startswith('-'):
                    negative = True
                s = s.replace('-', '')
            has_dot = '.' in s
            has_comma = ',' in s
            decimal_sep = None
            thousands_sep = None
            if has_dot and has_comma:
                # El separador decimal suele ser el último símbolo separador
                last_dot = s.rfind('.')
                last_comma = s.rfind(',')
                if last_dot > last_comma:
                    decimal_sep = '.'
                    thousands_sep = ','
                else:
                    decimal_sep = ','
                    thousands_sep = '.'
            elif has_dot:
                last_dot = s.rfind('.')
                digits_after = len(s) - last_dot - 1
                if digits_after in (1, 2):
                    decimal_sep = '.'
                else:
                    thousands_sep = '.'
            elif has_comma:
                last_comma = s.rfind(',')
                digits_after = len(s) - last_comma - 1
                if digits_after in (1, 2):
                    decimal_sep = ','
                else:
                    thousands_sep = ','
            # Eliminar miles
            s_clean = s.replace(thousands_sep, '') if thousands_sep else s
            # Unificar decimal a punto
            if decimal_sep and decimal_sep != '.':
                s_clean = s_clean.replace(decimal_sep, '.')
            # Si no hay decimales, agregar .00
            if '.' not in s_clean:
                s_clean = s_clean + '.00'
            try:
                value = Decimal(s_clean).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
                if negative:
                    value = -value
            except (InvalidOperation, ValueError):
                return "0.00"
            return f"{value:,.2f}"

        if 'total' in datos:
            datos['total'] = _normalize_amount_string(datos.get('total'))
        
        # Agregar metadatos
        datos["fecha_procesamiento"] = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        datos["archivo_imagen"] = imagen_path
        
        # Mostrar resultados
        print("DATOS EXTRAIDOS:")
        print(f"{CSVColumnsNames.TOTAL.value}: {datos.get(CSVColumns.TOTAL.value, 'NO_ENCONTRADO')}")
        print(f"{CSVColumnsNames.FECHA_TRANSFERENCIA.value}: {datos.get(CSVColumns.FECHA_TRANSFERENCIA.value, 'NO_ENCONTRADO')}")
        print(f"{CSVColumnsNames.RECEPTOR.value}: {datos.get(CSVColumns.RECEPTOR.value, 'NO_ENCONTRADO')}")
        print(f"{CSVColumnsNames.TRANSACTION_TYPE.value}: {datos.get(CSVColumns.TRANSACTION_TYPE.value, 'NO_ENCONTRADO')}")
        print(f"{CSVColumnsNames.ID_TRANSACCION.value}: {datos.get(CSVColumns.ID_TRANSACCION.value, 'NO_ENCONTRADO')}")
        print(f"{CSVColumnsNames.CUENTA_ORIGEN.value}: {datos.get(CSVColumns.CUENTA_ORIGEN.value, 'NO_ENCONTRADO')}")
        
        return datos
        
    except json.JSONDecodeError as e:
        print(f"Error al parsear JSON: {e}")
        print(f"Respuesta original: {result}")
        return None
        
    except Exception as e:
        print(f"Error procesando imagen: {e}")
        return None

def guardar_en_json(datos, archivo_json="docs/invoices/invoices.json"):
    """
    Guarda los datos extraídos en un archivo JSON en la carpeta docs/invoices.
    
    Args:
        datos: Diccionario con los datos extraídos
        archivo_json: Ruta completa al archivo JSON donde guardar
    """
    try:
        # Crear directorio si no existe
        directorio = os.path.dirname(archivo_json)
        if not os.path.exists(directorio):
            os.makedirs(directorio)
        
        # Leer datos existentes si el archivo existe
        if os.path.exists(archivo_json):
            with open(archivo_json, 'r', encoding='utf-8') as f:
                try:
                    invoices = json.load(f)
                    if not isinstance(invoices, list):
                        # Si el archivo no contiene una lista, crear una nueva
                        invoices = []
                except json.JSONDecodeError:
                    # Si el archivo está corrupto, crear una nueva lista
                    print("Archivo JSON corrupto, creando nuevo...")
                    invoices = []
        else:
            invoices = []
        
        # Agregar nuevos datos
        invoices.append(datos)
        
        # Guardar archivo actualizado
        with open(archivo_json, 'w', encoding='utf-8') as f:
            json.dump(invoices, f, indent=2, ensure_ascii=False)
        
        print(f"Datos guardados en {archivo_json}")
        print(f"Total de registros en archivo: {len(invoices)}")
        return True
        
    except Exception as e:
        print(f"Error guardando archivo JSON: {e}")
        return False

def procesar_imagen(ruta_imagen):
    """
    Función de conveniencia para procesar una imagen y guardar automáticamente.
    
    Args:
        ruta_imagen: Ruta a la imagen a procesar
    """
    print(f"Procesando: {ruta_imagen}")
    resultado = leer_recibo(ruta_imagen)
    
    if resultado:
        if guardar_en_json(resultado):
            print("Imagen procesada y guardada exitosamente!")
            return resultado
        else:
            print("Error al guardar datos")
    else:
        print("Error al procesar imagen")
    
    return None

# Ejecutar el lector de recibos
if __name__ == "__main__":
    print("LECTOR DE RECIBOS")
    print("=" * 30)
    print()
    
    # Analizar la imagen de transferencia
    resultado = leer_recibo("docs/invoices/alquiler-septiembre.jpg")
    
    if resultado:
        print("\nAnalisis completado exitosamente!")
        
        # Guardar en JSON en la carpeta docs/invoices
        if guardar_en_json(resultado):
            print("Datos agregados al archivo docs/invoices/invoices.json")
        else:
            print("Error al guardar en archivo JSON")
    else:
        print("\nNo se pudieron extraer los datos del recibo.")
    
    print("\n" + "=" * 30)
    print("Para usar con otra imagen:")
    print("leer_recibo('ruta/a/tu/imagen.jpg')")