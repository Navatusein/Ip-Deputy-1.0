import os
from os.path import join, dirname
from dotenv import load_dotenv
from dataclasses import dataclass


@dataclass
class DbConfig:
    connection_string: str


@dataclass
class TgBot:
    token: str
    admin_ids: list


@dataclass
class Config:
    db: DbConfig
    tg_bot: TgBot


def load_config():
    return Config(
        tg_bot=TgBot(
            token=os.environ.get("BOT_TOKEN"),
            admin_ids=list(map(int, os.environ.get("ADMINS").split(','))),
        ),
        db=DbConfig(
            connection_string=os.environ.get("DB_STRING"),
        ),
    )
