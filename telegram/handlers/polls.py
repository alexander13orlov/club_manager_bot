from aiogram import Router
router = Router()

@router.message(commands=[\"poll\"])
async def create_poll_handler(message):
    await message.answer(\"Poll placeholder\")
