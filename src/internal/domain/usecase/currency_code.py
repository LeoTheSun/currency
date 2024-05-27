from abc import ABC, abstractmethod
from internal.domain.entity.currency_code import CurrencyCode

class ICurrencyCodeStorage(ABC):
    @abstractmethod
    def create_or_update(self, currencyCode: CurrencyCode) -> CurrencyCode: pass

class ICurrencyCodeWebAPI(ABC):
    @abstractmethod
    def get_data(self) -> list[CurrencyCode]: pass

class CurrencyCodeUsecase:
    def __init__(self, currencyCodeStorage: ICurrencyCodeStorage, currencyCodeWebAPI: ICurrencyCodeWebAPI):
        self.__storage = currencyCodeStorage
        self.__webAPI = currencyCodeWebAPI
    
    def read_data_from_web(self) -> None:
        data = self.__webAPI.get_data()
        for element in data:
            self.__storage.create_or_update(element)
