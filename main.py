
import json
import logging
import random

from shutil import rmtree

from aiogram import Bot, Dispatcher, types
from aiogram.enums import ChatMemberStatus
from aiogram.filters.command import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import FSInputFile, InputMediaPhoto, InputMedia, InputMediaDocument
from aiogram import F
import sys
import os

from Keyboards.AdminKeyboards import InlineAdminButtons
from Modules.additional_funcs import add_watermark
from States.AdminStates import AdminStates

sys.path.append(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
)

from Keyboards.UserKeyboards import InlineButtons

from Modules.DB_transactions import *

from States.UserStates import *


from config import token, CHANNEL_ID, images_path, langs_path, admin_IDs, CHAT_ID

logging.basicConfig(level=logging.INFO)
bot = Bot(token=token, parse_mode="HTML")
dp = Dispatcher()


async def is_subscribed(USER_ID):
    member = await bot.get_chat_member(CHANNEL_ID, USER_ID)

    if member.status not in [ChatMemberStatus.LEFT, ChatMemberStatus.KICKED]:
        return True
    else:
        return False



@dp.message(Command("start"))
async def start_message(
    message: types.Message, state: FSMContext, command: Command = None
):
    await state.clear()

    # await message.delete()

    subs_status = await is_subscribed(message.from_user.id)
    user_status = await check_user(str(message.from_user.id))

    if not user_status:
        await create_user(
            str(message.from_user.id), message.from_user.username, lang=lang
        )

    status = None
    id = None
    if command.args:
        args = command.args

        print(args)

        if "info" == args[:4]:
            status = "info"
            id = args.replace("info_","")
        elif "reserve" == args[:7]:
            status = "reserve"
            id = args.replace("reserve_","")
        elif "photo" == args[:5]:
            status = "photo"
            id = args.replace("photo_","")


    if not subs_status:
        await update_status(str(message.from_user.id), status, id)

        await message.answer(lang_dict[lang]["not_follow"],
                             reply_markup=InlineButtons.start_kb__not_sub(
                                lang_dict[lang]["buttons"]["start_kb__not_follow"]["text"],
                                 lang_dict[lang]["buttons"]["start_kb__not_follow"]["url"]
                            ))

    else:

        if id:
            car_info = await get_post(id)

            if status == "info":
                await message.answer(f"Информация о машине <b>{car_info.car_name}</b>:")

                try:
                    media = car_info.information_files.split("|")
                    for i in media:
                        if i == "":
                            media.remove(i)
                            break

                    media = [i.split(":") for i in media]
                    media = sorted(media, key=lambda x: float(x[1]))

                    media_group = []
                    for i in media:
                        media_group.append(InputMediaDocument(media=i[0], caption=car_info.information))

                    await message.answer_media_group(media=media_group)
                except:
                    await message.answer(car_info.information)

            elif status == "reserve":
                await message.answer(f"Бронь машины <b>{car_info.car_name}</b>:")
                await message.answer("<i>Пришлите ваши паспортные данные в следующем формате:</i>\n\n"
                                     "* Серия номер *\n"
                                     "* Фамилия Имя Отчество *\n"
                                     "* Дата рождения (29.01.2000) *")

                await state.update_data(car_name=car_info.car_name,
                                        post_id=car_info.id)

                await state.set_state(UserState.wait_user_data.state)

            elif status == "photo":
                await message.answer(f"Дополнительные фото машины <b>{car_info.car_name}</b>:")
                images = await get_post_photos(id)

                group = []
                for image in images:
                    if image == "" or image == images[0]:
                        continue
                    else:
                        group.append(image.split(":"))
                group = sorted(group, key=lambda x: float(x[1]))

                media_group = []
                for image in group:
                    media_group.append(InputMediaPhoto(media=image[0]))

                try:
                    await message.answer_media_group(media_group)
                except:
                    await message.answer("Отсутствуют")


            await update_status(str(message.from_user.id), "followed")

        else:
            print("Неправильные данные при /start")



    await update_last_start(str(message.from_user.id))

@dp.message(Command("admin"))
async def admin_message(message: types.Message, state: FSMContext, command: Command = None):

    await state.clear()

    if message.from_user.id in admin_IDs:
        await message.answer("Вы находитесь в меню админа, выберите действие", reply_markup=InlineAdminButtons.start_kb())


@dp.callback_query(F.data == "hide")
async def hide(callback: types.CallbackQuery, state: FSMContext):
    await bot.answer_callback_query(callback.id)
    await callback.message.delete()

@dp.callback_query(F.data == "menu")
async def menu(callback: types.CallbackQuery, state: FSMContext):
    await bot.answer_callback_query(callback.id)
    state_ = await state.get_state()
    data = await state.get_data()

    await state.clear()

    if callback.from_user.id in admin_IDs:

        try:
            await delete_post_db(data['post_id'])
        except:
            pass

        await callback.message.delete()
        await callback.message.answer("Вы находитесь в меню админа, выберите действие",
                             reply_markup=InlineAdminButtons.start_kb())



@dp.callback_query(F.data == "back")
async def back(callback: types.CallbackQuery, state: FSMContext):
    await bot.answer_callback_query(callback.id)

    state_ = await state.get_state()

    if state_ == AdminStates.create_post_name.state:
        await callback.message.delete()
        await callback.message.answer("Вы находитесь в меню админа, выберите действие",
                                      reply_markup=InlineAdminButtons.start_kb())

        data = await state.get_data()
        await delete_post_db(data['post_id'])

    elif state_ == AdminStates.create_post_photos.state:
        await callback.message.delete()
        await callback.message.answer("Пришлите название машины, которое будет привязано к посту",
                                         reply_markup=InlineAdminButtons.back_kb())

        _ = str(uuid.uuid4())
        await state.update_data(post_id=_)
        await create_post_db(_)

        await state.set_state(AdminStates.create_post_name.state)


    elif state_ == AdminStates.create_post_info.state:
        await callback.message.delete()

        await callback.message.answer("Пришлите пост, который будет опубликован в канал", reply_markup=InlineAdminButtons.back_kb())
        await state.set_state(AdminStates.create_post_photos.state)

    elif state_ == AdminStates.create_post_more_photos.state:
        await callback.message.delete()

        await callback.message.answer("Напишите информацию для данной машины", reply_markup=InlineAdminButtons.back_kb())
        await state.set_state(AdminStates.create_post_info.state)

@dp.callback_query(F.data == "create_post")
async def create_post(callback: types.CallbackQuery, state: FSMContext):
    await bot.answer_callback_query(callback.id)

    await callback.message.edit_text("Пришлите название машины, которое будет привязано к посту", reply_markup=InlineAdminButtons.back_kb())

    _ = str(uuid.uuid4())
    await state.update_data(post_id=_)
    await create_post_db(_)

    await state.set_state(AdminStates.create_post_name.state)

@dp.callback_query(F.data == "all_posts")
async def create_post(callback: types.CallbackQuery, state: FSMContext):
    await bot.answer_callback_query(callback.id)

    page = 0
    try:
        page = int(callback.data.split("-")[-1])
    except:
        pass

    all_posts = await get_posts()

    if len(all_posts)%5 == 0:
        last_page = (len(all_posts)//5) - 1
    else:
        last_page = (len(all_posts) // 5)

    try:
        posts = all_posts[page*5:(page+1)*5]
    except:
        posts = all_posts[page*5:]

    try:
        if len(all_posts[(page+1)*5:(page+2)*5]) > 0:
            next = True
        else:
            next = False
    except:
        next = False

    try:
        if len(all_posts[(page-1) * 5:(page) * 5]) > 0:
            previous = True
        else:
            previous = False
    except:
        previous = False

    buttons = []
    for post in posts:
        buttons.append({"text":post.car_name, "callback_data":f"a_post_{post.id}"})

    await callback.message.edit_text("Выберите интересуемый пост",
                                     reply_markup=InlineAdminButtons.posts_kb(page=page,
                                                                              last_page=last_page,
                                                                              buttons=buttons,
                                                                              previous=previous,
                                                                              next=next))


@dp.callback_query(F.data[:6] == "a_post")
async def a_post(callback: types.CallbackQuery, state: FSMContext):
    await bot.answer_callback_query(callback.id)

    car_id = callback.data.replace("a_post_", "")
    car_info = await get_post(car_id)

    await callback.message.delete()
    await callback.message.answer_photo(photo=car_info.images.split("|")[0], caption=car_info.text,
                                        reply_markup=InlineAdminButtons.post_kb())



@dp.callback_query(F.data[:6] == "cancel")
async def create_post(callback: types.CallbackQuery, state: FSMContext):
    await bot.answer_callback_query(callback.id)

    id = callback.data.split("_")[-1]
    await posting_cancel(id)

    await callback.message.edit_text("Вы успешно отменили постинг", reply_markup=None)

@dp.callback_query(F.data == "send_post_now")
async def create_post(callback: types.CallbackQuery, state: FSMContext):
    await bot.answer_callback_query(callback.id)
    data = await state.get_data()

    await update_post_data(id=data['post_id'],
                           information=data['post_info'],
                           post_date=datetime.datetime.now(),
                           posted_status=True)

    post = await get_post(data['post_id'])

    await bot.send_photo(chat_id=CHANNEL_ID, photo=post.images.split("|")[0], caption=post.text, reply_markup=InlineButtons.default_post_kb(data['post_id']))



    await callback.message.answer("Пост был успешно опубликован")

    await state.clear()
    await callback.message.answer("Вы находитесь в меню админа, выберите действие",
                         reply_markup=InlineAdminButtons.start_kb())

@dp.callback_query(F.data[:7] == "approve")
async def approve(callback: types.CallbackQuery, state: FSMContext):
    await bot.answer_callback_query(callback.id)

    await callback.message.edit_text(callback.message.html_text + "\n\n<b>Подтвержден ✅</b>", reply_markup=None)

    bid_id = callback.data.split("_")[-1]
    data = await get_bid(bid_id)
    car_info = await get_post(data.post_id)

    await bot.send_message(chat_id=int(data.user_id), text=f"Ваша заявка на бронирование автомобиля <b>{car_info.car_name}</b> была успешно утверждена, чтобы приступить к оплате бронирования, нажмите кнопку <b>Далее</b>", reply_markup=InlineButtons.payment_kb(bid_id))


@dp.callback_query(F.data[:6] == "reject")
async def reject(callback: types.CallbackQuery, state: FSMContext):
    await bot.answer_callback_query(callback.id)

    await callback.message.edit_text(callback.message.html_text + "\n\n<b>Отклонен ❌</b>", reply_markup=None)

    bid_id = callback.data.split("_")[-1]
    data = await get_bid(bid_id)
    car_info = await get_post(data.post_id)

    await bot.send_message(chat_id=int(data.user_id),
                           text=f"Ваша заявка на бронирование автомобиля <b>{car_info.car_name}</b> была отклонена.")

    await delete_bid(bid_id)

@dp.callback_query(F.data[:7] == "payment")
async def payment(callback: types.CallbackQuery, state: FSMContext):
    await bot.answer_callback_query(callback.id)

    bid_id = callback.data.split("_")[-1]
    data = await get_bid(bid_id)
    car_info = await get_post(data.post_id)

    await bot.send_message(chat_id=int(data.user_id),
                           text=f"Для оплаты брони автомобиля <b>{car_info.car_name}</b> напишите менеджеру. Он составит договор и вышлет реквизиты.",
                           reply_markup=InlineButtons.reject_kb())

    await delete_bid(bid_id)

@dp.callback_query(F.data == "skip")
async def payment(callback: types.CallbackQuery, state: FSMContext):
    await bot.answer_callback_query(callback.id)
    data = await state.get_data()

    post = await get_post(data['post_id'])

    images = await get_not_ready_post_photos(data['post_id'])
    # print(images)
    for index, img in enumerate(images):
        if img == "":
            continue

        image = img.split(":")[0]
        # print(image)
        file_path = (await bot.get_file(image)).file_path
        # print(file_path)
        await bot.download_file(file_path, destination=f"{os.getcwd()}\\{images_path}\\{image}.jpg")
        await asyncio.to_thread(add_watermark,
                                images_path, f"{image}.jpg")

    await callback.message.delete()

    res = await callback.message.answer_photo(photo=FSInputFile(f"{os.getcwd()}\\{images_path}\\new_{image}.png"), caption=post.text)
    # print(len(res))
    images_text = f"{res.photo[-1].file_id}|"

    await res.delete()

    await asyncio.to_thread(rmtree, f"{os.getcwd()}\\{images_path}")
    await asyncio.to_thread(os.mkdir, f"{os.getcwd()}\\{images_path}")

    await update_post_photo_final(data['post_id'], images_text)

    post = await get_post(data['post_id'])
    await callback.message.answer_photo(photo=post.images.split("|")[0], caption=post.text)

    await asyncio.sleep(0.2)
    await callback.message.answer("<b>Информация (доступна по кнопке):</b>\n\n" + data["post_info"])
    await asyncio.sleep(0.2)
    await callback.message.answer("<b>Доп. фотографии (доступны по кнопке):</b>")
    await callback.message.answer("Отсутствуют")


    await callback.message.answer("Укажите дату и время отправки данного поста в канал в формате "
                         "<b>24.04.2024 13:03</b>, либо нажмите <i>Сейчас</i> для моментальной отправки",
                         reply_markup=InlineAdminButtons.confirm_post_kb())

    await state.set_state(AdminStates.create_post_confirm.state)


@dp.message(F.text | F.photo | F.video | F.document)
async def message_distributor(message: types.Message, state: FSMContext):
    state_ = await state.get_state()
    data = await state.get_data()

    if state_ == AdminStates.create_post_name.state:

        await update_post_name(data['post_id'], message.text)
        await message.answer("Пришлите пост, который будет опубликован в канал",
                                         reply_markup=InlineAdminButtons.back_kb())

        await state.set_state(AdminStates.create_post_photos.state)

    elif state_ == AdminStates.create_post_photos.state:

        try:
            text = message.html_text
            f = text.split("\n", 1)[0]
            other  = text.split("\n", 1)[1]

            text = "<blockquote>"+f+"</blockquote>\n"+other

            await update_post_photo(data['post_id'], message.photo[-1].file_id, text)

            await message.answer("Напишите информацию для данной машины", reply_markup=InlineAdminButtons.back_kb())
            await state.set_state(AdminStates.create_post_info.state)

        except:

            await message.answer("Отправьте пост в правильном формате")
            return

    elif state_ == AdminStates.create_post_info.state:
        info = message.html_text

        try:
            file_id = message.document.file_id
            await update_post_documents(data['post_id'], file_id + ":" + str(datetime.datetime.now().timestamp()))
        except:
            pass

        await asyncio.sleep(random.randint(10, 50) / 100)
        status = await update_post_information_upload_status(data['post_id'])

        await asyncio.sleep(0.5)

        if status:

            await state.update_data(post_info=info)
            await message.answer("Пришлите больше фотографий машины, чтобы пользователь мог посмотреть их в боте, либо пропустите этот шаг", reply_markup=InlineAdminButtons.back_kb(True))
            await state.set_state(AdminStates.create_post_more_photos.state)

    elif state_ == AdminStates.create_post_more_photos.state:

        photo_id = message.photo[-1].file_id
        await update_post_photo(data['post_id'],photo_id+":"+str(datetime.datetime.now().timestamp()))

        await asyncio.sleep(random.randint(10,70)/100)
        status = await update_post_upload_status(data['post_id'])

        await asyncio.sleep(0.7)

        if status:

            await message.answer("Подождите немного, идет подготовка фотографий с вотермаркой")

            m_g = []
            images = await get_not_ready_post_photos(data['post_id'])
            # print(images)
            for index, img in enumerate(images):
                if img == "":
                    continue

                image = img.split(":")[0]
                # print(image)
                file_path = (await bot.get_file(image)).file_path
                # print(file_path)
                await bot.download_file(file_path, destination=f"{os.getcwd()}\\{images_path}\\{image}.jpg")
                await asyncio.to_thread(add_watermark,
                                        images_path, f"{image}.jpg")
                m_g.append(InputMediaPhoto(media=FSInputFile(f"{os.getcwd()}\\{images_path}\\new_{image}.png")))

            res = await message.answer_media_group(media=m_g)
            # print(len(res))
            images_text = ""
            for index, msg in enumerate(res):
                if index != 0:
                    images_text+=str(msg.photo[-1].file_id)+":"+images[index].split(":")[1]+"|"
                else:
                    images_text += str(msg.photo[-1].file_id) + "|"

            for msg in res:
                await msg.delete()

            await asyncio.to_thread(rmtree, f"{os.getcwd()}\\{images_path}")
            await asyncio.to_thread(os.mkdir, f"{os.getcwd()}\\{images_path}")

            await update_post_photo_final(data['post_id'], images_text)

            post = await get_post(data['post_id'])
            images = await get_post_photos(data['post_id'])


            await message.answer_photo(photo=post.images.split("|")[0], caption=post.text)
            await asyncio.sleep(0.2)
            await message.answer("<b>Информация (доступна по кнопке):</b>")

            try:
                media = post.information_files.split("|")
                for i in media:
                    if i == "":
                        media.remove(i)
                        break

                media = [i.split(":") for i in media]
                media = sorted(media, key=lambda x: float(x[1]))

                media_group = []
                for i in media:
                    media_group.append(InputMediaDocument(media=i[0], caption=data["post_info"]))

                await message.answer_media_group(media=media_group)
            except:
                await message.answer(data["post_info"])

            await asyncio.sleep(0.2)
            await message.answer("<b>Доп. фотографии (доступны по кнопке):</b>")

            group = []
            for image in images:
                if image == "" or image == images[0]:
                    continue
                else:
                    group.append(image.split(":"))
            group = sorted(group, key=lambda x: float(x[1]))

            media_group = []
            for image in group:
                media_group.append(InputMediaPhoto(media=image[0]))


            await message.answer_media_group(media_group)

            await message.answer("Укажите дату и время отправки данного поста в канал в формате "
                                 "<b>24.04.2024 13:03</b>, либо нажмите <i>Сейчас</i> для моментальной отправки", reply_markup=InlineAdminButtons.confirm_post_kb())

            await state.set_state(AdminStates.create_post_confirm.state)

    elif state_ == AdminStates.create_post_confirm.state:

        try:
            date = datetime.datetime.strptime(message.text, "%d.%m.%Y %H:%M")
        except:
            await message.answer("Вы неправильно указали формат даты, оппробуйте снова")
            return

        await update_post_data(id=data['post_id'],
                               information=data['post_info'],
                               post_date=date,
                               posted_status=False)

        await message.answer("Вы успешно запланировали пост, можете отменить его отправку по кнопке ниже", reply_markup=InlineAdminButtons.cancel_post(data['post_id']))

        await state.clear()
        await message.answer("Вы находитесь в меню админа, выберите действие",
                                      reply_markup=InlineAdminButtons.start_kb())


    elif state_ == UserState.wait_user_data.state:

        text = message.text
        if text.count("\n") != 2:
            await message.answer("Вы указали данные в неправильном формате")
            return
        else:

            result = await find_bid(str(message.from_user.id), data['post_id'])
            if result:
                await message.answer("Вы уже отправили заявку на бронь по данной машине, ожидайте ответа")
                return

            bid_id = await create_bid(str(message.from_user.id), data['post_id'])

            await message.answer("Ваши данные для бронирования были направлены на проверку модератору, дождитесь обратной связи")
            await bot.send_message(chat_id=CHAT_ID, text=f"Пользователь @{message.from_user.username} отправил свои данные на проверку для осуществления бронирования автомобиля <b>{data['car_name']}</b>:\n\n"
                                                         f"{text}",
                                   reply_markup=InlineAdminButtons.approve_reserve(bid_id))



    else:



        if message.from_user.id in admin_IDs:
            # print(message.photo[-1]., datetime.datetime.now().timestamp())
            print(message.html_text)
            await message.delete()

        else:
            await message.delete()


async def check_subscription():
    users = await get_users()
    for user in users:
        try:
            if (datetime.datetime.now() - user.last_start_time).seconds > 86400:
                await delete_user(user.id)

            if await is_subscribed(int(user.id)):

                status = user.status

                await update_status(user.id, "followed")

                car_info = await get_post(user.car_id)
                await bot.send_message(chat_id=int(user.id), text=car_info.information if status == "info" else car_info.reserve_text)

            else:
                await asyncio.sleep(0.1)
                continue

        except Exception as e:
            if "bot was blocked by the user" in str(e) or "user not found" in str(e):
                # print(f"Пользователь {user.id} удален из за ошибка {str(e)}")
                await delete_user(user.id)

            else:
                print(f"Error ({str(e)})")

async def check_posts():
    posts = await get_posts_for_posting()
    for post in posts:

        await bot.send_photo(chat_id=CHANNEL_ID, photo=post.images.split("|")[0],caption=post.text,
                               reply_markup=InlineButtons.default_post_kb(post.id))

        await update_post_status(id=post.id,
                                 posted_status=True)


async def cs_updater():
    while True:
        await check_subscription()
        await asyncio.sleep(1)

async def post_checker():
    while True:
        await check_posts()
        await asyncio.sleep(1)

async def main():
    await bot.delete_webhook(drop_pending_updates=True)

    asyncio.create_task(cs_updater())
    asyncio.create_task(post_checker())

    await dp.start_polling(bot)


if __name__ == "__main__":
    with open(langs_path, "r", encoding="utf-8") as file:
        lang_dict = json.loads(file.read())

    # parser = argparse.ArgumentParser(description="Telegram Bot")
    # parser.add_argument(
    #     "--lang",
    #     type=str,
    #     choices=["ru", "ua"],
    #     help="Language for the bot (ru/ua)",
    #     required=True,
    # )
    # args = parser.parse_args()

    global lang
    # lang = args.lang
    lang = "ru"


    asyncio.run(async_create_db())
    asyncio.run(main())
