from models.SearchInfo import SearchInfo
from utils.MarkupGenerator import MarkupGenerator

class User:
    def __init__(self, id: int, journey_to_find: SearchInfo, markup_generator: MarkupGenerator):
        self.id = id
        self.journey_to_find = journey_to_find
        self.markup_generator = markup_generator