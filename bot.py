import sqlite3, telebot, requests
from telebot import types
from newsapi import NewsApiClient

telebot_token = "1794433387:AAGsLnL2AYlbBOoI5SFTuqqzU5ltMQ99P2U"
category = {'business', 'entertainment', 'general', 'health', 'science', 'sports', 'technology'}


bot = telebot.TeleBot(telebot_token, parse_mode=None)

def main():
    markup = types.ReplyKeyboardMarkup(True)
    key1 = types.KeyboardButton('Подписки по категориям')
    key2 = types.KeyboardButton('Подписки по ключевым словам')
    markup.add(key1)
    markup.add(key2)
    return markup

@bot.message_handler(commands=['start'])
def start(message):
    user_name = message.from_user.username
    if requests.post(url='http://127.0.0.1:5000/users', data={'id':message.from_user.id}):
        bot.send_message(message.chat.id, 'Привет, ' + str(user_name), reply_markup=main())

@bot.message_handler(commands=['help'])
def send_welcome(message):
    bot.reply_to(message, "Жмем на кнопочки")

flag = False
@bot.message_handler(content_types=['text'])
def cont(message):
    global flag
    if message.text == 'Подписки по категориям':
        keyboard = telebot.types.ReplyKeyboardMarkup(True)
        keyboard.row('Посмотреть подписку')
        keyboard.row('Добавить подписку', 'Удалить подписку')
        bot.send_message(message.chat.id, "Выберите действие", reply_markup=keyboard)

    elif message.text == 'Подписки по ключевым словам':
        keyboard = telebot.types.ReplyKeyboardMarkup(True)
        keyboard.row('Посмотреть подборку')
        keyboard.row('Добавить ключевое слово', 'Удалить ключевое слово')
        bot.send_message(message.chat.id, "Выберите действие", reply_markup=keyboard)

    elif message.text == 'Добавить ключевое слово':
        bot.send_message(message.chat.id, "Введите новое ключевое слово:")
        flag = True

    elif message.text == 'Посмотреть подписку' or message.text == 'Удалить подписку':
        keyboard = telebot.types.ReplyKeyboardMarkup(True)
        news = requests.get(url='http://127.0.0.1:5000/subscriptions/categories', params={'id':message.from_user.id}).json()
        for x in news:
            if message.text.find("Удалить") == 0:
                x = "Удалить " + x
            keyboard.row(x)
        print(news)
        if len(news) == 0:
            bot.send_message(message.chat.id, "У вас нет подписок", reply_markup=keyboard)
        else:
            bot.send_message(message.chat.id, "Выберите подписку", reply_markup=keyboard)

    elif message.text == 'Посмотреть подборку' or message.text == 'Удалить ключевое слово':
        keyboard = telebot.types.ReplyKeyboardMarkup(True)
        news = requests.get(url='http://127.0.0.1:5000/subscriptions/keywords', params={'id':message.from_user.id}).json()
        for x in news:
            if message.text.find("Удалить") == 0:
                x = "Удалить " + x
            keyboard.row(x)
        if len(news) == 0:
            bot.send_message(message.chat.id, "У вас нет подписок", reply_markup=keyboard)
        else:
            bot.send_message(message.chat.id, "Выберите подборку", reply_markup=keyboard)

    elif message.text in category:
        news = requests.get(url='http://127.0.0.1:5000/news', params={'category':message.text}).json()
        if news['totalResults'] == 0:
            bot.send_message(message.chat.id, "Новостей нет", reply_markup=main())
        for x in news["articles"][:10]:
            bot.send_message(message.chat.id, x["url"], reply_markup=main())

    elif message.text in requests.get(url='http://127.0.0.1:5000/subscriptions/keywords', params={'id':message.from_user.id}).json():
        news = requests.get(url='http://127.0.0.1:5000/news', params={'keyword':message.text}).json()
        if news['totalResults'] == 0:
            bot.send_message(message.chat.id, "Новостей нет", reply_markup=main())
        for x in news["articles"]:
            bot.send_message(message.chat.id, x["url"], reply_markup=main())

    elif message.text.find("Удалить") == 0:
        if message.text.split()[1] in requests.get(url='http://127.0.0.1:5000/subscriptions/categories', params={'id':message.from_user.id}).json():
            if requests.delete(url='http://127.0.0.1:5000/subscriptions/categories', data={'id':message.from_user.id, 'category':message.text.split()[1]}):
                bot.send_message(message.chat.id, "Подписка удалена", reply_markup=main())
            else:
                bot.send_message(message.chat.id, 'Ошибка', reply_markup=main())

        if message.text.split()[1] in requests.get(url='http://127.0.0.1:5000/subscriptions/keywords', params={'id':message.from_user.id}).json():
            if requests.delete(url='http://127.0.0.1:5000/subscriptions/keywords', data={'id':message.from_user.id, 'keyword':message.text.split()[1]}):
                bot.send_message(message.chat.id, "Подписка удалена", reply_markup=main())
            else:
                bot.send_message(message.chat.id, 'Ошибка', reply_markup=main())

    elif message.text == 'Добавить подписку':
        keyboard = telebot.types.ReplyKeyboardMarkup(True)
        for x in category:
            if not x in requests.get(url='http://127.0.0.1:5000/subscriptions/categories', params={'id':message.from_user.id}).json():
                keyboard.row("Добавить " + x)
        bot.send_message(message.chat.id, "Выберите подписку", reply_markup=keyboard)

    elif message.text.find("Добавить") == 0:
        if message.text.split()[1] in category:
            if requests.post(url='http://127.0.0.1:5000/subscriptions/categories', data={'id':message.from_user.id, 'category':message.text.split()[1]}):
                bot.send_message(message.chat.id, "Подписка добавлена", reply_markup=main())
            else:
                bot.send_message(message.chat.id, 'Ошибка', reply_markup=main())
    elif flag:
        if not message.text in requests.get(url='http://127.0.0.1:5000/subscriptions/categories', params={'id':message.from_user.id}).json():
            print(message.text)
            if requests.post(url='http://127.0.0.1:5000/subscriptions/keywords', data={'id':message.from_user.id, 'keyword':message.text}):
                bot.send_message(message.chat.id, "Ключевое слово добавлено", reply_markup=main())
            else:
                bot.send_message(message.chat.id, 'Ошибка', reply_markup=main())
        flag = False
    else:
        bot.send_message(message.chat.id, 'Я тебя не понимаю', reply_markup=main())

bot.polling()