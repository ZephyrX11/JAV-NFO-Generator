import os
import shutil
from typing import Optional
from pathlib import Path
import re
from config.settings import settings

class FileUtils:
    """Utility class for file operations."""
    
    @staticmethod
    def ensure_directory(directory: str) -> bool:
        """
        Ensure directory exists, create if it doesn't.
        
        Args:
            directory: Directory path to ensure
            
        Returns:
            True if directory exists or was created, False otherwise
        """
        try:
            os.makedirs(directory, exist_ok=True)
            return True
        except (OSError, PermissionError):
            return False
    
    @staticmethod
    def get_output_path(filename: str, output_dir: str = ".", metadata: dict = None) -> str:
        """
        Generate output path for NFO file, supporting tag replacement.
        """
        # Use output_dir or settings.OUTPUT_DIR_TEMPLATE
        if not output_dir or output_dir == ".":
            output_dir = getattr(settings, "OUTPUT_DIR_TEMPLATE", "<ID>")
        # Replace tags in output_dir if metadata is provided
        if metadata:
            def tag_replacer(match):
                tag = match.group(1)
                value = metadata.get(tag.lower(), "")
                if tag.lower() == "title" and isinstance(value, str) and len(value) > 50:
                    value = value[:50].rstrip() + "..."
                return str(value) if value else tag
            output_dir = re.sub(r"<([A-Z_]+)>", tag_replacer, output_dir)
        # Sanitize output_dir to be a valid folder name
        output_dir = re.sub(r'[<>:"\\|?*\x00-\x1F]', '_', output_dir).strip() or "."

        # Use the output video name (without extension) as the NFO base name
        video_base = FileUtils.get_output_video_name(filename, output_dir, metadata)
        nfo_base = os.path.splitext(video_base)[0]
        nfo_filename = f"{nfo_base}.nfo"

        return os.path.join(output_dir, nfo_filename)
    
    @staticmethod
    def write_nfo_file(content: str, filepath: str) -> bool:
        """
        Write NFO content to file.
        
        Args:
            content: NFO content to write
            filepath: Path to write the file to
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Ensure directory exists
            directory = os.path.dirname(filepath)
            if directory and not FileUtils.ensure_directory(directory):
                return False
            
            # Write file with UTF-8 encoding
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
            return True
        except (IOError, OSError, PermissionError):
            return False
    
    @staticmethod
    def file_exists(filepath: str) -> bool:
        """
        Check if file exists.
        
        Args:
            filepath: Path to check
            
        Returns:
            True if file exists, False otherwise
        """
        return os.path.isfile(filepath)
    
    @staticmethod
    def get_file_size(filepath: str) -> Optional[int]:
        """
        Get file size in bytes.
        
        Args:
            filepath: Path to file
            
        Returns:
            File size in bytes, None if error
        """
        try:
            return os.path.getsize(filepath)
        except (OSError, FileNotFoundError):
            return None
    
    @staticmethod
    def backup_file(filepath: str, backup_suffix: str = ".backup") -> bool:
        """
        Create a backup of a file.
        
        Args:
            filepath: Path to file to backup
            backup_suffix: Suffix for backup file
            
        Returns:
            True if backup successful, False otherwise
        """
        if not FileUtils.file_exists(filepath):
            return False
            
        backup_path = f"{filepath}{backup_suffix}"
        
        try:
            shutil.copy2(filepath, backup_path)
            return True
        except (OSError, PermissionError):
            return False
    
    @staticmethod
    def get_relative_path(filepath: str, base_dir: str = ".") -> str:
        """
        Get relative path from base directory.
        
        Args:
            filepath: Full file path
            base_dir: Base directory
            
        Returns:
            Relative path
        """
        try:
            return os.path.relpath(filepath, base_dir)
        except ValueError:
            return filepath
    
    @staticmethod
    def get_output_video_name(filename: str, output_dir: str = ".", metadata: dict = None) -> str:
        """
        Generate output video file name, supporting tag replacement.
        """
        ext = os.path.splitext(filename)[1]
        video_name_template = getattr(settings, "OUTPUT_VIDEO_NAME_TEMPLATE", "<ID><EXT>")
        if metadata:
            def tag_replacer(match):
                tag = match.group(1)
                value = metadata.get(tag.lower(), "")
                if tag.lower() == "title" and isinstance(value, str) and len(value) > 50:
                    value = value[:50].rstrip() + "..."
                if tag.lower() == "ext":
                    value = ext
                return str(value) if value else tag
            video_name = re.sub(r"<([A-Z_]+)>", tag_replacer, video_name_template)
        else:
            video_name = os.path.basename(filename)
        # Sanitize filename
        video_name = re.sub(r'[<>:"/\\|?*\x00-\x1F]', '_', video_name).strip() or "video" + ext
        return video_name