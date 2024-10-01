import asyncio
import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.parser import BytesParser
from email.policy import default
from aiosmtpd.controller import Controller
from io import BytesIO
from telegram.constants import ParseMode
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters

# Initialize the Telegram bot with your bot token
TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID")
SMTP_SERVER = os.environ.get("SMTP_SERVER")
SMTP_PORT = int(os.environ.get("SMTP_PORT"))
SMTP_USERNAME = os.environ.get("SMTP_USERNAME")
SMTP_PASSWORD = os.environ.get("SMTP_PASSWORD")

def send_mail(sender, recipient, subject, body_text):
    message = MIMEMultipart('alternative')
    message['Subject'] = subject
    message['From'] = sender
    message['To'] = recipient
    message.attach(MIMEText(body_text, 'plain'))

    try:
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.ehlo()
        server.starttls()  # Secure the connection
        server.ehlo()
        server.login(SMTP_USERNAME, SMTP_PASSWORD)
        server.sendmail(sender, recipient, message.as_string())
        print("Email sent successfully!")
    except Exception as e:
        print(f"Error sending email: {e}")
    finally:
        server.quit()

class MessageHandlerSMTP:
    def __init__(self, bot):
        self.bot = bot

    async def handle_DATA(self, server, session, envelope):
        mail = BytesParser(policy=default).parsebytes(envelope.content)
        mail_from = envelope.mail_from
        rcpt_tos = envelope.rcpt_tos
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

        # Send basic email info to Telegram chat
        await self.bot.send_message(
            chat_id=CHAT_ID, text=basic_info, parse_mode=ParseMode.HTML
        )

        # Send the email body as a file
        await self.bot.send_document(
            chat_id=CHAT_ID, document=email_content_io, filename="email_content.html"
        )

        return "250 Message accepted for delivery"


# Function to respond with "pong" when receiving "ping"
async def ping_command(update, context):
    await update.message.reply_text("pong")


# Generic message handler to detect the word "ping" in any text message
async def text_message(update, context):
    if "ping" in update.message.text.lower():
        send_mail("amazon@simeonevilardo.com", "simeone.vilardo@gmail.com", "Ping", "Pong")
        await update.message.reply_text("pong")


async def main():
    # Create the Telegram bot instance
    application = ApplicationBuilder().token(TOKEN).build()

    # Initialize the Telegram bot application
    await application.initialize()

    bot = application.bot

    # Instantiate the handler for the SMTP server
    handler_smtp = MessageHandlerSMTP(bot)
    controller = Controller(handler_smtp, hostname="0.0.0.0", port=1025)

    # Set up Telegram command handlers
    application.add_handler(CommandHandler("ping", ping_command))
    application.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), text_message))

    # Start the Telegram bot in the background
    controller.start()
    print("SMTP Server started on port 1025...")
    print("Telegram Bot listening for 'ping' messages...")

    try:
        application.run_polling()
    except:
        controller.stop()
        print("SMTP Server stopped.")
        print("Telegram Bot stopped.")


if __name__ == "__main__":
    asyncio.run(main())
