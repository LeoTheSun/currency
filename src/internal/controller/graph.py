from abc import ABC, abstractmethod
from decimal import Decimal
from typing import Union
from fastapi import FastAPI
from dash import Dash, dcc, html, Input, Output
from fastapi.middleware.wsgi import WSGIMiddleware
from datetime import date, datetime, timedelta
from internal.domain.entity.delta_rate import DeltaRate
from internal.domain.entity.exchange_rate import ExchangeRate
import plotly.graph_objs as go

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
    @abstractmethod
    def get_GBP_data(self) -> list[ExchangeRate]: pass
    @abstractmethod
    def get_USD_data(self) -> list[ExchangeRate]: pass
    @abstractmethod
    def get_TRY_data(self) -> list[ExchangeRate]: pass
    @abstractmethod
    def get_EUR_data(self) -> list[ExchangeRate]: pass
    @abstractmethod
    def get_CNY_data(self) -> list[ExchangeRate]: pass
    @abstractmethod
    def get_INR_data(self) -> list[ExchangeRate]: pass
    @abstractmethod
    def get_JPY_data(self) -> list[ExchangeRate]: pass
    @abstractmethod
    def get_delta_GBP_data(self) -> list[DeltaRate]: pass
    @abstractmethod
    def get_delta_USD_data(self) -> list[DeltaRate]: pass
    @abstractmethod
    def get_delta_TRY_data(self) -> list[DeltaRate]: pass
    @abstractmethod
    def get_delta_EUR_data(self) -> list[DeltaRate]: pass
    @abstractmethod
    def get_delta_CNY_data(self) -> list[DeltaRate]: pass
    @abstractmethod
    def get_delta_INR_data(self) -> list[DeltaRate]: pass
    @abstractmethod
    def get_delta_JPY_data(self) -> list[DeltaRate]: pass
    @abstractmethod
    def get_std_date(self) -> date: pass


class GraphHandler:
    def __init__(self, exchangeRateUsecase: IExchangeRateUsecase) -> None:
        self.__exchangeRateUsecase = exchangeRateUsecase
        self.__n_clicks = 0

    def __generate_std_layout(self) -> html.Div:
        d = self.__exchangeRateUsecase.get_std_date()
        layout = html.Div([
            html.H1('Постройщик графиков по изменению курса валют'),
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
            html.H4('Выбор типа графика:'),
            dcc.RadioItems(
                id='my-radio-1',
                options=[
                    {'label': f'Относительные значения валют от {d.day}.{d.month}.{d.year}', 'value': 'REL'},
                    {'label': 'Абсолютные значения валют', 'value': 'ABS'}
                ],
                inline=True
            ),
            html.H4('Выбор источника данных:'),
            dcc.RadioItems(
                id='my-radio-2',
                options=[
                    {'label': 'Локальная SQLite база данных', 'value': 'DB'},
                    {'label': 'Веб-источник', 'value': 'WEB'}
                ],
                inline=True
            ),
            html.Br(),
            html.Button(
                id='my-button',
                children='Построить график',
                n_clicks=self.__n_clicks),
            html.Div(id='my-output')
        ])
        return layout

    def __get_graph(self, start_date: date, end_date: date, codes: list[str], type: str, source: str) -> html.Div:
        if (source == 'WEB'):
            if ('GBP' in codes):
                self.__exchangeRateUsecase.read_GBP_data(start_date.day, start_date.month, start_date.year, end_date.day, end_date.month, end_date.year)
            if ('USD' in codes):
                self.__exchangeRateUsecase.read_USD_data(start_date.day, start_date.month, start_date.year, end_date.day, end_date.month, end_date.year)
            if ('TRY' in codes):
                self.__exchangeRateUsecase.read_TRY_data(start_date.day, start_date.month, start_date.year, end_date.day, end_date.month, end_date.year)
            if ('EUR' in codes):
                self.__exchangeRateUsecase.read_EUR_data(start_date.day, start_date.month, start_date.year, end_date.day, end_date.month, end_date.year)
            if ('CNY' in codes):
                self.__exchangeRateUsecase.read_CNY_data(start_date.day, start_date.month, start_date.year, end_date.day, end_date.month, end_date.year)
            if ('INR' in codes):
                self.__exchangeRateUsecase.read_INR_data(start_date.day, start_date.month, start_date.year, end_date.day, end_date.month, end_date.year)
            if ('JPY' in codes):
                self.__exchangeRateUsecase.read_JPY_data(start_date.day, start_date.month, start_date.year, end_date.day, end_date.month, end_date.year)
        if (type == 'REL'):
            if ('GBP' in codes):
                self.__exchangeRateUsecase.create_delta_GBP_data()
            if ('USD' in codes):
                self.__exchangeRateUsecase.create_delta_USD_data()
            if ('TRY' in codes):
                self.__exchangeRateUsecase.create_delta_TRY_data()
            if ('EUR' in codes):
                self.__exchangeRateUsecase.create_delta_EUR_data()
            if ('CNY' in codes):
                self.__exchangeRateUsecase.create_delta_CNY_data()
            if ('INR' in codes):
                self.__exchangeRateUsecase.create_delta_INR_data()
            if ('JPY' in codes):
                self.__exchangeRateUsecase.create_delta_JPY_data()
        labels: list[str] = []
        data_x: list[list[Decimal]] = []
        data_y: list[list[date]] = []
        if (type == 'REL'):
            if ('GBP' in codes):
                all_data = self.__exchangeRateUsecase.get_delta_GBP_data()
                data = [item for item in all_data if item.Date >= start_date and item.Date <= end_date]
                deltas = [item.Delta for item in data]
                dates = [item.Date for item in data]
                labels.append('Фунт Стерлингов')
                data_x.append(deltas)
                data_y.append(dates)
            if ('USD' in codes):
                all_data = self.__exchangeRateUsecase.get_delta_USD_data()
                data = [item for item in all_data if item.Date >= start_date and item.Date <= end_date]
                deltas = [item.Delta for item in data]
                dates = [item.Date for item in data]
                labels.append('Доллар США')
                data_x.append(deltas)
                data_y.append(dates)
            if ('TRY' in codes):
                all_data = self.__exchangeRateUsecase.get_delta_TRY_data()
                data = [item for item in all_data if item.Date >= start_date and item.Date <= end_date]
                deltas = [item.Delta for item in data]
                dates = [item.Date for item in data]
                labels.append('Турецкая лира')
                data_x.append(deltas)
                data_y.append(dates)
            if ('EUR' in codes):
                all_data = self.__exchangeRateUsecase.get_delta_EUR_data()
                data = [item for item in all_data if item.Date >= start_date and item.Date <= end_date]
                deltas = [item.Delta for item in data]
                dates = [item.Date for item in data]
                labels.append('Евро')
                data_x.append(deltas)
                data_y.append(dates)
            if ('CNY' in codes):
                all_data = self.__exchangeRateUsecase.get_delta_CNY_data()
                data = [item for item in all_data if item.Date >= start_date and item.Date <= end_date]
                deltas = [item.Delta for item in data]
                dates = [item.Date for item in data]
                labels.append('Китайский юань')
                data_x.append(deltas)
                data_y.append(dates)
            if ('INR' in codes):
                all_data = self.__exchangeRateUsecase.get_delta_INR_data()
                data = [item for item in all_data if item.Date >= start_date and item.Date <= end_date]
                deltas = [item.Delta for item in data]
                dates = [item.Date for item in data]
                labels.append('Индийская рупия')
                data_x.append(deltas)
                data_y.append(dates)
            if ('JPY' in codes):
                all_data = self.__exchangeRateUsecase.get_delta_JPY_data()
                data = [item for item in all_data if item.Date >= start_date and item.Date <= end_date]
                deltas = [item.Delta for item in data]
                dates = [item.Date for item in data]
                labels.append('Йена')
                data_x.append(deltas)
                data_y.append(dates)  
        else:
            if ('GBP' in codes):
                all_data = self.__exchangeRateUsecase.get_GBP_data()
                data = [item for item in all_data if item.Date >= start_date and item.Date <= end_date]
                rates = [item.Rate for item in data]
                dates = [item.Date for item in data]
                labels.append('Фунт Стерлингов')
                data_x.append(rates)
                data_y.append(dates)
            if ('USD' in codes):
                all_data = self.__exchangeRateUsecase.get_USD_data()
                data = [item for item in all_data if item.Date >= start_date and item.Date <= end_date]
                rates = [item.Rate for item in data]
                dates = [item.Date for item in data]
                labels.append('Доллар США')
                data_x.append(rates)
                data_y.append(dates)
            if ('TRY' in codes):
                all_data = self.__exchangeRateUsecase.get_TRY_data()
                data = [item for item in all_data if item.Date >= start_date and item.Date <= end_date]
                rates = [item.Rate for item in data]
                dates = [item.Date for item in data]
                labels.append('Турецкая лира')
                data_x.append(rates)
                data_y.append(dates)
            if ('EUR' in codes):
                all_data = self.__exchangeRateUsecase.get_EUR_data()
                data = [item for item in all_data if item.Date >= start_date and item.Date <= end_date]
                rates = [item.Rate for item in data]
                dates = [item.Date for item in data]
                labels.append('Евро')
                data_x.append(rates)
                data_y.append(dates)
            if ('CNY' in codes):
                all_data = self.__exchangeRateUsecase.get_CNY_data()
                data = [item for item in all_data if item.Date >= start_date and item.Date <= end_date]
                rates = [item.Rate for item in data]
                dates = [item.Date for item in data]
                labels.append('Китайский юань')
                data_x.append(rates)
                data_y.append(dates)
            if ('INR' in codes):
                all_data = self.__exchangeRateUsecase.get_INR_data()
                data = [item for item in all_data if item.Date >= start_date and item.Date <= end_date]
                rates = [item.Rate for item in data]
                dates = [item.Date for item in data]
                labels.append('Индийская рупия')
                data_x.append(rates)
                data_y.append(dates)
            if ('JPY' in codes):
                all_data = self.__exchangeRateUsecase.get_JPY_data()
                data = [item for item in all_data if item.Date >= start_date and item.Date <= end_date]
                rates = [item.Rate for item in data]
                dates = [item.Date for item in data]
                labels.append('Йена')
                data_x.append(rates)
                data_y.append(dates) 
        fig = go.Figure()
        for i in range(len(labels)):
            fig.add_scatter(y=data_x[i], x=data_y[i], name=labels[i])
        fig.update_layout(
            title='График изменения курса валют',
            xaxis_title="Дата",
            yaxis_title="Курс валют",
            legend_title="Название валют"
        )
        graph = dcc.Graph(figure=fig)
        div = html.Div(graph)
        return div

    def __validate(self, start_date: str, end_date: str, value: list[str], value_radio_1: str, value_radio_2: str) -> Union[html.Div, None]:
        errors: list[str] = []
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
        if (not value):
            errors.append('Валюты для считывания не выбраны')
        if(not value_radio_1):
            errors.append('Выбор типа графика не указан')
        if(not value_radio_2):
            errors.append('Выбор источника данных не указан')
        if (errors):
            errors_in_li: list[html.Li] = []
            for error in errors:
                errors_in_li.append(html.Li(error))
            return html.Div([
                html.Br(),
                'Ошибки:',
                html.Ul(errors_in_li)
            ])
        return None

    def __callback(self, start_date: str, end_date: str, value: list[str], value_radio_1: str, value_radio_2: str, n_clicks: int) -> html.Div:
        if (n_clicks == self.__n_clicks):
            return html.Div()
        self.__n_clicks = n_clicks
        err = self.__validate(start_date, end_date, value, value_radio_1, value_radio_2)
        if (err):
            return err
        return self.__get_graph(date.fromisoformat(start_date), date.fromisoformat(end_date),value, value_radio_1, value_radio_2)
        
    def register(self, app: FastAPI) -> None:
        appDash = Dash(requests_pathname_prefix='/graph/')
        appDash.layout = self.__generate_std_layout()
        @appDash.callback(
            Output('my-output', 'children'),
            Input('my-date-picker-range', 'start_date'),
            Input('my-date-picker-range', 'end_date'),
            Input('my-checklist', 'value'),
            Input('my-radio-1', 'value'),
            Input('my-radio-2', 'value'),
            Input('my-button', 'n_clicks'),
        )
        def callback(start_date: str, end_date: str, value: list[str], value_radio_1: str , value_radio_2: str, n_clicks: int) -> html.Div:
            return self.__callback(start_date, end_date, value, value_radio_1, value_radio_2, n_clicks)
        grapgApp = WSGIMiddleware(appDash.server)
        app.mount('/graph/', grapgApp)