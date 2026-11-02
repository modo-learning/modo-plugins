"""Build the ChatGPT / Codex version of the modo-ai-skills plugin from the Claude plugin.

The Claude plugin (plugins/modo-ai-skills) is the only source that is edited.
This script writes the OpenAI package to openai/plugins/modo-ai-skills and the
marketplace file partner admins import (.agents/plugins/marketplace.json).
Never edit the output by hand: change the Claude source, the patches in
openai/overlays/ or openai/manifest.json, then re-run.

What changes for ChatGPT:
- Only assess-my-ai-work, help-me-improve, export-assessment and modo-design
  ship. save-to-passport and the Modo connector come later.
- Each openai/overlays/<skill>/<file>.patch holds FIND/REPLACE blocks. Every
  FIND must appear exactly once in the source file, so a change to the Claude
  skill that touches patched text fails the build instead of drifting.
- The label line reads "by ChatGPT" in skill text and templates. The rubric,
  RECORD.md and the record schema are copied byte for byte (they are shared
  with the Claude plugin and the modo-mcp server).

Usage (from any folder):
    python3 -I scripts/build_openai_plugin.py          # write the output
    python3 -I scripts/build_openai_plugin.py --check  # fail if the output is stale
"""

import json
import pathlib
import re
import shutil
import sys
import tempfile

ROOT = pathlib.Path(__file__).resolve().parent.parent
SOURCE = ROOT / "plugins" / "modo-ai-skills"
OPENAI = ROOT / "openai"
OUT = OPENAI / "plugins" / "modo-ai-skills"
OVERLAYS = OPENAI / "overlays"
MANIFEST = OPENAI / "manifest.json"
MARKETPLACE = ROOT / ".agents" / "plugins" / "marketplace.json"
SCHEMA = pathlib.Path(__file__).resolve().parent / "schemas" / "agent-plugins-1.0.0-plugin.schema.json"
SCHEMA_URL = "https://agent-plugins.org/schemas/1.0.0/plugin.schema.json"

SKILLS = ("assess-my-ai-work", "help-me-improve", "export-assessment", "modo-design")
# Files only the OpenAI build ships, copied byte for byte from their single source.
EXTRA = {"skills/assess-my-ai-work/scripts/derive_levels.py": ROOT / "scripts" / "derive_levels.py"}
SHARED_AS_IS = re.compile(r"^(rubric-v[0-9.]+\.md|RECORD\.md|assessment-record\.schema\.json)$")
LABEL_FROM = "Self-assessment by Claude using Modo rubric"
LABEL_TO = "Self-assessment by ChatGPT using Modo rubric"
LABEL_FILES = re.compile(r"^(SKILL\.md|.*\.html)$")

BLOCK = re.compile(r"<<<<<<< FIND\n(.*?)\n=======\n(.*?)\n?>>>>>>> REPLACE", re.S)


class BuildError(Exception):
    pass


def parse_patch(text: str) -> list:
    blocks = BLOCK.findall(text)
    if not blocks:
        raise BuildError("patch has no FIND/REPLACE blocks")
    return [(find, replace) for find, replace in blocks]


def apply_patch(source: str, blocks: list, name: str) -> str:
    for find, replace in blocks:
        count = source.count(find)
        if count != 1:
            first = find.splitlines()[0][:70]
            raise BuildError(f"{name}: FIND found {count} times (must be exactly once): {first!r}")
        source = source.replace(find, replace)
    return source


def transform(rel: pathlib.PurePosixPath, data: bytes) -> bytes:
    """The OpenAI bytes for one source file of an included skill."""
    if SHARED_AS_IS.match(rel.name):
        return data
    patch = OVERLAYS / rel.parent / f"{rel.name}.patch"
    if not patch.exists() and not LABEL_FILES.match(rel.name):
        return data
    text = data.decode("utf-8")
    if patch.exists():
        text = apply_patch(text, parse_patch(patch.read_text()), str(rel))
    if LABEL_FILES.match(rel.name):
        text = text.replace(LABEL_FROM, LABEL_TO)
    return text.encode("utf-8")


def manifest() -> dict:
    claude = json.loads((SOURCE / ".claude-plugin" / "plugin.json").read_text())
    extra = json.loads(MANIFEST.read_text())
    out = {"$schema": SCHEMA_URL, "name": claude["name"], "version": claude["version"]}
    out["description"] = extra["description"]
    out["author"] = claude["author"]
    for key in ("homepage", "repository"):
        out[key] = extra[key]
    out["license"] = claude["license"]
    out["keywords"] = extra["keywords"]
    out["extensions"] = extra["extensions"]
    return out


def marketplace(plugin: dict) -> dict:
    return {
        "name": "modo-plugins",
        "interface": {"displayName": "Modo plugins"},
        "plugins": [{
            "name": plugin["name"],
            "source": {"source": "local", "path": "./openai/plugins/modo-ai-skills"},
            "policy": {"installation": "AVAILABLE", "authentication": "ON_INSTALL"},
            "category": "Productivity",
        }],
    }


def validate_manifest(data: dict) -> list:
    """The checks of the vendored agent-plugins.org 1.0.0 schema (stdlib only)."""
    schema = json.loads(SCHEMA.read_text())
    props = schema["properties"]
    problems = [f"missing {k}" for k in schema["required"] if k not in data]
    problems += [f"unknown field {k}" for k in data if k not in props]
    types = {"string": str, "object": dict, "array": list}
    for key, value in data.items():
        rule = props.get(key)
        if rule and "type" in rule and not isinstance(value, types[rule["type"]]):
            problems.append(f"{key} must be {rule['type']}")
    name = props["name"]
    if isinstance(data.get("name"), str):
        n = data["name"]
        if not (name["minLength"] <= len(n) <= name["maxLength"]) or not re.fullmatch(name["pattern"], n):
            problems.append("name does not match the schema pattern")
    author_keys = props["author"]["properties"]
    problems += [f"unknown author field {k}" for k in data.get("author", {}) if k not in author_keys]
    problems += [f"keywords must be strings" for k in data.get("keywords", []) if not isinstance(k, str)]
    problems += [f"extensions.{k} must be an object" for k, v in data.get("extensions", {}).items()
                 if not isinstance(v, dict)]
    return problems


def build(out: pathlib.Path, market: pathlib.Path) -> None:
    if out.exists():
        shutil.rmtree(out)
    for skill in SKILLS:
        for path in sorted((SOURCE / "skills" / skill).rglob("*")):
            if path.is_dir():
                continue
            rel = pathlib.PurePosixPath("skills", *path.relative_to(SOURCE / "skills").parts)
            target = out / rel
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(transform(pathlib.PurePosixPath(*rel.parts[1:]), path.read_bytes()))
    for rel, source in EXTRA.items():
        (out / rel).parent.mkdir(parents=True, exist_ok=True)
        (out / rel).write_bytes(source.read_bytes())
    for patch in OVERLAYS.rglob("*.patch"):
        rel = patch.relative_to(OVERLAYS)
        if rel.parts[0] not in SKILLS or not (SOURCE / "skills" / rel.parent / rel.stem).exists():
            raise BuildError(f"patch {rel} has no source file in an included skill")
    data = manifest()
    problems = validate_manifest(data)
    if problems:
        raise BuildError("plugin.json: " + "; ".join(problems))
    (out / "plugin.json").write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n")
    shutil.copy(SOURCE / "LICENSE", out / "LICENSE")
    market.parent.mkdir(parents=True, exist_ok=True)
    market.write_text(json.dumps(marketplace(data), indent=2) + "\n")


def tree(root: pathlib.Path) -> dict:
    return {p.relative_to(root).as_posix(): p.read_bytes() for p in root.rglob("*") if p.is_file()}


def check() -> list:
    with tempfile.TemporaryDirectory() as tmp:
        tmp = pathlib.Path(tmp)
        build(tmp / "out", tmp / "marketplace.json")
        want, have = tree(tmp / "out"), tree(OUT) if OUT.exists() else {}
        problems = [f"missing {k}" for k in sorted(set(want) - set(have))]
        problems += [f"extra {k}" for k in sorted(set(have) - set(want))]
        problems += [f"stale {k}" for k in sorted(set(want) & set(have)) if want[k] != have[k]]
        if not MARKETPLACE.exists() or MARKETPLACE.read_bytes() != (tmp / "marketplace.json").read_bytes():
            problems.append(f"stale {MARKETPLACE.relative_to(ROOT)}")
    return problems


if __name__ == "__main__":
    try:
        if "--check" in sys.argv[1:]:
            problems = check()
            for p in problems:
                print(p, file=sys.stderr)
            if problems:
                print("OpenAI build is out of date: run python3 -I scripts/build_openai_plugin.py", file=sys.stderr)
                sys.exit(1)
            print("OpenAI build is up to date")
        else:
            build(OUT, MARKETPLACE)
            print(f"wrote {OUT.relative_to(ROOT)} and {MARKETPLACE.relative_to(ROOT)}")
    except BuildError as error:
        print(f"build failed: {error}", file=sys.stderr)
        sys.exit(1)
