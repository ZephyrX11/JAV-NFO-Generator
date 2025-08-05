from abc import ABC, abstractmethod
from typing import Dict, Optional, Any
import time
import requests
from config.settings import settings

class BaseScraper(ABC):
    """Base class for all scrapers."""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': settings.USER_AGENT
        })
    
    def _make_request(self, url: str, method: str = 'GET', **kwargs) -> Optional[requests.Response]:
        """
        Make HTTP request with error handling and rate limiting.
        
        Args:
            url: URL to request
            method: HTTP method
            **kwargs: Additional request parameters
            
        Returns:
            Response object or None if failed
        """
        try:
            # Add timeout if not specified
            if 'timeout' not in kwargs:
                kwargs['timeout'] = settings.REQUEST_TIMEOUT
            
            response = self.session.request(method, url, **kwargs)
            response.raise_for_status()
            
            # Rate limiting
            time.sleep(settings.REQUEST_DELAY)
            
            return response
        except requests.exceptions.RequestException as e:
            print(f"Request failed: {e}")
            return None
    
    @abstractmethod
    def search(self, jav_code: str) -> Optional[Dict[str, Any]]:
        """
        Search for metadata by JAV code.
        
        Args:
            jav_code: The JAV code to search for
            
        Returns:
            Dictionary with metadata or None if not found
        """
        pass
    
    @abstractmethod
    def get_name(self) -> str:
        """
        Get scraper name.
        
        Returns:
            Scraper name
        """
        pass
    
    def format_metadata(self, raw_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Format raw metadata into standard format.
        
        Args:
            raw_data: Raw metadata from scraper
            
        Returns:
            Formatted metadata
        """
        # Default implementation - subclasses should override
        return raw_data
    
    def validate_response(self, response: requests.Response) -> bool:
        """
        Validate if response contains valid data.
        
        Args:
            response: HTTP response
            
        Returns:
            True if response is valid, False otherwise
        """
        return response.status_code == 200 and len(response.content) > 0 