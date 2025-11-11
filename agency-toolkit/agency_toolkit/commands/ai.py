"""AI text generation command for multi-provider support."""

import json
import logging
import sys
from pathlib import Path

import httpx
import typer

from agency_toolkit.core.prompt_profiles import get_profile, list_profiles
from agency_toolkit.exceptions import AIProviderError, ValidationError
from agency_toolkit.providers import get_text_provider, list_text_providers

logger = logging.getLogger(__name__)

ai_command = typer.Typer(help="Interact with text AI providers")


def _load_profile(profile: str | None = None) -> dict:
    """Load Mistral profile configuration.

    Args:
        profile: Profile name (e.g., 'code', 'creative'). If None, returns empty dict.

    Returns:
        Dict with profile settings: {model, temperature, system_prompt}

    Raises:
        ValueError: If profile name not found in available profiles.
    """
    if not profile:
        return {}

    profile_data = get_profile(profile)
    if profile_data is None:
        available_profiles = [p.get("id", "unknown") for p in list_profiles()]
        available = ", ".join(available_profiles)
        raise ValueError(
            f"Profile '{profile}' not found. Available profiles: {available}"
        )

    # Map profile fields to expected format
    return {
        "model": profile_data.get("model"),
        "temperature": profile_data.get("temperature"),
        "system_prompt": profile_data.get("prompt"),
    }


def _load_prompt(
    prompt: str | None = None,
    prompt_file: Path | None = None,
    from_stdin: bool = False,
) -> str:
    """Load prompt from various sources with priority: stdin > file > direct.

    Args:
        prompt: Direct prompt string.
        prompt_file: Path to file containing prompt.
        from_stdin: Whether to read from stdin.

    Returns:
        Final prompt string.

    Raises:
        ValueError: If no valid prompt provided or prompt is empty.
        FileNotFoundError: If prompt_file doesn't exist.
    """
    final_prompt = ""

    if from_stdin:
        final_prompt = sys.stdin.read().strip()
        if not final_prompt:
            raise ValueError("No input received from stdin")
    elif prompt_file:
        if not prompt_file.exists():
            raise FileNotFoundError(f"Prompt file not found: {prompt_file}")
        final_prompt = prompt_file.read_text(encoding="utf-8").strip()
    elif prompt:
        final_prompt = prompt.strip()
    else:
        raise ValueError("No prompt provided. Use --prompt, --prompt-file, or --stdin")

    if not final_prompt:
        raise ValueError("Empty prompt provided")

    return final_prompt


@ai_command.callback(invoke_without_command=True)
def ai(
    ctx: typer.Context,
    prompt: str | None = typer.Option(
        None, "--prompt", "-p", help="The prompt/query to send to the AI."
    ),
    prompt_file: Path | None = typer.Option(
        None, "--prompt-file", "-f", help="Load prompt from a file."
    ),
    stdin: bool = typer.Option(False, "--stdin", help="Read prompt from stdin (pipe)."),
    profile: str | None = typer.Option(
        None,
        "--profile",
        help="Use a predefined profile (e.g., 'code', 'creative', 'debug').",
    ),
    provider: str = typer.Option(
        "mistral", "--provider", help="Text provider to use (mistral, ollama, google)."
    ),
    model: str | None = typer.Option(
        None, "--model", "-m", help="The model to use (provider-specific)."
    ),
    temperature: float = typer.Option(
        0.7, "--temperature", help="Controls randomness of output."
    ),
    max_tokens: int = typer.Option(
        1000, "--max-tokens", help="The maximum number of tokens to generate."
    ),
    json_output_legacy: bool = typer.Option(
        False, "--json-output", help="[DEPRECATED] Use global --json flag instead."
    ),
) -> None:
    """Interact with text AI models via CLI.

    Examples:
        # Direct prompt (default: Mistral)
        toolkit ai --prompt "Hello, world!"

        # Using Google GenAI
        toolkit ai --provider google --prompt "Explain quantum computing"

        # Using Ollama (free, local)
        toolkit ai --provider ollama --prompt "Analyze this code"

        # Using a profile
        toolkit ai --profile code --prompt "Review this function"

        # From file
        toolkit ai --prompt-file prompt.txt

        # From stdin
        echo "Analyze this" | toolkit ai --stdin

        # With JSON output (global flag)
        toolkit --json ai --prompt "Hello"
    """
    config = ctx.obj

    try:
        # Handle interactive mode
        if not prompt and not prompt_file and not stdin:
            prompt = typer.prompt("Enter your prompt")

        # Load prompt
        final_prompt = _load_prompt(prompt, prompt_file, stdin)

        # Load profile settings
        profile_settings = _load_profile(profile)

        # Profile settings override defaults
        if profile_settings:
            if model is None:
                model = profile_settings.get("model")
            temperature = profile_settings.get("temperature", temperature)
            system_prompt = profile_settings.get("system_prompt")
        else:
            system_prompt = None

        # Get provider
        try:
            provider_class = get_text_provider(provider)
        except ValueError as e:
            available = ", ".join(list_text_providers())
            typer.secho(f"✗ Error: {e}\nAvailable providers: {available}", fg="red")
            raise typer.Exit(1)

        # Initialize provider
        provider_instance = provider_class()

        # Validate model before API call (STAB-1.3)
        if model is not None:
            available_models = provider_instance.get_available_models()
            if model not in available_models:
                error_msg = (
                    f"✗ Error: Model '{model}' is not available for "
                    f"provider '{provider}'. "
                    f"Available models: {', '.join(available_models)}"
                )
                typer.secho(error_msg, fg="red")
                raise typer.Exit(1)

        # Generate response
        result_data = provider_instance.generate(
            prompt=final_prompt,
            model=model,
            temperature=temperature,
            max_tokens=max_tokens,
            system_prompt=system_prompt,
        )

        # Wrap with status (v3.3 pattern)
        output_data = {"status": "success", "module": "mistral", **result_data}

        # Output switch (v3.3)
        if config.json_output:
            print(json.dumps(output_data))
        else:
            # Human-readable output - just show the response text
            typer.echo(result_data["response"])

    except ValidationError as e:
        output_data = {"status": "error", "module": "mistral", "message": str(e)}
        if not config.json_output:
            typer.secho(f"✗ Validation Error: {e}", fg="red")
        else:
            print(json.dumps(output_data))
        raise typer.Exit(1)

    except FileNotFoundError as e:
        output_data = {
            "status": "error",
            "module": "mistral",
            "message": f"File not found: {e}",
        }
        if not config.json_output:
            typer.secho(f"✗ File not found: {e}", fg="red")
        else:
            print(json.dumps(output_data))
        raise typer.Exit(1)

    except AIProviderError as e:
        output_data = {
            "status": "error",
            "module": "mistral",
            "message": f"AI provider error: {e}",
        }
        if not config.json_output:
            typer.secho(f"✗ AI Provider Error: {e}", fg="red")
            typer.secho(
                "  Hint: Check your API credentials and network connection.", dim=True
            )
        else:
            print(json.dumps(output_data))
        raise typer.Exit(1)

    except httpx.HTTPError as e:
        output_data = {
            "status": "error",
            "module": "mistral",
            "message": f"Network error: {e}",
        }
        if not config.json_output:
            typer.secho(f"✗ Network Error: {e}", fg="red")
            typer.secho(
                "  Hint: Check your internet connection and try again.", dim=True
            )
        else:
            print(json.dumps(output_data))
        logger.debug(f"Full HTTP error: {e}", exc_info=True)
        raise typer.Exit(1)

    except Exception as e:
        output_data = {
            "status": "error",
            "module": "mistral",
            "message": f"Unexpected error: {e}",
        }
        if not config.json_output:
            typer.secho(f"✗ Unexpected Error: {e}", fg="red")
            typer.secho("  Hint: Run with --debug for more information.", dim=True)
        else:
            print(json.dumps(output_data))
        logger.debug("Unexpected error in ai command", exc_info=True)
        raise typer.Exit(1)
