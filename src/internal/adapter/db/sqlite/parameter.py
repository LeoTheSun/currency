from internal.adapter.db.sqlite.utils import format_query
from pkg.sqlite.sqlite import SQLite
from logging import Logger
from internal.domain.entity.parameter import Parameter


class parameterStorage:
    def __init__(self, sqlite: SQLite, logger: Logger):
        self.__sqlite = sqlite
        self.__logger = logger
    
    def create(self, parameter: Parameter) -> Parameter:
        q = """
            INSERT INTO parameters (name, value)
            VALUES (?, ?)
            RETURNING id;
        """
        self.__logger.debug(f"SQL Query: '{format_query(q)}'")
        raw_id = self.__sqlite.query_row(q, (parameter.Name, parameter.Value,))
        parameter = Parameter(
            Id=int(raw_id[0]),
            Name=parameter.Name,
            Value=parameter.Value
        )
        return parameter
    
    def get_one(self, parameter: Parameter) -> Parameter:
        q = """
            SELECT id, name, value
			FROM parameters
			WHERE name = ?
        """
        self.__logger.debug(f"SQL Query: '{format_query(q)}'")
        raw_parameter = self.__sqlite.query_row(q, (parameter.Name, ))
        parameter = Parameter(
            Id=int(raw_parameter[0]),
            Name=str(raw_parameter[1]),
            Value=str(raw_parameter[2])
        )
        return parameter