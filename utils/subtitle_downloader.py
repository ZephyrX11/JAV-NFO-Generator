import requests
import re
import os
import time
from urllib.parse import urljoin
from typing import List, Optional, Dict
from config.settings import settings


class SubtitleDownloader:
    """Quiet, deduplicated subtitle downloader from subtitlecat.com (no counters)."""

    def __init__(self):
        self.headers = {'User-Agent': settings.USER_AGENT}
        self.base_url = "https://subtitlecat.com/"

    def _guess_lang_from_filename(self, filename: str) -> str:
        """Guess source language from filename if not detected in HTML."""
        fname = filename.lower()
        if ".en" in fname:
            return "english"
        elif ".ja" in fname:
            return "japanese"
        elif "zh-tw" in fname:
            return "chinese"
        elif ".zh" in fname or "-c.html" in fname:
            return "chinese"
        elif ".ko" in fname:
            return "korean"
        return "unknown"

    def search_subtitles(self, jav_id: str) -> List[Dict[str, str]]:
        """Find subtitle page URLs and detect source languages."""
        url = f"{self.base_url}index.php?search={jav_id}"
        try:
            r = requests.get(url, headers=self.headers, timeout=settings.REQUEST_TIMEOUT)
            if r.status_code != 200:
                return []

            pattern = rf'<td[^>]*>.*?{re.escape(jav_id)}.*?</td>'
            td_matches = re.findall(pattern, r.text, re.DOTALL | re.IGNORECASE)

            results = []
            for td in td_matches:
                hrefs = re.findall(r'href=["\']([^"\']+)["\']', td)
                translated_match = re.search(r'translated from ([a-zA-Z]+)', td, re.IGNORECASE)
                source_lang = translated_match.group(1).lower() if translated_match else None

                for href in hrefs:
                    if href.startswith('subs/'):
                        full_url = self.base_url + href
                        if not source_lang:
                            source_lang = self._guess_lang_from_filename(href)
                        results.append({"url": full_url, "source": source_lang})
            return results
        except:
            return []

    def get_download_links(self, page_url: str) -> List[Dict[str, str]]:
        """Extract direct subtitle download links from a subtitle page."""
        try:
            r = requests.get(page_url, headers=self.headers, timeout=settings.REQUEST_TIMEOUT)
            if r.status_code != 200:
                return []
            download_links = []
            patterns = {
                'en': r'download_en.*?href="([^"]+)"',
                'ja': r'download_ja.*?href="([^"]+)"',
                'zh': r'download_zh.*?href="([^"]+)"',
                'ko': r'download_ko.*?href="([^"]+)"',
            }
            for lang, pattern in patterns.items():
                for match in re.findall(pattern, r.text):
                    download_url = urljoin(page_url, match)
                    download_links.append({'url': download_url, 'language': lang})
            return download_links
        except:
            return []

    def download_subtitle(self, download_url: str, jav_id: str, language: str,
                          output_dir: str = "", video_filename: str = "",
                          metadata: dict = None, source_lang: str = "unknown") -> Optional[str]:
        """Download a single subtitle file (no counters in name)."""
        try:
            if not output_dir or output_dir == ".":
                output_dir = getattr(settings, "OUTPUT_DIR_TEMPLATE", "<ID>")
            if metadata:
                def tag_replacer(m):
                    tag = m.group(1)
                    value = metadata.get(tag.lower(), "")
                    if tag.lower() == "title" and isinstance(value, str) and len(value) > 50:
                        value = value[:50].rstrip() + "..."
                    return str(value) if value else tag
                output_dir = re.sub(r"<([A-Z_]+)>", tag_replacer, output_dir)

            output_dir = re.sub(r'[<>:"\\|?*\x00-\x1F]', '_', output_dir).strip() or "."
            os.makedirs(output_dir, exist_ok=True)

            if video_filename:
                base_name = f"{os.path.splitext(video_filename)[0]}.{language}.translated_from_{source_lang}"
            else:
                base_name = f"{jav_id}.{language}.translated_from_{source_lang}"

            subtitle_filename = f"{base_name}.{settings.SUBTITLE_FORMAT}"
            filepath = os.path.join(output_dir, subtitle_filename)

            if os.path.exists(filepath):
                return None  # don't count or redownload

            r = requests.get(download_url, headers=self.headers, timeout=settings.REQUEST_TIMEOUT)
            if r.status_code == 200:
                with open(filepath, 'wb') as f:
                    f.write(r.content)
                return filepath
            return None
        except:
            return None

    def download_subtitles_for_jav(self, jav_id: str, output_dir: str = "",
                                   video_filename: str = "", metadata: dict = None,
                                   force_enable: bool = False) -> List[str]:
        """Download all available subtitles for a JAV ID."""
        if not settings.SUBTITLE_DOWNLOAD_ENABLED and not force_enable:
            return []

        subtitle_pages = self.search_subtitles(jav_id)
        if not subtitle_pages:
            return []

        seen_urls = set()
        downloaded_files = []

        for page in subtitle_pages:
            download_links = self.get_download_links(page["url"])
            for link in download_links:
                if link['url'] in seen_urls:
                    continue
                seen_urls.add(link['url'])

                if link['language'] in settings.SUBTITLE_LANGUAGES:
                    filepath = self.download_subtitle(
                        link['url'], jav_id, link['language'], output_dir,
                        video_filename, metadata, source_lang=page["source"]
                    )
                    if filepath:
                        downloaded_files.append(filepath)

            time.sleep(settings.REQUEST_DELAY)

        # Minimal output: only files actually saved
        for f in downloaded_files:
            print(os.path.basename(f))
        return downloaded_files
