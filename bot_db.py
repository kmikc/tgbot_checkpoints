import datetime

from peewee import (SqliteDatabase, Model, IntegerField,
                    DateTimeField)

db = SqliteDatabase('checkpoint_settings.db')


class BaseModel(Model):

    class Meta:
        database = db


class BotSettings(BaseModel):

    id = IntegerField(primary_key=True)
    chat_id = IntegerField()
    gmt_value = IntegerField()
    notify_cp = IntegerField()
    datetime = DateTimeField(default=datetime.datetime.now)
    # chat_type = CharField()
    # chat_title = CharField()
    # chat_username = CharField()

    class Meta:
        table_name = 'bot_settings'


class CycleSettings(BaseModel):

    id = IntegerField(primary_key=True)
    # next_cp_utc = DateTimeField()
    # next_cycle_utc = DateTimeField()
    # current_cp_number = IntegerField()
    # next_cp_number = IntegerField()

    class Meta:
        table_name = 'cycle_settings'
