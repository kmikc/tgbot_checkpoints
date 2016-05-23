#!/usr/bin/env python
# -*- coding: utf-8 -*-

import StringIO
import json
import logging
import random
import urllib
import urllib2
# import datetime
from datetime import datetime, timedelta
#from pytz import timezone
from unicodedata import normalize

# for sending images
#from PIL import Image
#import multipart

# standard app engine imports
#from google.appengine.api import urlfetch
#from google.appengine.ext import ndb
#import webapp2

TOKEN = '___INSERTE_TOKEN_AQUI___'
TOKEN = '116784588:AAHOTpxmRQ-iFTXVyNw_3Ad-Z5aynsdWuGQ'

BASE_URL = 'https://api.telegram.org/bot' + TOKEN + '/'


# ================================

#class EnableStatus(ndb.Model):
    # key name: str(chat_id)
#    enabled = ndb.BooleanProperty(indexed=False, default=False)


# ================================

def setEnabled(chat_id, yes):
    es = EnableStatus.get_or_insert(str(chat_id))
    es.enabled = yes
    es.put()


def getEnabled(chat_id):
    es = EnableStatus.get_by_id(str(chat_id))
    if es:
        return es.enabled
    return False


# ================================

class MeHandler(webapp2.RequestHandler):
    def get(self):
        urlfetch.set_default_fetch_deadline(60)
        self.response.write(json.dumps(json.load(urllib2.urlopen(BASE_URL + 'getMe'))))


class GetUpdatesHandler(webapp2.RequestHandler):
    def get(self):
        urlfetch.set_default_fetch_deadline(60)
        self.response.write(json.dumps(json.load(urllib2.urlopen(BASE_URL + 'getUpdates'))))


class SetWebhookHandler(webapp2.RequestHandler):
    def get(self):
        urlfetch.set_default_fetch_deadline(60)
        url = self.request.get('url')
        if url:
            self.response.write(json.dumps(json.load(urllib2.urlopen(BASE_URL + 'setWebhook', urllib.urlencode({'url': url})))))


class WebhookHandler(webapp2.RequestHandler):
    def post(self):
        urlfetch.set_default_fetch_deadline(60)
        body = json.loads(self.request.body)
        logging.info('request body:')
        logging.info(body)
        self.response.write(json.dumps(body))

        update_id = body['update_id']
        message = body['message']
        message_id = message.get('message_id')
        date = message.get('date')
        #text = normalize('NFKD', message.get('text')).encode('ASCII', 'ignore')
        text = message.get('text')
        fr = message.get('from')
        chat = message['chat']
        chat_id = chat['id']

        mensajes_cp = [u'proximo cp', u'siguiente cp', u'proximo checkpoint', u'siguiente checkpoint', u'proximo check point', u'siguiente check point']
        mensajes_ciclo = [u'fin de ciclo', u'fin del ciclo', u'final de ciclo', u'final del ciclo', u'proximo ciclo', u'siguiente ciclo', u'ciclo nuevo', u'nuevo ciclo']

        all_messages = mensajes_cp + mensajes_ciclo

        if not text:
            logging.info('no text')
            return
        else:
            text = normalize('NFKD', text).encode('ASCII', 'ignore')

        def reply(msg=None, img=None):
            if msg:
                resp = urllib2.urlopen(BASE_URL + 'sendMessage', urllib.urlencode({
                    'chat_id': str(chat_id),
                    'text': msg.encode('utf-8'),
                    'disable_web_page_preview': 'true',
                    'reply_to_message_id': str(message_id),
                })).read()
            elif img:
                resp = multipart.post_multipart(BASE_URL + 'sendPhoto', [
                    ('chat_id', str(chat_id)),
                    ('reply_to_message_id', str(message_id)),
                ], [
                    ('photo', 'image.jpg', img),
                ])
            else:
                logging.error('no msg or img specified')
                resp = None

            logging.info('send response:')
            logging.info(resp)

        def reply_message():

            _init_cycle = datetime.strptime('2015-06-24 07:00', '%Y-%m-%d %H:%M')
            _now = datetime.now() - timedelta(hours=3)
            #fmt = "%Y-%m-%d %H:%M:%S %Z%z"
            #now = datetime.now(timezone('America/Santiago'))

            messages = []

            revise_ciclo = [find_text for find_text in mensajes_ciclo if find_text in text.lower()]

            if len(revise_ciclo) > 0:

                ding_ding_ding = False
                while (not ding_ding_ding):
                    _end_cycle = _init_cycle + timedelta(hours=175)
                    if (_end_cycle < _now):
                        _init_cycle = _end_cycle
                    else:
                        ding_ding_ding = True

                messages.append('El final de este ciclo es en:\n{0}'.format(str(_end_cycle)))

            revise_cp = [find_text for find_text in mensajes_cp if find_text in text.lower()]

            if len(revise_cp) > 0:

                ding_ding_ding = False
                while (not ding_ding_ding):
                    _end_cycle = _init_cycle + timedelta(hours=5)
                    if (_end_cycle < _now):
                        _init_cycle = _end_cycle
                    else:
                        ding_ding_ding = True

                messages.append('El proximo CheckPoint es en:\n{0}'.format(str(_end_cycle)))

            msg = ", ".join(messages)

            resp = urllib2.urlopen(BASE_URL + 'sendMessage', urllib.urlencode(
                {
                    'chat_id': str(chat_id),
                    'text': msg.encode('utf-8'),
                    'disable_web_page_preview': 'true',
                    #'reply_to_message_id': str(message_id),
                })).read()
            logging.info(resp)

        revise_message = [find_text for find_text in all_messages if find_text in text.lower()]

        if text.startswith('/'):
            if text == '/start':
                reply('Bot enabled')
                setEnabled(chat_id, True)

            elif text == '/stop':
                reply('Bot disabled')
                setEnabled(chat_id, False)
            elif text == '/image':
                img = Image.new('RGB', (512, 512))
                base = random.randint(0, 16777216)
                pixels = [base+i*j for i in range(512) for j in range(512)]  # generate sample image
                img.putdata(pixels)
                output = StringIO.StringIO()
                img.save(output, 'JPEG')
                reply(img=output.getvalue())
            elif text == '/status':
                reply('Status: ', chat_id)

#        elif 'ping' in text.lower():
#            reply('pong xD')

        elif len(revise_message) > 0:
            reply_message()


app = webapp2.WSGIApplication([
    ('/me', MeHandler),
    ('/updates', GetUpdatesHandler),
    ('/set_webhook', SetWebhookHandler),
    ('/webhook', WebhookHandler),
], debug=True)
