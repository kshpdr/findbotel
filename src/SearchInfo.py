from unique_data import *
import datetime


class SearchInfo:
    departure_airports = [airport.lower() for airport in list(outbounddepartureairports.values())]
    arrival_airports = [airport.lower() for airport in list(outboundarrivalairports.values())]

    def __init__(self, flight_from=None, flight_to=None, start_date: datetime.datetime = None,
                 end_date: datetime.datetime = None, adults: int = 0, kids: int = 0, offers=None, current_offer=None):
        if flight_to is None:
            flight_to = []
        if flight_from is None:
            flight_from = []
        if offers is None:
            offers = []
        self.flight_from = flight_from
        self.flight_to = flight_to
        self.start_date = start_date
        self.end_date = end_date
        self.adults = adults
        self.kids = kids
        self.offers = offers
        self.current_offer = current_offer

    def set_flight_from(self, airport_names: list):
        """Set a flight_from parameter to the list, when all airports are correct"""
        airport_names = self.lower_list(airport_names)
        missing_airports = self.missing_airports(airport_names, self.departure_airports)

        if len(missing_airports) != 0:
            error_message = [f'{airport} ' for airport in missing_airports]
            raise Exception(error_message)

        flight_from = self.get_codes(airport_names, outbounddepartureairports)
        self.flight_from = flight_from
        return self

    def set_flight_to(self, airport_names):
        """Set a flight_to parameter to the list, when all airports are correct"""
        airport_names = self.lower_list(airport_names)
        missing_airports = self.missing_airports(airport_names, self.arrival_airports)

        if len(missing_airports) != 0:
            error_message = [f'{airport} ' for airport in missing_airports]
            raise Exception(error_message)

        flight_to = self.get_codes(airport_names, outboundarrivalairports)
        self.flight_to = flight_to
        return self

    def missing_airports(self, airports_to_check, airports):
        """Checks whether some input airports are missing and return a list of them"""
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

    def get_codes(self, airports_to_check, target_airports):
        """Finds a code of all airports and returns a list of them"""
        codes = []
        for airport in airports_to_check:
            for key in list(target_airports.keys()):
                if airport in target_airports[key].lower():
                    codes.append(key)
        return codes

    def set_start_date(self, start_date: datetime.datetime):
        """Sets a start date of a journey"""
        self.start_date = datetime.datetime(int(start_date[2]), int(start_date[1]), int(start_date[0]))
        return self

    def set_end_date(self, end_date: datetime.datetime):
        """Sets an end date of a journey"""
        end_date = datetime.datetime(int(end_date[2]), int(end_date[1]), int(end_date[0]))
        if self.start_date > end_date:
            raise Exception("Sorry, end date can't be earlier than the start date. Try again!")
        self.end_date = end_date
        return self

    def set_adults(self, adults: int):
        """Sets amount of adults"""
        self.adults = adults
        return self

    def set_kids(self, kids: int):
        """Sets amount of kids"""
        self.kids = kids
        return self

    def set_offers(self, offers: list):
        self.current_offer = 0
        self.offers = offers
        return self

    def lower_list(self, array: list):
        """Return list with lowercased elements in it"""
        return [elem.lower() for elem in array]

    def add_airport_to_flight_from(self, airport: str):
        """Adds one airport to flight_from parameter"""
        self.flight_from.append(airport)

    def delete_airport_to_flight_from(self, airport: str):
        """Deletes an airport to flight_from parameter"""
        self.flight_from.remove(airport)

    def __str__(self):
        return f"SearchInfo: " \
               f"Flight from: {self.flight_from} \n" \
               f"Flight to: {self.flight_to} \n" \
               f"Start date: {self.start_date} \n" \
               f"End date: {self.end_date} \n" \
               f"Adults: {self.adults} \n" \
               f"Kids: {self.kids} \n"
