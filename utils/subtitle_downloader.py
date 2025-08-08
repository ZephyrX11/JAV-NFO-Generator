import requests
import re
import os
import time
from urllib.parse import urljoin
from typing import List, Optional, Dict
from config.settings import settings
from utils.file_utils import FileUtils


class SubtitleDownloader:
    """Download subtitles from subtitlecat.com and other sources."""
    
    def __init__(self):
        self.headers = {
            'User-Agent': settings.USER_AGENT,
        }
        self.base_url = "https://subtitlecat.com/"
    
    def search_subtitles(self, jav_id: str) -> List[str]:
        """Search for subtitle pages for a given JAV ID."""
        url = f"{self.base_url}index.php?search={jav_id}"
        
        try:
            response = requests.get(url, headers=self.headers, timeout=settings.REQUEST_TIMEOUT)
            
            if response.status_code != 200:
                print(f"Failed to get search results: {response.status_code}")
                return []
            
            # Find all td elements containing the search term
            pattern = rf'<td[^>]*>.*?{re.escape(jav_id)}.*?</td>'
            td_matches = re.findall(pattern, response.text, re.DOTALL | re.IGNORECASE)
            
            urls = []
            for td in td_matches:
                # Extract href from anchor tags within each td
                href_pattern = r'href=["\']([^"\']+)["\']'
                href_matches = re.findall(href_pattern, td)
                
                for href in href_matches:
                    if href.startswith('subs/'):
                        full_url = self.base_url + href
                        urls.append(full_url)
            
            return urls
            
        except Exception as e:
            print(f"Error searching for subtitles: {e}")
            return []
    
    def get_download_links(self, page_url: str) -> List[Dict[str, str]]:
        """Get download links from a subtitle page."""
        try:
            response = requests.get(page_url, headers=self.headers, timeout=settings.REQUEST_TIMEOUT)
            if response.status_code != 200:
                print(f"Failed to fetch page: {response.status_code}")
                return []
            
            download_links = []
            
            # Find download links for different languages
            patterns = {
                'en': r'download_en.*?href="([^"]+)"',
                'ja': r'download_ja.*?href="([^"]+)"',
                'zh': r'download_zh.*?href="([^"]+)"',
                'ko': r'download_ko.*?href="([^"]+)"',
            }
            
            for lang, pattern in patterns.items():
                matches = re.findall(pattern, response.text)
                for match in matches:
                    # Convert relative URLs to absolute
                    if match.startswith('/'):
                        download_url = "https://subtitlecat.com" + match
                    else:
                        download_url = urljoin(page_url, match)
                    
                    download_links.append({
                        'url': download_url,
                        'language': lang
                    })
            
            return download_links
            
        except Exception as e:
            print(f"Error fetching download links from {page_url}: {e}")
            return []
    
    def download_subtitle(self, download_url: str, jav_id: str, language: str, 
                         output_dir: str = "", video_filename: str = "", metadata: dict = None, counter: int = 0) -> Optional[str]:
        """Download a subtitle file."""
        try:
            # Determine output directory - use the same logic as video files
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
            
            # Create output directory if it doesn't exist
            os.makedirs(output_dir, exist_ok=True)
            
            # Generate subtitle filename based on video filename
            if video_filename:
                # Use video filename as base, add language suffix
                video_base = os.path.splitext(video_filename)[0]
                if counter > 0:
                    subtitle_filename = f"{video_base}.{language}.{counter}.{settings.SUBTITLE_FORMAT}"
                else:
                    subtitle_filename = f"{video_base}.{language}.{settings.SUBTITLE_FORMAT}"
            else:
                # Fallback to template-based naming
                filename = settings.SUBTITLE_FILENAME_TEMPLATE
                filename = filename.replace("<ID>", jav_id)
                filename = filename.replace("<LANG>", language)
                filename = filename.replace("<EXT>", settings.SUBTITLE_FORMAT)
                if counter > 0:
                    filename = filename.replace(f".{settings.SUBTITLE_FORMAT}", f".{counter}.{settings.SUBTITLE_FORMAT}")
                subtitle_filename = filename
            
            filepath = os.path.join(output_dir, subtitle_filename)
            
            # Check if file already exists
            if os.path.exists(filepath):
                print(f"⚠ Subtitle already exists: {filepath}")
                return filepath
            
            # Download the file
            response = requests.get(download_url, headers=self.headers, timeout=settings.REQUEST_TIMEOUT)
            
            if response.status_code == 200:
                with open(filepath, 'wb') as f:
                    f.write(response.content)
                print(f"✓ Downloaded subtitle: {filepath}")
                return filepath
            else:
                print(f"✗ Failed to download subtitle: {response.status_code}")
                return None
                
        except Exception as e:
            print(f"✗ Error downloading subtitle: {e}")
            return None
    
    def download_subtitles_for_jav(self, jav_id: str, output_dir: str = "", video_filename: str = "", metadata: dict = None, force_enable: bool = False) -> List[str]:
        """Download all available subtitles for a JAV ID."""
        if not settings.SUBTITLE_DOWNLOAD_ENABLED and not force_enable:
            print("Subtitle download is disabled in settings")
            return []
        
        print(f"Searching for subtitles for: {jav_id}")
        
        # Search for subtitle pages
        subtitle_urls = self.search_subtitles(jav_id)
        
        if not subtitle_urls:
            print(f"No subtitle pages found for {jav_id}")
            return []
        
        print(f"Found {len(subtitle_urls)} subtitle pages")
        
        downloaded_files = []
        language_counters = {}  # Track counters for each language
        
        # Process each subtitle page
        for i, url in enumerate(subtitle_urls, 1):
            print(f"[{i}/{len(subtitle_urls)}] Processing subtitle page:")
            
            # Get download links from this page
            download_links = self.get_download_links(url)
            
            # Download subtitles for preferred languages
            for link_info in download_links:
                language = link_info['language']
                download_url = link_info['url']
                
                # Check if this language is in our preferred list
                if language in settings.SUBTITLE_LANGUAGES:
                    # Initialize counter for this language if not exists
                    if language not in language_counters:
                        language_counters[language] = 0
                    else:
                        language_counters[language] += 1
                    
                    filepath = self.download_subtitle(download_url, jav_id, language, output_dir, video_filename, metadata, language_counters[language])
                    if filepath:
                        downloaded_files.append(filepath)
            
            # Be nice to the server
            time.sleep(settings.REQUEST_DELAY)
        
        print(f"Download complete! Downloaded {len(downloaded_files)} subtitle files")
        return downloaded_files 