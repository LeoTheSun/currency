from internal.adapter.db.sqlite.utils import format_query
from pkg.sqlite.sqlite import SQLite
from logging import Logger
from internal.domain.entity.exchange_rate import ExchangeRate
from datetime import date
from decimal import Decimal


class ExchangeRateStorage:
    def __init__(self, sqlite: SQLite, logger: Logger):
        self.__sqlite = sqlite
        self.__logger = logger

    def exists(self, exchangeRate: ExchangeRate) -> bool:
        q = """
            SELECT EXISTS (
			    SELECT id
			    FROM exchange_rates
			    WHERE date = ? AND code = ?
		    );
        """
        self.__logger.debug(f"SQL Query: '{format_query(q)}'")
        exists = bool(self.__sqlite.query_row(q, (str(exchangeRate.Date), exchangeRate.Code, ))[0])
        return exists
    
    def create(self, exchangeRate: ExchangeRate) -> ExchangeRate:
        q = """
            INSERT INTO exchange_rates (date, count, rate, change, code)
            VALUES (?, ?, ?, ?, ?)
            RETURNING id;
        """
        self.__logger.debug(f"SQL Query: '{format_query(q)}'")
        raw_id = self.__sqlite.query_row(q, (str(exchangeRate.Date), exchangeRate.Count, str(exchangeRate.Rate), str(exchangeRate.Change), exchangeRate.Code,))
        exchangeRate = ExchangeRate(
            Id=int(raw_id[0]),
            Date=exchangeRate.Date,
            Count=exchangeRate.Count,
            Rate=exchangeRate.Rate,
            Change=exchangeRate.Change,
            Code=exchangeRate.Code
        )
        return exchangeRate
    
    def get_one(self, exchangeRate: ExchangeRate) -> ExchangeRate:
        q = """
			SELECT id, date, count, rate, change, code
			FROM exchange_rates
			WHERE date = ? AND code = ?;
        """
        self.__logger.debug(f"SQL Query: '{format_query(q)}'")
        raw_exchangeRate = self.__sqlite.query_row(q, (str(exchangeRate.Date), exchangeRate.Code, ))
        
        d = str(raw_exchangeRate[1]).split('-')
        exchangeRate = ExchangeRate(
            Id=int(raw_exchangeRate[0]),
            Date=date(int(d[0]), int(d[1]), int(d[2])),
            Count=int(raw_exchangeRate[2]),
            Rate=Decimal(raw_exchangeRate[3]),
            Change=Decimal(raw_exchangeRate[4]),
            Code=str(raw_exchangeRate[5]),
        )
        return exchangeRate

    def update(self, exchangeRate: ExchangeRate) -> None:
        q = """
            UPDATE exchange_rates
            SET rate = ?, change = ?, count = ?
            WHERE date = ? AND code = ?;
        """
        self.__logger.debug(f"SQL Query: '{format_query(q)}'")
        self.__sqlite.exec(q, (str(exchangeRate.Rate), str(exchangeRate.Change), exchangeRate.Count, str(exchangeRate.Date), exchangeRate.Code,))

    def create_or_update(self, exchangeRate: ExchangeRate) -> ExchangeRate:
        if self.exists(exchangeRate) is False:
            exchangeRate = self.create(exchangeRate)
            return exchangeRate
        er = self.get_one(exchangeRate)
        if (er.Count == exchangeRate.Count and er.Rate == exchangeRate.Rate and er.Change == exchangeRate.Change):
            exchangeRate = er
            return exchangeRate
        self.update(exchangeRate)
        exchangeRate = ExchangeRate(
            Id=er.Id,
            Date=er.Date,
            Count=exchangeRate.Count,
            Rate=exchangeRate.Rate,
            Change=exchangeRate.Change,
            Code=er.Code
        )
        return exchangeRate
        
    
    def get_many(self, exchangeRate: ExchangeRate) -> list[ExchangeRate]:
        q = """
            SELECT id, date, count, rate, change, code
            FROM exchange_rates
            WHERE code = ?;
        """
        self.__logger.debug(f"SQL Query: '{format_query(q)}'")
        raw_exchangeRate_list = self.__sqlite.query(q, (exchangeRate.Code,))
        exchangeRate_list: list[ExchangeRate] = []
        for raw_exchangeRate in raw_exchangeRate_list:
            d = str(raw_exchangeRate[1]).split('-')
            exchangeRate = ExchangeRate(
                Id=int(raw_exchangeRate[0]),
                Date=date(int(d[0]), int(d[1]), int(d[2])),
                Count=int(raw_exchangeRate[2]),
                Rate=Decimal(raw_exchangeRate[3]),
                Change=Decimal(raw_exchangeRate[4]),
                Code=str(raw_exchangeRate[5]),
            )
            exchangeRate_list.append(exchangeRate)
        return exchangeRate_list