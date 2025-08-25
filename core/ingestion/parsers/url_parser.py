"""
URL parser for extracting content from web pages.
"""

import logging
from typing import Dict, Any, Optional
import asyncio
import aiohttp
from urllib.parse import urlparse, urljoin

try:
    from bs4 import BeautifulSoup
    from readability import Document
except ImportError:
    BeautifulSoup = None
    Document = None

from .base import BaseParser, ParsedContent
from .factory import register_parser

logger = logging.getLogger(__name__)


@register_parser('url')
class URLParser(BaseParser):
    """
    Parser for web URLs using BeautifulSoup and readability-lxml.
    
    Extracts main content from web pages, filtering out navigation,
    ads, and other non-content elements.
    """
    
    def __init__(self):
        """Initialize URL parser."""
        super().__init__()
        
        if BeautifulSoup is None or Document is None:
            raise ImportError(
                "BeautifulSoup4 and readability-lxml are required for URL parsing. "
                "Install them with: pip install beautifulsoup4 readability-lxml"
            )
    
    def can_parse(self, source: Dict[str, Any]) -> bool:
        """
        Check if this parser can handle the given source.
        
        Args:
            source: Source dictionary with type and URL information
            
        Returns:
            True if source type is 'url'
        """
        return source.get('type', '').lower() == 'url'
    
    async def parse(self, source: Dict[str, Any]) -> ParsedContent:
        """
        Parse URL content and extract main text.
        
        Args:
            source: Source dictionary with URL information
            
        Returns:
            ParsedContent object with extracted content
            
        Raises:
            ValueError: If URL cannot be parsed
        """
        self.logger.info(f"🌐 Starting URL parsing: {source.get('url', 'unknown')}")
        
        try:
            url = source.get('url')
            if not url:
                raise ValueError("URL source must have a 'url' field")
            
            # Fetch HTML content
            html_content = await self._fetch_html(url)
            
            # Extract main content using readability
            main_content = self._extract_main_content(html_content, url)
            
            # Parse with BeautifulSoup for additional metadata
            soup = BeautifulSoup(html_content, 'html.parser')
            
            # Extract metadata
            metadata = self._extract_web_metadata(soup, source, url)
            
            # Extract title
            title = self._extract_title(soup, main_content)
            
            # Convert to markdown
            content_md = self._html_to_markdown(main_content)
            
            # Create origin information
            origin = self._create_origin_info(source)
            origin['url'] = url
            
            # Detect language
            language = self._detect_language(content_md)
            
            # Create parsed content object
            parsed_content = ParsedContent(
                content_md=self._clean_content(content_md),
                title=title,
                metadata=metadata,
                origin=origin,
                language=language
            )
            
            self.logger.info(f"✅ URL parsed successfully: {parsed_content.get_summary()}")
            return parsed_content
            
        except Exception as e:
            self.logger.error(f"❌ URL parsing failed: {str(e)}")
            raise ValueError(f"Failed to parse URL: {str(e)}")
    
    async def _fetch_html(self, url: str) -> str:
        """
        Fetch HTML content from URL.
        
        Args:
            url: URL to fetch
            
        Returns:
            HTML content as string
        """
        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        timeout = aiohttp.ClientTimeout(total=30)
        
        async with aiohttp.ClientSession(timeout=timeout, headers=headers) as session:
            async with session.get(url) as response:
                if response.status != 200:
                    raise ValueError(f"HTTP {response.status}: Failed to fetch URL")
                
                return await response.text()
    
    def _extract_main_content(self, html_content: str, url: str) -> str:
        """
        Extract main content using readability.
        
        Args:
            html_content: Raw HTML content
            url: Original URL for context
            
        Returns:
            Cleaned main content HTML
        """
        doc = Document(html_content)
        return doc.summary()
    
    def _extract_web_metadata(self, soup: BeautifulSoup, source: Dict[str, Any], url: str) -> Dict[str, Any]:
        """
        Extract metadata from web page.
        
        Args:
            soup: BeautifulSoup object
            source: Source dictionary
            url: Page URL
            
        Returns:
            Metadata dictionary
        """
        metadata = self._extract_metadata(source)
        
        # Basic URL info
        parsed_url = urlparse(url)
        metadata.update({
            'url': url,
            'domain': parsed_url.netloc,
            'path': parsed_url.path
        })
        
        # Meta tags
        meta_description = soup.find('meta', attrs={'name': 'description'})
        if meta_description:
            metadata['description'] = meta_description.get('content', '')
        
        meta_keywords = soup.find('meta', attrs={'name': 'keywords'})
        if meta_keywords:
            metadata['keywords'] = meta_keywords.get('content', '')
        
        # Open Graph tags
        og_title = soup.find('meta', attrs={'property': 'og:title'})
        if og_title:
            metadata['og_title'] = og_title.get('content', '')
        
        og_description = soup.find('meta', attrs={'property': 'og:description'})
        if og_description:
            metadata['og_description'] = og_description.get('content', '')
        
        # Author
        author = soup.find('meta', attrs={'name': 'author'})
        if author:
            metadata['author'] = author.get('content', '')
        
        return metadata
    
    def _extract_title(self, soup: BeautifulSoup, main_content: str) -> Optional[str]:
        """
        Extract title from web page.
        
        Args:
            soup: BeautifulSoup object
            main_content: Main content HTML
            
        Returns:
            Page title or None
        """
        # Try title tag first
        title_tag = soup.find('title')
        if title_tag and title_tag.text.strip():
            return title_tag.text.strip()
        
        # Try h1 from main content
        content_soup = BeautifulSoup(main_content, 'html.parser')
        h1 = content_soup.find('h1')
        if h1 and h1.text.strip():
            return h1.text.strip()
        
        # Try Open Graph title
        og_title = soup.find('meta', attrs={'property': 'og:title'})
        if og_title:
            return og_title.get('content', '').strip()
        
        return None
    
    def _html_to_markdown(self, html_content: str) -> str:
        """
        Convert HTML content to markdown.
        
        Args:
            html_content: HTML content
            
        Returns:
            Markdown formatted content
        """
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # Remove script and style elements
        for script in soup(["script", "style"]):
            script.decompose()
        
        # Convert common HTML elements to markdown
        content_parts = []
        
        for element in soup.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'p', 'div', 'article', 'section']):
            text = element.get_text().strip()
            if not text:
                continue
            
            if element.name == 'h1':
                content_parts.append(f"# {text}")
            elif element.name == 'h2':
                content_parts.append(f"## {text}")
            elif element.name == 'h3':
                content_parts.append(f"### {text}")
            elif element.name == 'h4':
                content_parts.append(f"#### {text}")
            elif element.name == 'h5':
                content_parts.append(f"##### {text}")
            elif element.name == 'h6':
                content_parts.append(f"###### {text}")
            else:
                content_parts.append(text)
        
        # If no structured content found, just get all text
        if not content_parts:
            content_parts.append(soup.get_text())
        
        return '\n\n'.join(content_parts)
