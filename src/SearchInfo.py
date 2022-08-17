from unique_data import *
import datetime

class SearchInfo:
    # def __init__(self, flight_from, flight_to, start_date, end_date, persons, kids):
    #     self.flight_from = flight_from
    #     self.flight_to = flight_to
    #     self.start_date = start_date
    #     self.end_date = end_date
    #     self.persons = persons
    #     self.kids = kids

    def set_flight_from(self, flight_from: list):
        airports = [airport.lower() for airport in list(outbounddepartureairports.values())]
        flight_from = [airport.lower() for airport in flight_from]

        missing_airports = self.missing_airports(flight_from, airports)
        if len(missing_airports) != 0:
            error_message = [f'{airport} ' for airport in missing_airports]
            raise Exception(error_message)

        self.flight_from = flight_from
        return self

    def set_flight_to(self, flight_to):
        airports = [airport.lower() for airport in list(outboundarrivalairports.values())]
        flight_to = [airport.lower() for airport in flight_to]

        missing_airports = self.missing_airports(flight_to, airports)
        if len(missing_airports) != 0:
            error_message = [f'{airport} ' for airport in missing_airports]
            raise Exception(error_message)

        self.flight_to = flight_to
        return self

    def missing_airports(self, airports_to_check, airports):
        missing_airports = []
        for airport_to_check in airports_to_check:
            found = False
            for airport in airports:
                if airport_to_check in airport:
                    found = True
                    break
            if not found:
                missing_airports.append(airport_to_check)

        return missing_airports

    def set_start_date(self, start_date):
        self.start_date = datetime.datetime(int(start_date[2]), int(start_date[1]), int(start_date[0]))
        return self

    def set_end_date(self, end_date):
        self.end_date = datetime.datetime(int(end_date[2]), int(end_date[1]), int(end_date[0]))
        return self

    def persons(self, persons):
        self.persons = persons
        return self

    def kids(self, kids):
        self.kids = kids
        return self

    def __str__(self):
        return f"SearchInfo: " \
               f"Flight from: {self.flight_from} \n" \
               f"Flight to: {self.flight_to} \n" \
               f"Start date: {self.start_date} \n" \
               f"End date: {self.end_date} \n" \
               f"Persons: {self.persons} \n" \
               f"Kids: {self.kids} \n"
