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
            
            # Generate output path
            output_path = FileUtils.get_output_path(filename, output_dir)
            
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
            'series': '',
            'year': '',
            'release_date': '',
            'runtime': '',
            'country': 'Japan',
            'rating': 'R',
            'jav_id': '',
            'content_id': '',
            'plot': '',
            'outline': '',
            'tagline': '',
            'director': '',
            'studio': '',
            'label': '',
            'genres': '',
            'actress': '',
            'actress_image': '',
            'poster': '',
            'fanart': ''
        }
        
        # Convert all values to strings and ensure they exist
        formatted = {}
        for key, default_value in defaults.items():
            value = metadata.get(key, default_value)
            formatted[key] = str(value) if value is not None else default_value
        
        return formatted
    
    def _format_basic_content(self, metadata: Dict[str, str]) -> str:
        """
        Format basic NFO content as fallback.
        
        Args:
            metadata: Metadata dictionary
            
        Returns:
            Basic NFO content
        """
        return f"""<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<movie>
    <title>{metadata.get('title', '')}</title>
    <originaltitle>{metadata.get('original_title', '')}</originaltitle>
    <year>{metadata.get('year', '')}</year>
    <releasedate>{metadata.get('release_date', '')}</releasedate>
    <runtime>{metadata.get('runtime', '')}</runtime>
    <country>{metadata.get('country', 'Japan')}</country>
    <mpaa>{metadata.get('rating', 'R')}</mpaa>
    <id>{metadata.get('jav_id', '')}</id>
    <uniqueid type="jav" default="true">{metadata.get('jav_id', '')}</uniqueid>
    <uniqueid type="content_id">{metadata.get('content_id', '')}</uniqueid>
    <plot>{metadata.get('plot', '')}</plot>
    <director>{metadata.get('director', '')}</director>
    <studio>{metadata.get('studio', '')}</studio>
    <label>{metadata.get('label', '')}</label>
    <genre>{metadata.get('genres', '')}</genre>
    <actor>
        <name>{metadata.get('actress', '')}</name>
        <role>Actress</role>
        <thumb>{metadata.get('actress_image', '')}</thumb>
    </actor>
    <thumb aspect="poster">{metadata.get('poster', '')}</thumb>
    <fanart>
        <thumb>{metadata.get('fanart', '')}</thumb>
    </fanart>
</movie>"""
    
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