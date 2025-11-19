from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from core.services.user_service import UserService
import re
from datetime import datetime
import phonenumbers
from email_validator import validate_email as validate_email_lib, EmailNotValidError

router = Router()
SKIP_SIGNAL = "-"  # сигнал для пропуска поля


class RegistrationStates(StatesGroup):
    full_name = State()
    birthdate = State()
    gender = State()
    phone = State()
    email = State()


# ----------------- Helper validators -----------------
def validate_full_name(text: str) -> str | None:
    if text == SKIP_SIGNAL:
        return None
    parts = text.strip().split()
    if len(parts) < 2:
        return None
    return " ".join(p.capitalize() for p in parts)


def validate_birthdate(text: str) -> str | None:
    if text == SKIP_SIGNAL:
        return None
    text = text.strip()

    # Полная дата дд.мм.гггг
    if re.fullmatch(r"\d{1,2}\.\d{1,2}\.\d{4}", text):
        day, month, year = map(int, text.split("."))
        try:
            datetime(year, month, day)
            return text
        except ValueError:
            return None

    # Только год
    if re.fullmatch(r"\d{4}", text):
        year = int(text)
        current_year = datetime.now().year
        if current_year-90 <= year <= current_year-10:
            return text
        return None

    return None


def validate_gender(text: str) -> str | None:
    if text == SKIP_SIGNAL:
        return None
    g = text.strip().lower()
    if g in ["м", "муж", "male"]:
        return "М"
    elif g in ["ж", "жен", "female"]:
        return "Ж"
    return None


def validate_phone(text: str) -> str | None:
    if text == SKIP_SIGNAL:
        return None
    text = text.strip()
    try:
        pn = phonenumbers.parse(text, None)
        if phonenumbers.is_valid_number(pn):
            return phonenumbers.format_number(pn, phonenumbers.PhoneNumberFormat.INTERNATIONAL)
    except phonenumbers.NumberParseException:
        return None
    return None


def validate_email(text: str) -> str | None:
    if text == SKIP_SIGNAL:
        return None
    text = text.strip()
    try:
        v = validate_email_lib(text)
        return v.email
    except EmailNotValidError:
        return None


# ----------------- FSM Handlers -----------------
def register_registration_handlers(router: Router, user_service: UserService):
    
    @router.message(Command("register"))
    async def start_registration(message: Message, state: FSMContext):
        if message.chat.type != "private":
            return await message.reply("Регистрация доступна только в личных сообщениях.")
        await state.set_state(RegistrationStates.full_name)
        await message.answer(
            "Введите ваше ФИО (например, Иван Иванов) или '-' чтобы пропустить:"
        )

    @router.message(RegistrationStates.full_name)
    async def reg_fullname(message: Message, state: FSMContext):
        value = validate_full_name(message.text)
        if value is None and message.text != SKIP_SIGNAL:
            return await message.reply(
                "❌ Некорректное ФИО. Минимум имя и фамилия (например, Иван Иванов), или '-' чтобы пропустить."
            )
        await state.update_data(full_name=value)
        await state.set_state(RegistrationStates.birthdate)
        await message.answer(
            "Введите дату рождения (дд.мм.гггг, например 12.11.1990 или просто год 1990) или '-' чтобы пропустить:"
        )

    @router.message(RegistrationStates.birthdate)
    async def reg_birthdate(message: Message, state: FSMContext):
        value = validate_birthdate(message.text)
        if value is None and message.text != SKIP_SIGNAL:
            return await message.reply(
                "❌ Некорректный формат даты, допускаются лица от 10 до 90 лет. Введите дд.мм.гггг (например, 12.11.1990) или год (1900–текущий), или '-' чтобы пропустить."
            )
        await state.update_data(birthdate=value)
        await state.set_state(RegistrationStates.gender)
        await message.answer(
            "Введите пол (М/Ж, муж/жен, male/female) или '-' чтобы пропустить:"
        )

    @router.message(RegistrationStates.gender)
    async def reg_gender(message: Message, state: FSMContext):
        value = validate_gender(message.text)
        if value is None and message.text != SKIP_SIGNAL:
            return await message.reply(
                "❌ Некорректный пол. Введите М/Ж, муж/жен, male/female или '-' чтобы пропустить."
            )
        await state.update_data(gender=value)
        await state.set_state(RegistrationStates.phone)
        await message.answer(
            "Введите телефон (например, +7 912 345-67-89) или '-' чтобы пропустить:"
        )

    @router.message(RegistrationStates.phone)
    async def reg_phone(message: Message, state: FSMContext):
        value = validate_phone(message.text)
        if value is None and message.text != SKIP_SIGNAL:
            return await message.reply(
                "❌ Некорректный телефон. Используйте корректный международный формат или '-' чтобы пропустить. Например: +7 912 345-67-89"
            )
        await state.update_data(phone=value)
        await state.set_state(RegistrationStates.email)
        await message.answer(
            "Введите email (например, example@mail.com) или '-' чтобы пропустить:"
        )

    @router.message(RegistrationStates.email)
    async def reg_email(message: Message, state: FSMContext):
        value = validate_email(message.text)
        if value is None and message.text != SKIP_SIGNAL:
            return await message.reply(
                "❌ Некорректный email. Введите корректный email (например, example@mail.com) или '-' чтобы пропустить."
            )
        await state.update_data(email=value)

        data = await state.get_data()

        # сохраняем данные через сервис; пропущенные поля будут None
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
