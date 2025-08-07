#!/usr/bin/env python3
"""
JAV NFO Generator - A CLI tool for scraping JAV metadata and generating .nfo files.
"""

import os
import sys
from typing import List, Optional
import click
from colorama import init, Fore, Style
from tqdm import tqdm
import requests

# Initialize colorama for cross-platform colored output
init()

# Add project root to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from config.settings import settings
from scrapers.factory import ScraperFactory
from generators.nfo import NFOGenerator
from utils.pattern import PatternMatcher
from utils.file_utils import FileUtils
from utils.translator import Translator
from utils.cache import translation_cache

class JAVNFOGenerator:
    """Main application class for JAV NFO Generator."""
    
    def __init__(self):
        self.scraper_factory = ScraperFactory()
        self.nfo_generator = NFOGenerator()
        self.translator = Translator()
    
    def search_manual(self, jav_id: str, output_dir: str = ".", generate_nfo: bool = False, translate: bool = False) -> bool:
        """
        Manual search for a specific JAV ID or content ID.
        
        Args:
            jav_id: The JAV ID or content ID to search for
            output_dir: Output directory for NFO files
            generate_nfo: Whether to generate NFO file or output to terminal
            translate: Whether to translate metadata
            
        Returns:
            True if successful, False otherwise
        """
        # Normalize and validate JAV ID
        jav_id = PatternMatcher.normalize_jav_code(jav_id)
        if not PatternMatcher.validate_jav_code(jav_id):
            print(f"{Fore.RED}Invalid JAV ID format: {jav_id}{Style.RESET_ALL}")
            return False
        
        print(f"{Fore.CYAN}Searching for JAV ID: {jav_id}{Style.RESET_ALL}")
        
        # Search all scrapers
        results = self.scraper_factory.search_all(jav_id)
        
        # Find the best result
        best_result = self._get_best_result(results)
        
        if best_result:
            print(f"{Fore.GREEN}Found metadata for {jav_id}{Style.RESET_ALL}")
            
            # Apply translation if requested
            if translate:
                print(f"{Fore.CYAN}Translating metadata...{Style.RESET_ALL}")
                best_result = self.translator.translate_metadata(best_result, force_enable=True)
            
            if generate_nfo:
                # Generate NFO file
                success = self.nfo_generator.generate_nfo(
                    best_result, 
                    f"{jav_id}.mp4",  # Use JAV ID as filename
                    output_dir
                )
                
                if success:
                    print(f"{Fore.GREEN}Successfully generated NFO file{Style.RESET_ALL}")
                    return True
                else:
                    print(f"{Fore.RED}Failed to generate NFO file{Style.RESET_ALL}")
                    return False
            else:
                # Output metadata to terminal
                self._print_metadata(best_result)
                return True
        else:
            print(f"{Fore.YELLOW}No metadata found for {jav_id}{Style.RESET_ALL}")
            return False
    
    def search_auto(self, directory: str = ".", output_dir: str = ".", translate: bool = False) -> int:
        """
        Auto-detect video files and generate NFO files.
        
        Args:
            directory: Directory to scan for video files
            output_dir: Output directory for NFO files
            translate: Whether to translate metadata
            
        Returns:
            Number of successfully processed files
        """
        print(f"{Fore.CYAN}Scanning directory: {directory}{Style.RESET_ALL}")
        
        # Find video files with JAV codes
        video_files = PatternMatcher.find_video_files(directory)
        
        if not video_files:
            print(f"{Fore.YELLOW}No video files with JAV codes found in {directory}{Style.RESET_ALL}")
            return 0
        
        print(f"{Fore.CYAN}Found {len(video_files)} video files with JAV codes{Style.RESET_ALL}")
        
        # Process each file
        success_count = 0
        for filename, jav_code in tqdm(video_files, desc="Processing files"):
            print(f"\n{Fore.CYAN}Processing: {filename} ({jav_code}){Style.RESET_ALL}")
            
            # Check if NFO already exists
            nfo_path = FileUtils.get_output_path(filename, output_dir)
            if FileUtils.file_exists(nfo_path):
                print(f"{Fore.YELLOW}NFO file already exists: {nfo_path}{Style.RESET_ALL}")
                continue
            
            # Search for metadata
            results = self.scraper_factory.search_all(jav_code)
            best_result = self._get_best_result(results)
            
            if best_result:
                # Apply translation if requested
                if translate:
                    print(f"{Fore.CYAN}Translating metadata for {filename}...{Style.RESET_ALL}")
                    best_result = self.translator.translate_metadata(best_result, force_enable=True)
                
                # Generate NFO file (pass metadata for tag replacement)
                nfo_success = self.nfo_generator.generate_nfo(best_result, filename, output_dir)
                if nfo_success:
                    # Download poster and fanart images to output dir
                    nfo_dir = os.path.dirname(FileUtils.get_output_path(filename, output_dir, best_result))
                    if not os.path.exists(nfo_dir):
                        os.makedirs(nfo_dir, exist_ok=True)
                    for img_type in ["cover", "poster"]:
                        url = best_result.get(img_type)
                        if url:
                            ext = os.path.splitext(url)[1] or ".jpg"
                            if img_type == "cover":
                                img_filename = f"fanart{ext}"
                            elif img_type == "poster":
                                img_filename = f"folder{ext}"
                            img_path = os.path.join(nfo_dir, img_filename)
                            try:
                                r = requests.get(url, timeout=15)
                                if r.status_code == 200:
                                    with open(img_path, "wb") as f:
                                        f.write(r.content)
                                    print(f"Downloaded {img_type} image: {img_path}")
                                else:
                                    print(f"Failed to download {img_type} image: {url}")
                            except Exception as e:
                                print(f"Error downloading {img_type} image: {e}")
                    success_count += 1
                    print(f"{Fore.GREEN}Successfully generated NFO for {filename}{Style.RESET_ALL}")
                else:
                    print(f"{Fore.RED}Failed to generate NFO for {filename}{Style.RESET_ALL}")
            else:
                print(f"{Fore.YELLOW}No metadata found for {jav_code}{Style.RESET_ALL}")
        
        return success_count
    
    def _get_best_result(self, results: dict) -> Optional[dict]:
        """
        Get the best result from multiple scrapers.
        
        Args:
            results: Dictionary of results from different scrapers
            
        Returns:
            Best metadata result or None
        """
        # Filter out None results
        valid_results = {k: v for k, v in results.items() if v is not None}
        
        if not valid_results:
            return None
        
        # For now, return the first valid result
        # In the future, this could implement more sophisticated selection logic
        return list(valid_results.values())[0]
    
    def list_scrapers(self) -> None:
        """List available scrapers."""
        scrapers = self.scraper_factory.get_available_scrapers()
        print(f"{Fore.CYAN}Available scrapers:{Style.RESET_ALL}")
        for scraper in scrapers:
            print(f"  - {scraper}")
    
    def _print_metadata(self, metadata: dict) -> None:
        """
        Print metadata in a formatted way to terminal.
        
        Args:
            metadata: Metadata dictionary to print
        """
        print(f"\n{Fore.CYAN}=== Metadata ==={Style.RESET_ALL}")
        
        # Basic info
        print(f"{Fore.GREEN}Id          :{Style.RESET_ALL} {metadata.get('jav_id', 'N/A')}")
        print(f"{Fore.GREEN}ContentId   :{Style.RESET_ALL} {metadata.get('content_id', 'N/A')}")
        print(f"{Fore.GREEN}Title       :{Style.RESET_ALL} {metadata.get('title', 'N/A')}")
        print(f"{Fore.GREEN}OriginalTitle:{Style.RESET_ALL} {metadata.get('original_title', 'N/A')}")
        print(f"{Fore.GREEN}Description :{Style.RESET_ALL} {metadata.get('plot', 'N/A')}")
        print(f"{Fore.GREEN}ReleaseYear :{Style.RESET_ALL} {metadata.get('year', 'N/A')}")
        print(f"{Fore.GREEN}ReleaseDate :{Style.RESET_ALL} {metadata.get('release_date', 'N/A')}")
        print(f"{Fore.GREEN}Runtime     :{Style.RESET_ALL} {metadata.get('runtime', 'N/A')}")
        print(f"{Fore.GREEN}Rating      :{Style.RESET_ALL} {metadata.get('rating', 'N/A')}")
        print(f"{Fore.GREEN}Votes       :{Style.RESET_ALL} {metadata.get('votes', 'N/A')}")
        
        print(f"{Fore.GREEN}Directors    :{Style.RESET_ALL} {metadata.get('directors', 'N/A')}")
        print(f"{Fore.GREEN}Studio      :{Style.RESET_ALL} {metadata.get('studio', 'N/A')}")
        print(f"{Fore.GREEN}Label       :{Style.RESET_ALL} {metadata.get('label', 'N/A')}")
        print(f"{Fore.GREEN}Series      :{Style.RESET_ALL} {metadata.get('series', 'N/A')}")
        
        print(f"{Fore.GREEN}Genres      :{Style.RESET_ALL} {metadata.get('genres', 'N/A')}")
        print(f"{Fore.GREEN}Actresses   :{Style.RESET_ALL} {metadata.get('actresses', 'N/A')}")
        
        # Images
        print(f"{Fore.GREEN}Cover       :{Style.RESET_ALL} {metadata.get('cover', 'N/A')}")
        print(f"{Fore.GREEN}Poster      :{Style.RESET_ALL} {metadata.get('poster', 'N/A')}")
        print(f"{Fore.GREEN}Fanart      :{Style.RESET_ALL} {metadata.get('fanart', 'N/A')}")
        
        print(f"{Fore.CYAN}================{Style.RESET_ALL}\n")
    
    def test_scraper(self, scraper_name: str, jav_code: str) -> None:
        """
        Test a specific scraper.
        
        Args:
            scraper_name: Name of the scraper to test
            jav_code: JAV code to test with
        """
        scraper = self.scraper_factory.create_scraper(scraper_name)
        if not scraper:
            print(f"{Fore.RED}Scraper '{scraper_name}' not found{Style.RESET_ALL}")
            return
        
        print(f"{Fore.CYAN}Testing {scraper_name} scraper with {jav_code}{Style.RESET_ALL}")
        
        result = scraper.search(jav_code)
        if result:
            print(f"{Fore.GREEN}Success! Found metadata:{Style.RESET_ALL}")
            print(f"  Title: {result.get('title', 'N/A')}")
            print(f"  Actress: {result.get('actress', 'N/A')}")
            print(f"  Runtime: {result.get('runtime', 'N/A')}")
            print(f"  Year: {result.get('year', 'N/A')}")
        else:
            print(f"{Fore.YELLOW}No metadata found{Style.RESET_ALL}")
    
    def show_cache_stats(self) -> None:
        """Show translation cache statistics."""
        stats = translation_cache.get_cache_stats()
        print(f"{Fore.CYAN}=== Translation Cache Statistics ==={Style.RESET_ALL}")
        for field_type, count in stats.items():
            print(f"{Fore.GREEN}{field_type}:{Style.RESET_ALL} {count} entries")
        print(f"{Fore.CYAN}===================================={Style.RESET_ALL}")
    
    def clear_cache(self, field_type: str = None) -> None:
        """
        Clear translation cache.
        
        Args:
            field_type: Specific field type to clear (None for all)
        """
        translation_cache.clear_cache(field_type)
        if field_type:
            print(f"{Fore.GREEN}Cleared cache for {field_type}{Style.RESET_ALL}")
        else:
            print(f"{Fore.GREEN}Cleared all translation cache{Style.RESET_ALL}")
    
    def export_cache(self, output_file: str) -> None:
        """
        Export translation cache to file.
        
        Args:
            output_file: Output file path
        """
        translation_cache.export_cache(output_file)
        print(f"{Fore.GREEN}Exported cache to {output_file}{Style.RESET_ALL}")
    
    def import_cache(self, input_file: str) -> None:
        """
        Import translation cache from file.
        
        Args:
            input_file: Input file path
        """
        translation_cache.import_cache(input_file)
        print(f"{Fore.GREEN}Imported cache from {input_file}{Style.RESET_ALL}")

# CLI Commands
@click.group()
@click.version_option(version="1.0.0")
def cli():
    """JAV NFO Generator - Scrape JAV metadata and generate .nfo files."""
    pass

@cli.command()
@click.option('--id', '-i', required=True, help='JAV ID or content ID to search for')
@click.option('--output', '-o', default='.', help='Output directory for NFO files')
@click.option('--nfo', is_flag=True, help='Generate NFO file instead of terminal output')
@click.option('--translate', '-t', is_flag=True, help='Translate metadata to English')
def search(id, output, nfo, translate):
    """Search for metadata using a specific JAV ID or content ID. Outputs to terminal by default, use --nfo to generate NFO file."""
    app = JAVNFOGenerator()
    success = app.search_manual(id, output, generate_nfo=nfo, translate=translate)
    sys.exit(0 if success else 1)

@cli.command()
@click.option('--directory', '-d', default='.', help='Directory to scan for video files')
@click.option('--output', '-o', default='.', help='Output directory for NFO files')
@click.option('--translate', '-t', is_flag=True, help='Translate metadata to English')
def auto(directory, output, translate):
    """Auto-detect video files and generate NFO files."""
    app = JAVNFOGenerator()
    success_count = app.search_auto(directory, output, translate)
    print(f"\n{Fore.GREEN}Successfully processed {success_count} files{Style.RESET_ALL}")
    sys.exit(0 if success_count > 0 else 1)

@cli.command()
@click.option('--directory', '-d', required=True, help='Directory containing video files')
@click.option('--output', '-o', default='.', help='Output directory for NFO files')
@click.option('--translate', '-t', is_flag=True, help='Translate metadata to English')
def batch(directory, output, translate):
    """Process multiple directories in batch mode."""
    app = JAVNFOGenerator()
    success_count = app.search_auto(directory, output, translate)
    print(f"\n{Fore.GREEN}Successfully processed {success_count} files{Style.RESET_ALL}")
    sys.exit(0 if success_count > 0 else 1)

@cli.command()
def list_scrapers():
    """List available scrapers."""
    app = JAVNFOGenerator()
    app.list_scrapers()

@cli.command()
@click.option('--scraper', '-s', required=True, help='Scraper name to test')
@click.option('--id', '-i', required=True, help='JAV ID to test with')
def test(scraper, id):
    """Test a specific scraper."""
    app = JAVNFOGenerator()
    app.test_scraper(scraper, id)

@cli.command()
def cache_stats():
    """Show translation cache statistics."""
    app = JAVNFOGenerator()
    app.show_cache_stats()

@cli.command()
@click.option('--field', '-f', help='Specific field type to clear (genres, actress, director, etc.)')
def clear_cache(field):
    """Clear translation cache."""
    app = JAVNFOGenerator()
    app.clear_cache(field)

@cli.command()
@click.option('--output', '-o', required=True, help='Output file path')
def export_cache(output):
    """Export translation cache to file."""
    app = JAVNFOGenerator()
    app.export_cache(output)

@cli.command()
@click.option('--input', '-i', required=True, help='Input file path')
def import_cache(input):
    """Import translation cache from file."""
    app = JAVNFOGenerator()
    app.import_cache(input)

if __name__ == '__main__':
    cli()

