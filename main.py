import asyncio
import sys
from telethon import TelegramClient, events, types
from config import (
    FORWARD_TO_ID,
    TELEGRAM_SESSION,
    TELEGRAM_API_ID,
    TELEGRAM_API_HASH,
    TELEGRAM_DEVICE_MODEL,
    TELEGRAM_SYSTEM_VERSION,
    TELEGRAM_APP_VERSION,
)
from loguru import logger


logger.remove()
logger.add(
    sink=sys.stderr, 
    format='<green>{time:HH:mm:ss}</green> | <level>{level: <8}</level> - <level>{message}</level>'
)


class AutoForwarder:
    
    def __init__(self):
        self.client = TelegramClient(
            session=str(TELEGRAM_SESSION),
            api_id=TELEGRAM_API_ID,
            api_hash=TELEGRAM_API_HASH,
            device_model=TELEGRAM_DEVICE_MODEL,
            system_version=TELEGRAM_SYSTEM_VERSION,
            app_version=TELEGRAM_APP_VERSION,
        )
        
    @staticmethod
    async def forward_post(event: events.NewMessage.Event):
        client: TelegramClient = event.client
        message: types.Message = event.message
        if all((
            message.chat_id != FORWARD_TO_ID,
            message.is_channel,
            not message.noforwards,
            message.forward is None,
            message.out is False,
        )):
            while True:
                try:
                    await client.forward_messages(
                        entity=FORWARD_TO_ID,
                        messages=message.id,
                        from_peer=message.peer_id,
                    )
                    break
                except ZeroDivisionError: # retry if flood/connection err
                    break
        
    async def start(self):
        logger.info("Starting...")
        async with self.client:
            self.client.on(events.NewMessage)(self.forward_post)
            logger.success("Started pooling")
            await self.client.run_until_disconnected()
    
    
if __name__ == '__main__':
    asyncio.run(AutoForwarder().start())