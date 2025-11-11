"""Interactive questionnaire for briefing data collection."""

import logging

logger = logging.getLogger(__name__)


def collect_interactive(questions: dict) -> dict:
    """Collect briefing information interactively from user.

    Args:
        questions: Template with required/optional questions

    Returns:
        Dict with collected responses
    """
    print("\n=== Project Briefing Generator ===\n")

    answers = {}

    # Collect required fields
    if "required" in questions:
        print("Required Information:")
        for field in questions["required"]:
            label = field.get("label", field.get("name", "Field"))
            help_text = field.get("help", "")

            prompt = f"{label}"
            if help_text:
                prompt += f" ({help_text})"
            prompt += ": "

            value = input(prompt).strip()
            while not value:
                value = input(f"{label} (required): ").strip()

            field_name = field.get("name", label.lower().replace(" ", "_"))
            answers[field_name] = value

    # Collect optional fields
    if "optional" in questions:
        print("\nOptional Information (press Enter to skip):")
        for field in questions["optional"]:
            label = field.get("label", field.get("name", "Field"))
            help_text = field.get("help", "")

            prompt = f"{label}"
            if help_text:
                prompt += f" ({help_text})"
            prompt += ": "

            value = input(prompt).strip()

            if value:
                field_name = field.get("name", label.lower().replace(" ", "_"))

                # Handle list fields
                if field.get("type") == "list":
                    answers[field_name] = [v.strip() for v in value.split(",")]
                else:
                    answers[field_name] = value

    print("\n" + "=" * 40 + "\n")
    return answers
