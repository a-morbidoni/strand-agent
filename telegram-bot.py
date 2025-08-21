"""
Bot de Telegram para procesar recibos automáticamente.

Este archivo contiene toda la lógica del bot de Telegram que escucha mensajes,
procesa imágenes de recibos y guarda los datos extraídos.
"""

import os
import asyncio
import logging
from datetime import datetime
from telegram import Update
from telegram.ext import Application, MessageHandler, filters, ContextTypes
import subprocess
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

# Configurar logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO,
    handlers=[
        logging.FileHandler('telegram_bot.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class TelegramBot:
    """
    Bot de Telegram para recibir imágenes de recibos y procesarlas automáticamente.
    """
    
    def __init__(self, token: str):
        self.token = token
        self.app = Application.builder().token(token).build()
        
        # Configurar handlers
        self.app.add_handler(MessageHandler(filters.PHOTO, self.handle_photo))
        self.app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_text))
        self.app.add_handler(MessageHandler(filters.Document.ALL, self.handle_document))
        
    async def handle_photo(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """
        Maneja las fotos recibidas en el chat.
        """
        user = update.effective_user
        chat_id = update.effective_chat.id
        
        logger.info(f"Foto recibida de {user.username} ({user.id}) en chat {chat_id}")
        
        try:
            # Obtener la foto de mayor resolución
            photo = update.message.photo[-1]
            
            # Descargar la foto
            file = await context.bot.get_file(photo.file_id)
            
            # Crear nombre único para el archivo
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"recibo_telegram_{timestamp}_{user.id}.jpg"
            file_path = os.path.join("docs/invoices", filename)
            
            # Crear directorio si no existe
            os.makedirs("docs/invoices", exist_ok=True)
            
            # Descargar archivo
            await file.download_to_drive(file_path)
            
            # Enviar mensaje de confirmación
            await update.message.reply_text("📸 Imagen recibida! Procesando recibo...")
            
            logger.info(f"Imagen guardada en: {file_path}")
            
            # Llamar al orchestrator para procesar la imagen
            await update.message.reply_text("🔄 Leyendo datos del recibo...")
            
            resultado = await self.llamar_orchestrator_async(file_path)
            
            if resultado:
                await update.message.reply_text(
                    f"✅ Imagen procesada exitosamente!\n\n"
                    f"📊 Los datos han sido agregados a Google Sheets automáticamente."
                )
            else:
                await update.message.reply_text(
                    "❌ Error procesando el recibo. "
                    "Revisa los logs para más detalles."
                )
                
        except Exception as e:
            logger.error(f"Error procesando foto: {e}")
            await update.message.reply_text(
                f"❌ Error procesando la imagen: {str(e)}"
            )
    
    async def handle_text(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """
        Maneja los mensajes de texto recibidos.
        """
        user = update.effective_user
        chat_id = update.effective_chat.id
        text = update.message.text
        
        logger.info(f"Mensaje de texto de {user.username} ({user.id}): {text}")
        
        # Respuestas automáticas
        if text.lower() in ['hola', 'hi', 'hello']:
            await update.message.reply_text(
                "¡Hola! 👋\n\n"
                "Soy tu asistente de recibos. Envíame una foto de tu recibo "
                "y yo extraeré automáticamente:\n"
                "💰 Total\n"
                "📅 Fecha\n"
                "👤 Receptor\n\n"
                "💳 Cuenta Origen\n"
                "🔑 Id Transaccion\n"
                "¡Pruébalo enviando una imagen!"
            )
        elif text.lower() in ['ayuda', 'help']:
            await update.message.reply_text(
                "🤖 **Comandos disponibles:**\n\n"
                "📸 Envía una **foto** de tu recibo\n"
                "📄 Envía un **documento** (imagen)\n"
                "💬 Escribe 'hola' para saludar\n"
                "❓ Escribe 'ayuda' para ver este mensaje\n"
                "📊 Escribe 'estado' para ver estadísticas\n\n"
                "¡Todo se procesa automáticamente!"
            )
        elif text.lower() == 'estado':
            stats = await self.get_stats()
            await update.message.reply_text(stats)
        else:
            await update.message.reply_text(
                "👋 ¡Hola! Para procesar un recibo, envíame una foto del mismo.\n"
                "Escribe 'ayuda' si necesitas más información."
            )
    
    async def handle_document(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """
        Maneja documentos/archivos recibidos.
        """
        user = update.effective_user
        document = update.message.document
        
        logger.info(f"Documento recibido de {user.username}: {document.file_name}")
        
        # Verificar si es una imagen
        if document.mime_type and document.mime_type.startswith('image/'):
            await self.handle_photo(update, context)
        else:
            await update.message.reply_text(
                "📄 Solo puedo procesar imágenes de recibos.\n"
                "Por favor envía una foto o imagen."
            )
    
    async def llamar_orchestrator_async(self, file_path: str):
        """
        Llama al orchestrator para procesar la imagen de forma asíncrona.
        """
        try:
            # Ejecutar orchestrator en un hilo separado
            loop = asyncio.get_event_loop()
            resultado = await loop.run_in_executor(
                None,
                self._ejecutar_orchestrator,
                file_path
            )
            
            return resultado
                
        except Exception as e:
            logger.error(f"Error llamando al orchestrator: {e}")
            return False
    
    def _ejecutar_orchestrator(self, file_path: str):
        """
        Ejecuta el orchestrator de forma síncrona.
        """
        try:
            # Llamar al orchestrator con la imagen específica usando el Python del entorno virtual
            venv_python = os.path.join(os.getcwd(), "venv", "Scripts", "python.exe")
            result = subprocess.run([
                venv_python, "orchestrator.py", "--imagen", file_path
            ], capture_output=True, text=True, timeout=120, encoding='utf-8')
            
            if result.returncode == 0:
                logger.info(f"Orchestrator ejecutado exitosamente para: {file_path}")
                logger.info(f"Output: {result.stdout}")
                return True
            else:
                logger.error(f"Error en orchestrator - Return code: {result.returncode}")
                logger.error(f"Stderr: {result.stderr}")
                logger.error(f"Stdout: {result.stdout}")
                return False
                
        except subprocess.TimeoutExpired:
            logger.error("Timeout ejecutando orchestrator")
            return False
        except Exception as e:
            logger.error(f"Error ejecutando orchestrator: {e}")
            return False
    
    async def get_stats(self):
        """
        Obtiene estadísticas del sistema.
        """
        try:
            # Contar imágenes en la carpeta
            import glob
            extensiones = ['*.jpg', '*.jpeg', '*.png', '*.bmp', '*.tiff', '*.webp']
            imagenes = []
            for ext in extensiones:
                imagenes.extend(glob.glob(os.path.join("docs/invoices", ext)))
            
            # Leer JSON para obtener registros
            if os.path.exists("docs/invoices/invoices.json"):
                import json
                with open("docs/invoices/invoices.json", 'r', encoding='utf-8') as f:
                    invoices_data = json.load(f)
                total_registros = len(invoices_data) if invoices_data else 0
            else:
                total_registros = 0
            
            stats = (
                "📊 **Estadísticas del Sistema**\n\n"
                f"🖼️ Imágenes en carpeta: {len(imagenes)}\n"
                f"📄 Registros en JSON: {total_registros}\n"
                f"🕒 Última actualización: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}"
            )
            
            return stats
            
        except Exception as e:
            return f"❌ Error obteniendo estadísticas: {e}"
    
    async def start_bot(self):
        """
        Inicia el bot de Telegram.
        """
        logger.info("Iniciando bot de Telegram...")
        await self.app.initialize()
        await self.app.start()
        await self.app.updater.start_polling()
        
        logger.info("Bot de Telegram iniciado. Escuchando mensajes...")
        
        try:
            # Mantener el bot ejecutándose
            await asyncio.Future()  # Run forever
        except KeyboardInterrupt:
            logger.info("Deteniendo bot...")
        finally:
            await self.app.updater.stop()
            await self.app.stop()
            await self.app.shutdown()

async def run_telegram_bot(token: str):
    """
    Función principal para ejecutar el bot de Telegram.
    
    Args:
        token: Token del bot de Telegram
    """
    bot = TelegramBot(token)
    
    print("🤖 INICIANDO BOT DE TELEGRAM")
    print("=" * 40)
    print("📱 El bot está escuchando mensajes...")
    print("📸 Envía fotos de recibos para procesarlos automáticamente")
    print("💬 Escribe 'ayuda' para ver comandos disponibles")
    print("🛑 Presiona Ctrl+C para detener")
    print()
    
    await bot.start_bot()

# Configuración del bot - Token desde variable de entorno
BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

if __name__ == "__main__":
    import sys
    
    # Priorizar token desde línea de comandos, sino usar el del archivo
    if len(sys.argv) >= 2:
        token = sys.argv[1]
        print(f"🔑 Usando token desde línea de comandos")
    else:
        token = BOT_TOKEN
        if not token:
            print("❌ Error: Token no configurado")
            print()
            print("Opciones para configurar el token:")
            print("1. Crea un archivo .env con TELEGRAM_BOT_TOKEN=tu_token")
            print("2. Ejecuta: python telegram-bot.py TU_BOT_TOKEN")
            print()
            print("Para obtener un token:")
            print("1. Busca @BotFather en Telegram")
            print("2. Envía /newbot")
            print("3. Sigue las instrucciones")
            print("4. Copia el token que te proporciona")
            print("5. Agrégalo al archivo .env")
            sys.exit(1)
        else:
            print(f"🔑 Usando token desde variable de entorno")
    
    try:
        asyncio.run(run_telegram_bot(token))
    except KeyboardInterrupt:
        print("\n🛑 Bot de Telegram detenido")
        sys.exit(0)
