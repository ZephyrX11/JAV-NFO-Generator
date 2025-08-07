from typing import Dict, Any, Optional
from config.settings import settings
from utils.file_utils import FileUtils

class NFOGenerator:
    """Generator for NFO files."""
    
    def __init__(self):
        self.template = settings.NFO_TEMPLATE
    
    def generate_nfo(self, metadata: Dict[str, Any], filename: str, output_dir: str = ".") -> bool:
        """
        Generate NFO file from metadata.
        
        Args:
            metadata: Metadata dictionary
            filename: Original video filename
            output_dir: Output directory for NFO file
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Generate NFO content
            content = self._format_content(metadata)
            
            # Generate output path (pass metadata for tag replacement)
            output_path = FileUtils.get_output_path(filename, output_dir, metadata)
            
            # Write NFO file
            if FileUtils.write_nfo_file(content, output_path):
                print(f"Generated NFO file: {output_path}")
                return True
            else:
                print(f"Failed to write NFO file: {output_path}")
                return False
                
        except Exception as e:
            print(f"Error generating NFO file: {e}")
            return False
    
    def _format_content(self, metadata: Dict[str, Any]) -> str:
        """
        Format metadata into NFO content.

        Args:
            metadata: Metadata dictionary

        Returns:
            Formatted NFO content
        """
        # Ensure all required fields are present
        formatted_metadata = self._ensure_required_fields(metadata)

        # Use genre and actress arrays if available, otherwise fall back to string parsing
        genres = metadata.get('genres', [])
        actresses = metadata.get('actresses', [])

        # Generate genre tags from array
        genre_tags = '\n'.join([f"    <genre>{genre}</genre>" for genre in genres])

        # Generate actor tags from actress array with individual thumb URLs
        actor_tags = '\n'.join([
            f"    <actor>\n        <name>{actress['name']}</name>\n        <role>actress</role>\n        <thumb>{actress.get('image', '')}</thumb>\n    </actor>"
            for actress in actresses
        ])

        formatted_metadata['genre_tags'] = genre_tags
        formatted_metadata['actor_tags'] = actor_tags

        # Format the template
        try:
            return self.template.format(**formatted_metadata)
        except KeyError as e:
            print(f"Missing required field in template: {e}")
            # Fallback to basic formatting
            return self._format_basic_content(formatted_metadata)
    
    def _ensure_required_fields(self, metadata: Dict[str, Any]) -> Dict[str, str]:
        """
        Ensure all required fields are present with default values.
        
        Args:
            metadata: Raw metadata
            
        Returns:
            Metadata with all required fields
        """
        defaults = {
            'title': '',
            'original_title': '',
            'sort_title': '',
            'jav_id': '',
            'content_id': '',
            'release_date': '',
            'year': '',
            'runtime': '',
            'mpaa': 'XXX',
            'rating': '',
            'votes': '',
            'plot': '',
            'outline': '',
            'tagline': '',
            'series': '',
            'director': '',
            'studio': '',
            'label': '',
            'genres': [],
            'actresses': [],
            'cover': '',
            'poster': '',
            'fanart': ''
        }
        
        # Convert all values to strings and ensure they exist
        formatted = {}
        for key, default_value in defaults.items():
            value = metadata.get(key, default_value)
            # Keep arrays as arrays, convert others to strings
            if key in ['genres', 'actresses']:
                formatted[key] = value if isinstance(value, list) else default_value
            else:
                formatted[key] = str(value) if value is not None else default_value

        return formatted
    
    def _format_basic_content(self, metadata: Dict[str, str]) -> str:
        """
        Format basic NFO content as fallback.
        """
        # Use genre and actress arrays if available, otherwise fall back to string parsing
        genres = metadata.get('genres', [])
        actresses = metadata.get('actresses', [])

        # Build genre tags from array
        genre_tags = '\n'.join([f"    <genre>{genre}</genre>" for genre in genres])

        # Build actor tags from actress array with individual thumb URLs
        actor_tags = '\n'.join([
            f"    <actor>\n        <name>{actress['name']}</name>\n        <role>actress</role>\n        <thumb>{actress.get('image', '')}</thumb>\n    </actor>"
            for actress in actresses
        ])
        return f"""<?xml version=\"1.0\" encoding=\"UTF-8\" standalone=\"yes\"?>\n<movie>\n    <title>{metadata.get('title', '')}</title>\n    <originaltitle>{metadata.get('original_title', '')}</originaltitle>\n    <year>{metadata.get('year', '')}</year>\n    <releasedate>{metadata.get('release_date', '')}</releasedate>\n    <runtime>{metadata.get('runtime', '')}</runtime>\n    <country>{metadata.get('country', 'Japan')}</country>\n    <mpaa>{metadata.get('rating', 'R')}</mpaa>\n    <id>{metadata.get('jav_id', '')}</id>\n    <uniqueid type=\"jav\" default=\"true\">{metadata.get('jav_id', '')}</uniqueid>\n    <uniqueid type=\"content_id\">{metadata.get('content_id', '')}</uniqueid>\n    <plot>{metadata.get('plot', '')}</plot>\n    <director>{metadata.get('director', '')}</director>\n    <studio>{metadata.get('studio', '')}</studio>\n    <label>{metadata.get('label', '')}</label>\n{genre_tags}\n{actor_tags}\n    <thumb aspect=\"poster\">{metadata.get('poster', '')}</thumb>\n    <fanart>\n        <thumb>{metadata.get('fanart', '')}</thumb>\n    </fanart>\n</movie>"""
    
    def generate_batch(self, metadata_list: list, output_dir: str = ".") -> int:
        """
        Generate NFO files for multiple items.
        
        Args:
            metadata_list: List of tuples (filename, metadata)
            output_dir: Output directory
            
        Returns:
            Number of successfully generated files
        """
        success_count = 0
        
        for filename, metadata in metadata_list:
            if self.generate_nfo(metadata, filename, output_dir):
                success_count += 1
        
        return success_count 