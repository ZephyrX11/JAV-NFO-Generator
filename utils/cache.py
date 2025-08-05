"""
Translation cache utilities for storing and retrieving translated values.
"""

import os
import json
import hashlib
from typing import Dict, Any, Optional
from pathlib import Path
from config.settings import settings


class TranslationCache:
    """Cache for translated values to ensure consistency."""
    
    def __init__(self, cache_file: str = None):
        """
        Initialize the translation cache.
        
        Args:
            cache_file: Path to cache file (default: ~/.jav_nfo_cache.json)
        """
        if cache_file is None:
            cache_dir = Path.home() / ".jav_nfo_generator"
            cache_dir.mkdir(exist_ok=True)
            cache_file = cache_dir / "translation_cache.json"
        
        self.cache_file = Path(cache_file)
        self.cache = self._load_cache()
    
    def _load_cache(self) -> Dict[str, Any]:
        """Load cache from file."""
        if self.cache_file.exists():
            try:
                with open(self.cache_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except (json.JSONDecodeError, IOError) as e:
                print(f"Warning: Could not load cache file: {e}")
                return self._get_default_cache()
        return self._get_default_cache()
    
    def _get_default_cache(self) -> Dict[str, Any]:
        """Get default cache structure."""
        return {
            'genres': {},
            'actress': {},
            'director': {},
            'studio': {},
            'label': {},
            'series': {},
            'metadata': {}
        }
    
    def _save_cache(self):
        """Save cache to file."""
        try:
            with open(self.cache_file, 'w', encoding='utf-8') as f:
                json.dump(self.cache, f, ensure_ascii=False, indent=2)
        except IOError as e:
            print(f"Warning: Could not save cache file: {e}")
    
    def _get_cache_key(self, text: str, field_type: str) -> str:
        """
        Generate a cache key for the given text and field type.
        
        Args:
            text: Text to translate
            field_type: Type of field (genres, actress, director, etc.)
            
        Returns:
            Cache key string
        """
        # Create a hash of the text and field type
        key_data = f"{text.lower().strip()}:{field_type}"
        return hashlib.md5(key_data.encode('utf-8')).hexdigest()
    
    def get_cached_translation(self, text: str, field_type: str) -> Optional[str]:
        """
        Get cached translation for text.
        
        Args:
            text: Original text
            field_type: Type of field (genres, actress, director, etc.)
            
        Returns:
            Cached translation or None if not found
        """
        if not text or field_type not in self.cache:
            return None
        
        cache_key = self._get_cache_key(text, field_type)
        return self.cache[field_type].get(cache_key)
    
    def set_cached_translation(self, text: str, field_type: str, translation: str):
        """
        Cache a translation.
        
        Args:
            text: Original text
            field_type: Type of field (genres, actress, director, etc.)
            translation: Translated text
        """
        if not text or not translation or field_type not in self.cache:
            return
        
        cache_key = self._get_cache_key(text, field_type)
        self.cache[field_type][cache_key] = translation
        self._save_cache()
    
    def get_cached_metadata(self, jav_id: str) -> Optional[Dict[str, Any]]:
        """
        Get cached metadata for a JAV ID.
        
        Args:
            jav_id: JAV ID
            
        Returns:
            Cached metadata or None if not found
        """
        return self.cache['metadata'].get(jav_id)
    
    def set_cached_metadata(self, jav_id: str, metadata: Dict[str, Any]):
        """
        Cache metadata for a JAV ID.
        
        Args:
            jav_id: JAV ID
            metadata: Metadata dictionary
        """
        self.cache['metadata'][jav_id] = metadata
        self._save_cache()
    
    def clear_cache(self, field_type: str = None):
        """
        Clear cache or specific field type.
        
        Args:
            field_type: Specific field type to clear (None for all)
        """
        if field_type:
            if field_type in self.cache:
                self.cache[field_type].clear()
        else:
            self.cache = self._get_default_cache()
        
        self._save_cache()
    
    def get_cache_stats(self) -> Dict[str, int]:
        """
        Get cache statistics.
        
        Returns:
            Dictionary with cache entry counts
        """
        return {
            field_type: len(entries) 
            for field_type, entries in self.cache.items()
        }
    
    def export_cache(self, output_file: str):
        """
        Export cache to a file.
        
        Args:
            output_file: Output file path
        """
        try:
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(self.cache, f, ensure_ascii=False, indent=2)
        except IOError as e:
            print(f"Error exporting cache: {e}")
    
    def import_cache(self, input_file: str):
        """
        Import cache from a file.
        
        Args:
            input_file: Input file path
        """
        try:
            with open(input_file, 'r', encoding='utf-8') as f:
                imported_cache = json.load(f)
            
            # Merge with existing cache
            for field_type, entries in imported_cache.items():
                if field_type in self.cache:
                    self.cache[field_type].update(entries)
            
            self._save_cache()
        except (json.JSONDecodeError, IOError) as e:
            print(f"Error importing cache: {e}")


# Global cache instance
translation_cache = TranslationCache() 