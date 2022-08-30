import random


class Offer:
    def __init__(self, hotelid, departuredate, returndate, countadults,
                 countchildren, price, inbounddepartureairport, inboundarrivalairport,
                 inboundairline, inboundarrivaldatetime, outbounddepartureairport,
                 outboundarrivalairport, outboundairline, outboundarrivaldatetime,
                 mealtype, oceanview, roomtype):
        self.hotelid = hotelid
        self.departuredate = departuredate
        self.returndate = returndate
        self.countadults = countadults
        self.countchildren = countchildren
        self.price = price
        self.inbounddepartureairport = inbounddepartureairport
        self.inboundarrivalairport = inboundarrivalairport
        self.inboundairline = inboundairline
        self.inboundarrivaldatetime = inboundarrivaldatetime
        self.outbounddepartureairport = outbounddepartureairport
        self.outboundarrivalairport = outboundarrivalairport
        self.outboundairline = outboundairline
        self.outboundarrivaldatetime = outboundarrivaldatetime
        self.mealtype = mealtype
        self.oceanview = oceanview
        self.roomtype = roomtype

    def __str__(self):
        str = f"🏨 {self.hotel.name} {self.hotelid} with {self.hotel.category_stars} ⭐ \n" \
              f"💶 {self.price} EUR \n" \
              f"🛏️ Type of room is {self.roomtype} \n"
        if self.oceanview == "true":
            str += "🌅 Room with ocean view \n"
        if self.mealtype == "allinclusive":
            str += "🥘 All inclusive \n"
        elif self.mealtype == "breakfast":
            str += "🥐 Only breakfast \n"
        return str
    #
    # def __repr__(self):
    #     return str(self)

    def set_hotel(self, hotel):
        self.hotel = hotel
        # for test purposes
        #self.photo_path = f"media/{random.randint(1,11)}.jpg"
        self.photo_path = f"../media/{random.randint(1, 11)}.jpg"
        # for a real life case
        # self.photo_path = f"../media/{hotel.id}.jpeg"
        return self