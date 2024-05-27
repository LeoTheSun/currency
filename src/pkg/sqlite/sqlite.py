from sqlite3 import connect
from typing import Any
from config.config import SQLite as Cfg
from datetime import date


class SQLite:
    def __init__(self, cfg: Cfg):
        exception = None
        for _ in range(cfg.tries):
            try:
                self.__connection = connect(cfg.path, cfg.timeout, check_same_thread=False)
            except Exception as e:
                exception = e
                continue
            exception = None
            break
        if exception is not None:
            raise Exception('ошибка подключения к базе данных')
    
    def exec(self, sql: str, args: set[Any]=()) -> None:
        cursor = self.__connection.cursor()
        cursor.execute(sql, args)
        cursor.close()
        self.__connection.commit()

    def query(self, sql: str, args: set[Any]=()) -> list[Any]:
        cursor = self.__connection.cursor()
        cursor.execute(sql, args)
        result = cursor.fetchall()
        cursor.close()
        return result
        
    def query_row(self, sql: str, args: set[Any]=()) -> Any:
        cursor = self.__connection.cursor()
        cursor.execute(sql, args)
        result = cursor.fetchone()
        return result

    def setup_database(self):
        self.exec("""
            CREATE TABLE IF NOT EXISTS currency_codes (
                id INTEGER PRIMARY KEY AUTOINCREMENT, 
                country TEXT,
                currency TEXT,
                code TEXT,
                number INTEGER
            );
        """)
        self.exec("""
            CREATE TABLE IF NOT EXISTS exchange_rates (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date TEXT,
                count INTEGER,
                rate TEXT,
                change TEXT,
                code TEXT
            );
        """)
        self.exec("""
            CREATE TABLE IF NOT EXISTS delta_rates (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date TEXT,
                delta TEXT,
                code TEXT
            );
        """)
        self.exec("""
            CREATE TABLE IF NOT EXISTS parameters (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT,
                value TEXT
            );
        """)

    def set_std_date(self, std_date: str):
        d = std_date.split('.')
        std_date = date(int(d[2]), int(d[1]), int(d[0]))
        q = """
            SELECT EXISTS (
			    SELECT id
			    FROM parameters
			    WHERE name = 'std_date'
		    );
        """
        exists = bool(self.query_row(q)[0])
        if (not exists):
            q = f"""
                INSERT INTO parameters (name, value)
                VALUES ('std_date', '{str(std_date)}');
            """
            self.exec(q)