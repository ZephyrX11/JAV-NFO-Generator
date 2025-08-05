# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2024-12-19

### Added
- Initial release of JAV NFO Generator
- CLI tool for scraping JAV metadata from Fanza
- Manual search functionality with `--id` parameter
- Auto-detection of video files in directories
- Batch processing capabilities
- NFO file generation with proper XML formatting
- Translation support (Google Translate, DeepL)
- Smart translation caching system
- Individual genre and actress caching for maximum efficiency
- Genre filtering to skip unwanted genres
- Support for both JAV ID and Content ID formats
- Global installation support via pipx
- Cache management commands (stats, clear, export, import)
- Comprehensive error handling and logging
- Cross-platform support (Linux, macOS, Windows)

### Features
- **Metadata Scraping**: Fanza GraphQL API integration
- **Translation**: Multi-service support with caching
- **NFO Generation**: Kodi-compatible XML format
- **Cache System**: Persistent translation cache
- **CLI Interface**: Intuitive command-line interface
- **Configuration**: Environment-based settings

### Technical
- Modular architecture with separate scrapers, generators, and utilities
- Comprehensive test coverage
- Proper package structure for distribution
- Documentation and examples 