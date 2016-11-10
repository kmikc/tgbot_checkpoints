#!/usr/bin/env python
# -*- coding: utf-8 -*-

from telegram.ext import Updater, CommandHandler
import sqlite3 as lite

'''

Una muestra de como viene el parámetro 'update'
para obtener, por ejemplo el chat id --> update.message.chat.id

{
    'message': {
        'migrate_to_chat_id': 0,
        'delete_chat_photo': False,
        'new_chat_photo': [],
        'entities': [{
            'length': 28,
            'type': u'bot_command',
            'offset': 0
        }],
        'text': u'/gmt@ingress_checkpoints_bot',
        'migrate_from_chat_id': 0,
        'channel_chat_created': False,
        'from': {
            'username': u'MalKarakter',
            'first_name': u'Rodrigo',
            'last_name': u'Parkes',
            'type': '',
            'id': 37307558
        },
        'supergroup_chat_created': False,
        'chat': {
            'username': '',
            'first_name': '',
            'all_members_are_admins': False,
            'title': u'Testeando',
            'last_name': '',
            'type': u'supergroup',
            'id': -1001055036813
        },
        'photo': [],
        'date': 1478750378,
        'group_chat_created': False,
        'caption': '',
        'message_id': 1049,
        'new_chat_title': ''
    },
    'update_id': 560641983
}
'''

def start(bot, update):
    update.message.reply_text('Oli')

def help(bot, update):
    str_result = '=)'
    update.message.reply_text(str_result)

def gmt(bot, update, args):
    str_result = 'args: {}'.format(args[0])
    try:
        var_gmt = int(args[0])
        ok = True

    except:
        str_result = "Valor no numérico"
        ok = False

    if ok:
        conn = None
        try:
            conn = lite.connect('gmt.db')
            cur = conn.cursor()

            # Cuenta regstros existentes
            cur.execute("SELECT COUNT(*) FROM chat_gmt WHERE chat_id=:CHATID", {"CHATID": update.message.chat.id})
            row_count = cur.fetchone()[0]

            # Seg�n resultado obtenido, actualiza o inserta
            if row_count > 0:
                cur.execute("UPDATE chat_gmt SET gmt_value=? WHERE chat_id=?", (var_gmt, update.message.chat.id))
                conn.commit()
                str_result = 'Registro actualizado'
            else:
                cur.execute("INSERT INTO chat_gmt (chat_id, gmt_value) VALUES (?, ?)", (update.message.chat.id, var_gmt))
                conn.commit()
                str_result = 'Registro ingresado'

        except:
            str_result = 'No se pudo conectar'

        finally:
            if conn:
                conn.close()

    update.message.reply_text(str_result)

def checkpoints(bot, update):
    str_result = '=)'
    update.message.reply_text(str_result)

# TOKEN
updater = Updater('140837439:AAFR0JP70z5QsNmKB60aX_mEfbfrtkdQ8wY')

# COMANDOS
updater.dispatcher.add_handler(CommandHandler('start', start))
updater.dispatcher.add_handler(CommandHandler('help', help))
updater.dispatcher.add_handler(CommandHandler('gmt', gmt, pass_args=True))
updater.dispatcher.add_handler(CommandHandler('checkpoints', checkpoints))

updater.start_polling()
updater.idle()
