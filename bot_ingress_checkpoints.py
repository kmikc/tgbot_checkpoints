#!/usr/bin/env python
# -*- coding: utf-8 -*-
import telebot
import logging
from unicodedata import normalize
from datetime import datetime, timedelta

bot = telebot.TeleBot("140837439:AAFR0JP70z5QsNmKB60aX_mEfbfrtkdQ8wY")

#
# COMANDOS
#

@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    bot.reply_to(message, "Holi, no hay nada aqui todavía =)")

#
# FILTRAR MENSAJES "proximo cp"... etc.
#

@bot.message_handler(func=lambda message: True)
def echo_all(message):
    logging.basicConfig(filename='bot_ingress_checkpoints.log', filemode='w', level=logging.DEBUG)
    logging.info(message)

    text = message.text
    mensajes_cp = [u'proximo cp', u'siguiente cp', u'proximo checkpoint', u'siguiente checkpoint', u'proximo check point', u'siguiente check point']
    mensajes_ciclo = [u'fin de ciclo', u'fin del ciclo', u'final de ciclo', u'final del ciclo', u'proximo ciclo', u'siguiente ciclo', u'ciclo nuevo', u'nuevo ciclo']
    all_messages = mensajes_cp + mensajes_ciclo
    revise_message = [find_text for find_text in all_messages if find_text in text.lower()]

    if len(revise_message) > 0:
        _init_cycle = datetime.strptime('2015-06-24 07:00', '%Y-%m-%d %H:%M')
        _now = datetime.now()

        messages = []
        revise_ciclo = [find_text for find_text in mensajes_ciclo if find_text in text.lower()]

        if len(revise_ciclo) > 0:

            _match = False
            while (not _match):
                _end_cycle = _init_cycle + timedelta(hours=175)
                if (_end_cycle < _now):
                    _init_cycle = _end_cycle
                else:
                    _match = True

            messages.append('El final de este ciclo es en:\n{0}'.format(str(_end_cycle)))

        revise_cp = [find_text for find_text in mensajes_cp if find_text in text.lower()]

        if len(revise_cp) > 0:

            _match = False
            while (not _match):
                _end_cycle = _init_cycle + timedelta(hours=5)
                if (_end_cycle < _now):
                    _init_cycle = _end_cycle
                else:
                    _match = True

            messages.append('El proximo CheckPoint es en:\n{0}'.format(str(_end_cycle)))

        msg = ", ".join(messages)

        _respuesta = msg.encode('utf-8')
        bot.reply_to(message, _respuesta)

bot.polling()