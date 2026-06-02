from pathlib import Path
import yaml

DATA_DIR = Path("data/recipes")
OUT_FILE = Path("recipes_export.txt")

lines = []

for folder in sorted(DATA_DIR.iterdir()):
    if not folder.is_dir():
        continue
    recipe_file = folder / "recipe.yaml"
    if not recipe_file.exists():
        continue

    with open(recipe_file, encoding="utf-8") as f:
        r = yaml.safe_load(f)

    lines.append(f"=== {r['name']} ===")
    lines.append(f"Folder  : {folder.name}")
    lines.append(f"Cuisine : {r.get('cuisine', '')}")
    lines.append(f"Servings: {r.get('servings', 1)}")
    lines.append(f"Tags    : {', '.join(r.get('tags', []))}")
    lines.append("")

    lines.append("Description:")
    desc = r.get("description", "").strip()
    lines.append(desc if desc else "(none)")
    lines.append("")

    lines.append("Ingredients:")
    for ing in r.get("ingredients", []):
        key = ing["ingredient"]
        qty_parts = []
        for k, v in ing.items():
            if k == "ingredient":
                continue
            unit = k[len("quantity"):].lstrip("_")
            qty_parts.append(f"{v} {unit}".strip() if unit else str(v))
        qty_str = " / ".join(qty_parts) if qty_parts else "(no quantity)"
        lines.append(f"  - {key}: {qty_str}")

    lines.append("")
    lines.append("-" * 60)
    lines.append("")

OUT_FILE.write_text("\n".join(lines), encoding="utf-8")
print(f"Written to {OUT_FILE}  ({len(lines)} lines)")
