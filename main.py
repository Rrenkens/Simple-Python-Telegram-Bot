import telebot
import requests
import re
import threading
import time
from threading import Thread

# Enter your bot token
token = "Enter your bot token"
file_name_for_cur_user = "Data/cur_user_data.txt"
file_name_for_all_user = "Data/all_user_data.txt"

first_appear = True
bot = telebot.TeleBot(token)
bot.remove_webhook()
cur_user_data = set()
all_user_data = set()
next_call_time = time.time()


def save_data(name_of_file, data):
    with open(name_of_file, 'w', encoding='utf-8') as file:
        for element in data:
            file.write(str(element) + " ")
    # print(name_of_file, data)


def save_all_data():
    global next_call_time, file_name_for_cur_user, \
        file_name_for_cur_user, cur_user_data, all_user_data, first_appear
    if not first_appear:
        # print("save_all_data")

        thread1 = Thread(target=save_data,
                         args=(file_name_for_all_user, all_user_data,))
        thread2 = Thread(target=save_data,
                         args=(file_name_for_cur_user, cur_user_data,))

        thread1.start()
        thread2.start()
        thread1.join()
        thread2.join()

    first_appear = False

    next_call_time = next_call_time + 10
    threading.Timer(next_call_time - time.time(), save_all_data).start()


def load_data(name_of_file, data):
    data.clear()
    with open(name_of_file, 'r', encoding='utf-8') as file:
        for element in set(map(int, file.read().split())):
            data.add(element)
        print(name_of_file, data)


def load_all_data():
    # print("load_all_data")
    global cur_user_data, all_user_data,\
        file_name_for_cur_user, file_name_for_all_user

    thread1 = Thread(target=load_data,
                     args=(file_name_for_all_user, all_user_data,))
    thread2 = Thread(target=load_data,
                     args=(file_name_for_cur_user, cur_user_data,))

    thread1.start()
    thread2.start()
    thread1.join()
    thread2.join()


@bot.message_handler(commands=['start'])
def handle_start(message):
    if message.from_user.id not in cur_user_data:
        cur_user_data.add(message.from_user.id)
        user_markup = telebot.types.ReplyKeyboardMarkup(True)
        user_markup.row('/help', '/stop')
        user_markup.row('Anime Chan', 'Top Anime', 'Top Airing Anime')
        user_markup.row('Top Upcoming Anime', 'Top Manga', 'Top Novels')
        if message.from_user.id not in all_user_data:
            all_user_data.add(message.from_user.id)
            bot.send_message(message.from_user.id,
                             "Hello! I am a bot who loves anime"
                             " and anime girls very much)",
                             reply_markup=user_markup)
            bot.send_photo(message.from_user.id,
                           "https://static.zerochan.net/Miyamae."
                           "Tomoka.full.65810.jpg")
        else:
            bot.send_message(message.from_user.id,
                             "Hello! I knew you were coming back!)",
                             reply_markup=user_markup)
            bot.send_photo(message.from_user.id,
                           "https://images.wallpaperscraft.ru/"
                           "image/suzumiya_haruhi_no_yuutsu"
                           "_devushka_podmigivanie_palec_"
                           "34754_1280x960.jpg")
    else:
        bot.send_message(message.from_user.id, "You are already with us)")
        bot.send_photo(message.from_user.id, "https://d1hlpam123zqko."
                                             "cloudfront.net/d5a/"
                                             "32ac7/fe7b/487e/99f6/"
                                             "bc50807aa4f8/large/37063.jpg")


@bot.message_handler(commands=['help'])
def handle_help(message):
    bot.send_message(message.from_user.id, "To start the work write - /start\n"
                                           "To get the top 5 anime for"
                                           " all time write - Top Anime\n"
                                           "To get the top 5 anime that"
                                           " go write - Top Airing Anime\n"
                                           "To get the top 5 anime coming"
                                           " soon write - Top Upcoming Anime\n"
                                           "To get the top 5 manga for all"
                                           " time write - Top Manga\n"
                                           "To get the top 5 short stories"
                                           " for all time write - Top Novels\n"
                                           "To get an anime girl picture write"
                                           " -- Anime-Chan\n"
                                           "To complete the work write - /stop")
    bot.send_photo(message.from_user.id,
                   "https://i.pinimg.com/originals/06/be/52/"
                   "06be528e4775b19741d52e2956bdfd7a.jpg")


@bot.message_handler(commands=['stop'])
def handle_stop(message):
    if message.from_user.id in cur_user_data:
        hide_markup = telebot.types.ReplyKeyboardRemove()
        bot.send_message(message.from_user.id,
                         'Bye, I will miss((',
                         reply_markup=hide_markup)
        bot.send_photo(message.from_user.id,
                       "https://i.ytimg.com/vi/fFlQRTGxvZI/maxresdefault.jpg")
        cur_user_data.remove(message.from_user.id)


@bot.message_handler(content_types=['text'])
def handle_text(message):
    if message.from_user.id in cur_user_data:
        if message.text == 'Anime Chan':
            anime_chan(message)
        elif message.text == 'Top Anime':
            url = 'https://myanimelist.net/topanime.php'
            parsing(message, url)
        elif message.text == 'Top Airing Anime':
            url = 'https://myanimelist.net/topanime.php?type=airing'
            parsing(message, url)
        elif message.text == 'Top Upcoming Anime':
            url = 'https://myanimelist.net/topanime.php?type=upcoming'
            parsing(message, url)
        elif message.text == 'Top Manga':
            url = 'https://myanimelist.net/topmanga.php?type=manga'
            parsing(message, url)
        elif message.text == 'Top Novels':
            url = 'https://myanimelist.net/topmanga.php?type=novels'
            parsing(message, url)
        else:
            bot.send_message(message.from_user.id, "I don't understand you(")
            bot.send_photo(message.from_user.id,
                           "http://i58.beon.ru/68/56/2315668/24/90354324/"
                           "toradoramizugiservice03.jpeg")
            return


def parsing(message, url):
    count = 0
    request = requests.get(url)
    document = request.content.decode('utf-8', errors='ignore')
    key_word = "href="
    words = document.split()
    for i in range(1, len(words)):
        if key_word in words[i] and words[i - 1] == 'fw-b"':
            count += 1
            ans = re.search('href="(.+?)"', words[i])
            new_request = requests.get(ans.group(1))
            new_document = new_request.content.decode('utf-8', errors='ignore')
            new_key_word = "jpg"
            new_words = new_document.split()
            for j in range(0, len(new_words)):
                if new_key_word in new_words[j]:
                    new_ans = re.search('content="(.+?)"', new_words[j])
                    bot.send_photo(message.from_user.id, new_ans.group(1))
                    bot.send_message(message.from_user.id, ans.group(1))
                    break
            if count == 5:
                break


def anime_chan(message):
    request = requests.get('http://animepicsx.net/random')
    document = request.content.decode('utf-8', errors='ignore')
    key_word = 'jpg'
    words = document.split()
    for i in range(0, len(words)):
        if key_word in words[i]:
            temp = re.search('"(.+?)"', words[i])
            try:
                bot.send_photo(message.from_user.id, photo=temp.group(1))
            except Exception as excep:
                anime_chan(message)
            return
    anime_chan(message)


def main():
    # print("main")
    load_all_data()
    save_all_data()


if __name__ == '__main__':
    main()

bot.polling(none_stop=True)
