from abc import ABC, abstractmethod
from fastapi import FastAPI
from dash import Dash, dcc, html, Input, Output
from fastapi.middleware.wsgi import WSGIMiddleware
from datetime import date, datetime, timedelta


class IExchangeRateUsecase(ABC):
    @abstractmethod
    def read_GBP_data(self, startDay: int, startMonth: int, startYear: int, endDay: int, endMonth: int, endYear: int) -> None: pass
    @abstractmethod
    def read_USD_data(self, startDay: int, startMonth: int, startYear: int, endDay: int, endMonth: int, endYear: int) -> None: pass
    @abstractmethod
    def read_TRY_data(self, startDay: int, startMonth: int, startYear: int, endDay: int, endMonth: int, endYear: int) -> None: pass
    @abstractmethod
    def read_EUR_data(self, startDay: int, startMonth: int, startYear: int, endDay: int, endMonth: int, endYear: int) -> None: pass
    @abstractmethod
    def read_CNY_data(self, startDay: int, startMonth: int, startYear: int, endDay: int, endMonth: int, endYear: int) -> None: pass
    @abstractmethod
    def read_INR_data(self, startDay: int, startMonth: int, startYear: int, endDay: int, endMonth: int, endYear: int) -> None: pass
    @abstractmethod
    def read_JPY_data(self, startDay: int, startMonth: int, startYear: int, endDay: int, endMonth: int, endYear: int) -> None: pass
    @abstractmethod
    def create_delta_GBP_data(self) -> None: pass
    @abstractmethod
    def create_delta_USD_data(self) -> None: pass
    @abstractmethod
    def create_delta_TRY_data(self) -> None: pass
    @abstractmethod
    def create_delta_EUR_data(self) -> None: pass
    @abstractmethod
    def create_delta_CNY_data(self) -> None: pass
    @abstractmethod
    def create_delta_INR_data(self) -> None: pass
    @abstractmethod
    def create_delta_JPY_data(self) -> None: pass


class ICurrencyCodeUsecase(ABC):
    @abstractmethod
    def read_data_from_web(self) -> None: pass


class ReaderHandler:
    def __init__(self, exchangeRateUsecase: IExchangeRateUsecase, currencyCodeUsecase: ICurrencyCodeUsecase) -> None:
        self.__exchangeRateUsecase = exchangeRateUsecase
        self.__currencyCodeUsecase = currencyCodeUsecase
        self.__n_clicks_1 = 0
        self.__n_clicks_2 = 0
        

    def __generate_std_layout(self) -> html.Div:
        layout = html.Div([
            html.H1('Считыватель данных о валютах в локальную SQLite базу данных'),
            html.H4('Выбор диапозона дат:'),
            dcc.DatePickerRange(
                id="my-date-picker-range",
                min_date_allowed=date(1992, 1, 1),
                max_date_allowed=datetime.now().date() - timedelta(days=1),
                display_format='DD.MM.YYYY',
            ),
            html.H4('Выбор валют:'),
            dcc.Checklist(
                id='my-checklist',
                options=[
                    {'label': 'Фунт Стерлингов', 'value': 'GBP'},
                    {'label': 'Доллар США', 'value': 'USD'},
                    {'label': 'Турецкая лира', 'value': 'TRY'},
                    {'label': 'Евро', 'value': 'EUR'},
                    {'label': 'Китайский юань', 'value': 'CNY'},
                    {'label': 'Индийская рупия', 'value': 'INR'},
                    {'label': '	Йена', 'value': 'JPY'}
                ],
                value=[],
                inline=True
            ),
            html.Br(),
            html.Div([
                html.Button(children='Считать', id='my-button-1', n_clicks=self.__n_clicks_1),
                html.Button(children='Расчитать относительные изменения', id='my-button-2', n_clicks=self.__n_clicks_2),
            ]),
            html.Div(id='my-output')
        ])
        return layout

    def __read_data(self, start_date: str, end_date: str, value: list[str]) -> html.Div:
        errors: list[str] = []
        if (not value):
            errors.append('Валюты для считывания не выбраны')
        if (not start_date):
            errors.append('Дата начала отсчёта указана не коректно')
        else:
            start_date = date.fromisoformat(start_date)
        if (not end_date):
            errors.append('Дата конца отсчёта указана не коректно')
        else:
            end_date = date.fromisoformat(end_date)
        if (start_date and end_date):
            if (start_date > end_date):
                errors.append('Дата начала отсчёта не должен быть позже даты конца отсчёта')
            if (start_date == end_date):
                errors.append('Дата начала отсчёта не должен быть равна дате конца отсчёта')
            if (end_date - start_date > timedelta(days=365*2)):
                errors.append('Переод отсчёта не должен превышать два года')
        if (errors):
            errors_in_li: list[html.Li] = []
            for error in errors:
                errors_in_li.append(html.Li(error))
            return html.Div([
                html.Br(),
                'Ошибки:',
                html.Ul(errors_in_li)
            ])
        self.__currencyCodeUsecase.read_data_from_web()
        if ('GBP' in value):
            self.__exchangeRateUsecase.read_GBP_data(start_date.day, start_date.month, start_date.year, end_date.day, end_date.month, end_date.year)
        if ('USD' in value):
            self.__exchangeRateUsecase.read_USD_data(start_date.day, start_date.month, start_date.year, end_date.day, end_date.month, end_date.year)
        if ('TRY' in value):
            self.__exchangeRateUsecase.read_TRY_data(start_date.day, start_date.month, start_date.year, end_date.day, end_date.month, end_date.year)
        if ('EUR' in value):
            self.__exchangeRateUsecase.read_EUR_data(start_date.day, start_date.month, start_date.year, end_date.day, end_date.month, end_date.year)
        if ('CNY' in value):
            self.__exchangeRateUsecase.read_CNY_data(start_date.day, start_date.month, start_date.year, end_date.day, end_date.month, end_date.year)
        if ('INR' in value):
            self.__exchangeRateUsecase.read_INR_data(start_date.day, start_date.month, start_date.year, end_date.day, end_date.month, end_date.year)
        if ('JPY' in value):
            self.__exchangeRateUsecase.read_JPY_data(start_date.day, start_date.month, start_date.year, end_date.day, end_date.month, end_date.year)
        return html.Div([
            html.Br(),
            f'Валюты {", ".join(value)} за период от {start_date.day}.{start_date.month}.{start_date.year} до {end_date.day}.{end_date.month}.{end_date.year} успешно считаны'
        ])

    def __create_delta_data(self, value: list[str]) -> html.Div:
        if (not value):
            return html.Div([
                html.Br(),
                'Ошибки:',
                html.Ul(html.Li(
                    'Валюты для расчёта относительных изменений не выбраны'
                ))
            ])
        if ('GBP' in value):
            self.__exchangeRateUsecase.create_delta_GBP_data()
        if ('USD' in value):
            self.__exchangeRateUsecase.create_delta_USD_data()
        if ('TRY' in value):
            self.__exchangeRateUsecase.create_delta_TRY_data()
        if ('EUR' in value):
            self.__exchangeRateUsecase.create_delta_EUR_data()
        if ('CNY' in value):
            self.__exchangeRateUsecase.create_delta_CNY_data()
        if ('INR' in value):
            self.__exchangeRateUsecase.create_delta_INR_data()
        if ('JPY' in value):
            self.__exchangeRateUsecase.create_delta_JPY_data()
        return html.Div([
            html.Br(),
            f'Относительные изменения по валютам {", ".join(value)} успешно рассчитаны'
        ])
        
    def __callback(self, start_date: str, end_date: str, value: list[str], n_clicks_1: int, n_clicks_2: int) -> html.Div:
        if (n_clicks_1 != self.__n_clicks_1):
            self.__n_clicks_1 = n_clicks_1
            return self.__read_data(start_date, end_date, value)
        if (n_clicks_2 != self.__n_clicks_2):
            self.__n_clicks_2 = n_clicks_2
            return self.__create_delta_data(value)
        return html.Div()


    def register(self, app: FastAPI) -> None:
        appDash = Dash(requests_pathname_prefix='/reader/')
        appDash.layout = self.__generate_std_layout()
        @appDash.callback(
            Output('my-output', 'children'),
            Input('my-date-picker-range', 'start_date'),
            Input('my-date-picker-range', 'end_date'),
            Input('my-checklist', 'value'),
            Input('my-button-1', 'n_clicks'),
            Input('my-button-2', 'n_clicks')
        )
        def callback(start_date: str, end_date: str, value: list[str], n_clicks_1: int, n_clicks_2: int) -> html.Div:
            return self.__callback(start_date, end_date, value, n_clicks_1, n_clicks_2)
        readerApp = WSGIMiddleware(appDash.server)
        app.mount('/reader/', readerApp)
