"""
Template rendering engine for personalizing emails.
Supports HTML templates and plain text templates with placeholder injection.
"""

import re
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Tuple
from src.config import Config, logger


class TemplateEngine:
    """Manages loading and rendering of email templates."""

    def __init__(self, templates_dir: Path = None):
        self.templates_dir = templates_dir or Config.TEMPLATES_DIR

    def get_template_path(self, template_name: str) -> Path:
        """Finds .html or .txt template by base name."""
        html_path = self.templates_dir / f"{template_name}.html"
        if html_path.exists():
            return html_path
        txt_path = self.templates_dir / f"{template_name}.txt"
        if txt_path.exists():
            return txt_path
        # Return html path as default for informative error message
        return html_path

    def load_template(self, template_name: str) -> Tuple[str, str]:
        """
        Loads template content from disk.
        Returns (raw_content, content_type: 'html' or 'plain')
        """
        path = self.get_template_path(template_name)
        if not path.exists():
            raise FileNotFoundError(f"Template '{template_name}' not found in {self.templates_dir}")

        with open(path, "r", encoding="utf-8") as f:
            content = f.read()

        content_type = "html" if path.suffix.lower() == ".html" else "plain"
        return content, content_type

    def render(self, template_name: str, context: Dict[str, Any]) -> Tuple[str, str, str]:
        """
        Renders an email template with context variables.
        Returns:
            (subject, rendered_content, content_type)
        """
        raw_content, content_type = self.load_template(template_name)

        # Merge standard system variables into context
        enriched_context = {
            "current_year": str(datetime.now().year),
            "sender_name": Config.SENDER_NAME,
            **context
        }

        # Safe placeholder replacement using standard regex
        # Replaces {variable_name} with context.get('variable_name', '')
        def replacer(match):
            key = match.group(1).strip()
            return str(enriched_context.get(key, f"[{key}]"))

        rendered = re.sub(r"\{([a-zA-Z0-9_]+)\}", replacer, raw_content)

        # Extract Subject line
        # If HTML has <title>...</title>, use that as subject; otherwise generate a clean default
        subject = f"Reminder: {enriched_context.get('title', 'Action Required')}"
        if content_type == "html":
            title_match = re.search(r"<title>(.*?)</title>", rendered, re.IGNORECASE | re.DOTALL)
            if title_match:
                subject = title_match.group(1).strip()

        return subject, rendered, content_type
