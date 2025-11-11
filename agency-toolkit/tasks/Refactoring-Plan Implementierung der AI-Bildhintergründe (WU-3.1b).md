## Refactoring-Plan: Implementierung der AI-Bildhintergründe (WU-3.1b)

Dieses Refactoring schließt die Lücke zwischen `orchestrator.py` und `social/generator.py`, indem es die in `IMAGE_GENERATION_DESIGN.md` geplante Logik implementiert.

### Phase 1: Erstellung der fehlenden "Werkzeuge"

Wir müssen die beiden Funktionen implementieren, die im Designdokument (Abschnitt 4.1 und 4.2) als notwendig erachtet werden, bevor der Generator sie nutzen kann.

#### 1.1. Task: `enhance_image_prompt` implementieren

Der wichtigste fehlende Teil ist die Funktion, die einen einfachen "Konzept"-String in einen optimierten Prompt für die Bild-KI umwandelt.

  * **Datei:** `agency_toolkit/providers/mistral_provider.py` (oder ein neues `core/ai/enhancers.py`)
  * **Aktion:** Erstellen Sie die Funktion `enhance_image_prompt` (oder eine ähnliche) wie in Abschnitt 4.2 des `IMAGE_GENERATION_DESIGN.md` beschrieben.
  * **Logik:**
    1.  Die Funktion sollte einen `concept: str` als Input nehmen.
    2.  Sie sollte das `PROMPT_ENHANCER_PROFILE` (System-Prompt) aus dem Design-Dokument verwenden.
    3.  Sie ruft den AI-Text-Provider (z.B. Mistral) auf.
    4.  Sie gibt den verbesserten `str` (nur den Prompt) zurück.
    5.  Fehlerbehandlung mit `AIProviderError` (oder `MistralAPIError`) aus `exceptions.py`.

#### 1.2. Task: `generate_image` zugänglich machen

Wir müssen sicherstellen, dass der Social Generator die Bildgenerierungsfunktion aufrufen kann.

  * **Datei:** `agency_toolkit/image_gen.py` (oder der entsprechende Provider aus `providers/`)
  * **Aktion:** Stellen Sie sicher, dass die Funktion `generate_image` sauber importierbar ist und die in Abschnitt 4.1 des `IMAGE_GENERATION_DESIGN.md` definierte Signatur (prompt, seed, width, height) akzeptiert.

-----

### Phase 2: Refactoring des `core/social/generator.py`

Jetzt passen wir den Generator an, um diese Werkzeuge zu nutzen.

#### 2.1. Task: Imports hinzufügen

  * **Datei:** `agency_toolkit/core/social/generator.py`
  * **Aktion:** Fügen Sie die notwendigen Imports hinzu:
    ```python
    import logging
    from pathlib import Path
    from PIL import Image as PILImage # (Bereits vorhanden)

    # NEUE IMPORTS
    from agency_toolkit.image_gen import generate_image # (Oder der korrekte Pfad)
    from agency_toolkit.providers.mistral_provider import enhance_image_prompt # (Oder der korrekte Pfad)
    from agency_toolkit.exceptions import ImageProviderError, AIProviderError
    from agency_toolkit.core.social.rendering import create_base_image, draw_text_on_image
    # ...andere ...
    ```

#### 2.2. Task: Die `generate`-Funktion anpassen (Kern-Logik)

Dies ist die Hauptänderung. Wir ersetzen die aktuelle `if/else`-Logik für den Hintergrund durch eine priorisierte Kette.

  * **Datei:** `agency_toolkit/core/social/generator.py`
  * **Aktion:** Modifizieren Sie den Logikblock "Create image" (ca. Zeile 80).

**Alte Logik (vereinfacht):**

```python
    if background_image_path:
        # Lade Bild von Pfad
        image = PILImage.open(background_image_path).convert("RGB")
        # ... resize ...
    else:
        # Erstelle Gradient
        image = create_base_image(width, height, template, resolved_color)

    draw_text_on_image(image, text, template, width, height)
```

**Neue Logik (Implementierung des Designs):**

```python
    logger = logging.getLogger(__name__) # Logger sicherstellen
    bg_image_to_load = background_image_path  # Priorität 1: Expliziter Pfad

    # Priorität 2: AI-generiertes Bild, falls kein expliziter Pfad vorhanden ist
    if not bg_image_to_load and bg_concept:
        logger.info(f"AI background concept detected: '{bg_concept}'")
        try:
            # 1. Prompt verbessern (Phase 1.1)
            enhanced_prompt = enhance_image_prompt(bg_concept)
            logger.debug(f"Enhanced AI prompt: '{enhanced_prompt}'")

            # 2. Deterministischen Seed generieren (pro DESIGN.md 6.1)
            # Wir hashen Text + Konzept für Konsistenz
            seed = hash(text + bg_concept) % (2**32)

            # 3. Bild generieren (Phase 1.2)
            img_result = generate_image(
                prompt=enhanced_prompt,
                seed=seed,
                width=width,
                height=height,
                # provider=... (kann aus Config oder Kontext kommen)
            )

            bg_image_to_load = Path(img_result["path"])
            logger.info(f"AI background generated successfully: {bg_image_to_load}")

        except (AIProviderError, ImageProviderError, ImportError) as e:
            logger.error(f"AI background generation failed for concept '{bg_concept}'. Error: {e}", exc_info=True)
            # Fallback auf Gradient, bg_image_to_load bleibt None
            bg_image_to_load = None
        except Exception as e:
            logger.error(f"Unexpected error in AI background generation: {e}", exc_info=True)
            bg_image_to_load = None # Sicherer Fallback

    # Finale Bild-Erstellung (Priorität 1 oder 2)
    if bg_image_to_load:
        try:
            image = PILImage.open(bg_image_to_load).convert("RGB")
            # Sicherstellen, dass die Größe exakt passt
            if image.size != (width, height):
                image = image.resize((width, height), PILImage.Resampling.LANCZOS)
        except Exception as e:
            logger.warning(f"Failed to load background image '{bg_image_to_load}': {e}. Using gradient fallback.")
            # Fallback auf Gradient
            image = create_base_image(width, height, template, resolved_color)
    else:
        # Priorität 3: Gradient/Solid (Fallback)
        logger.debug("Using base gradient/color background.")
        image = create_base_image(width, height, template, resolved_color)

    # Text-Rendering (unverändert)
    draw_text_on_image(image, text, template, width, height)

    # ... (Rest der Funktion: Speichern & Rückgabe) ...
```

-----

### Phase 3: Validierung

1.  **Orchestrator-Prüfung:** `core/orchestrator.py` (Zeile 244) übergibt `bg_concept` bereits korrekt aus dem Kontext. Das ist fertig.
2.  **Bestehende Tests:** Die Tests, die zuvor `bg_concept` als "unerwartetes" Argument gemeldet haben, sollten jetzt (mit Mocks für die neuen Funktionen) korrekt durchlaufen.
3.  **Neue Tests (Kritisch):**
      * Erstellen Sie einen neuen Integrationstest (`test_social_orchestration_with_ai_background`):
      * **Mocken** Sie `enhance_image_prompt` (gibt "enhanced prompt" zurück).
      * **Mocken** Sie `generate_image` (gibt `{"path": "mock/image.png"}` zurück).
      * Stellen Sie sicher, dass `create_base_image` **NICHT** aufgerufen wird.
      * Stellen Sie sicher, dass `PILImage.open` mit `"mock/image.png"` aufgerufen wird.
      * Erstellen Sie einen Testfall, bei dem `generate_image` einen `ImageProviderError` auslöst, und stellen Sie sicher, dass `create_base_image` (der Fallback) **aufgerufen** wird.

Mit diesem Plan wird die `bg_concept`-Funktionalität wie im Design-Dokument vorgesehen implementiert, die "God Function"-Problematik wird durch Einhaltung der Trennung von Verantwortlichkeiten (Rendering, AI-Enhancement, Image-Generation) weiter aufgelöst und die Architektur-Lücke wird geschlossen.
