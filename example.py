#!/usr/bin/env python3
"""
Example usage of JAV NFO Generator library.
"""

import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from scrapers.factory import ScraperFactory
from generators.nfo import NFOGenerator
from utils.pattern import PatternMatcher

def example_manual_search():
    """Example of manual search functionality."""
    print("=== Manual Search Example ===")
    
    # Create scraper factory
    factory = ScraperFactory()
    
    # Search for a specific JAV code
    jav_code = "sone00638"  # Example code
    print(f"Searching for JAV code: {jav_code}")
    
    # Search all scrapers
    results = factory.search_all(jav_code)
    
    # Process results
    for scraper_name, metadata in results.items():
        if metadata:
            print(f"\nFound metadata from {scraper_name}:")
            print(f"  Title: {metadata.get('title', 'N/A')}")
            print(f"  Actress: {metadata.get('actress', 'N/A')}")
            print(f"  Runtime: {metadata.get('runtime', 'N/A')}")
            print(f"  Year: {metadata.get('year', 'N/A')}")
            
            # Generate NFO file
            generator = NFOGenerator()
            success = generator.generate_nfo(metadata, f"{jav_code}.mp4", "example_output")
            
            if success:
                print(f"  ✓ Generated NFO file: example_output/{jav_code}.nfo")
            else:
                print(f"  ✗ Failed to generate NFO file")
        else:
            print(f"\nNo metadata found from {scraper_name}")

def example_auto_detection():
    """Example of auto-detection functionality."""
    print("\n=== Auto Detection Example ===")
    
    # Create test files (for demonstration)
    test_files = [
        "ABC-123.mp4",
        "DEF-456.avi", 
        "GHI-789.mkv",
        "invalid.txt"
    ]
    
    print("Simulating video files in current directory:")
    for filename in test_files:
        jav_code = PatternMatcher.extract_jav_code(filename)
        if jav_code:
            print(f"  {filename} -> JAV code: {jav_code}")
        else:
            print(f"  {filename} -> No JAV code found")
    
    # Find video files with JAV codes
    video_files = PatternMatcher.find_video_files(".")
    print(f"\nFound {len(video_files)} video files with JAV codes")
    
    for filename, jav_code in video_files:
        print(f"  {filename} ({jav_code})")

def example_scraper_test():
    """Example of testing scrapers."""
    print("\n=== Scraper Test Example ===")
    
    factory = ScraperFactory()
    
    # List available scrapers
    scrapers = factory.get_available_scrapers()
    print(f"Available scrapers: {scrapers}")
    
    # Test each scraper
    test_code = "sone00638"
    for scraper_name in scrapers:
        scraper = factory.create_scraper(scraper_name)
        if scraper:
            print(f"\nTesting {scraper_name} scraper...")
            result = scraper.search(test_code)
            
            if result:
                print(f"  ✓ Found metadata")
                print(f"    Title: {result.get('title', 'N/A')}")
            else:
                print(f"  ✗ No metadata found")

def main():
    """Run all examples."""
    print("JAV NFO Generator - Example Usage\n")
    
    try:
        example_manual_search()
        example_auto_detection()
        example_scraper_test()
        
        print("\n=== Example completed successfully! ===")
        print("\nTo use the CLI tool:")
        print("  python main.py search --code XXX-123")
        print("  python main.py auto")
        print("  python main.py list-scrapers")
        
    except Exception as e:
        print(f"\nExample failed with error: {e}")
        return False
    
    return True

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1) 