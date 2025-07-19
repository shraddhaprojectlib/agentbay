from peewee import *

db = SqliteDatabase("project.db")

class BaseModel(Model):
    class Meta:
        database = db


class User(BaseModel):
    name = CharField()
    email = CharField(unique=True)
    username = CharField(unique=True)
    password = CharField()


class Tool(BaseModel):
    name = CharField()
    type = CharField()
    description = TextField()
    url = TextField(unique=True)
    user = ForeignKeyField(User, backref="tools", on_delete="CASCADE")


db.connect()
db.create_tables([User,Tool])
print("🟢 database is online")
#runs only once till there are no updates in list
