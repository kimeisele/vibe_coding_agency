"""Batch processing for social posts from CSV/JSON."""

import csv
import json
import logging
from pathlib import Path

from agency_toolkit.core.social.background import generate_background
from agency_toolkit.core.social.generator import generate as generate_social_post

logger = logging.getLogger(__name__)


def process_single_post(
    config,
    text: str,
    style: str = "modern",
    color: str = "blue",
    custom_color: str | None = None,
    format_type: str = "square",
    bg_concept: str | None = None,
    bg_seed: int | None = None,
    output_path: Path | None = None,
    dry_run: bool = False,
) -> dict:
    """Process a single social post generation.

    Args:
        config: Configuration object
        text: Main text content
        style: Template style
        color: Color scheme
        custom_color: Custom hex color if color='custom'
        format_type: Image format
        bg_concept: Optional background concept
        bg_seed: Optional seed for background
        output_path: Custom output path
        dry_run: Preview mode

    Returns:
        dict with 'status', 'path', 'cost', and optional 'error' keys
    """
    background_image_path = None
    total_cost = 0.0

    try:
        output_dir = output_path or (config.output_dir / "social")

        # Handle background image generation if requested
        if bg_concept and not dry_run:
            bg_result = generate_background(
                bg_concept=bg_concept,
                bg_seed=bg_seed,
                provider=getattr(config.image, "provider", "pollinations"),
                config=config,
            )
            background_image_path = Path(bg_result["path"])
            total_cost += bg_result.get("cost", 0.0)

        # Generate social post
        result_data = generate_social_post(
            text=text,
            style=style,
            color=color,
            custom_color=custom_color,
            format_name=format_type,
            output_dir=output_dir,
            dry_run=dry_run,
            background_image_path=background_image_path,
        )

        return {
            "status": "success",
            "path": result_data["path"],
            "cost": total_cost,
        }

    except Exception as e:
        logger.error(f"Failed to generate post: {e}")
        return {
            "status": "error",
            "error": str(e),
        }


def process_batch_csv(
    config,
    csv_path: Path,
    output_dir: Path | None = None,
    dry_run: bool = False,
) -> dict:
    """Process multiple social posts from CSV file.

    CSV columns: text, style, color, format, bg_concept, bg_seed

    Args:
        config: Configuration object
        csv_path: Path to CSV file
        output_dir: Custom output directory
        dry_run: Preview mode

    Returns:
        dict with 'total', 'successful', 'failed', 'results' keys
    """
    if not csv_path.exists():
        raise FileNotFoundError(f"CSV file not found: {csv_path}")

    results = []
    total = 0
    successful = 0
    failed = 0

    with open(csv_path, encoding="utf-8") as f:
        reader = csv.DictReader(f)

        if "text" not in reader.fieldnames:
            raise ValueError("CSV file must have a 'text' column.")

        for row in reader:
            total += 1
            text = row.get("text", "").strip()

            if not text:
                logger.warning(f"Row {total}: Missing text, skipping")
                failed += 1
                results.append({"status": "error", "error": "Missing text"})
                continue

            result = process_single_post(
                config=config,
                text=text,
                style=row.get("style", "modern"),
                color=row.get("color", "blue"),
                custom_color=row.get("custom_color"),
                format_type=row.get("format", "square"),
                bg_concept=row.get("bg_concept"),
                bg_seed=int(row["bg_seed"]) if row.get("bg_seed") else None,
                output_path=output_dir,
                dry_run=dry_run,
            )

            if result["status"] == "success":
                successful += 1
            else:
                failed += 1

            results.append(result)

    if total == 0:
        raise ValueError("CSV file is empty or contains no data rows.")

    return {
        "total": total,
        "successful": successful,
        "failed": failed,
        "results": results,
    }


def process_batch_json(
    config,
    json_path: Path,
    output_dir: Path | None = None,
    dry_run: bool = False,
) -> dict:
    """Process multiple social posts from JSON file.

    JSON format: {"posts": [{"text": "...", "style": "...", ...}, ...]}

    Args:
        config: Configuration object
        json_path: Path to JSON file
        output_dir: Custom output directory
        dry_run: Preview mode

    Returns:
        dict with 'total', 'successful', 'failed', 'results' keys
    """
    if not json_path.exists():
        raise FileNotFoundError(f"JSON file not found: {json_path}")

    data = json.loads(json_path.read_text())
    posts = []
    if isinstance(data, list):
        posts = data
    elif isinstance(data, dict) and isinstance(data.get("posts"), list):
        posts = data["posts"]
    else:
        raise ValueError(
            "JSON data must be an array of posts, or an object with a 'posts' key containing an array."
        )

    results = []
    total = 0
    successful = 0
    failed = 0

    for post in posts:
        total += 1
        text = post.get("text", "").strip()

        if not text:
            logger.warning(f"Post {total}: Missing text, skipping")
            failed += 1
            results.append({"status": "error", "error": "Missing text"})
            continue

        result = process_single_post(
            config=config,
            text=text,
            style=post.get("style", "modern"),
            color=post.get("color", "blue"),
            custom_color=post.get("custom_color"),
            format_type=post.get("format", "square"),
            bg_concept=post.get("bg_concept"),
            bg_seed=post.get("bg_seed"),
            output_path=output_dir,
            dry_run=dry_run,
        )

        if result["status"] == "success":
            successful += 1
        else:
            failed += 1

        results.append(result)

    return {
        "total": total,
        "successful": successful,
        "failed": failed,
        "results": results,
    }
