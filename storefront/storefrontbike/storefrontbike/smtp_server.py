import asyncio
from aiosmtpd.controller import Controller
from email.message import EmailMessage

class CustomSMTPHandler:
    async def handle_DATA(self, server, session, envelope):
        print(f"Message from: {envelope.mail_from}")
        print(f"Message to: {envelope.rcpt_tos}")
        print("Message data:")
        print(envelope.content.decode('utf8', errors='replace'))
        return '250 OK'

controller = Controller(CustomSMTPHandler(), hostname='localhost', port=1025)

controller.start()

print("SMTP server started successfully on localhost:1025")

try:
    loop = asyncio.get_running_loop()
except RuntimeError:
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

try:
    loop.run_forever()
except KeyboardInterrupt:
    pass
finally:
    controller.stop()

