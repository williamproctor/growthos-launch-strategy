#!/usr/bin/env python3
"""
Render Charlie character images via OpenAI gpt-image-1.

Reads OPENAI_API_KEY from .env in the script's directory.
Saves outputs to ./assets/ alongside this script.

Usage:
    ./.venv/bin/python render_charlie.py <scene-name>
    ./.venv/bin/python render_charlie.py all
    ./.venv/bin/python render_charlie.py --list

Scene catalog lives in SCENES below. Add scenes there.
"""
import base64
import sys
import os
from pathlib import Path

# Force line-buffered stdout so progress prints appear live when running in
# the background (otherwise output is block-buffered and only flushes on exit).
sys.stdout.reconfigure(line_buffering=True)

# --- Load .env from script directory (no third-party dotenv dependency) ---
SCRIPT_DIR = Path(__file__).parent
ENV_FILE = SCRIPT_DIR / ".env"
if ENV_FILE.exists():
    for raw in ENV_FILE.read_text().splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        k, v = line.split("=", 1)
        os.environ.setdefault(k.strip(), v.strip().strip('"').strip("'"))

if not os.environ.get("OPENAI_API_KEY"):
    sys.exit("error: OPENAI_API_KEY not set (expected in .env or env)")

from openai import OpenAI  # noqa: E402

ASSETS = SCRIPT_DIR / "assets"
ASSETS.mkdir(exist_ok=True)

# --- Model config ---
# gpt-image-2 (snapshot 2026-04-21): state-of-the-art OpenAI image model.
# Accepts flexible sizes (any width/height that satisfies: max edge <= 3840px,
# both edges multiples of 16, long:short ratio <= 3:1, total pixels 655,360 -
# 8,294,400). Popular: 1024x1024, 1536x1024, 1024x1536, 2048x2048.
# Quality: low / medium / high / auto (default).
# Pricing (high quality): 1024x1024 = $0.211; landscape/portrait = $0.165.
MODEL = "gpt-image-2"

# Set to "low" to relax content filtering if you hit false positives.
# Default "auto" mirrors normal OpenAI safety. The comic-book render in our
# native-tool prototype run was blocked there; gpt-image-2's default filter
# is different and usually permits this kind of editorial illustration.
MODERATION = "auto"

# --- Style anchors ---
# When we pick the final style direction, anchor every prompt to one of these.
# NOTE: do NOT name specific living artists, studios, or proprietary IP in these
# prompts. The OpenAI image moderation filter blocks references like "Studio
# Ghibli," "Pixar," "Wallace and Gromit," "Saul Bass," etc. Describe the
# AESTHETIC instead — the model is excellent at interpreting visual descriptions.
STYLE_AARDMAN = (
    "Rendered as a stop-motion clay character. Visible thumbprints in the clay surface, "
    "slightly imperfect hand-sculpted modeling, hand-built miniature diorama setting with practical "
    "lighting placed inside the set. Warm, rough, tactile quality of British stop-motion claymation — "
    "exaggerated features, charming imperfection, tangible plasticine texture."
)
STYLE_PHOTOREAL = (
    "Photographic realism, shot on a 50mm prime lens, shallow depth of field, "
    "natural office light. Mundane corporate setting, dry serious tone. "
    "Not stylized, not illustrated, no painterly effects."
)
STYLE_PIXAR = (
    "High-quality 3D animated character rendered in a modern feature-film CGI style. "
    "Stylized but appealing, soft global illumination, subsurface scattering on the fur, "
    "exaggerated proportions, large expressive eyes. Polished family-friendly animation studio aesthetic."
)
STYLE_2D = (
    "Modern 2D vector animated character. Flat colors, clean confident black linework, "
    "minimal cell shading. Modern animated TV aesthetic."
)
STYLE_COMIC = (
    "Modern graphic novel illustration. Bold black inked linework with varied line weights, "
    "halftone shading, muted earth-tone palette with a single accent color. Drawn, not photographic."
)
STYLE_FELT_PUPPET = (
    "Rendered as a tactile felt-and-fabric puppet character — a real handcrafted television puppet "
    "for children's programming. Hand-stitched fabric textures visible, button or plastic eyes, "
    "soft fabric jowls and ears with clear stitching, soft warm practical stage lighting. Built as "
    "a real tangible puppet for filming — not CG, not 3D animation. Charming handmade aesthetic."
)
STYLE_GHIBLI = (
    "Rendered as a hand-painted watercolor illustration in the style of classic Japanese feature "
    "animation from the 1980s and 1990s. Soft painterly brushwork with visible water washes, gentle "
    "color gradients, atmospheric warm lighting, earth-tone palette of muted greens, browns, and "
    "warm whites. Hand-drawn character animation aesthetic with traditional cel framing on textured "
    "paper. Soft and contemplative — not 3D, not photographic."
)
STYLE_ANIME = (
    "Rendered as a Japanese cel-shaded anime character. Bold black outlines, flat color planes with "
    "sharp shadow shapes, expressive eyes in classic anime style, detailed background line art. "
    "Slightly intense dramatic energy, like a serious shonen anime character. Graphic and bold, not painterly."
)
STYLE_PIXEL_ART = (
    "Rendered as 16-bit pixel art in the style of late 1990s 16-bit console video games. "
    "Limited 16-color palette, visible pixel grid, dithering for shading. The character is a recognizable "
    "English bulldog rendered as a pixel sprite at modest resolution. Background: a stylized pixel-art office "
    "scene with simple geometric props. Crisp, retro, deliberately low-resolution aesthetic."
)
STYLE_MIDCENTURY = (
    "Rendered as mid-century modern flat illustration in the vintage 1950s-60s editorial magazine style. "
    "Bold flat geometric shapes, limited muted color palette of cream, burnt orange, teal, and warm brown, "
    "no gradients, simplified forms. The character reduced to confident geometric shapes that still read "
    "as a bulldog. Sophisticated, designer-y, vintage editorial illustration style."
)

# --- Charlie base description (carries across every scene) ---
CHARLIE = (
    "Charlie, a senior English bulldog character with a graying muzzle, heavy jowls and folds, "
    "weary world-tired eyes, slight scowl. He often wears a small dark sweater with a tiny gold lapel pin. "
    "Personality: bored, observational, the Larry David of marketing dogs. "
    "He never looks playful, cute, or aspirational. He looks like he has been in too many meetings."
)

# --- Scenes ---
# Each scene: scene_id -> dict(size, quality, style, action)
SCENES = {
    # Smoke test — low quality, cheap (~$0.006). Validates pipeline end-to-end.
    "smoke-test": dict(size="1024x1024", quality="low", style=STYLE_PHOTOREAL,
        action="Tight portrait of his face. Looking at the camera with a tired, weary expression. "
               "Plain neutral background, soft window light."),

    # Hero portrait set (all five styles, already rendered for the comparison grid)
    "hero-photoreal": dict(size="1024x1024", quality="high", style=STYLE_PHOTOREAL,
        action="Three-quarter angle portrait. Head slightly turned toward camera, weary stare. "
               "Background: softly out-of-focus office with a closed laptop on a wood desk."),

    "hero-aardman": dict(size="1024x1024", quality="high", style=STYLE_AARDMAN,
        action="Tight portrait at his desk. Looking directly at camera. "
               "Hand-built miniature office set: small wooden desk, tiny knitted sweater, miniature props."),

    # Expanded style comparison set (gpt-image-2 renders, May 27)
    "style-06-felt-puppet": dict(size="1024x1024", quality="high", style=STYLE_FELT_PUPPET,
        action="Mid-shot of the puppet character looking directly at the camera with a weary expression. "
               "He sits behind a small puppet-stage desk with a tiny prop laptop and coffee mug. "
               "Soft warm practical stage lighting illuminates the felt textures."),

    "style-07-ghibli": dict(size="1024x1024", quality="high", style=STYLE_GHIBLI,
        action="Painterly portrait of the bulldog at a wooden desk by a window in a warm wood-paneled office. "
               "Soft natural daylight filters through the window. He looks weary and reflective, slight scowl. "
               "Painted illustration aesthetic with visible brush texture."),

    "style-08-anime": dict(size="1024x1024", quality="high", style=STYLE_ANIME,
        action="Dramatic three-quarter portrait. The character's expression is intense and weary, "
               "with sharp cel-shaded lighting from one side. An office background rendered in detailed "
               "anime line art. Bold confident outlines, flat color planes."),

    "style-09-pixel-art": dict(size="1024x1024", quality="high", style=STYLE_PIXEL_ART,
        action="Wide pixel-art scene showing the bulldog sprite in an office: a pixelated desk, a pixelated "
               "chair, a window with light streaming in. Mid-shot showing both the character and the "
               "environment. Limited 16-color palette, visible pixel grid."),

    "style-10-midcentury": dict(size="1024x1024", quality="high", style=STYLE_MIDCENTURY,
        action="Stylized flat portrait of the bulldog character seated at a desk. Simplified geometric forms "
               "for body, head, jowls. Balanced graphic composition. Vintage magazine illustration aesthetic, "
               "limited muted color palette."),

    # Visual reference set — the six foundational scenes from the character sheet.
    # Currently only hero is rendered; the rest below are ready to fire when style direction is locked.
    "desk": dict(size="1536x1024", quality="high", style=STYLE_PHOTOREAL,
        action="Wide establishing shot. Sitting in an oversized leather chair behind a desk that's slightly too tall for him. "
               "Paws resting on the desk in front of a closed silver MacBook. Coffee mug, framed photo, papers, a fountain pen. "
               "Empty office. Natural overcast daylight. He stares profoundly unimpressed at the laptop."),

    "conference-room": dict(size="1536x1024", quality="high", style=STYLE_PHOTOREAL,
        action="Asleep at the far end of a long empty conference room table. Empty chairs around the table. "
               "A whiteboard in the background covered in marketing acronyms. Fluorescent office light. "
               "Wide and still. Slightly absurd, slightly sad."),

    "reaction": dict(size="1024x1024", quality="high", style=STYLE_PHOTOREAL,
        action="Tight close-up on his face. He side-eyes the camera with a mock-shocked expression. "
               "Soft natural light, neutral background. Expression reads: 'I cannot believe what I just saw.'"),

    "commute": dict(size="1024x1536", quality="high", style=STYLE_PHOTOREAL,
        action="Standing on a sidewalk outside an unmarked office building. Tiny work badge on a thin lanyard. "
               "Light rain, morning. He looks down at the sidewalk, weary. Cinematic still, low contrast."),

    "webcam-stare": dict(size="1024x1024", quality="high", style=STYLE_PHOTOREAL,
        action="POV from a laptop webcam: he stares directly at the screen. Tiny Bluetooth earpiece visible. "
               "Office background slightly blurred. He looks tired but attentive. Implied joke: he's in a meeting."),
}


def build_prompt(scene):
    return (
        f"{CHARLIE}\n\n"
        f"SCENE: {scene['action']}\n\n"
        f"STYLE: {scene['style']}\n\n"
        f"NEGATIVE: cute, adorable, happy, playful, anthropomorphic standing on hind legs, "
        f"outdoor adventure framing, other animals or people in frame, "
        f"dialogue burned into image."
    )


def render(scene_id):
    if scene_id not in SCENES:
        sys.exit(f"unknown scene: {scene_id}\navailable: {', '.join(SCENES)}")
    scene = SCENES[scene_id]
    out = ASSETS / f"charlie-{scene_id}.png"
    print(f"→ rendering {scene_id}  ·  {MODEL}  ·  {scene['size']}  ·  q={scene['quality']}")
    client = OpenAI()
    resp = client.images.generate(
        model=MODEL,
        prompt=build_prompt(scene),
        size=scene["size"],
        quality=scene["quality"],
        moderation=MODERATION,
        n=1,
    )
    out.write_bytes(base64.b64decode(resp.data[0].b64_json))
    print(f"  ✓ saved: {out}  ({out.stat().st_size // 1024} KB)")


def main():
    if len(sys.argv) < 2 or sys.argv[1] in ("-h", "--help"):
        print(f"usage: {Path(sys.argv[0]).name} <scene-id | all | --list>")
        print(f"scenes: {', '.join(SCENES)}")
        sys.exit(0)

    args = sys.argv[1:]
    if args == ["--list"]:
        for name, s in SCENES.items():
            print(f"  {name:<28}  {s['size']:<10}  q={s['quality']}")
        return
    if args == ["all"]:
        args = list(SCENES)

    failures: list[tuple[str, str]] = []
    for scene_id in args:
        try:
            render(scene_id)
        except Exception as e:
            msg = f"{type(e).__name__}: {str(e)[:160]}"
            print(f"  ✗ failed: {scene_id}  ({msg})")
            failures.append((scene_id, msg))

    if failures:
        print()
        print(f"completed with {len(failures)} failure(s):")
        for sid, msg in failures:
            print(f"  - {sid}: {msg}")
        sys.exit(2)


if __name__ == "__main__":
    main()
