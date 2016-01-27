#!/usr/bin/env python
# -*- coding: utf-8 -*-

import StringIO
import json
import logging
import random
import urllib
import urllib2
from datetime import datetime, timedelta
from unicodedata import normalize

TOKEN = '___INSERTE_TOKEN_AQUI___'
TOKEN = '140837439:AAFR0JP70z5QsNmKB60aX_mEfbfrtkdQ8wY'
BASE_URL = 'https://api.telegram.org/bot' + TOKEN + '/'

def setEnabled(chat_id, yes):
    es = EnableStatus.get_or_insert(str(chat_id))
    es.enabled = yes
    es.put()


def getEnabled(chat_id):
    es = EnableStatus.get_by_id(str(chat_id))
    if es:
        return es.enabled
    return False

