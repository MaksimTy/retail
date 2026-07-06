"""
Telegram message handlers.
"""

from telegram import Update
from telegram.ext import ContextTypes, MessageHandler, filters
from retail.agent.core import RetailAgent

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle incoming messages."""
    question = update.message.text
    agent = RetailAgent()
    
    try:
        answer = agent.ask(question)
        await update.message.reply_text(answer)
    except Exception as e:
        await update.message.reply_text(f"Sorry, I encountered an error: {str(e)}")