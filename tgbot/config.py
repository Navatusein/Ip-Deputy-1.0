from dataclasses import dataclass

from environs import Env


@dataclass
class TgBot:
    name: str
    token: str
    admin_ids: list[int]
    use_redis: bool


@dataclass
class Config:
    tg_bot: TgBot


def load_config(path: str = None):
    env = Env()
    env.read_env(path)

    return Config(
        tg_bot=TgBot(
            name=env.str("BOT_NAME"),
            token=env.str("BOT_TOKEN"),
            admin_ids=list(map(int, env.list("ADMINS"))),
            use_redis=env.bool("USE_REDIS"),
        ),
    )
