from dataclasses import dataclass
from dataclasses_json import DataClassJsonMixin
from yamldataclassconfig.config import YamlDataClassConfig


@dataclass
class App(DataClassJsonMixin):
    name: str = None
    version: str = None


@dataclass
class SQLite(DataClassJsonMixin):
    path: str = None
    timeout: int = None
    tries: int = None
    std_date: str = None


@dataclass
class Config(YamlDataClassConfig):
    app: App = None
    sqlite: SQLite = None


def new_config(path: str = './config/config.yml') -> Config:
    cfg = Config()
    cfg.load(path)
    return cfg