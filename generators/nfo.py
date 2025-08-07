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

        # Use director, genre and actress arrays
        directors = metadata.get('directors', [])
        genres = metadata.get('genres', [])
        actresses = metadata.get('actresses', [])

        director_tags = '\n'.join([f"    <director>{director}</director>" for director in directors])
        genre_tags = '\n'.join([f"    <genre>{genre}</genre>" for genre in genres])
        actor_tags = '\n'.join([
            f"    <actor>\n        <name>{actress['name']}</name>\n        <role>actress</role>\n        <thumb>{actress.get('image', '')}</thumb>\n    </actor>"
            for actress in actresses
        ])

        formatted_metadata['director_tags'] = director_tags
        formatted_metadata['genre_tags'] = genre_tags
        formatted_metadata['actor_tags'] = actor_tags

        # Format the template
        try:
            return self.template.format(**formatted_metadata)
        except KeyError as e:
            print(f"Missing required field in template: {e}")
    
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
            'directors': [],
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
            if key in ['directors', 'genres', 'actresses']:
                formatted[key] = value if isinstance(value, list) else default_value
            else:
                formatted[key] = str(value) if value is not None else default_value

        return formatted

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