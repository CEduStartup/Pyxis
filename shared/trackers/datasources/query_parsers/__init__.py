from abc import ABCMeta, abstractmethod

class QueryParserCommon(object):
    
   __metaclass__ = ABCMeta
   
   @abstractmethod
   def parse_query(self, query): pass