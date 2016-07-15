#!/usr/bin/env python
# -*- coding: utf-8 -*-
import telebot
import logging
from unicodedata import normalize
from datetime import datetime, timedelta
from time import mktime
import sqlite3 as lite
import sys

bot = telebot.TeleBot("140837439:AAFR0JP70z5QsNmKB60aX_mEfbfrtkdQ8wY")

#
# COMANDOS
#

@bot.message_handler(commands=['help', 'gmt', 'checkpoints'])
def send_welcome(message):

    if 'help' in message.text:
        bot.reply_to(message, "Por ahora con solo escribir 'proximo cp', 'fin de ciclo' o similares, se mostrará la fecha y hora")

    elif 'gmt' in message.text:
        #var_gmt = sys.argv[1]
        try:
            var_gmt = int(message.text.replace("/gmt ", ""))
            ok = True

        except:
            resp = "Valor no numérico"
            ok = False

        if ok:
            conn = None
            try:
                conn = lite.connect('gmt.db')
                cur = conn.cursor()

                # Cuenta regstros existentes
                cur.execute("SELECT COUNT(*) FROM chat_gmt WHERE chat_id=:CHATID", {"CHATID": message.chat.id})
                row_count = cur.fetchone()[0]

                # Seg�n resultado obtenido, actualiza o inserta
                if row_count > 0:
                    bot.reply_to(message, 'UPDATE')
                    # TO DO!!!!
                    resp = 'Registro actualizado'
                else:
                    bot.reply_to(message, 'INSERT')
                    cur.execute("INSERT INTO chat_gmt (chat_id, gmt_value) VALUES (?, ?)", (message.chat.id, var_gmt))
                    conn.commit()
                    resp = 'Registro ingresado'

            except:
                resp = 'No se pudo conectar'

            finally:
                if conn:
                    conn.close()

        bot.reply_to(message, resp)

    elif 'checkpoints' in message.text:
        t0 = datetime.strptime('2014-07-09 11', '%Y-%m-%d %H')
        hours_per_cycle = 175

        t = datetime.now()

        seconds = mktime(t.timetuple()) - mktime(t0.timetuple())
        cycles = seconds // (3600 * hours_per_cycle)
        start = t0 + timedelta(hours=cycles * hours_per_cycle)
        checkpoints = map(lambda x: start + timedelta(hours=x), range(0, hours_per_cycle, 5))
        nextcp_mark = False

        acheckpoints = []
        for num, checkpoint in enumerate(checkpoints):

            if checkpoint > t and nextcp_mark == False:
                str_checkpoint = format(str(checkpoint)) + ' <---'
                nextcp_mark = True
            else:
                str_checkpoint = format(str(checkpoint))

            acheckpoints.append(str_checkpoint)


        res = ' \n '.join(acheckpoints)
        bot.reply_to(message, res)

#
# FILTRAR MENSAJES "proximo cp"... etc.
#

@bot.message_handler(func=lambda message: True)
def echo_all(message):
    #logging.basicConfig(filename='bot_ingress_checkpoints.log', filemode='w', level=logging.DEBUG)
    #logging.info(message)

    #text = message.text
    text = normalize('NFKD', message.text).encode('ASCII', 'ignore')
    mensajes_cp = [u'proximo cp', u'siguiente cp', u'proximo checkpoint', u'siguiente checkpoint', u'proximo check point', u'siguiente check point']
    mensajes_ciclo = [u'fin de ciclo', u'fin del ciclo', u'final de ciclo', u'final del ciclo', u'proximo ciclo', u'siguiente ciclo', u'ciclo nuevo', u'nuevo ciclo']
    all_messages = mensajes_cp + mensajes_ciclo
    revise_message = [find_text for find_text in all_messages if find_text in text.lower()]

    if len(revise_message) > 0:
        _init_cycle = datetime.strptime('2015-06-24 06:00', '%Y-%m-%d %H:%M')
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


#while True:
#    try:
#        bot.polling(none_stop=True)
#    except request.exceptions.ConnectionError as e:
#        print >> sys.stderr, str(e)
#        time.sleep(15)

bot.polling(none_stop=True)
