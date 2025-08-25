"""
PDF parser for extracting text and metadata from PDF files.
"""

import logging
from typing import Dict, Any, Optional
from pathlib import Path
import tempfile
import base64

try:
    import fitz  # PyMuPDF
except ImportError:
    fitz = None

from .base import BaseParser, ParsedContent
from .factory import register_parser

logger = logging.getLogger(__name__)


@register_parser('pdf')
class PDFParser(BaseParser):
    """
    Parser for PDF files using PyMuPDF.
    
    Extracts text content, metadata, and basic document structure
    from PDF files provided as file paths or base64 encoded content.
    """
    
    def __init__(self):
        """Initialize PDF parser."""
        super().__init__()
        
        if fitz is None:
            raise ImportError(
                "PyMuPDF is required for PDF parsing. "
                "Install it with: pip install pymupdf"
            )
    
    def can_parse(self, source: Dict[str, Any]) -> bool:
        """
        Check if this parser can handle the given source.
        
        Args:
            source: Source dictionary with type and content information
            
        Returns:
            True if source type is 'pdf'
        """
        return source.get('type', '').lower() == 'pdf'
    
    async def parse(self, source: Dict[str, Any]) -> ParsedContent:
        """
        Parse PDF content and extract text and metadata.
        
        Args:
            source: Source dictionary with PDF content or file path
            
        Returns:
            ParsedContent object with extracted text and metadata
            
        Raises:
            ValueError: If PDF cannot be parsed
        """
        self.logger.info("📄 Starting PDF parsing")
        
        try:
            # Get PDF document
            doc = self._open_pdf_document(source)
            
            # Extract text content
            content_md = self._extract_text_content(doc)
            
            # Extract metadata
            metadata = self._extract_pdf_metadata(doc, source)
            
            # Extract title (from metadata or first heading)
            title = self._extract_title(doc, metadata)
            
            # Create origin information
            origin = self._create_origin_info(source)
            
            # Detect language
            language = self._detect_language(content_md)
            
            # Close document
            doc.close()
            
            # Create parsed content object
            parsed_content = ParsedContent(
                content_md=self._clean_content(content_md),
                title=title,
                metadata=metadata,
                origin=origin,
                language=language
            )
            
            self.logger.info(f"✅ PDF parsed successfully: {parsed_content.get_summary()}")
            return parsed_content
            
        except Exception as e:
            self.logger.error(f"❌ PDF parsing failed: {str(e)}")
            raise ValueError(f"Failed to parse PDF: {str(e)}")
    
    def _open_pdf_document(self, source: Dict[str, Any]) -> 'fitz.Document':
        """
        Open PDF document from source.
        
        Args:
            source: Source dictionary
            
        Returns:
            PyMuPDF Document object
        """
        if 'file_path' in source:
            # Open from file path
            file_path = Path(source['file_path'])
            if not file_path.exists():
                raise ValueError(f"PDF file not found: {file_path}")
            
            return fitz.open(str(file_path))
        
        elif 'content' in source:
            # Handle base64 encoded content
            content = source['content']
            
            if isinstance(content, str):
                # Assume base64 encoded
                try:
                    pdf_bytes = base64.b64decode(content)
                except Exception as e:
                    raise ValueError(f"Invalid base64 PDF content: {e}")
            else:
                # Assume raw bytes
                pdf_bytes = content
            
            return fitz.open(stream=pdf_bytes, filetype="pdf")
        
        else:
            raise ValueError("PDF source must have either 'file_path' or 'content'")
    
    def _extract_text_content(self, doc: 'fitz.Document') -> str:
        """
        Extract text content from PDF document.
        
        Args:
            doc: PyMuPDF Document object
            
        Returns:
            Extracted text content in markdown format
        """
        content_parts = []
        
        for page_num in range(len(doc)):
            page = doc[page_num]
            
            # Extract text
            text = page.get_text()
            
            if text.strip():
                # Add page separator for multi-page documents
                if page_num > 0:
                    content_parts.append(f"\n\n---\n**Page {page_num + 1}**\n\n")
                
                content_parts.append(text.strip())
        
        return '\n\n'.join(content_parts)
    
    def _extract_pdf_metadata(self, doc: 'fitz.Document', source: Dict[str, Any]) -> Dict[str, Any]:
        """
        Extract metadata from PDF document.
        
        Args:
            doc: PyMuPDF Document object
            source: Source dictionary
            
        Returns:
            Metadata dictionary
        """
        metadata = self._extract_metadata(source)
        
        # Get PDF metadata
        pdf_metadata = doc.metadata
        
        if pdf_metadata:
            metadata.update({
                'pdf_title': pdf_metadata.get('title', ''),
                'pdf_author': pdf_metadata.get('author', ''),
                'pdf_subject': pdf_metadata.get('subject', ''),
                'pdf_creator': pdf_metadata.get('creator', ''),
                'pdf_producer': pdf_metadata.get('producer', ''),
                'pdf_creation_date': pdf_metadata.get('creationDate', ''),
                'pdf_modification_date': pdf_metadata.get('modDate', '')
            })
        
        # Document statistics
        metadata.update({
            'page_count': len(doc),
            'is_encrypted': doc.is_encrypted,
            'is_pdf': True
        })
        
        return metadata
    
    def _extract_title(self, doc: 'fitz.Document', metadata: Dict[str, Any]) -> Optional[str]:
        """
        Extract title from PDF.
        
        Args:
            doc: PyMuPDF Document object
            metadata: Extracted metadata
            
        Returns:
            Document title or None
        """
        # Try PDF metadata title first
        pdf_title = metadata.get('pdf_title', '').strip()
        if pdf_title:
            return pdf_title
        
        # Try to find title from first page content
        if len(doc) > 0:
            first_page = doc[0]
            text = first_page.get_text()
            
            # Look for the first non-empty line as potential title
            lines = text.split('\n')
            for line in lines:
                line = line.strip()
                if line and len(line) > 5 and len(line) < 200:
                    return line
        
        return None
