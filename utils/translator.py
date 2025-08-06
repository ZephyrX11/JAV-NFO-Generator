import requests
import time
from typing import Optional, Dict, Any
from config.settings import settings
from utils.cache import translation_cache

class Translator:
    """Translation utility class."""
    
    def __init__(self):
        self.api_key = settings.TRANSLATION_API_KEY
        self.service = settings.TRANSLATION_SERVICE
        self.source_lang = settings.TRANSLATION_SOURCE_LANG
        self.target_lang = settings.TRANSLATION_TARGET_LANG
        self.session = requests.Session()
    
    def translate_text(self, text: str, field_type: str = "general") -> Optional[str]:
        """
        Translate text using the configured translation service with caching.
        
        Args:
            text: Text to translate
            field_type: Type of field for caching (genres, actress, director, etc.)
            
        Returns:
            Translated text or None if failed
        """
        if not text or not text.strip():
            return text
        
        # Check cache first
        cached_translation = translation_cache.get_cached_translation(text, field_type)
        if cached_translation:
            return cached_translation
        
        # Translate using service
        translated_text = None
        if self.service == "google":
            translated_text = self._translate_google(text)
        elif self.service == "deepl":
            translated_text = self._translate_deepl(text)
        else:
            print(f"Unsupported translation service: {self.service}")
            return text
        
        # Cache the translation if successful
        if translated_text and translated_text != text:
            translation_cache.set_cached_translation(text, field_type, translated_text)
        
        return translated_text
    
    def _translate_google(self, text: str) -> Optional[str]:
        """
        Translate using Google Translate API.
        
        Args:
            text: Text to translate
            
        Returns:
            Translated text or None if failed
        """
        try:
            # Simple Google Translate API call (free tier)
            url = "https://translate.googleapis.com/translate_a/single"
            params = {
                'client': 'gtx',
                'sl': self.source_lang,
                'tl': self.target_lang,
                'dt': 't',
                'q': text
            }
            
            response = self.session.get(url, params=params, timeout=10)
            response.raise_for_status()
            
            # Parse response
            data = response.json()
            if data and len(data) > 0 and len(data[0]) > 0:
                translated_parts = []
                for part in data[0]:
                    if part[0]:  # Translated text
                        translated_parts.append(part[0])
                return ''.join(translated_parts)
            
            return text
            
        except Exception as e:
            print(f"Google translation failed: {e}")
            return text
    
    def _translate_deepl(self, text: str) -> Optional[str]:
        """
        Translate using DeepL API.
        
        Args:
            text: Text to translate
            
        Returns:
            Translated text or None if failed
        """
        if not self.api_key:
            print("DeepL API key not configured")
            return text
        
        try:
            url = "https://api-free.deepl.com/v2/translate"
            headers = {
                'Authorization': f'DeepL-Auth-Key {self.api_key}',
                'Content-Type': 'application/x-www-form-urlencoded'
            }
            data = {
                'text': text,
                'source_lang': self.source_lang.upper(),
                'target_lang': self.target_lang.upper()
            }
            
            response = self.session.post(url, headers=headers, data=data, timeout=10)
            response.raise_for_status()
            
            result = response.json()
            if result and 'translations' in result and len(result['translations']) > 0:
                return result['translations'][0]['text']
            
            return text
            
        except Exception as e:
            print(f"DeepL translation failed: {e}")
            return text
    
    def translate_metadata(self, metadata: Dict[str, Any], force_enable: bool = False) -> Dict[str, Any]:
        """
        Translate metadata fields based on configuration with caching.
        
        Args:
            metadata: Original metadata dictionary
            force_enable: Force enable translation regardless of settings
            
        Returns:
            Metadata with translated fields
        """
        if not settings.TRANSLATION_ENABLED and not force_enable:
            return metadata
        
        translated_metadata = metadata.copy()
        
        for field in settings.TRANSLATION_FIELDS:
            field = field.strip()
            if field in metadata and metadata[field]:
                original_text = metadata[field]
                
                # Handle comma-separated fields (genres, actress)
                if field in ['genres', 'actress'] and ',' in original_text:
                    translated_text = self._translate_comma_separated(original_text, field, force_enable=force_enable)
                else:
                    # Use field-specific caching for single values
                    translated_text = self.translate_text(original_text, field)
                
                if translated_text and translated_text != original_text:
                    translated_metadata[field] = translated_text
                    print(f"Translated {field}: {original_text[:50]}... → {translated_text[:50]}...")
                
                # Rate limiting for API calls (only if not cached)
                if not translation_cache.get_cached_translation(original_text, field):
                    time.sleep(0.5)
        
        return translated_metadata
    
    def _translate_comma_separated(self, text: str, field_type: str, force_enable: bool = False) -> str:
        """
        Translate comma-separated values individually with caching.
        """
        if not text or not text.strip():
            return text
        # Split by comma and clean up
        items = [item.strip() for item in text.split(',') if item.strip()]
        translated_items = []
        for item in items:
            if field_type == 'actress' and (settings.TRANSLATION_ENABLED or force_enable):
                # Translate the full name as a single string
                translated_item = self.translate_text(item, field_type) or item
                # After translation, split and switch first and last part if possible
                parts = translated_item.split()
                if len(parts) == 2:
                    item = f"{parts[1]} {parts[0]}"
                elif len(parts) > 2:
                    item = f"{parts[-1]} {' '.join(parts[1:-1])} {parts[0]}"
                else:
                    item = translated_item
                translated_items.append(item)
                continue
            # Not actress or translation not enabled, normal translation
            cached_translation = translation_cache.get_cached_translation(item, field_type)
            if cached_translation:
                translated_items.append(cached_translation)
                continue
            translated_item = self.translate_text(item, field_type)
            if translated_item and translated_item != item:
                translated_items.append(translated_item)
            else:
                translated_items.append(item)
        return ', '.join(translated_items)
    
    def is_enabled(self) -> bool:
        """
        Check if translation is enabled.
        
        Returns:
            True if translation is enabled
        """
        return settings.TRANSLATION_ENABLED
    
    def get_supported_services(self) -> list:
        """
        Get list of supported translation services.
        
        Returns:
            List of supported services
        """
        return ["google", "deepl"] 