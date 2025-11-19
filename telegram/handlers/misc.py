from aiogram import Router
router = Router()

@router.message(commands=[\"help\"])
async def help_cmd(message):
    await message.answer(\"Help placeholder\")
