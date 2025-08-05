import requests
import time
from typing import Optional, Dict, Any
from config.settings import settings

class Translator:
    """Translation utility class."""
    
    def __init__(self):
        self.api_key = settings.TRANSLATION_API_KEY
        self.service = settings.TRANSLATION_SERVICE
        self.source_lang = settings.TRANSLATION_SOURCE_LANG
        self.target_lang = settings.TRANSLATION_TARGET_LANG
        self.session = requests.Session()
    
    def translate_text(self, text: str) -> Optional[str]:
        """
        Translate text using the configured translation service.
        
        Args:
            text: Text to translate
            
        Returns:
            Translated text or None if failed
        """
        if not text or not text.strip():
            return text
        
        if self.service == "google":
            return self._translate_google(text)
        elif self.service == "deepl":
            return self._translate_deepl(text)
        else:
            print(f"Unsupported translation service: {self.service}")
            return text
    
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
                translated_text = self.translate_text(original_text)
                
                if translated_text and translated_text != original_text:
                    translated_metadata[field] = translated_text
                    print(f"Translated {field}: {original_text[:50]}... → {translated_text[:50]}...")
                
                # Rate limiting for API calls
                time.sleep(0.5)
        
        return translated_metadata
    
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