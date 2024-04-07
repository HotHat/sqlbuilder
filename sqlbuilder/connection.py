import time
from .builder import Builder
from .grammar import Grammar
from .driver import DriverBase


class QueryException(Exception):
    pass


class Connection:
    def __init__(self, driver: DriverBase, table_prefix=''):
        self.driver = driver
        self.table_prefix = table_prefix

    def table(self, table):
        return self.new_query().table(table)

    def get_grammar(self):
        return Grammar(self.table_prefix)

    def new_query(self):
        return Builder(self, self.get_grammar())

    def select(self, query, bindings):
        bindings = bindings if bindings else []

        def fn(sql, binder):
            return self.driver.fetch_all(sql, binder)

        return self.run(query, bindings, fn)

    def insert(self, query, bindings):
        bindings = bindings if bindings else []

        def fn(sql, binder):
            self.driver.statement(sql, binder)
            return self.driver.last_rowid()

        return self.run(query, bindings, fn)

    def update(self, query, bindings):
        return self.effecting_statement(query, bindings)

    def delete(self, query, bindings):
        return self.effecting_statement(query, bindings)

    def effecting_statement(self, query, bindings):
        def fn(sql, binder):
            return self.driver.statement(sql, binder)

        return self.run(query, bindings, fn)

    @staticmethod
    def elapsed_time(start):
        return round(time.time() * 1000) - start

    def log_query(self, query, bindings, elapsed_time):
        pass

    def run(self, query, bindings, fn):
        start = round(time.time() * 1000)
        try:
            result = fn(query, bindings)
        except Exception as e:
            raise QueryException(query, bindings)

        self.log_query(query, bindings, self.elapsed_time(start))

        return result