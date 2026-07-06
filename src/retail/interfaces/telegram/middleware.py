"""
Telegram middleware for logging and rate limiting.
"""

import logging
from telegram import Update
from telegram.ext import ContextTypes

logger = logging.getLogger(__name__)

async def log_middleware(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Log incoming updates."""
    user = update.effective_user
    if user:
        logger.info(f"Message from {user.id} (@{user.username}): {update.message.text}")