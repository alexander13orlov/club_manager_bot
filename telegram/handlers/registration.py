from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext

router = Router()  # создаем локальный роутер


class RegistrationStates(StatesGroup):
    full_name = State()
    birthdate = State()
    gender = State()
    phone = State()
    email = State()


# DI: user_service передается при регистрации роутеров
def register_registration_handlers(router: Router, user_service):
    
    @router.message(Command("register"))
    async def start_registration(message: Message, state: FSMContext):
        if message.chat.type != "private":
            return await message.reply("Регистрация доступна только в личных сообщениях.")
        
        await state.set_state(RegistrationStates.full_name)
        await message.answer("Введите ваше ФИО:")

    @router.message(RegistrationStates.full_name)
    async def reg_fullname(message: Message, state: FSMContext):
        await state.update_data(full_name=message.text)
        await state.set_state(RegistrationStates.birthdate)
        await message.answer("Введите дату рождения (дд.мм.гггг или просто год):")

    @router.message(RegistrationStates.birthdate)
    async def reg_birthdate(message: Message, state: FSMContext):
        await state.update_data(birthdate=message.text)
        await state.set_state(RegistrationStates.gender)
        await message.answer("Введите пол (М/Ж) или пропустите:")

    @router.message(RegistrationStates.gender)
    async def reg_gender(message: Message, state: FSMContext):
        await state.update_data(gender=message.text)
        await state.set_state(RegistrationStates.phone)
        await message.answer("Введите телефон (можно в любом формате):")

    @router.message(RegistrationStates.phone)
    async def reg_phone(message: Message, state: FSMContext):
        await state.update_data(phone=message.text)
        await state.set_state(RegistrationStates.email)
        await message.answer("Введите email или пропустите:")

    @router.message(RegistrationStates.email)
    async def reg_email(message: Message, state: FSMContext):
        await state.update_data(email=message.text)

        data = await state.get_data()

        # сохраняем данные через асинхронный сервис
        await user_service.update_extra_info(
            user_id=message.from_user.id,
            fio=data.get("full_name"),
            birth_date=data.get("birthdate"),
            gender=data.get("gender"),
            phone=data.get("phone"),
            email=data.get("email"),
        )

        await state.clear()
        await message.answer("Регистрация завершена! Спасибо 🙌")
