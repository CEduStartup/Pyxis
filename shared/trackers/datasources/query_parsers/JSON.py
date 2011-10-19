import abc
import json
from . import QueryParserCommon

class QueryParserJSON(QueryParserCommon):
    def parse_query(self, query):
        return json.loads(query)
        