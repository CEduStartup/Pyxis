import abc
import json
from shared.trackers.datasources.query_parsers import QueryParserCommon

class QueryParserJSON(QueryParserCommon):
    def parse_query(self, query):
        return json.loads(query)
        