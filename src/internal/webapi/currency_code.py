from requests import get
from bs4 import BeautifulSoup, Tag
from internal.domain.entity.currency_code import CurrencyCode


class CurrencyCodeWebAPi:
    def __init__(self):
        self.URL = 'https://www.iban.ru/currency-codes'
    
    def __tag_to_dataclass(self, htmlRow: Tag) -> CurrencyCode:
        cols: list[Tag] = htmlRow.find_all('td')
        number=cols[3].get_text()
        if number == '':
            number = -1
        else:
            number = int(number)
        currencyCode = CurrencyCode(
            Country=cols[0].get_text(),
            Currency=cols[1].get_text(),
            Code=cols[2].get_text(),
            Number=number
        )
        return currencyCode

    def get_data(self) -> list[CurrencyCode]:
        response = get(self.URL)
        bs = BeautifulSoup(response.content, "lxml")
        table = bs.find('table', attrs={'class': 'table table-bordered downloads tablesorter'})
        tableBody = table.find('tbody')
        rows = tableBody.find_all('tr')
        currencyCodeList: list[CurrencyCode] = []
        for row in rows:
            currencyCode = self.__tag_to_dataclass(row)
            if currencyCode.Code:
                currencyCodeList.append(currencyCode)
        return currencyCodeList