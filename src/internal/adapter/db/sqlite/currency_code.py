from pkg.sqlite.sqlite import SQLite
from logging import Logger
from internal.domain.entity.currency_code import CurrencyCode
from internal.adapter.db.sqlite.utils import format_query



class CurrencyCodeStorage:
    def __init__(self, sqlite: SQLite, logger: Logger):
        self.__sqlite = sqlite
        self.__logger = logger

    def exists(self, currencyCode: CurrencyCode) -> bool:
        q = """
            SELECT EXISTS (
			    SELECT id
			    FROM currency_codes
			    WHERE code = ?
		    );
        """
        self.__logger.debug(f"SQL Query: '{format_query(q)}'")
        exists = bool(self.__sqlite.query_row(q, (currencyCode.Code,))[0])
        return exists

    def create(self, currencyCode: CurrencyCode) -> CurrencyCode:
        q = """
            INSERT INTO currency_codes (country, currency, code, number)
            VALUES (?, ?, ?, ?)
            RETURNING id;
        """
        self.__logger.debug(f"SQL Query: '{format_query(q)}'")
        raw_id = self.__sqlite.query_row(q, (currencyCode.Country, currencyCode.Currency, currencyCode.Code, currencyCode.Number,))
        currencyCode = CurrencyCode(
            Id=int(raw_id[0]),
            Country=currencyCode.Country,
            Currency=currencyCode.Currency,
            Code=currencyCode.Code,
            Number=currencyCode.Number
        )
        return currencyCode
    
    def get_one(self, currencyCode: CurrencyCode) -> CurrencyCode:
        q = """
			SELECT id, country, currency, code, number
			FROM currency_codes
			WHERE code = ?;
        """
        self.__logger.debug(f"SQL Query: '{format_query(q)}'")
        raw_currencyCode = self.__sqlite.query_row(q, (currencyCode.Code,))
        currencyCode = CurrencyCode(
            Id=int(raw_currencyCode[0]),
            Country=str(raw_currencyCode[1]),
            Currency=str(raw_currencyCode[2]),
            Code=str(raw_currencyCode[3]),
            Number=int(raw_currencyCode[4])
        )
        return currencyCode
    
    def update(self, currencyCode: CurrencyCode) -> None:
        q = """
            UPDATE currency_codes
            SET country = ?, currency = ?, number = ?
            WHERE code = ?;
        """
        self.__logger.debug(f"SQL Query: '{format_query(q)}'")
        self.__sqlite.exec(q, (currencyCode.Country, currencyCode.Currency, currencyCode.Number, currencyCode.Code,))

    def create_or_update(self, currencyCode: CurrencyCode) -> CurrencyCode:
        if self.exists(currencyCode) is False:
            currencyCode = self.create(currencyCode)
            return currencyCode
        cc = self.get_one(currencyCode)
        if (cc.Country == currencyCode.Country and cc.Currency == currencyCode.Currency and cc.Number == currencyCode.Number):
            currencyCode == cc
            return currencyCode
        self.update(currencyCode)
        currencyCode = CurrencyCode(
            Id=cc.Id,
            Country=currencyCode.Country,
            Currency=currencyCode.Currency,
            Code=cc.Code,
            Number=currencyCode.Number,
        )
        return currencyCode

