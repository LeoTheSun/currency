from abc import ABC, abstractmethod
from internal.domain.entity.exchange_rate import ExchangeRate
from internal.domain.entity.parameter import Parameter
from internal.domain.entity.delta_rate import DeltaRate
from datetime import date, timedelta


class IExchangeRateStorage(ABC):
    @abstractmethod
    def create_or_update(self, exchangeRate: ExchangeRate) -> ExchangeRate: pass
    @abstractmethod
    def get_one(self, exchangeRate: ExchangeRate) -> ExchangeRate: pass
    @abstractmethod
    def get_many(self, exchangeRate: ExchangeRate) -> list[ExchangeRate]: pass

class IExchangeRateWebAPI(ABC):
    @abstractmethod
    def get_GBP_data(self, startDay: int, startMonth: int, startYear: int, endDay: int, endMonth: int, endYear: int) -> list[ExchangeRate]: pass
    @abstractmethod
    def get_USD_data(self, startDay: int, startMonth: int, startYear: int, endDay: int, endMonth: int, endYear: int) -> list[ExchangeRate]: pass
    @abstractmethod
    def get_TRY_data(self, startDay: int, startMonth: int, startYear: int, endDay: int, endMonth: int, endYear: int) -> list[ExchangeRate]: pass
    @abstractmethod
    def get_EUR_data(self, startDay: int, startMonth: int, startYear: int, endDay: int, endMonth: int, endYear: int) -> list[ExchangeRate]: pass
    @abstractmethod
    def get_CNY_data(self, startDay: int, startMonth: int, startYear: int, endDay: int, endMonth: int, endYear: int) -> list[ExchangeRate]: pass
    @abstractmethod
    def get_INR_data(self, startDay: int, startMonth: int, startYear: int, endDay: int, endMonth: int, endYear: int) -> list[ExchangeRate]: pass
    @abstractmethod
    def get_JPY_data(self, startDay: int, startMonth: int, startYear: int, endDay: int, endMonth: int, endYear: int) -> list[ExchangeRate]: pass

class IParameterStorage(ABC):
    @abstractmethod
    def get_one(self, parameter: Parameter) -> Parameter: pass

class IDeltaRateStorage(ABC):
    @abstractmethod
    def create_or_update(self, deltaRate: DeltaRate) -> DeltaRate: pass
    @abstractmethod
    def get_many(self, deltaRate: DeltaRate) -> list[DeltaRate]: pass

class ExchangeRateUsecase:
    def __init__(self, exchangeRateStorage: IExchangeRateStorage, deltaRateStorage: IDeltaRateStorage, parameterStorage: IParameterStorage, exchangeRateWebAPI: IExchangeRateWebAPI):
        self.__exchangeRateStorage = exchangeRateStorage
        self.__deltaRateStorage = deltaRateStorage
        self.__parameterStorage = parameterStorage
        self.__webAPI = exchangeRateWebAPI
        self.__std_date: date = None

    def __check_std_date(self) -> None:
        if not self.__std_date:
            parameter = self.__parameterStorage.get_one(Parameter(
                Name='std_date'
            ))
            d = parameter.Value.split('-')
            self.__std_date = date(int(d[0]), int(d[1]), int(d[2]))
    
    def read_GBP_data(self, startDay: int, startMonth: int, startYear: int, endDay: int, endMonth: int, endYear: int) -> None:
        self.__check_std_date()
        data = self.__webAPI.get_GBP_data(startDay, startMonth, startYear, endDay, endMonth, endYear)
        for element in data:
            self.__exchangeRateStorage.create_or_update(element)

    def read_USD_data(self, startDay: int, startMonth: int, startYear: int, endDay: int, endMonth: int, endYear: int) -> None:
        self.__check_std_date()
        data = self.__webAPI.get_USD_data(startDay, startMonth, startYear, endDay, endMonth, endYear)
        for element in data:
            self.__exchangeRateStorage.create_or_update(element)

    def read_TRY_data(self, startDay: int, startMonth: int, startYear: int, endDay: int, endMonth: int, endYear: int) -> None:
        self.__check_std_date()
        data = self.__webAPI.get_TRY_data(startDay, startMonth, startYear, endDay, endMonth, endYear)
        for element in data:
            self.__exchangeRateStorage.create_or_update(element)

    def read_EUR_data(self, startDay: int, startMonth: int, startYear: int, endDay: int, endMonth: int, endYear: int) -> None:
        self.__check_std_date()
        data = self.__webAPI.get_EUR_data(startDay, startMonth, startYear, endDay, endMonth, endYear)
        for element in data:
            self.__exchangeRateStorage.create_or_update(element)

    def read_CNY_data(self, startDay: int, startMonth: int, startYear: int, endDay: int, endMonth: int, endYear: int) -> None:
        self.__check_std_date()
        data = self.__webAPI.get_CNY_data(startDay, startMonth, startYear, endDay, endMonth, endYear)
        for element in data:
            self.__exchangeRateStorage.create_or_update(element)

    def read_INR_data(self, startDay: int, startMonth: int, startYear: int, endDay: int, endMonth: int, endYear: int) -> None:
        self.__check_std_date()
        data = self.__webAPI.get_INR_data(startDay, startMonth, startYear, endDay, endMonth, endYear)
        for element in data:
            self.__exchangeRateStorage.create_or_update(element)

    def read_JPY_data(self, startDay: int, startMonth: int, startYear: int, endDay: int, endMonth: int, endYear: int) -> None:
        self.__check_std_date()
        data = self.__webAPI.get_JPY_data(startDay, startMonth, startYear, endDay, endMonth, endYear)
        for element in data:
            self.__exchangeRateStorage.create_or_update(element)

    def create_delta_GBP_data(self) -> None:
        self.__check_std_date()
        start = self.__std_date - timedelta(days=1)
        end = self.__std_date + timedelta(days=1)
        self.read_GBP_data(start.day, start.month, start.year, end.day, end.month, end.year)
        std_exchangeRate = self.__exchangeRateStorage.get_one(ExchangeRate(
            Date=self.__std_date,
            Code='GBP'
        ))
        exchangeRate_list = self.__exchangeRateStorage.get_many(std_exchangeRate)
        for exchangeRate in exchangeRate_list:
            self.__deltaRateStorage.create_or_update(DeltaRate(
                Date=exchangeRate.Date,
                Delta=exchangeRate.Rate - std_exchangeRate.Rate,
                Code=exchangeRate.Code
            ))

    def create_delta_USD_data(self) -> None:
        self.__check_std_date()
        start = self.__std_date - timedelta(days=1)
        end = self.__std_date + timedelta(days=1)
        self.read_USD_data(start.day, start.month, start.year, end.day, end.month, end.year)
        std_exchangeRate = self.__exchangeRateStorage.get_one(ExchangeRate(
            Date=self.__std_date,
            Code='USD'
        ))
        exchangeRate_list = self.__exchangeRateStorage.get_many(std_exchangeRate)
        for exchangeRate in exchangeRate_list:
            self.__deltaRateStorage.create_or_update(DeltaRate(
                Date=exchangeRate.Date,
                Delta=exchangeRate.Rate - std_exchangeRate.Rate,
                Code=exchangeRate.Code
            ))

    def create_delta_TRY_data(self) -> None:
        self.__check_std_date()
        start = self.__std_date - timedelta(days=1)
        end = self.__std_date + timedelta(days=1)
        self.read_TRY_data(start.day, start.month, start.year, end.day, end.month, end.year)
        std_exchangeRate = self.__exchangeRateStorage.get_one(ExchangeRate(
            Date=self.__std_date,
            Code='TRY'
        ))
        exchangeRate_list = self.__exchangeRateStorage.get_many(std_exchangeRate)
        for exchangeRate in exchangeRate_list:
            self.__deltaRateStorage.create_or_update(DeltaRate(
                Date=exchangeRate.Date,
                Delta=exchangeRate.Rate - std_exchangeRate.Rate,
                Code=exchangeRate.Code
            ))
    
    def create_delta_EUR_data(self) -> None:
        self.__check_std_date()
        start = self.__std_date - timedelta(days=1)
        end = self.__std_date + timedelta(days=1)
        self.read_EUR_data(start.day, start.month, start.year, end.day, end.month, end.year)
        std_exchangeRate = self.__exchangeRateStorage.get_one(ExchangeRate(
            Date=self.__std_date,
            Code='EUR'
        ))
        exchangeRate_list = self.__exchangeRateStorage.get_many(std_exchangeRate)
        for exchangeRate in exchangeRate_list:
            self.__deltaRateStorage.create_or_update(DeltaRate(
                Date=exchangeRate.Date,
                Delta=exchangeRate.Rate - std_exchangeRate.Rate,
                Code=exchangeRate.Code
            ))

    def create_delta_CNY_data(self) -> None:
        self.__check_std_date()
        start = self.__std_date - timedelta(days=1)
        end = self.__std_date + timedelta(days=1)
        self.read_CNY_data(start.day, start.month, start.year, end.day, end.month, end.year)
        std_exchangeRate = self.__exchangeRateStorage.get_one(ExchangeRate(
            Date=self.__std_date,
            Code='CNY'
        ))
        exchangeRate_list = self.__exchangeRateStorage.get_many(std_exchangeRate)
        for exchangeRate in exchangeRate_list:
            self.__deltaRateStorage.create_or_update(DeltaRate(
                Date=exchangeRate.Date,
                Delta=exchangeRate.Rate - std_exchangeRate.Rate,
                Code=exchangeRate.Code
            ))

    def create_delta_INR_data(self) -> None:
        self.__check_std_date()
        start = self.__std_date - timedelta(days=1)
        end = self.__std_date + timedelta(days=1)
        self.read_INR_data(start.day, start.month, start.year, end.day, end.month, end.year)
        std_exchangeRate = self.__exchangeRateStorage.get_one(ExchangeRate(
            Date=self.__std_date,
            Code='INR'
        ))
        exchangeRate_list = self.__exchangeRateStorage.get_many(std_exchangeRate)
        for exchangeRate in exchangeRate_list:
            self.__deltaRateStorage.create_or_update(DeltaRate(
                Date=exchangeRate.Date,
                Delta=exchangeRate.Rate - std_exchangeRate.Rate,
                Code=exchangeRate.Code
            ))

    def create_delta_JPY_data(self) -> None:
        self.__check_std_date()
        start = self.__std_date - timedelta(days=1)
        end = self.__std_date + timedelta(days=1)
        self.read_JPY_data(start.day, start.month, start.year, end.day, end.month, end.year)
        std_exchangeRate = self.__exchangeRateStorage.get_one(ExchangeRate(
            Date=self.__std_date,
            Code='JPY'
        ))
        exchangeRate_list = self.__exchangeRateStorage.get_many(std_exchangeRate)
        for exchangeRate in exchangeRate_list:
            self.__deltaRateStorage.create_or_update(DeltaRate(
                Date=exchangeRate.Date,
                Delta=exchangeRate.Rate - std_exchangeRate.Rate,
                Code=exchangeRate.Code
            ))

    def get_std_date(self) -> date:
        parameter = self.__parameterStorage.get_one(Parameter(
            Name='std_date'
        ))
        d = parameter.Value.split('-')
        return date(int(d[0]), int(d[1]), int(d[2]))

    def get_GBP_data(self) -> list[ExchangeRate]:
        return self.__exchangeRateStorage.get_many(ExchangeRate(
            Code='GBP'
        ))
    
    def get_USD_data(self) -> list[ExchangeRate]:
        return self.__exchangeRateStorage.get_many(ExchangeRate(
            Code='USD'
        ))
    
    def get_TRY_data(self) -> list[ExchangeRate]:
        return self.__exchangeRateStorage.get_many(ExchangeRate(
            Code='TRY'
        ))
    
    def get_EUR_data(self) -> list[ExchangeRate]:
        return self.__exchangeRateStorage.get_many(ExchangeRate(
            Code='EUR'
        ))
    
    def get_CNY_data(self) -> list[ExchangeRate]:
        return self.__exchangeRateStorage.get_many(ExchangeRate(
            Code='CNY'
        ))
    
    def get_INR_data(self) -> list[ExchangeRate]:
        return self.__exchangeRateStorage.get_many(ExchangeRate(
            Code='INR'
        ))
    
    def get_JPY_data(self) -> list[ExchangeRate]:
        return self.__exchangeRateStorage.get_many(ExchangeRate(
            Code='JPY'
        ))

    def get_delta_GBP_data(self) -> list[DeltaRate]:
        return self.__deltaRateStorage.get_many(DeltaRate(
            Code='GBP'
        ))
    
    def get_delta_USD_data(self) -> list[DeltaRate]:
        return self.__deltaRateStorage.get_many(DeltaRate(
            Code='USD'
        ))
    
    def get_delta_TRY_data(self) -> list[DeltaRate]:
        return self.__deltaRateStorage.get_many(DeltaRate(
            Code='TRY'
        ))
    
    def get_delta_EUR_data(self) -> list[DeltaRate]:
        return self.__deltaRateStorage.get_many(DeltaRate(
            Code='EUR'
        ))
    
    def get_delta_CNY_data(self) -> list[DeltaRate]:
        return self.__deltaRateStorage.get_many(DeltaRate(
            Code='CNY'
        ))
    
    def get_delta_INR_data(self) -> list[DeltaRate]:
        return self.__deltaRateStorage.get_many(DeltaRate(
            Code='INR'
        ))
    
    def get_delta_JPY_data(self) -> list[DeltaRate]:
        return self.__deltaRateStorage.get_many(DeltaRate(
            Code='JPY'
        ))
    