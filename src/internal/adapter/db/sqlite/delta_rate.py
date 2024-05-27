from internal.adapter.db.sqlite.utils import format_query
from pkg.sqlite.sqlite import SQLite
from logging import Logger
from internal.domain.entity.delta_rate import DeltaRate
from datetime import date
from decimal import Decimal


class DeltaRateStorage:
    def __init__(self, sqlite: SQLite, logger: Logger):
        self.__sqlite = sqlite
        self.__logger = logger

    def exists(self, deltaRate: DeltaRate) -> bool:
        q = """
            SELECT EXISTS (
			    SELECT id
			    FROM delta_rates
			    WHERE date = ? AND code = ?
		    );
        """
        self.__logger.debug(f"SQL Query: '{format_query(q)}'")
        exists = bool(self.__sqlite.query_row(q, (str(deltaRate.Date), deltaRate.Code, ))[0])
        return exists
    
    def create(self, deltaRate: DeltaRate) -> DeltaRate:
        q = """
            INSERT INTO delta_rates (date, delta, code)
            VALUES (?, ?, ?)
            RETURNING id;
        """
        self.__logger.debug(f"SQL Query: '{format_query(q)}'")
        raw_id = self.__sqlite.query_row(q, (str(deltaRate.Date), str(deltaRate.Delta), deltaRate.Code,))
        deltaRate = DeltaRate(
            Id=int(raw_id[0]),
            Date=deltaRate.Date,
            Delta=deltaRate.Delta,
            Code=deltaRate.Code
        )
        return deltaRate
    
    def get_one(self, deltaRate: DeltaRate) -> DeltaRate:
        q = """
			SELECT id, date, delta, code
			FROM delta_rates
			WHERE date = ? AND code = ?;
        """
        self.__logger.debug(f"SQL Query: '{format_query(q)}'")
        raw_deltaRate = self.__sqlite.query_row(q, (str(deltaRate.Date), deltaRate.Code, ))
        d = str(raw_deltaRate[1]).split('-')
        deltaRate = DeltaRate(
            Id=int(raw_deltaRate[0]),
            Date=date(int(d[0]), int(d[1]), int(d[2])),
            Delta=Decimal(raw_deltaRate[2]),
            Code=str(raw_deltaRate[3]),
        )
        return deltaRate

    def update(self, deltaRate: DeltaRate) -> None:
        q = """
            UPDATE delta_rates
            SET delta = ?
            WHERE date = ? AND code = ?;
        """
        self.__logger.debug(f"SQL Query: '{format_query(q)}'")
        self.__sqlite.exec(q, (str(deltaRate.Delta), str(deltaRate.Date), deltaRate.Code,))

    def create_or_update(self, deltaRate: DeltaRate) -> DeltaRate:
        if self.exists(deltaRate) is False:
            deltaRate = self.create(deltaRate)
            return deltaRate
        dr = self.get_one(deltaRate)
        if (dr.Delta == deltaRate.Delta):
            deltaRate = dr
            return deltaRate
        self.update(deltaRate)
        deltaRate = DeltaRate(
            Id=dr.Id,
            Date=dr.Date,
            Delta=deltaRate.Delta,
            Code=dr.Code
        )
        return deltaRate
        
    def get_many(self, deltaRate: DeltaRate) -> list[DeltaRate]:
        q = """
            SELECT id, date, delta, code
            FROM delta_rates
            WHERE code = ?;
        """
        self.__logger.debug(f"SQL Query: '{format_query(q)}'")
        raw_deltaRate_list = self.__sqlite.query(q, (deltaRate.Code,))
        deltaRate_list: list[DeltaRate] = []
        for raw_deltaRate in raw_deltaRate_list:
            d = str(raw_deltaRate[1]).split('-')
            deltaRate = DeltaRate(
                Id=int(raw_deltaRate[0]),
                Date=date(int(d[0]), int(d[1]), int(d[2])),
                Delta=Decimal(raw_deltaRate[2]),
                Code=str(raw_deltaRate[3])
            )
            deltaRate_list.append(deltaRate)
        return deltaRate_list