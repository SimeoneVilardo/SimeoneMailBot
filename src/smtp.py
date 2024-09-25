import asyncio
from email.parser import BytesParser
from email.policy import default
from aiosmtpd.controller import Controller
from io import BytesIO

import telegram as tg


class MessageHandler:
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

        await tg.send_to_telegram_text(basic_info)
        await tg.send_to_telegram_file(email_content_io, "email_content.html")

        return "250 Message accepted for delivery"


async def main():
    handler = MessageHandler()
    controller = Controller(handler, hostname="0.0.0.0", port=1025)

    print("SMTP Server started on port 1025...")
    controller.start()

    try:
        await asyncio.Event().wait()
    except KeyboardInterrupt:
        controller.stop()
        print("SMTP Server stopped.")


if __name__ == "__main__":
    asyncio.run(main())
