from datetime import date, timedelta
from decimal import Decimal
from enum import Enum
from time import localtime
from requests import get
from bs4 import BeautifulSoup, Tag
from internal.domain.entity.currency_code import CurrencyCode
from internal.domain.entity.exchange_rate import ExchangeRate


class ExchangeRateWebAPi:
    class CurrencyCodeEnum(Enum):
        GBP = 52146
        USD = 52148
        TRY = 52158
        EUR = 52170
        CNY = 52207
        INR = 52238
        JPY = 52246

    def __generateURL(self, currencyCode: CurrencyCodeEnum, startDay: int, startMonth: int, startYear: int, endDay: int, endMonth: int, endYear: int) -> str:
        try:
            start = date(startYear, startMonth, startDay)
        except Exception:
            raise Exception('Дата начала отсчёта указана некоректно')
        try:
            end = date(endYear, endMonth, endDay)
        except Exception:
            raise Exception('Дата конца отсчёта указана некоректно')
        now = localtime()
        now = date(now.tm_year, now.tm_mon, now.tm_mday)
        if start > now:
            raise Exception('Дата начала отсчёта не может быть позже сегодняшней даты')
        if end > now:
            raise Exception('Дата конца отсчёта не может быть позже сегодняшней даты')
        if start > end:
            raise Exception('Дата начала отсчёта не может быть позже даты конца отсчёта')
        if start == end:
            raise Exception('Дата начала отсчёта не может совпадать с датой конца отсчёта')
        if end-start > timedelta(days=365*2):
            raise Exception('Диапозон дат не может быть больше двух лет')
        return f'https://www.finmarket.ru/currency/rates/?id=10148&pv=1&cur={currencyCode.value}&bd={startDay}&bm={startMonth}&by={startYear}&ed={endDay}&em={endMonth}&ey={endYear}#archive'



    def __tag_to_dataclass(self, code: str, htmlRow: Tag) -> ExchangeRate:
        cols: list[Tag] = htmlRow.find_all('td')
        d = cols[0].get_text().split('.')
        return ExchangeRate(
            Date=date(int(d[2]), int(d[1]), int(d[0])),
            Count=int(cols[1].get_text()),
            Rate=Decimal(cols[2].get_text().replace(',', '.')),
            Change=Decimal(cols[3].get_text().replace(',', '.').replace('+', '')),
            Code=code,
        )

    def __get_data(self, currencyCode: CurrencyCodeEnum, startDay: int, startMonth: int, startYear: int, endDay: int, endMonth: int, endYear: int) -> list[CurrencyCode]:
        url = self.__generateURL(currencyCode, startDay, startMonth, startYear, endDay, endMonth, endYear)
        response = get(url)
        bs = BeautifulSoup(response.content, "lxml")
        table = bs.find('table', attrs={'class': 'karramba'})
        tableBody = table.find('tbody')
        rows = tableBody.find_all('tr')
        name = currencyCode.name
        currencyCodeList: list[CurrencyCode] = []
        for row in rows:
            
            currencyCode = self.__tag_to_dataclass(name, row)
            currencyCodeList.append(currencyCode)
        return currencyCodeList

    def get_GBP_data(self, startDay: int, startMonth: int, startYear: int, endDay: int, endMonth: int, endYear: int) -> list[CurrencyCode]:
        return self.__get_data(self.CurrencyCodeEnum.GBP, startDay, startMonth, startYear, endDay, endMonth, endYear)

    def get_USD_data(self, startDay: int, startMonth: int, startYear: int, endDay: int, endMonth: int, endYear: int) -> list[CurrencyCode]:
        return self.__get_data(self.CurrencyCodeEnum.USD, startDay, startMonth, startYear, endDay, endMonth, endYear)
    
    def get_TRY_data(self, startDay: int, startMonth: int, startYear: int, endDay: int, endMonth: int, endYear: int) -> list[CurrencyCode]:
        return self.__get_data(self.CurrencyCodeEnum.TRY, startDay, startMonth, startYear, endDay, endMonth, endYear)
    
    def get_EUR_data(self, startDay: int, startMonth: int, startYear: int, endDay: int, endMonth: int, endYear: int) -> list[CurrencyCode]:
        return self.__get_data(self.CurrencyCodeEnum.EUR, startDay, startMonth, startYear, endDay, endMonth, endYear)
    
    def get_CNY_data(self, startDay: int, startMonth: int, startYear: int, endDay: int, endMonth: int, endYear: int) -> list[CurrencyCode]:
        return self.__get_data(self.CurrencyCodeEnum.CNY, startDay, startMonth, startYear, endDay, endMonth, endYear)

    def get_INR_data(self, startDay: int, startMonth: int, startYear: int, endDay: int, endMonth: int, endYear: int) -> list[CurrencyCode]:
        return self.__get_data(self.CurrencyCodeEnum.INR, startDay, startMonth, startYear, endDay, endMonth, endYear)

    def get_JPY_data(self, startDay: int, startMonth: int, startYear: int, endDay: int, endMonth: int, endYear: int) -> list[CurrencyCode]:
        return self.__get_data(self.CurrencyCodeEnum.JPY, startDay, startMonth, startYear, endDay, endMonth, endYear)

    def __init__(self):
        pass