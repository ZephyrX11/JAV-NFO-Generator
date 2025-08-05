from typing import Dict, List, Optional, Type
from .base import BaseScraper
from .fanza import FanzaScraper

class ScraperFactory:
    """Factory class for managing scrapers."""
    
    _scrapers: Dict[str, Type[BaseScraper]] = {
        'fanza': FanzaScraper,
    }
    
    @classmethod
    def get_available_scrapers(cls) -> List[str]:
        """
        Get list of available scraper names.
        
        Returns:
            List of scraper names
        """
        return list(cls._scrapers.keys())
    
    @classmethod
    def create_scraper(cls, name: str) -> Optional[BaseScraper]:
        """
        Create a scraper instance by name.
        
        Args:
            name: Name of the scraper to create
            
        Returns:
            Scraper instance or None if not found
        """
        scraper_class = cls._scrapers.get(name.lower())
        if scraper_class:
            return scraper_class()
        return None
    
    @classmethod
    def create_all_scrapers(cls) -> List[BaseScraper]:
        """
        Create instances of all available scrapers.
        
        Returns:
            List of all scraper instances
        """
        return [cls.create_scraper(name) for name in cls.get_available_scrapers()]
    
    @classmethod
    def register_scraper(cls, name: str, scraper_class: Type[BaseScraper]) -> None:
        """
        Register a new scraper.
        
        Args:
            name: Name for the scraper
            scraper_class: Scraper class to register
        """
        cls._scrapers[name.lower()] = scraper_class
    
    @classmethod
    def search_all(cls, jav_code: str) -> Dict[str, Optional[Dict]]:
        """
        Search all scrapers for metadata.
        
        Args:
            jav_code: JAV code to search for
            
        Returns:
            Dictionary mapping scraper names to metadata results
        """
        results = {}
        
        for name in cls.get_available_scrapers():
            scraper = cls.create_scraper(name)
            if scraper:
                try:
                    results[name] = scraper.search(jav_code)
                except Exception as e:
                    print(f"Error searching with {name} scraper: {e}")
                    results[name] = None
        
        return results 