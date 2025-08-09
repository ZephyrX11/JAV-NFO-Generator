#!/usr/bin/env python3
"""
JAV NFO Generator CLI - Command Line Interface
"""

import os
import sys
from typing import Optional
import click
from colorama import init, Fore, Style

# Initialize colorama for cross-platform colored output
init()

# Add project root to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from main import JAVNFOGenerator

# CLI Command Groups
@click.group()
@click.version_option(version="1.0.0", prog_name="JAV NFO Generator")
@click.option('--verbose', '-v', is_flag=True, help='Enable verbose output')
@click.option('--quiet', '-q', is_flag=True, help='Suppress output')
@click.pass_context
def cli(ctx, verbose, quiet):
    """JAV NFO Generator - Scrape JAV metadata and generate .nfo files."""
    ctx.ensure_object(dict)
    ctx.obj['verbose'] = verbose
    ctx.obj['quiet'] = quiet

# Search Commands
@cli.group()
def search():
    """Search for metadata using various methods."""
    pass

@search.command()
@click.option('--id', '-i', required=True, help='JAV ID or content ID to search for')
@click.option('--output', '-o', default='.', help='Output directory for files')
@click.option('--nfo', is_flag=True, help='Outputs metadata in NFO format')
@click.option('--translate', '-t', is_flag=True, help='Translate metadata to English')
@click.pass_context
def manual(ctx, id, output, nfo, translate):
    """Search for metadata using a specific JAV ID or content ID."""
    app = JAVNFOGenerator()
    success = app.search_manual(
        id, output, 
        generate_nfo=nfo, 
        translate=translate
    )
    sys.exit(0 if success else 1)

# Auto Commands
@cli.group()
def auto():
    """Auto-detect and process video files."""
    pass

@auto.command()
@click.option('--directory', '-d', default='.', help='Directory to scan for video files')
@click.option('--output', '-o', default='.', help='Output directory for files')
@click.option('--translate', '-t', is_flag=True, help='Translate metadata to English')
@click.pass_context
def scan(ctx, directory, output, translate):
    """Auto-detect video files and generate NFO files."""
    app = JAVNFOGenerator()
    success_count = app.search_auto(
        directory, output, translate
    )
    print(f"\n{Fore.GREEN}Successfully processed {success_count} files{Style.RESET_ALL}")
    sys.exit(0 if success_count > 0 else 1)

@auto.command()
@click.option('--directory', '-d', required=True, help='Directory containing video files')
@click.option('--output', '-o', default='.', help='Output directory for files')
@click.option('--translate', '-t', is_flag=True, help='Translate metadata to English')
@click.pass_context
def batch(ctx, directory, output, translate):
    """Process multiple directories in batch mode."""
    app = JAVNFOGenerator()
    success_count = app.search_auto(
        directory, output, translate
    )
    print(f"\n{Fore.GREEN}Successfully processed {success_count} files{Style.RESET_ALL}")
    sys.exit(0 if success_count > 0 else 1)

# Utility Commands
@cli.group()
def utils():
    """Utility commands for managing the application."""
    pass

@utils.command()
def scrapers():
    """List available scrapers."""
    app = JAVNFOGenerator()
    app.list_scrapers()

@utils.command()
@click.option('--scraper', '-s', required=True, help='Scraper name to test')
@click.option('--id', '-i', required=True, help='JAV ID to test with')
def test_scraper(scraper, id):
    """Test a specific scraper."""
    app = JAVNFOGenerator()
    app.test_scraper(scraper, id)

# Cache Commands
@cli.group()
def cache():
    """Manage translation cache."""
    pass

@cache.command()
def stats():
    """Show translation cache statistics."""
    app = JAVNFOGenerator()
    app.show_cache_stats()

@cache.command()
@click.option('--field', '-f', help='Specific field type to clear (genres, actress, director, etc.)')
def clear(field):
    """Clear translation cache."""
    app = JAVNFOGenerator()
    app.clear_cache(field)

@cache.command()
@click.option('--output', '-o', required=True, help='Output file path')
def export(output):
    """Export translation cache to file."""
    app = JAVNFOGenerator()
    app.export_cache(output)

@cache.command()
@click.option('--input', '-i', required=True, help='Input file path')
def import_cache(input):
    """Import translation cache from file."""
    app = JAVNFOGenerator()
    app.import_cache(input)

if __name__ == '__main__':
    cli() 