from typing import Dict, Any, Optional, List
from enum import Enum
from pathlib import Path
import json
import logging
from datetime import datetime
from .types import Document, DocumentFormat, DocumentTemplate, DocumentSection

logger = logging.getLogger(__name__)

from importlib import import_module

class FormatOptions:
    """Available format customization options"""
    HTML_STYLES = ["default", "minimal", "professional", "modern"]
    MARKDOWN_EXTENSIONS = ["basic", "extended", "github", "academic"]
    PDF_TEMPLATES = ["basic", "report", "presentation", "documentation"]
    EXCEL_LAYOUTS = ["simple", "detailed", "dashboard"]

class FormatHandler:
    """
    Handles conversion of documents to different output formats
    """
    
    def __init__(self, templates_dir: Optional[Path] = None):
        self.templates_dir = templates_dir or Path("templates")
        self.templates_dir.mkdir(parents=True, exist_ok=True)
        
        # Format-specific settings
        self.format_settings = {
            DocumentFormat.HTML: {
                "css_framework": "tailwind",
                "template": "default_html.j2",
                "scripts": []
            },
            DocumentFormat.MARKDOWN: {
                "template": "default_md.j2",
                "extensions": ["tables", "fenced_code"]
            },
            DocumentFormat.PDF: {
                "template": "default_pdf.j2",
                "font_size": 11,
                "margin": 2.54  # cm
            },
            DocumentFormat.EXCEL: {
                "template": "default_excel.j2",
                "sheet_name": "Documentation"
            }
        }

    def format_document(
        self,
        document: Document,
        output_format: DocumentFormat,
        style_config: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Formats a document according to the specified output format
        
        Args:
            document: Document to format
            output_format: Desired output format
            style_config: Optional custom style configuration
            
        Returns:
            Formatted document content as string
        """
        try:
            # Merge default settings with custom config
            settings = self.format_settings[output_format].copy()
            if style_config:
                settings.update(style_config)

            # Format content based on type
            if output_format == DocumentFormat.HTML:
                return self._format_html(document, settings)
            elif output_format == DocumentFormat.MARKDOWN:
                return self._format_markdown(document, settings)
            elif output_format == DocumentFormat.PDF:
                return self._format_pdf(document, settings)
            elif output_format == DocumentFormat.EXCEL:
                return self._format_excel(document, settings)
            else:
                raise ValueError(f"Unsupported format: {output_format}")

        except Exception as e:
            logger.error(f"Error formatting document: {str(e)}")
            raise

    def _format_html(self, document: Document, settings: Dict[str, Any]) -> str:
        """Formats document as HTML with customizable styling"""
        try:
            # Build HTML structure
            html = [
                "<!DOCTYPE html>",
                "<html>",
                "<head>",
                f"<title>{document.title}</title>",
                self._get_html_styles(settings),
                "</head>",
                "<body>",
                f'<div class="container mx-auto px-4 py-8">',
                f'<h1 class="text-4xl font-bold mb-8">{document.title}</h1>'
            ]

            # Add sections
            for section in sorted(document.sections, key=lambda s: s.order):
                html.extend([
                    f'<section class="mb-8">',
                    f'<h2 class="text-2xl font-semibold mb-4">{section.title}</h2>',
                    f'<div class="prose max-w-none">{section.content}</div>',
                    '</section>'
                ])

            # Close HTML structure
            html.extend([
                "</div>",
                self._get_html_scripts(settings),
                "</body>",
                "</html>"
            ])

            return "\n".join(html)

        except Exception as e:
            logger.error(f"Error formatting HTML: {str(e)}")
            raise

    def _format_markdown(self, document: Document, settings: Dict[str, Any]) -> str:
        """Formats document as Markdown with extensions"""
        try:
            md = [f"# {document.title}\n"]
            
            # Add metadata section if present
            if document.metadata:
                md.extend([
                    "---",
                    "metadata:",
                    self._format_metadata_yaml(document.metadata),
                    "---\n"
                ])

            # Add sections
            for section in sorted(document.sections, key=lambda s: s.order):
                md.extend([
                    f"## {section.title}\n",
                    section.content,
                    "\n"
                ])

            return "\n".join(md)

        except Exception as e:
            logger.error(f"Error formatting Markdown: {str(e)}")
            raise

    def _format_pdf(self, document: Document, settings: Dict[str, Any]) -> str:
        """
        Formats document for PDF generation
        Note: Actual PDF generation would require additional libraries
        """
        try:
            # Create LaTeX-style content that can be converted to PDF
            content = [
                r"\documentclass{article}",
                r"\usepackage[utf8]{inputenc}",
                r"\usepackage{geometry}",
                f"\\geometry{{margin={settings['margin']}cm}}",
                f"\\title{{{document.title}}}",
                r"\begin{document}",
                f"\\fontsize{{{settings['font_size']}}}{{16}}\\selectfont",
                f"\\maketitle"
            ]

            # Add sections
            for section in sorted(document.sections, key=lambda s: s.order):
                content.extend([
                    f"\\section{{{section.title}}}",
                    section.content
                ])

            content.append(r"\end{document}")
            return "\n".join(content)

        except Exception as e:
            logger.error(f"Error formatting PDF: {str(e)}")
            raise

    def _format_excel(self, document: Document, settings: Dict[str, Any]) -> str:
        """
        Formats document for Excel export
        Returns JSON structure that can be converted to Excel
        """
        try:
            excel_data = {
                "metadata": {
                    "title": document.title,
                    "created_at": datetime.utcnow().isoformat(),
                    "sheet_name": settings["sheet_name"]
                },
                "sections": []
            }

            # Format sections as rows
            for section in sorted(document.sections, key=lambda s: s.order):
                excel_data["sections"].append({
                    "title": section.title,
                    "content": section.content,
                    "order": section.order
                })

            return json.dumps(excel_data, indent=2)

        except Exception as e:
            logger.error(f"Error formatting Excel: {str(e)}")
            raise

    def _get_html_styles(self, settings: Dict[str, Any]) -> str:
        """Gets HTML style configuration"""
        if settings["css_framework"] == "tailwind":
            return '''
            <link href="https://cdn.jsdelivr.net/npm/tailwindcss@2.2.19/dist/tailwind.min.css" rel="stylesheet">
            <link href="https://cdn.jsdelivr.net/npm/@tailwindcss/typography@0.4.1/dist/typography.min.css" rel="stylesheet">
            '''
        return ""

    def _get_html_scripts(self, settings: Dict[str, Any]) -> str:
        """Gets HTML script configuration"""
        scripts = []
        for script in settings.get("scripts", []):
            if script.startswith("https://cdnjs.cloudflare.com"):
                scripts.append(f'<script src="{script}"></script>')
        return "\n".join(scripts)

    def _format_metadata_yaml(self, metadata: Dict[str, Any]) -> str:
        """Formats metadata as YAML-style text"""
        yaml_lines = []
        for key, value in metadata.items():
            if isinstance(value, dict):
                yaml_lines.append(f"  {key}:")
                for k, v in value.items():
                    yaml_lines.append(f"    {k}: {v}")
            else:
                yaml_lines.append(f"  {key}: {value}")
        return "\n".join(yaml_lines)

    def save_formatted(
        self,
        content: str,
        output_format: DocumentFormat,
        output_dir: Path,
        filename: str
    ) -> Path:
        """
        Saves formatted content to a file
        
        Args:
            content: Formatted content to save
            output_format: Format of the content
            output_dir: Directory to save to
            filename: Base filename without extension
            
        Returns:
            Path to saved file
        """
        try:
            output_dir.mkdir(parents=True, exist_ok=True)
            
            # Add appropriate extension
            extensions = {
                DocumentFormat.HTML: ".html",
                DocumentFormat.MARKDOWN: ".md",
                DocumentFormat.PDF: ".pdf",
                DocumentFormat.EXCEL: ".xlsx"
            }
            
            extension = extensions.get(output_format, ".txt")
            output_path = output_dir / f"{filename}{extension}"
            
            # Save content
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(content)
                
            return output_path

        except Exception as e:
            logger.error(f"Error saving formatted content: {str(e)}")
            raise