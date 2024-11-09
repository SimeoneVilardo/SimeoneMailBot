import asyncio
import os
from email.parser import BytesParser
from email.policy import default
from io import BytesIO

from aiosmtpd.controller import Controller
from telegram import Update
from telegram.constants import ParseMode
from telegram.ext import ContextTypes, Application, CommandHandler

TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID")
SMTP_SERVER = os.environ.get("SMTP_SERVER")
SMTP_PORT = int(os.environ.get("SMTP_PORT"))
SMTP_USERNAME = os.environ.get("SMTP_USERNAME")
SMTP_PASSWORD = os.environ.get("SMTP_PASSWORD")
DOMAINS = os.environ.get("DOMAINS", "").split(",")


class MessageHandlerSMTP:
    def __init__(self, bot):
        self.bot = bot

    async def handle_DATA(self, server, session, envelope):
        rcpt_tos = envelope.rcpt_tos
        if all(not s.endswith(d) for s in rcpt_tos for d in DOMAINS):
            return "550 5.7.1 Access denied, message rejected"
        mail_from = envelope.mail_from
        mail = BytesParser(policy=default).parsebytes(envelope.content)
        subject = mail["subject"] if mail["subject"] else "(No Subject)"

        basic_info = (
            f"Email from: {mail_from}\n"
            f"Recipients: {', '.join(rcpt_tos)}\n"
            f"Subject: {subject}"
        )
        print(basic_info)

        email_body = mail.get_body(preferencelist=("html", "plain")).get_content()
        email_content_io = BytesIO()
        email_content_io.write(email_body.encode("utf-8"))
        email_content_io.seek(0)

        await self.bot.send_message(chat_id=CHAT_ID, text=basic_info, parse_mode=ParseMode.MARKDOWN)
        await self.bot.send_document(chat_id=CHAT_ID, document=email_content_io, filename="content.html")

        return "250 Message accepted for delivery"


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text("Hello! I am a bot that will forward emails to this chat.")


async def main():
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))

    handler_smtp = MessageHandlerSMTP(app.bot)
    controller = Controller(handler_smtp, hostname="0.0.0.0", port=1025)

    controller.start()
    await app.run_polling()


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    print(loop)
    asyncio.run(main())
