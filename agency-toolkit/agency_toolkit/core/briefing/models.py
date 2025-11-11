"""Data models for briefing generation."""

from datetime import date

from pydantic import BaseModel, Field, field_validator


class BriefingData(BaseModel):
    """Project briefing data model.

    All briefing information stored in validated Pydantic model.
    Supports template-specific fields through extra='allow'.
    """

    # Core required fields
    client_name: str = Field(..., min_length=1)
    project_name: str = Field(..., min_length=1)
    deadline: date

    # Core optional fields
    project_type: str | None = Field(
        default=None, pattern="^(Print|Web|Social|Video|Other)?$"
    )
    budget: float | None = Field(default=None, ge=0)
    objectives: str | None = None
    target_audience: str | None = None
    deliverables: list[str] | None = None
    notes: str | None = None

    # Template-specific fields (dynamically added)
    main_objective: str | None = None
    context: str | None = None
    key_message: str | None = None
    platform: str | None = None
    format_aspect_ratio: str | None = None
    target_duration: str | None = None
    scope_pages: str | None = None
    competitors: str | None = None
    design_inspiration: str | None = None
    cms_preference: str | None = None
    hosting_provider: str | None = None
    integrations: str | None = None
    seo_needs: str | None = None
    content_status: str | None = None
    style_inspiration: str | None = None
    voiceover: str | None = None
    music: str | None = None
    graphics: str | None = None
    source_files: str | None = None
    call_to_action: str | None = None

    model_config = {
        "extra": "allow",  # Allow extra fields from templates
        "json_schema_extra": {
            "example": {
                "client_name": "Acme Corp",
                "project_name": "Website Redesign",
                "project_type": "Web",
                "deadline": "2024-12-31",
                "budget": 5000.0,
                "objectives": "Modernize digital presence",
                "target_audience": "B2B decision makers",
                "deliverables": ["Homepage", "Blog", "Contact page"],
                "notes": "Prefer modern design with dark theme",
            }
        },
    }

    @field_validator("client_name")
    @classmethod
    def validate_client_name(cls, v: str) -> str:
        """Validate client name format."""
        if not all(c.isalnum() or c.isspace() for c in v):
            raise ValueError("Client name must be alphanumeric with spaces only")
        return v
