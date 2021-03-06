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

#
#
# DEVUELVE EL TIMEZONE GUARDADO, SEGUN EL CHATID
#
#


def get_chat_timezone(p_chat_id):
    query = "SELECT timezone FROM chat_settings WHERE chat_id={CHATID};".\
        format(CHATID=p_chat_id)

    conn = lite.connect('checkpoint_settings.db')
    cur = conn.cursor()
    cur.execute(query)
    str_timezone = cur.fetchone()

    str_timezone = str_timezone[0]
    conn.commit()
    conn.close()

    return str_timezone


#
#
# DEVUELVE EL VALOR GUARDADO PARA EL GMT, SEGUN EL CHATID
#
#

def get_chat_gmtvalue(p_chat_id):
    query = "SELECT gmt_value FROM chat_settings WHERE chat_id={CHATID};".\
        format(CHATID=p_chat_id)

    conn = lite.connect('checkpoint_settings.db')
    cur = conn.cursor()
    cur.execute(query)
    str_timezone = cur.fetchone()

    str_timezone = str_timezone[0]
    conn.commit()
    conn.close()

    return str_timezone


#
#
# MUESTRA LOS VALORES GUARDADOS EN LA CONFIGURACION DE GMT Y TIMEZONE
#
#

def info(bot, update):
    chat_id = update.message.chat.id
    # update.message.reply_text("Timezone: " + str(get_chat_timezone(chat_id)))
    update.message.reply_text("GMT: " + str(get_chat_gmtvalue(chat_id)))
    update.message.reply_text("Chat id: " + str(chat_id))


#
#
# MUESTRA TEXTO DE AYUDA
#
#

def help(bot, update):
    str_result = '=)'
    update.message.reply_text(str_result)


#
#
# CONFIGURA EL VALOR DEL GMT, Y LO GUARDA EN DB
#
#

def gmt(bot, update, args):
    str_result = 'args: {}'.format(args[0])
    try:
        var_gmt = int(args[0])
        ok = True

    except ValueError:
        str_result = "Valor no numérico"
        ok = False

    if ok:
        conn = None
        try:
            conn = lite.connect('checkpoint_settings.db')
            cur = conn.cursor()

            # Cuenta regstros existentes
            cur.execute("SELECT COUNT(*) FROM chat_settings WHERE\
                chat_id=:CHATID", {"CHATID": update.message.chat.id})
            row_count = cur.fetchone()[0]

            # Segun resultado obtenido, actualiza o inserta
            if row_count > 0:
                cur.execute("UPDATE chat_settings SET gmt_value=? WHERE\
                    chat_id=?", (var_gmt, update.message.chat.id))
                conn.commit()
                str_result = 'Registro actualizado'
            else:
                cur.execute("INSERT INTO chat_settings (chat_id, gmt_value)\
                    VALUES (?, ?)", (update.message.chat.id, var_gmt))
                conn.commit()
                str_result = 'Registro ingresado'

        except:
            str_result = 'No se pudo conectar'

        finally:
            if conn:
                conn.close()

    update.message.reply_text(str_result)


#
#
# MUESTRA LISTADO DE CHECKPOINTS PARA EL ACTUAL CICLO
#
#

def checkpoints(bot, update):

    chat_id = update.message.chat.id
    gmt_value = get_chat_gmtvalue(chat_id)
    t0 = datetime.strptime('2017-02-26 03', '%Y-%m-%d %H') +\
        timedelta(hours=gmt_value)
    hours_per_cycle = 175

    t = datetime.now() + timedelta(hours=gmt_value)
    print(t)
    #
    # TO DO:
    #
    # Usar los tiempos de checkpoints en UTC, porque en el server da una hora,
    # y en local, a la hora le resta el gmt_value
    # Provocando una diferencia cuando se muestran
    # los checkpoints local vs server
    #

    seconds = mktime(t.timetuple()) - mktime(t0.timetuple())
    cycles = seconds // (3600 * hours_per_cycle)
    start = t0 + timedelta(hours=cycles * hours_per_cycle)
    checkpoints = map(lambda x: start + timedelta(hours=x),
                      range(0, hours_per_cycle, 5))
    nextcp_mark = False

    # Busco el año y número de ciclo en curso
    query = "SELECT cycle_year, cycle_number FROM next_notification_utc"
    conn = lite.connect("checkpoint_settings.db")
    cur = conn.cursor()
    cur.execute(query)

    row = cur.fetchone()
    current_cycle_year = row[0]
    current_cycle_number = row[1]

    acheckpoints = []

    str_checkpoint = "Ciclo en curso: " + format(current_cycle_year) +\
        "." + format(current_cycle_number)
    acheckpoints.append(str_checkpoint)

    i = 1
    for num, checkpoint in enumerate(checkpoints):

        if checkpoint > t and nextcp_mark is False:
            str_checkpoint = '- - - - - - - - - - - - - - - - - - - - - - -'
            acheckpoints.append(str_checkpoint)
            str_checkpoint = '#' + format(i) + ' - ' + format(str(checkpoint))
            acheckpoints.append(str_checkpoint)
            str_checkpoint = '- - - - - - - - - - - - - - - - - - - - - - -'
            nextcp_mark = True
        else:
            str_checkpoint = '#' + format(i) + ' - ' + format(str(checkpoint))

        i += 1
        acheckpoints.append(str_checkpoint)

    res = ' \n '.join(acheckpoints)
    update.message.reply_text(res)


def notify_checkpoint(bot, job):
    """
    SE EJECUTA CADA 10 SEGUNDOS PARA VERIFICAR SI YA PASO UN CHECKPOINT
    Y NOTIFICA A LOS GRUPOS QUE TENGAN HABILITADO
    """
    str_check_checkpoint = check_checkpoint()
    if str_check_checkpoint != '---':
        l_chatid = get_enabled_chat_notification()
        for k_chatid in l_chatid:
            try:
                gmt_value = get_chat_gmtvalue(k_chatid)
                cp_count = get_checkpoint_count()

                # Busco año y ciclo en curso
                query = "SELECT cycle_year, cycle_number FROM\
                    next_notification_utc"
                conn = lite.connect("checkpoint_settings.db")
                cur = conn.cursor()
                cur.execute(query)

                row = cur.fetchone()
                current_cycle_year = row[0]
                current_cycle_number = row[1]

                if str_check_checkpoint == 'CP':
                    bot.sendMessage(chat_id=k_chatid, text=str(current_cycle_year) + "." + str(current_cycle_number) + " - CHECKPOINT! #" + str(cp_count))
                    print("notify_checkpoint: " + str(k_chatid) + " | gmt_value: " + str(gmt_value))

                if str_check_checkpoint == 'CYCLE':
                    bot.sendMessage(chat_id=k_chatid, text=str(current_cycle_year) + "." + str(current_cycle_number) + " - CHECKPOINT! #" + str(cp_count) + ' - FIN DE CICLO!')
                    print("notify_checkpoint: FIN DE CICLO " + str(k_chatid) + " | gmt_value: " + str(gmt_value))

            except Exception as e:
                print(str(k_chatid) + ' ' + str(e))


def check_checkpoint():
    """
    COMPARA LA FECHA Y HORA ACTUAL (EN UTC) CON LA FECHA Y HORA GUARDADA
    PARA EL PROXIMO CHECKPOINT SI FECHA Y HORA ACTUAL ES MAYOR, ACTUALIZA
    EN 5 HORAS MAS EL PROXIMO CHECKPOINT Y DEVUELVE "TRUE",
    DE LO CONTRARIO DEVUELVE "FALSE"
    """

    str_return = '---'

    utc_now = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')
    print("utc_now       : ", utc_now)

    query = "SELECT next_cp_utc, next_cycle_utc, next_cp_number, cycle_year,\
        cycle_number FROM next_notification_utc"
    conn = lite.connect("checkpoint_settings.db")
    cur = conn.cursor()
    cur.execute(query)

    row = cur.fetchone()
    next_cp_utc = row[0]
    next_cycle_utc = row[1]
    next_cp_number = row[2]
    current_cycle_year = row[3]
    current_cycle_number = row[4]

    conn.commit()

    if utc_now > next_cp_utc:
        next_cp_utc = datetime.strptime(row[0], '%Y-%m-%d %H:%M:%S')
        next_cycle_utc = datetime.strptime(row[1], '%Y-%m-%d %H:%M:%S')
        str_return = 'CP'
        new_next_cp_utc = next_cp_utc + timedelta(hours=5)
        new_next_cp_utc = str(new_next_cp_utc)
        new_next_cp_number = next_cp_number + 1

        # Fin de ciclo?
        if new_next_cp_number > 35:
            new_next_cp_number = 1
            new_next_cycle_utc = next_cycle_utc + timedelta(hours=175)
            new_next_cycle_utc = str(new_next_cycle_utc)

            current_cycle_number += 1
            if current_cycle_number > 50:
                current_cycle_number = 1
                current_cycle_year += 1

            query_update = "UPDATE next_notification_utc SET next_cycle_utc = '" + new_next_cycle_utc + "', cycle_year = " + str(current_cycle_year) + ", cycle_number = " + str(current_cycle_number)
            cur.execute(query_update)
            conn.commit()

            str_return = 'CYCLE'

        query_update = "UPDATE next_notification_utc SET next_cp_utc = '" + new_next_cp_utc + "', next_cp_number = " + str(new_next_cp_number)
        cur.execute(query_update)
        conn.commit()

    conn.close()

    return str_return


#
#
# RECORRE LA LISTA DE CHATS QUE ESTAN ALMACENADOS
# Y REVISA SI TIENEN HABILITA LA OPCION PARA NOTIFICAR EL CHECKPOINT
# DEVUELVE "TRUE" O "FALSE" SEGUN SEA EL CASO
#
#

def get_enabled_chat_notification():
    query = "SELECT chat_id FROM chat_settings WHERE notify_cp = 1"
    chat_list = []

    conn = lite.connect('checkpoint_settings.db')
    cur = conn.cursor()
    cur.execute(query)

    rows = cur.fetchall()
    for row_item in rows:
        chat_list.append(row_item[0])

    conn.commit()
    conn.close()

    return chat_list


#
#
# MUESTRA EL ACTUAL NUMERO DE CHECKPOINT,
# RESTANDO 1 AL NUMERO GUARDADO (Mejorar esto)
#
#

def get_checkpoint_count():
    query = "SELECT next_cp_number FROM next_notification_utc"

    conn = lite.connect('checkpoint_settings.db')
    cur = conn.cursor()
    cur.execute(query)
    row = cur.fetchone()

    cp_count = row[0]
    conn.commit()
    conn.close()

    cp_count = cp_count - 1

    if cp_count < 1:
        cp_count = 35

    return cp_count


#
#
# CONFIGURA EL VALOR PARA COLUMNA DE NOTIFICACION,
# PARA RECIBIR AVISOS EN CADA CHECKPOINT
#
#

def notify(bot, update, args):
    print("notify")
    str_result = 'args: {}'.format(args[0])
    int_notify = 0
    print(str_result)
    try:
        var_notify = args[0]
        print(var_notify)
        ok = False

        if var_notify == 'on':
            int_notify = 1
            str_result = 'Notificaciones de checkpoints activadas'
            ok = True

        if var_notify == 'off':
            int_notify = 0
            str_result = 'Notificaciones de checkpoints desactivadas'
            ok = True

        if var_notify != 'on' and var_notify != 'off':
            str_result = 'Parámetros aceptados: "/notify on" o "/notify off"'
            ok = False

    except:
        str_result = "No se confguró nada"
        ok = False

    print(var_notify)
    print(int_notify)

    if ok:
        print("ok")
        conn = None
        try:
            conn = lite.connect('checkpoint_settings.db')
            cur = conn.cursor()

            # Cuenta regstros existentes
            cur.execute("SELECT COUNT(*) FROM chat_settings WHERE chat_id=:CHATID", {"CHATID": update.message.chat.id})
            row_count = cur.fetchone()[0]

            print("row_count: ", row_count)

            # Segun resultado obtenido, actualiza o inserta
            if row_count > 0:
                print("update: ", update.message.chat_id, " int_notify: ", int_notify)
                cur.execute("UPDATE chat_settings SET notify_cp=? WHERE chat_id=?", (int_notify, update.message.chat.id))
                conn.commit()
            else:
                print("insert ", update.message.chat_id)
                cur.execute("INSERT INTO chat_settings (chat_id, notify_cp) VALUES (?, ?)", (update.message.chat.id, int_notify))
                conn.commit()

        except:
            str_result = 'No se pudo conectar'

        finally:
            if conn:
                conn.close()

    update.message.reply_text(str_result)


# TOKEN
token = open('token').read().rstrip('\n')
updater = Updater(token)

# COMANDOS
updater.dispatcher.add_handler(CommandHandler('info', info))
updater.dispatcher.add_handler(CommandHandler('help', help))
updater.dispatcher.add_handler(CommandHandler('gmt', gmt, pass_args=True))
updater.dispatcher.add_handler(CommandHandler('checkpoints', checkpoints))
updater.dispatcher.add_handler(
    CommandHandler('notify', notify, pass_args=True))

# JOB QUEUE
jobqueue = updater.job_queue
checkpoint_queue = Job(notify_checkpoint, 10.0)
jobqueue.put(checkpoint_queue, next_t=5.0)

updater.start_polling()
updater.idle()
