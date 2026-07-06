"""
Telegram bot interface.
"""

import logging
from telegram import Update, Bot
from telegram.ext import Application, CommandHandler, MessageHandler, ContextTypes, filters
from retail.agent.core import RetailAgent
from retail.config.settings import settings

logger = logging.getLogger(__name__)

class TelegramBot:
    """Telegram bot for the retail AI agent."""

    def __init__(self):
        if not settings.TELEGRAM_BOT_TOKEN:
            raise ValueError("TELEGRAM_BOT_TOKEN is not set in environment variables")
        
        self.token = settings.TELEGRAM_BOT_TOKEN
        self.agent = RetailAgent()

    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle /start command."""
        await update.message.reply_text(
            "Welcome to the Retail AI Agent! Ask me any question about the retail data.\n"
            "Examples:\n"
            "- What is the total revenue?\n"
            "- How many orders are there?\n"
            "- Top 5 products by revenue?"
        )

    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle /help command."""
        await update.message.reply_text(
            "Available commands:\n"
            "/start - Start the bot\n"
            "/help - Show this help message\n\n"
            "Just send me a question about the retail data!"
        )

    async def handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle incoming messages."""
        question = update.message.text
        
        try:
            answer = self.agent.ask(question)
            await update.message.reply_text(answer)
        except Exception as e:
            logger.error(f"Error processing question: {e}")
            await update.message.reply_text(f"Sorry, I encountered an error: {str(e)}")

    def run(self) -> None:
        """Run the bot."""
        application = Application.builder().token(self.token).build()

        # Add handlers
        application.add_handler(CommandHandler("start", self.start))
        application.add_handler(CommandHandler("help", self.help_command))
        application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_message))

        # Run the bot
        logger.info("Starting Telegram bot...")
        application.run_polling()