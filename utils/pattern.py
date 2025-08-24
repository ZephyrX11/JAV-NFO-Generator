import re
import os
from typing import List, Optional, Tuple
from config.settings import settings

class PatternMatcher:
    """Utility class for pattern matching and JAV code extraction."""
    
    @staticmethod
    def extract_jav_code(filename: str) -> Optional[str]:
        """
        Extract JAV code from filename.
        
        Args:
            filename: The filename to extract code from
            
        Returns:
            JAV code if found, None otherwise
        """
        # Remove file extension
        name_without_ext = os.path.splitext(filename)[0]
        
        # Find JAV code pattern
        match = re.search(settings.JAV_CODE_PATTERN, name_without_ext, re.IGNORECASE)
        
        if match:
            return match.group().upper()
        return None
    
    @staticmethod
    def jav_code_to_content_id(jav_code: str) -> str:
        """
        Convert JAV code to Fanza content ID.
        
        Args:
            jav_code: JAV code (e.g., "SONE-638", "SDMF-022", "MILK-225", "DHLD-011")
            
        Returns:
            Fanza content ID (e.g., "sone00638", "1sdmf00022", "h_1240milk00225", "36dhld00011")
        """
        # Remove any non-alphanumeric characters except dash
        clean_code = re.sub(r'[^A-Za-z0-9-]', '', jav_code)
        
        # Split by dash
        parts = clean_code.split('-')
        if len(parts) != 2:
            return jav_code.lower()  # Return as-is if no dash found
        
        prefix, number = parts
        prefix_lower = prefix.lower()

        if prefix_lower == 't28':
            return f"55t28{number.zfill(5)}"
        
        if prefix_lower in ['abf', 'abw']:
            return f"118{prefix_lower}{number.zfill(3)}"
        
        no_zero_pad_codes = {'smus', 'smjh', 'smub', 'smjs', 'smjx', 'orecz', 'nost', 'mfc', 'mfcs'}
        if prefix_lower in no_zero_pad_codes:
            return f"{prefix_lower}{number.zfill(3)}"

        # Pad number with zeros to 5 digits
        padded_number = number.zfill(5)
        
        # Pattern 1: Prefix with "1" instead of "00" for specific codes
        prefix_1_codes = {
            'sdmf', 'dldss', 'sw', 'start', 'stars', 'piyo', 'sdam', 'sdmm', 'hawa', 'fsdss', 'senn'
        }
        if prefix_lower in prefix_1_codes:
            return f"1{prefix_lower}{padded_number}"
        
        # Pattern 2: Prefix with "h_" and specific numbers for certain maker codes
        h_prefix_codes = {
            'milk': 'h_1240',
            'ambi': 'h_237', 
            'fnew': 'h_491',
            'einav': 'h_1350',
            'pjab': 'h_1604'
        }
        if prefix_lower in h_prefix_codes:
            return f"{h_prefix_codes[prefix_lower]}{prefix_lower}{padded_number}"
        
        # Pattern 3: Numeric prefix before the code for specific patterns
        numeric_prefix_codes = {
            'dhld': '36',
            'fays': '55'
        }
        if prefix_lower in numeric_prefix_codes:
            return f"{numeric_prefix_codes[prefix_lower]}{prefix_lower}{padded_number}"
        
        # Default pattern: standard format
        return f"{prefix_lower}{padded_number}"
    
    @staticmethod
    def content_id_to_jav_code(content_id: str) -> str:
        """
        Convert Fanza content ID to JAV code.
        
        Args:
            content_id: Fanza content ID (e.g., "sone00638")
            
        Returns:
            JAV code (e.g., "SONE-638")
        """
        # Extract prefix (letters) and number
        match = re.match(r'([a-zA-Z]+)(\d+)', content_id)
        if not match:
            return content_id.upper()  # Return as-is if no pattern found
        
        prefix, number = match.groups()
        
        # Remove leading zeros from number
        clean_number = str(int(number))
        
        # Convert to uppercase
        prefix = prefix.upper()
        
        return f"{prefix}-{clean_number}"
    
    @staticmethod
    def is_video_file(filename: str) -> bool:
        """
        Check if file is a video file based on extension.
        
        Args:
            filename: The filename to check
            
        Returns:
            True if it's a video file, False otherwise
        """
        ext = os.path.splitext(filename)[1].lower()
        return ext in settings.VIDEO_EXTENSIONS
    
    @staticmethod
    def find_video_files(directory: str = ".", max_depth: int = 0) -> List[Tuple[str, str]]:
        """
        Find all video files in directory with their JAV codes.
        
        Args:
            directory: Directory to search in
            max_depth: Maximum depth to search (0 = current directory only)
            
        Returns:
            List of tuples (filename, jav_code)
        """
        video_files = []
        
        def scan_directory(current_dir: str, current_depth: int):
            """Recursively scan directory for video files."""
            try:
                for item in os.listdir(current_dir):
                    item_path = os.path.join(current_dir, item)
                    
                    # Check if it's a video file
                    if os.path.isfile(item_path) and PatternMatcher.is_video_file(item):
                        jav_code = PatternMatcher.extract_jav_code(item)
                        if jav_code:
                            # Store relative path from original directory
                            rel_path = os.path.relpath(item_path, directory)
                            video_files.append((rel_path, jav_code))
                    
                    # Recursively scan subdirectories if depth allows
                    elif os.path.isdir(item_path) and current_depth < max_depth:
                        scan_directory(item_path, current_depth + 1)
                        
            except FileNotFoundError:
                print(f"Directory {current_dir} not found.")
            except PermissionError:
                print(f"Permission denied accessing directory {current_dir}.")
        
        # Start scanning from the specified directory
        scan_directory(directory, 0)
        return video_files
    
    @staticmethod
    def normalize_jav_code(code: str) -> str:
        """
        Normalize JAV code format.
        
        Args:
            code: The JAV code to normalize
            
        Returns:
            Normalized JAV code
        """
        # Remove any non-alphanumeric characters except dash
        normalized = re.sub(r'[^A-Za-z0-9-]', '', code)
        
        # Convert to uppercase
        normalized = normalized.upper()
        
        return normalized
    
    @staticmethod
    def validate_jav_code(code: str) -> bool:
        """
        Validate JAV code format.
        
        Args:
            code: The JAV code to validate
            
        Returns:
            True if valid, False otherwise
        """
        if not code:
            return False
        
        # Check if it's a content ID format (e.g., sone00638)
        if re.match(r'^[a-zA-Z]+\d+$', code):
            return True
            
        # Check if it matches the JAV code pattern
        return bool(re.match(settings.JAV_CODE_PATTERN, code, re.IGNORECASE))
    
    @staticmethod
    def filter_genres(genres: str) -> str:
        """
        Filter out genres that should be skipped.
        
        Args:
            genres: Comma-separated genres string
            
        Returns:
            Filtered genres string
        """
        if not genres:
            return genres
        
        # Split genres and filter out skipped ones
        genre_list = [genre.strip() for genre in genres.split(',')]
        filtered_genres = []
        
        for genre in genre_list:
            if genre and genre not in settings.SKIP_GENRES:
                filtered_genres.append(genre)
        
        return ', '.join(filtered_genres) 
