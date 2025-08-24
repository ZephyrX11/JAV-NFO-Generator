import requests
import re
import os
import time
from urllib.parse import urljoin
from typing import List, Optional, Dict
from config.settings import settings
from concurrent.futures import ThreadPoolExecutor, as_completed


class SubtitleDownloader:
    """Ultra-fast, parallel subtitle downloader from subtitlecat.com."""

    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({'User-Agent': settings.USER_AGENT})
        self.base_url = "https://subtitlecat.com/"

    def _guess_lang_from_filename(self, filename: str) -> str:
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
        url = f"{self.base_url}index.php?search={jav_id}"
        try:
            r = self.session.get(url, timeout=settings.REQUEST_TIMEOUT)
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
        try:
            r = self.session.get(page_url, timeout=settings.REQUEST_TIMEOUT)
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
                return None  # already downloaded

            r = self.session.get(download_url, timeout=settings.REQUEST_TIMEOUT)
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
        if not settings.SUBTITLE_DOWNLOAD_ENABLED and not force_enable:
            return []

        subtitle_pages = self.search_subtitles(jav_id)
        if not subtitle_pages:
            return []

        seen_urls = set()
        downloaded_files = []

        with ThreadPoolExecutor(max_workers=4) as executor:  # crank up threads
            futures = []
            for page in subtitle_pages:
                download_links = self.get_download_links(page["url"])
                for link in download_links:
                    if link['url'] in seen_urls:
                        continue
                    seen_urls.add(link['url'])

                    if link['language'] in settings.SUBTITLE_LANGUAGES:
                        futures.append(
                            executor.submit(
                                self.download_subtitle, link['url'], jav_id,
                                link['language'], output_dir, video_filename,
                                metadata, page["source"]
                            )
                        )

            for future in as_completed(futures):
                filepath = future.result()
                if filepath:
                    downloaded_files.append(filepath)

        # Minimal output: only files actually saved
        for f in downloaded_files:
            print(os.path.basename(f))
        return downloaded_files
