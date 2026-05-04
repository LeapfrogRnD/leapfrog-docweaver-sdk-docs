from pathlib import Path
from typing import Any


class EmailTemplateManager:
    """Manages email templates and rendering."""

    def __init__(self, templates_dir: Path | None = None):
        if templates_dir is None:
            self.templates_dir = Path(__file__).parent / "templates"
        else:
            self.templates_dir = Path(templates_dir)

    def _load_template(self, template_name: str) -> str:
        template_path = self.templates_dir / template_name
        if not template_path.exists():
            msg = f"Template not found: {template_path}"
            raise FileNotFoundError(msg)

        return template_path.read_text(encoding="utf-8")

    def _render_template(self, template_content: str, context: dict[str, Any]) -> str:
        rendered = template_content
        for key, value in context.items():
            placeholder = f"{{{{ {key} }}}}"
            rendered = rendered.replace(placeholder, str(value))
        return rendered

    def render(
        self,
        template_name: str,
        payload: dict[str, Any],
    ) -> str:
        context = payload.copy()
        template = self._load_template(template_name)
        return self._render_template(template, context)
