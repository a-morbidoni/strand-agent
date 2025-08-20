# 🏦 Procesador de Transferencias Bancarias

Este agente de IA puede analizar imágenes de transferencias bancarias y cargar automáticamente los datos en Google Sheets.

## 🚀 Características

- **Análisis de imágenes**: Usa GPT-4 Vision para leer transferencias bancarias
- **Extracción de datos**: Extrae automáticamente total, fecha y receptor
- **Integración con Google Sheets**: Carga los datos directamente en tu hoja de cálculo
- **Fácil de usar**: Una sola función para procesar transferencias completas

## 📦 Instalación

1. **Instalar dependencias:**
```bash
pip install -r requirements.txt
```

2. **Configurar Google Sheets:**
```bash
python setup_google_sheets.py
```

## 🔧 Configuración

### 1. Google Sheets API

1. Ve a [Google Cloud Console](https://console.cloud.google.com/)
2. Crea un nuevo proyecto
3. Habilita Google Sheets API y Google Drive API
4. Crea credenciales de cuenta de servicio
5. Descarga el archivo JSON como `credentials.json`

### 2. Preparar tu Google Sheet

Tu hoja debe tener estos encabezados en la primera fila:
- **A1**: Fecha Procesamiento
- **B1**: Fecha Transferencia  
- **C1**: Total
- **D1**: Receptor

### 3. Obtener ID de la Google Sheet

El ID está en la URL: `https://docs.google.com/spreadsheets/d/[ESTE_ES_EL_ID]/edit`

## 🎯 Uso

### Procesamiento Simple

```python
from invoices import procesar_transferencia

# Procesar una transferencia
procesar_transferencia(
    ruta_imagen="mi_transferencia.jpg",
    sheet_id="1ABC123def456GHI789jkl",
    credentials_path="credentials.json"
)
```

### Uso Interactivo

```python
# Ejecutar el archivo principal
python invoices.py
```

### Funciones Disponibles

#### `procesar_transferencia(ruta_imagen, sheet_id, credentials_path)`
Función principal que procesa una transferencia completa.

**Parámetros:**
- `ruta_imagen`: Ruta a la imagen de la transferencia
- `sheet_id`: ID de tu Google Sheet
- `credentials_path`: Ruta al archivo de credenciales (por defecto: "credentials.json")

## 📸 Formatos de Imagen Soportados

- JPG/JPEG
- PNG  
- BMP
- TIFF

## 🔍 Datos Extraídos

El agente extrae automáticamente:

1. **Total/Monto**: El valor de la transferencia (sin símbolos de moneda)
2. **Fecha**: Fecha de la transferencia en formato DD/MM/AAAA
3. **Receptor**: Nombre de la persona o entidad que recibió el dinero

## 📊 Estructura de la Google Sheet

Los datos se guardan con esta estructura:

| Fecha Procesamiento | Fecha Transferencia | Total | Receptor |
|-------------------|-------------------|-------|----------|
| 15/12/2024 10:30:25 | 14/12/2024 | 1500.00 | Juan Pérez |

## 🛠️ Ejemplo Completo

```python
from invoices import procesar_transferencia

# 1. Tener tu imagen lista
imagen = "transferencia_banco.jpg"

# 2. Tu Google Sheet configurada
sheet_id = "1ABC123def456GHI789jkl"

# 3. Procesar
resultado = procesar_transferencia(imagen, sheet_id)
print(resultado)
```

## 🐛 Resolución de Problemas

### Error de credenciales
```
❌ Error: No se pueden cargar las credenciales
```
**Solución**: Verifica que `credentials.json` esté en el directorio correcto.

### Error de permisos de Google Sheet
```
❌ Error: No se puede acceder a la hoja
```
**Solución**: Comparte tu Google Sheet con el email de la cuenta de servicio.

### Imagen no encontrada
```
❌ Error: No se puede abrir la imagen
```
**Solución**: Verifica que la ruta de la imagen sea correcta.

## 📝 Notas

- El agente usa GPT-4 Vision, que requiere una API key de OpenAI válida
- La precisión depende de la calidad y claridad de la imagen
- Se recomienda usar imágenes con buena resolución y contraste
- El agente funciona mejor con capturas de pantalla completas de transferencias

## 🔒 Seguridad

- Las credenciales de Google se almacenan localmente
- Las imágenes se procesan de forma segura
- No se almacenan datos sensibles en el código

## 📞 Soporte

Si tienes problemas:
1. Ejecuta `python setup_google_sheets.py` para verificar la configuración
2. Revisa que todos los permisos estén correctos
3. Verifica que la imagen sea clara y legible
