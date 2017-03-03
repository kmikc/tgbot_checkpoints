#!/usr/bin/env python
# -*- coding: utf-8 -*-

from telegram.ext import Updater, CommandHandler, Job
from datetime import datetime, timedelta
from time import mktime
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

def get_chat_timezone(p_chat_id):
    query = "SELECT timezone FROM chat_settings WHERE chat_id={CHATID};".format(CHATID=p_chat_id)

    conn = lite.connect('checkpoint_settings.db')
    cur = conn.cursor()
    cur.execute(query)
    str_timezone = cur.fetchone()

    str_timezone = str_timezone[0]
    conn.commit()
    conn.close()

    return str_timezone


def get_chat_gmtvalue(p_chat_id):
    query = "SELECT gmt_value FROM chat_settings WHERE chat_id={CHATID};".format(CHATID=p_chat_id)

    conn = lite.connect('checkpoint_settings.db')
    cur = conn.cursor()
    cur.execute(query)
    str_timezone = cur.fetchone()

    str_timezone = str_timezone[0]
    conn.commit()
    conn.close()

    return str_timezone


def info(bot, update):
    chat_id = update.message.chat.id
    update.message.reply_text("Timezone: " + str(get_chat_timezone(chat_id)))
    update.message.reply_text("GMT: " + str(get_chat_gmtvalue(chat_id)))


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
            conn = lite.connect('checkpoint_settings.db')
            cur = conn.cursor()

            # Cuenta regstros existentes
            cur.execute("SELECT COUNT(*) FROM chat_settings WHERE chat_id=:CHATID", {"CHATID": update.message.chat.id})
            row_count = cur.fetchone()[0]

            # Seg�n resultado obtenido, actualiza o inserta
            if row_count > 0:
                cur.execute("UPDATE chat_settings SET gmt_value=? WHERE chat_id=?", (var_gmt, update.message.chat.id))
                conn.commit()
                str_result = 'Registro actualizado'
            else:
                cur.execute("INSERT INTO chat_settings (chat_id, gmt_value) VALUES (?, ?)", (update.message.chat.id, var_gmt))
                conn.commit()
                str_result = 'Registro ingresado'

        except:
            str_result = 'No se pudo conectar'

        finally:
            if conn:
                conn.close()

    update.message.reply_text(str_result)


def checkpoints(bot, update):
    #str_result = '=)'
    #update.message.reply_text(str_result)

    chat_id = update.message.chat.id
    gmt_value = get_chat_gmtvalue(chat_id)
    #t0 = datetime.strptime('2014-07-09 15', '%Y-%m-%d %H') + timedelta(hours=gmt_value)
    t0 = datetime.strptime('2017-02-26 03', '%Y-%m-%d %H') + timedelta(hours=gmt_value)
    hours_per_cycle = 175

    t = datetime.now()
    print t

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
    update.message.reply_text(res)


def notify_checkpoint(bot, job):
    if check_checkpoint() == True:
        l_chatid = get_enabled_chat_notification()
        for k_chatid in l_chatid:
            print "notify_checkpoint: " + str(k_chatid)
            bot.sendMessage(chat_id=k_chatid, text="Oli")


def check_checkpoint():
    print datetime.now()
    return False


def get_enabled_chat_notification():
    #chat_list = (37307558, -1001055036813)
    query = "SELECT chat_id FROM chat_settings WHERE notify_cp = 1"
    chat_list = []
    print query

    conn = lite.connect('checkpoint_settings.db')
    cur = conn.cursor()
    cur.execute(query)

    rows = cur.fetchall()
    for row_item in rows:
        print row_item[0]
        chat_list.append(row_item[0])

    print chat_list

    conn.commit()
    conn.close()

    return chat_list


# TOKEN
updater = Updater('140837439:AAFR0JP70z5QsNmKB60aX_mEfbfrtkdQ8wY')

# COMANDOS
updater.dispatcher.add_handler(CommandHandler('info', info))
updater.dispatcher.add_handler(CommandHandler('help', help))
updater.dispatcher.add_handler(CommandHandler('gmt', gmt, pass_args=True))
updater.dispatcher.add_handler(CommandHandler('checkpoints', checkpoints))

# JOB QUEUE
jobqueue = updater.job_queue
checkpoint_queue = Job(notify_checkpoint, 10.0)
jobqueue.put(checkpoint_queue, next_t=5.0)

updater.start_polling()
updater.idle()
