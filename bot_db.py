from peewee import SqliteDatabase, Model, IntegerField

db = SqliteDatabase('checkpoint_settings.db')


class BaseModel(Model):

    class Meta:
        database = db


class ChatSettings(BaseModel):

    id = IntegerField(primary_key=True)
    # chat_id
    # gmt_value

    class Meta:
        table_name = 'chat_settings'


class NextNotification(BaseModel):

    id = IntegerField(primary_key=True)
    # next_cp_utc
    # next_cycle_utc
    # next_cp_number

    class Meta:
        table_name = 'next_notification_utc'
