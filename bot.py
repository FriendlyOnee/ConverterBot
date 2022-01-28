import itertools
import telebot
import requests
import json
from additional_stuff import responses, currency

from telebot import types

with open("text.txt", 'r') as file:
    TOKEN = file.readline()
bot = telebot.TeleBot(TOKEN)

lang = None
base = ''
quote = ''
amount = None


@bot.message_handler(commands=['start'])
def language(message):
    keyboard = types.ReplyKeyboardMarkup(True)
    keyboard.row('English', 'Русский')
    send = bot.send_message(message.chat.id, responses['intro'], reply_markup=keyboard)
    bot.register_next_step_handler(send, lang_setter)


def lang_setter(message):
    global lang
    if message.text == 'English':
        lang = 'eng'
    elif message.text == 'Русский':
        lang = 'ru'
    welcome_message(message, lang)


def welcome_message(message, lang):
    if lang == 'eng' or lang is None:
        bot.send_message(message.chat.id, responses["about_me_eng"], reply_markup=types.ReplyKeyboardRemove())
    else:
        bot.send_message(message.chat.id, responses["about_me_rus"], reply_markup=types.ReplyKeyboardRemove())


@bot.message_handler(commands=['help'])
def help_message(message):
    if lang == 'eng' or lang is None:
        bot.send_message(message.chat.id, responses['help_msg_eng'])
    else:
        bot.send_message(message.chat.id, responses['help_msg_rus'])


@bot.message_handler(commands=['currencies'])
def currency_message(message):
    if lang == 'eng' or lang is None:
        cur_list = 'Available currencies:\n'
        b = dict(itertools.islice(currency.items(), 3, 6))
    else:
        cur_list = 'Доступные валюты:\n'
        b = dict(itertools.islice(currency.items(), 3))
    for i, j in b.items():
        cur_list += '{}\n'.format(i)
    bot.send_message(message.chat.id, cur_list)


@bot.message_handler(commands=['convert'])
def convert_message(message):
    keyboard = types.ReplyKeyboardMarkup(True)
    keyboard.row('BTC', 'ETH', 'USD')
    if lang == 'eng' or lang is None:
        keyboard.row('Back')
        send = bot.send_message(message.chat.id, responses['step_1_eng'], reply_markup=keyboard)
    else:
        keyboard.row('Назад')
        send = bot.send_message(message.chat.id, responses['step_1_rus'], reply_markup=keyboard)
    bot.register_next_step_handler(send, convert_message_2)


def convert_message_2(message):
    global base
    if message.text in ('BTC', 'ETH', 'USD'):
        base = message.text
    elif message.text in ('Back', 'Назад'):
        if lang == 'eng' or lang is None:
            bot.send_message(message.chat.id, 'You aborted convertation process',
                             reply_markup=types.ReplyKeyboardRemove())
        else:
            bot.send_message(message.chat.id, 'Вы прекратили процесс конвертации',
                             reply_markup=types.ReplyKeyboardRemove())
        return
    else:
        if lang == 'eng' or lang is None:
            bot.send_message(message.chat.id, responses['err_cur_eng'])
        else:
            bot.send_message(message.chat.id, responses['err_cur_rus'])
    if lang == 'eng' or lang is None:
        send = bot.send_message(message.chat.id, responses['step_2_eng'].format(base))
    else:
        send = bot.send_message(message.chat.id, responses['step_2_rus'].format(base))
    bot.register_next_step_handler(send, convert_message_3)


def convert_message_3(message):
    global quote
    if message.text in ('BTC', 'ETH', 'USD'):
        quote = message.text
    elif message.text in ('Back', 'Назад'):
        if lang == 'eng' or lang is None:
            bot.send_message(message.chat.id, 'You aborted convertation process',
                             reply_markup=types.ReplyKeyboardRemove())
        else:
            bot.send_message(message.chat.id, 'Вы прекратили процесс конвертации',
                             reply_markup=types.ReplyKeyboardRemove())
        return
    else:
        if lang == 'eng' or lang is None:
            bot.send_message(message.chat.id, responses['err_cur_eng'])
        else:
            bot.send_message(message.chat.id, responses['err_cur_rus'])
    if lang == 'eng' or lang is None:
        send = bot.send_message(message.chat.id, responses['step_3_eng'].format(a=base, b=quote),
                                reply_markup=types.ReplyKeyboardRemove())
    else:
        send = bot.send_message(message.chat.id, responses['step_3_rus'].format(a=base, b=quote),
                                reply_markup=types.ReplyKeyboardRemove())
    bot.register_next_step_handler(send, convert_message_4)


def convert_message_4(message):
    global amount
    if message.text in ('Back', 'Назад'):
        if lang == 'eng' or lang is None:
            bot.send_message(message.chat.id, 'You aborted convertation process',
                             reply_markup=types.ReplyKeyboardRemove())
        else:
            bot.send_message(message.chat.id, 'Вы прекратили процесс конвертации',
                             reply_markup=types.ReplyKeyboardRemove())
        return
    try:
        amount = int(message.text)
    except ValueError:
        if lang == 'eng' or lang is None:
            bot.send_message(message.chat.id, responses['err_int_eng'])
        else:
            bot.send_message(message.chat.id, responses['err_int_rus'])
        return
    else:
        if amount == 0:
            if lang == 'eng' or lang is None:
                bot.send_message(message.chat.id, responses['err_zero_eng'])
            else:
                bot.send_message(message.chat.id, responses['err_zero_rus'])
        else:
            bot.send_message(message.chat.id, pricing.get_price(base, quote, amount))


class pricing:
    @staticmethod
    def get_price(b, q, a):
        if b == q:
            if lang == 'eng' or lang is None:
                return responses['err_same_eng']
            else:
                return responses['err_same_rus']
        try:
            r = requests.get(f'https://min-api.cryptocompare.com/data/price?fsym={b}&tsyms={q}')
        except requests.exceptions.RequestException:
            if lang == 'eng' or lang is None:
                return responses['err_wrng_eng']
            else:
                return responses['err_wrng_rus']
        else:
            answer = json.loads(r.content)
            d = round(answer[q] * a, 2)
            if amount == 1 or amount is None:
                if lang == 'eng' or lang is None:
                    return f'1{base} is {answer[q]}{q}'
                else:
                    return f'1{base} это {answer[q]}{q}'
            else:
                if lang == 'eng' or lang is None:
                    return f'1{base} is {answer[q]}{q}, {a}{base} is {d}{q}'
                else:
                    return f'1{base} это {answer[q]}{q}, {a}{base} is {d}{q}'


bot.polling(none_stop=True)
