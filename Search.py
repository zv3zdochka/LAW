try:
    import datetime
    import aiohttp
    from bs4 import BeautifulSoup
    import asyncio
    import sys
    import time
    from aiogram import Bot, Dispatcher, types
    from aiogram.types import Message, FSInputFile
    from aiogram.utils.markdown import hbold
    from aiogram.enums import ParseMode
    from aiogram.filters import CommandStart
    import json
    import logging
    import requests

except ModuleNotFoundError:
    sys.exit("Required libraries are missing. Please install them using:\n"
             "pip install -r requirements.txt\n"
             "You can find the requirements.txt file at: https://github.com/zv3zdochka/Cheat_Ege.git")

TOKEN = "7104080784:AAFiU0STuHAsW-KsFOF5cwVozmdn1UCflB0"
auth_waiting = []
users = []
admins = []
ban = []
nicknames = {}
dp = Dispatcher()
bot = Bot(TOKEN, parse_mode=ParseMode.HTML)
first = True
creator = 1363003331

logging.basicConfig(filename='log.txt',
                    filemode='a',
                    format='%(asctime)s,%(msecs)d %(name)s %(levelname)s %(message)s',
                    datefmt='%H:%M:%S',
                    level="DEBUG")

logging.getLogger("urllib3").setLevel(logging.WARNING)
logging.getLogger("aiogram.event").setLevel(logging.CRITICAL)



class PageChecker:
    def __init__(self, subject_name, targets, start=-1):
        self.subject_name = subject_name
        self.targets = targets
        self.subject_url = self.subject_url_by_name(subject_name)
        if start == -1:
            pass
        else:
            self.start_id = start
            self.founded = []
            self.current_num = 0
            self.generate_test()

    async def check_page(self, session, page_id):
        if page_id is None:
            return

        url = f"{self.subject_url}/test?id={page_id}"

        try:
            async with session.get(url) as response:
                if response.status == 200:
                    html = await response.text()
                    text = BeautifulSoup(html, 'html.parser').get_text()

                    if len(text) == 118:
                        logging.warning(f"Page {url} not found.")
                        return

                    for target in self.targets:
                        if target in text:
                            return [page_id, target]

                    if "JavaScript" in text:
                        logging.warning(f"JavaScript on page {url}.")
                        return

        except Exception as e:
            logging.warning(f"Exeption {e} on {url}.")

    async def fetch_all(self, ids):
        async with aiohttp.ClientSession() as session:
            tasks = [self.check_page(session, page_id) for page_id in ids]
            return await asyncio.gather(*tasks)

    async def main(self, generator):
        ids = generator()
        while True:
            chunk = [next(ids) for _ in range(50)]
            results = await self.fetch_all(chunk)
            for page_id, result in zip(chunk, results):
                if result:
                    self.founded.append([result[0], result[1]])
            if None in chunk:
                break

    async def search_from_to(self):
        await self.main(self.id_generator_up)

    def id_generator_up(self):
        while self.start_id <= self.current_num:
            yield self.start_id
            self.start_id += 1
        else:
            while True:
                yield None

    def generate_test(self):
        problems = {1: 1}

        dif = {f'prob{i}': problems[i] for i in problems}
        self.current_num = int(requests.get(f'{self.subject_url}/test?a=generate', dif,
                                            allow_redirects=False).headers['location'].split('id=')[1].split('&nt')[0])

    def generate_test_r(self):
        problems = {1: 1}

        dif = {f'prob{i}': problems[i] for i in problems}
        return int(requests.get(f'{self.subject_url}/test?a=generate', dif,
                                allow_redirects=False).headers['location'].split('id=')[1].split('&nt')[0])

    @staticmethod
    def subject_url_by_name(name):
        subjects = {
            'math': 'https://math-ege.sdamgia.ru',
            'mathb': 'https://mathb-ege.sdamgia.ru',
            'phys': 'https://phys-ege.sdamgia.ru',
            'inf': 'https://inf-ege.sdamgia.ru',
            'rus': 'https://rus-ege.sdamgia.ru',
            'bio': 'https://bio-ege.sdamgia.ru',
            'en': 'https://en-ege.sdamgia.ru',
            'chem': 'https://chem-ege.sdamgia.ru',
            'geo': 'https://geo-ege.sdamgia.ru',
            'soc': 'https://soc-ege.sdamgia.ru',
            'de': 'https://de-ege.sdamgia.ru',
            'fr': 'https://fr-ege.sdamgia.ru',
            'lit': 'https://lit-ege.sdamgia.ru',
            'sp': 'https://sp-ege.sdamgia.ru',
            'hist': 'https://hist-ege.sdamgia.ru',
        }
        return subjects.get(name)


async def send_to_admins(smt: str):
    for admin in admins:
        await bot.send_message(admin, smt)


@dp.message(CommandStart())
async def command_start_handler(message: Message) -> None:
    nicknames[str(message.chat.id)] = str(message.chat.username)
    update_json()
    if message.chat.id in ban:
        pass

    elif message.chat.id not in admins and message.chat.id not in users:
        await message.answer(f"Hello, {hbold(message.from_user.full_name)} !\nAuthorization in progress.")
        auth_waiting.append(message.chat.id)
        await send_to_admins(
            f"New user requesting authorization \nId: {message.chat.id} \nName: {message.chat.username}")

    elif message.chat.id not in admins and message.chat.id in users:
        await message.answer(f"Hello, {hbold(message.from_user.full_name)}! You are authorized, wait for test.")

    elif message.chat.id in admins:
        await message.answer(f"Hello, {hbold(message.from_user.full_name)} !\n"
                             f"You are an admin.\n "
                             f"Search is running\n")
        if auth_waiting:
            await message.answer(f"Waiting for authorization:\n")
            for i in auth_waiting:
                await message.answer(str(i))


@dp.message()
async def echo_handler(message: types.Message) -> None:
    nicknames[str(message.chat.id)] = str(message.chat.username)
    update_json()
    if message.chat.id in ban:
        pass

    elif message.chat.id not in admins:
        await message.answer("Only admins can chat with the bot.\n"
                             "If you want to tell something to admins or to add the teacher write to: @sugarpups010\n"
                             "If you want respect from historic person use /respect.")

    else:
        text = message.text.split()
        if text[0] == '/allow':

            if int(text[1]) in auth_waiting:
                users.append(int(text[1]))
                auth_waiting.remove(int(text[1]))
                await bot.send_message(int(text[1]), str("You are authorized! \nEnjoy!"))
                await send_to_admins(f"New user authorized {text[1]} by {message.chat.id}")
                update_json()

            else:
                await message.answer("No such user, waiting for authorization.")

        elif text[0] == '/deny':
            if int(text[1]) in auth_waiting:
                auth_waiting.remove(int(text[1]))
                await bot.send_message(int(text[1]), str("Permission denied."))
                await bot.send_message(message.chat.id, f"Authorisation of user {text[1]} denied")
                await bot.send_message(creator, f"User {message.chat.id} denied {int(text[1])}.")

                update_json()
            else:
                await message.answer("No such user, waiting for authorization.")

        elif text[0] == '/help':
            await bot.send_message(message.chat.id, "God bless you!")

        elif text[0] == '/admin':
            if message.chat.id == creator:
                if int(text[1]) in admins:
                    await bot.send_message(message.chat.id, "Users is already an admin.")
                elif int(text[1]) not in users:
                    await bot.send_message(message.chat.id, "Wrong user.")

                elif int(text[1]) in ban:
                    await bot.send_message(message.chat.id, 'User in ban')

                elif int(text[1]) in users:
                    admins.append(int(text[1]))
                    await send_to_admins(f"User {int(text[1])} upgraded to admin by {message.chat.id}")
                    await bot.send_message(int(text[1]), "Now you`re an admin. Enjoy...")

            else:
                await bot.send_message(message.chat.id, "Only the creator can make admins.")
                await bot.send_message(creator, f"User {message.chat.id} tried to make admin user {int(text[1])}.")

        elif text[0] == '/text':
            await tell_users(' '.join(text[1:]))
            if message.chat.id != creator:
                await bot.send_message(creator, f"User {message.chat.id} text to all {' '.join(text[1:])}.")


        elif text[0] == '/textto':
            try:
                if int(text[1]) not in users:
                    await bot.send_message(message.chat.id, "No such user.")
                else:
                    await bot.send_message(int(text[1]), ' '.join(text[2:]))
                    if int(text[1]) != creator:
                        await bot.send_message(creator,
                                               f"User {message.chat.id} texted to {text[1]} this {' '.join(text[2:])}.")

            except Exception:
                await bot.send_message(message.chat.id, f"No such command, use /help")
        elif text[0] == '/users':
            await bot.send_message(message.chat.id, str(users))

        elif text[0] == '/all':
            await bot.send_message(message.chat.id, str(nicknames))

        elif text[0] == '/banned':
            await bot.send_message(message.chat.id, str(ban))

        elif text[0] == '/save':
            await bot.send_document(message.chat.id, FSInputFile(path='data.json'))
            await bot.send_document(message.chat.id, FSInputFile(path='users.json'))
            await bot.send_document(message.chat.id, FSInputFile(path='log.txt'))
            await bot.send_document(message.chat.id, FSInputFile(path='found.txt'))
            if message.chat.id != creator:
                await bot.send_message(creator, f"User {message.chat.id} save files.")

        elif text[0] == '/ban':
            if int(text[1]) == creator:
                await bot.send_message(message.chat.id, "You can`t ban the creator.")
                await bot.send_message(creator, f"User {message.chat.id} tried to ban you.")
            else:
                ban.append(int(text[1]))
                try:
                    users.remove(int(text[1]))
                    admins.remove(int(text[1]))
                except ValueError:
                    pass
                finally:
                    await send_to_admins(f"User {text[1]} was banned by {message.chat.id}")
                    update_json()

        elif text[0] == '/free':
            ban.remove(int(text[1]))
            await bot.send_message(message.chat.id, f"User {text[1]} is free. ")
            await send_to_admins(f"User {text[1]} released from ban by {message.chat.id}")
            update_json()

        elif text[0] == '/delete':
            if int(text[1]) == creator:
                await bot.send_message(message.chat.id, "You can`t delete the creator.")
                await bot.send_message(creator, f"User {message.chat.id} tried to delete you.")
            else:
                await bot.send_message(int(text[1]), 'Administrator deleted you.')
                users.remove(int(text[1]))
                await send_to_admins(f"User {text[1]} was successfully deleted by {message.chat.id}")
                update_json()

        else:
            await bot.send_message(message.chat.id, f"No such command, use /help")


def update_json():
    try:
        with open('users.json', 'w') as f:
            data = {}
            data['admins'] = admins
            data['users'] = users
            data['ban'] = ban
            data['nicknames'] = nicknames
            json.dump(data, f)
            del data
    except Exception as e:
        exit(e)


async def tell_users(text: str):
    for i in users:
        await bot.send_message(i, text)


async def main() -> None:
    await dp.start_polling(bot)


async def broadcaster(st: str):
    logging.info(f"Broadcast {st}.")
    try:
        await tell_users(st)
    except Exception as e:
        exit(e)


async def search():
    global first
    sleep_time = 15
    while True:
        s_t = time.time()
        if first:
            for key, value in data.items():
                pch = PageChecker(key, value[0])
                data[key] = [value[0], pch.generate_test_r()]
                del pch
            first = False

        for key, value in data.items():
            pch = PageChecker(key, value[0], value[1])
            await pch.search_from_to()
            for j in pch.founded:
                print(j)
                logging.info(f"Test {j} found in subject {pch.subject_name}.")
                await broadcaster(f"Subject: {pch.subject_name}\n"
                                  f"Id: {j[0]}\n"
                                  f"Target: {j[1]}")

                with open('found.txt', 'a') as f:
                    f.write(f"Found in subject {j[0]}: {j[1]}. On time {datetime.datetime.now()}\n")
            n_d = data[pch.subject_name]
            n_d[1] = pch.current_num
            data[pch.subject_name] = n_d
            del pch
        print(data)
        with open('data.json', 'w') as file:
            json.dump(data, file, ensure_ascii=False)

        if time.time() - s_t > 10:
            sleep_time -= 1
        if time.time() - s_t < 2:
            sleep_time += 1
        await asyncio.sleep(sleep_time)


if __name__ == "__main__":
    if len(sys.argv[1:]) != 0:
        logging.critical(f"Wrong command {' '.join(sys.argv)}.")
        exit('Usage: python Search.py')
    try:
        with open('data.json', 'r', errors='ignore', encoding="windows-1251") as file:
            data = json.load(file)
            for key, value in data.items():
                data[key] = [value[0], value[1]]

    except FileNotFoundError:
        logging.critical(f"No data.json.")
        exit("Add data.json file")
    try:
        with open('users.json', 'r', errors='ignore') as file:
            data_bot = dict(json.load(file))
            print(data_bot)
            users = data_bot.get('users')
            admins = data_bot.get('admins')
            nicknames = dict(data_bot.get('nicknames'))
            ban = data_bot.get('ban')

    except FileNotFoundError:
        logging.critical(f"No users.json.")
        exit("Add users.json file")


    async def run_all():
        await asyncio.gather(search(), main())


    asyncio.run(run_all())
