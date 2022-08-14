class SearchInfo:
    def __init__(self, flight_from, flight_to, start_date, end_date, persons, kids):
        self.flight_from = flight_from
        self.flight_to = flight_to
        self.start_date = start_date
        self.end_date = end_date
        self.persons = persons
        self.kids = kids

    def flight_from(self, flight_from):
        self.flight_from = flight_from
        return self

    def flight_to(self, flight_to):
        self.flight_to = flight_to
        return self

    def start_date(self, start_date):
        self.start_date = start_date
        return self

    def end_date(self, end_date):
        self.end_date = end_date
        return self

    def persons(self, persons):
        self.persons = persons
        return self

    def kids(self, kids):
        self.kids = kids
        return self
