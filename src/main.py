import logging
import structlog
from fastapi import FastAPI
from internal.controller.graph import GraphHandler
from internal.controller.reader import ReaderHandler
from pkg.logging.logging import get_logger, handle_app_logs_to_custom_logger
from pkg.sqlite.sqlite import SQLite
from config.config import new_config
from internal.adapter.db.sqlite.currency_code import CurrencyCodeStorage
from internal.adapter.db.sqlite.delta_rate import DeltaRateStorage
from internal.adapter.db.sqlite.exchange_rate import ExchangeRateStorage
from internal.adapter.db.sqlite.parameter import parameterStorage
from internal.domain.usecase.currency_code import CurrencyCodeUsecase
from internal.domain.usecase.exchange_rate import ExchangeRateUsecase
from internal.webapi.currency_code import CurrencyCodeWebAPi
from internal.webapi.exchange_rate import ExchangeRateWebAPi


try:
    cfg = new_config()
except Exception as e:
    logging.fatal(e)
    exit()
logger = get_logger('main.logger', 'INFO')
try:
    sqlite = SQLite(cfg.sqlite)
except Exception as e:
    logger.fatal(e)
    exit()
sqlite.setup_database()
sqlite.set_std_date(cfg.sqlite.std_date)
storageCurrencyCode = CurrencyCodeStorage(sqlite, logger)
webAPiCurrencyCode = CurrencyCodeWebAPi()
usecaseCurrencyCode = CurrencyCodeUsecase(storageCurrencyCode, webAPiCurrencyCode)
storageExchangeRate = ExchangeRateStorage(sqlite, logger)
storageDeltaRate = DeltaRateStorage(sqlite, logger)
storageParameter = parameterStorage(sqlite, logger)
webAPiExchangeRate = ExchangeRateWebAPi()
usecaseExchangeRate = ExchangeRateUsecase(storageExchangeRate, storageDeltaRate, storageParameter, webAPiExchangeRate)
handlerReader = ReaderHandler(usecaseExchangeRate, usecaseCurrencyCode)
handlerGraph = GraphHandler(usecaseExchangeRate)
app = FastAPI(
    title=cfg.app.name,
    version=cfg.app.version
)
handlerReader.register(app)
handlerGraph.register(app)
access_logger = structlog.stdlib.get_logger('api.access')
handle_app_logs_to_custom_logger(app, access_logger)



