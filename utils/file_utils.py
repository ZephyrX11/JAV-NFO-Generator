import os
import shutil
from typing import Optional
from pathlib import Path

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
    def get_output_path(filename: str, output_dir: str = ".") -> str:
        """
        Generate output path for NFO file.
        
        Args:
            filename: Original video filename
            output_dir: Output directory
            
        Returns:
            Full path for the NFO file
        """
        # Remove video extension and add .nfo
        base_name = os.path.splitext(filename)[0]
        nfo_filename = f"{base_name}.nfo"
        
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