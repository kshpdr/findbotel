class Hotel:
    def __init__(self, id, name, latitude, longitude, category_stars):
        self.id = id
        self.name = name
        self.latitude = latitude
        self.longitude = longitude
        self.category_stars = category_stars

    def __str__(self):
        return f"""Hotel: id: {self.id}
        name: {self.name}
        latitude: {self.latitude}
        longitude: {self.longitude}
        category_stars: {self.category_stars}"""