from abc import ABC, abstractmethod


class IStorage(ABC):
    @abstractmethod
    def list_movies(self):
        """Return parsed DB as a Python data structure"""
        pass

    @abstractmethod
    def add_movie(self, title, year, rating, poster):
        """Add entry to data"""
        pass

    @abstractmethod
    def delete_movie(self, title):
        """Delete entry from data"""
        pass

    @abstractmethod
    def update_movie(self, title):
        """Add non-default info: 'movie notes'."""
        pass
