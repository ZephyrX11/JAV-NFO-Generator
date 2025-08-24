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
        Translate metadata fields based on configuration.
        
        Args:
            metadata: Metadata dictionary to translate
            force_enable: Force translation even if disabled in settings
            
        Returns:
            Translated metadata dictionary
        """
        if not settings.TRANSLATION_ENABLED and not force_enable:
            return metadata
        
        translated_metadata = metadata.copy()
        
        # Check if R18.dev is set to English mode
        r18dev_english_mode = getattr(settings, 'R18DEV_LANGUAGE', 'jp') == 'en'
        field_sources = metadata.get('_field_sources', {})
        
        skipped_fields = []
        for field in settings.TRANSLATION_FIELDS:
            field = field.strip()
            if field not in metadata or not metadata[field]:
                continue
            
            original_value = metadata[field]

            # Skip translation if field is from R18.dev and R18DEV_LANGUAGE is 'en'
            if r18dev_english_mode and field_sources.get(field) == 'r18dev':
                skipped_fields.append(field)
                continue

            # Handle array fields (directors, genres, actresses)
            if field in ['genres', 'directors'] and isinstance(original_value, list):
                translated_value = self._translate_array(original_value, field)
            elif field in ['actresses', 'actresses_array'] and isinstance(original_value, list):
                translated_value = self._translate_actress_array(original_value)
            else:
                translated_value = self.translate_text(original_value, field)
            
            if translated_value and translated_value != original_value:
                translated_metadata[field] = translated_value
                print(f"Translated {field}: {str(original_value)[:20]}... → {str(translated_value)[:30]}...")
            
            # Rate limiting for API calls (only if not cached)
            if isinstance(original_value, str) and not translation_cache.get_cached_translation(original_value, field):
                time.sleep(0.5)
            
        if skipped_fields:
            print(f"Skipped translation for {', '.join(skipped_fields)}: R18.dev provided English data")
        
        return translated_metadata

    def _translate_array(self, items: list, field_type: str) -> list:
        """
        Translate a list of strings (e.g., genres).
        """
        translated_items = []
        for item in items:
            cached = translation_cache.get_cached_translation(item, field_type)
            if cached:
                translated_items.append(cached)
                continue
            translated = self.translate_text(item, field_type)
            translated_items.append(translated if translated else item)
        return translated_items

    def _translate_actress_array(self, actresses: list) -> list:
        """
        Translate a list of actress dicts (with 'name' and 'image').
        """
        translated_list = []
        for actress in actresses:
            name = actress.get("name", "")
            image = actress.get("image", "")
            cached = translation_cache.get_cached_translation(name, "actress")
            if cached:
                translated_name = cached
            else:
                translated_name = self.translate_text(name, "actress") or name
            translated_list.append({"name": translated_name, "image": image})
        return translated_list

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