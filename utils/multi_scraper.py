from typing import Dict, List, Optional, Any
from scrapers.factory import ScraperFactory
from config.settings import settings

class MultiScraperManager:
    """
    Manages multiple scrapers with configurable field priorities.
    """
    
    def __init__(self):
        self.scraper_factory = ScraperFactory()
        self.enabled_scrapers = settings.ENABLED_SCRAPERS
        
        # Field priority mappings
        self.field_priorities = {
            'title': settings.FIELD_PRIORITY_TITLE,
            'title_en': settings.FIELD_PRIORITY_TITLE,
            'actresses': settings.FIELD_PRIORITY_ACTRESSES,
            'actors': settings.FIELD_PRIORITY_ACTRESSES,
            'directors': settings.FIELD_PRIORITY_DIRECTORS,
            'categories': settings.FIELD_PRIORITY_CATEGORIES,
            'genres': settings.FIELD_PRIORITY_CATEGORIES,
            'maker': settings.FIELD_PRIORITY_STUDIO,
            'studio': settings.FIELD_PRIORITY_STUDIO,
            'series': settings.FIELD_PRIORITY_SERIES,
            'release_date': settings.FIELD_PRIORITY_RELEASE_DATE,
            'runtime': settings.FIELD_PRIORITY_RUNTIME,
            'description': settings.FIELD_PRIORITY_DESCRIPTION,
            'cover_url': settings.FIELD_PRIORITY_COVER,
            'poster_url': settings.FIELD_PRIORITY_POSTER,
            'gallery': settings.FIELD_PRIORITY_GALLERY
        }
    
    def search_all_scrapers(self, jav_code: str) -> Dict[str, Optional[Dict[str, Any]]]:
        """
        Search using all enabled scrapers.
        
        Args:
            jav_code: The JAV code to search for
            
        Returns:
            Dictionary mapping scraper names to their results
        """
        results = {}
        
        for scraper_name in self.enabled_scrapers:
            scraper = self.scraper_factory.create_scraper(scraper_name)
            if scraper:
                print(f"Searching with {scraper.get_name()}...")
                try:
                    result = scraper.search(jav_code)
                    results[scraper_name] = result
                    if result:
                        print(f"✓ {scraper.get_name()} found data")
                    else:
                        print(f"✗ {scraper.get_name()} found no data")
                except Exception as e:
                    print(f"✗ {scraper.get_name()} failed: {e}")
                    results[scraper_name] = None
            else:
                print(f"✗ Failed to create scraper: {scraper_name}")
                results[scraper_name] = None
        
        return results
    
    def merge_metadata(self, scraper_results: Dict[str, Optional[Dict[str, Any]]]) -> Dict[str, Any]:
        """
        Merge metadata from multiple scrapers based on field priorities.
        
        Args:
            scraper_results: Dictionary mapping scraper names to their results
            
        Returns:
            Merged metadata dictionary
        """
        merged = {}
        
        # Get all available fields from all scrapers
        all_fields = set()
        for result in scraper_results.values():
            if result:
                all_fields.update(result.keys())
        
        # For each field, use the highest priority scraper that has data
        field_sources = {}  # Track which scraper provided each field
        for field in all_fields:
            field_value, source_scraper = self._get_field_by_priority_with_source(field, scraper_results)
            if field_value is not None:
                merged[field] = field_value
                if source_scraper:
                    field_sources[field] = source_scraper
        
        # Add metadata about which scrapers were used
        merged['_scrapers_used'] = [name for name, result in scraper_results.items() if result is not None]
        merged['_merge_strategy'] = settings.SCRAPER_MERGE_STRATEGY
        merged['_field_sources'] = field_sources  # Track field sources for translation optimization
        
        return merged
    
    def _get_field_by_priority(self, field: str, scraper_results: Dict[str, Optional[Dict[str, Any]]]) -> Any:
        """
        Get field value based on scraper priority.
        
        Args:
            field: Field name to get
            scraper_results: Dictionary mapping scraper names to their results
            
        Returns:
            Field value from highest priority scraper that has data
        """
        value, _ = self._get_field_by_priority_with_source(field, scraper_results)
        return value
    
    def _get_field_by_priority_with_source(self, field: str, scraper_results: Dict[str, Optional[Dict[str, Any]]]) -> tuple[Any, Optional[str]]:
        """
        Get field value and source scraper based on scraper priority.
        
        Args:
            field: Field name to get
            scraper_results: Dictionary mapping scraper names to their results
            
        Returns:
            Tuple of (field value, source scraper name) from highest priority scraper that has data
        """
        # Get priority list for this field, fallback to enabled scrapers order
        priority_list = self.field_priorities.get(field, self.enabled_scrapers)
        
        if settings.SCRAPER_MERGE_STRATEGY == "merge" and field in ['actresses', 'actors', 'directors', 'categories', 'gallery']:
            # For list fields, merge data from all scrapers
            merged_value = self._merge_list_field(field, scraper_results)
            # For merged fields, we can't identify a single source, so return None for source
            return merged_value, None
        
        # Priority strategy: use first available
        for scraper_name in priority_list:
            if scraper_name in scraper_results and scraper_results[scraper_name]:
                result = scraper_results[scraper_name]
                if field in result and self._is_valid_value(result[field]):
                    return result[field], scraper_name
        
        return None, None
    
    def _merge_list_field(self, field: str, scraper_results: Dict[str, Optional[Dict[str, Any]]]) -> List[Any]:
        """
        Merge list fields from multiple scrapers, removing duplicates.
        
        Args:
            field: Field name to merge
            scraper_results: Dictionary mapping scraper names to their results
            
        Returns:
            Merged list with duplicates removed
        """
        merged_list = []
        seen_items = set()
        
        # Get priority list for this field
        priority_list = self.field_priorities.get(field, self.enabled_scrapers)
        
        for scraper_name in priority_list:
            if scraper_name in scraper_results and scraper_results[scraper_name]:
                result = scraper_results[scraper_name]
                if field in result and isinstance(result[field], list):
                    for item in result[field]:
                        # Create a unique identifier for the item
                        if isinstance(item, dict):
                            # For dict items, use name or id as identifier
                            identifier = item.get('name', item.get('id', str(item)))
                        else:
                            identifier = str(item)
                        
                        if identifier not in seen_items:
                            merged_list.append(item)
                            seen_items.add(identifier)
        
        return merged_list
    
    def _is_valid_value(self, value: Any) -> bool:
        """
        Check if a value is valid (not None, empty string, empty list, etc.)
        
        Args:
            value: Value to check
            
        Returns:
            True if value is valid, False otherwise
        """
        if value is None:
            return False
        if isinstance(value, str) and not value.strip():
            return False
        if isinstance(value, (list, dict)) and len(value) == 0:
            return False
        if isinstance(value, (int, float)) and value == 0:
            return False
        return True
    
    def search_with_priority(self, jav_code: str) -> Optional[Dict[str, Any]]:
        """
        Search using multiple scrapers and merge results based on priorities.
        
        Args:
            jav_code: The JAV code to search for
            
        Returns:
            Merged metadata dictionary or None if no data found
        """
        print(f"Searching with {len(self.enabled_scrapers)} enabled scrapers: {', '.join(self.enabled_scrapers)}")
        
        # Search all scrapers
        scraper_results = self.search_all_scrapers(jav_code)
        
        # Check if any scraper found data
        found_data = any(result is not None for result in scraper_results.values())
        if not found_data:
            print("No data found from any scraper")
            return None
        
        # Merge results based on priorities
        merged_metadata = self.merge_metadata(scraper_results)
        
        print(f"✓ Merged metadata from {len(merged_metadata.get('_scrapers_used', []))} scrapers")
        return merged_metadata
