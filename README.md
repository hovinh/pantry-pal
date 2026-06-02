# Pantry Pal

A Streamlit web app for browsing recipes, finding dishes you can make from what's in your pantry, and looking up nutrition information.

## Features

| Page | Description |
|---|---|
| **Recipe Gallery** | Browse all recipes as cards with image, ingredient list, tags, and a nutrition summary. |
| **Ingredient Picker** | Select what you have on hand → see which recipes you can make (with a match % bar) → get a colour-coded shopping checklist (have / need to buy). |
| **Nutrition Info** | View calorie, protein, fiber, fat, and carb breakdown for any recipe (per serving) or any individual ingredient (per 100 g). |

## Project Structure

```
pantry-pal/
├── app.py                        # Entry point — navigation router
├── pages/
│   ├── recipe_gallery.py         # Recipe Gallery page
│   ├── ingredient_picker.py      # Ingredient Picker page
│   └── nutrition.py              # Nutrition Info page
├── utils/
│   └── data_loader.py            # Data models, loading logic, nutrition calculation
├── data/
│   ├── ingredients.yaml          # Ingredient nutrition database (source of truth)
│   └── recipes/
│       └── <recipe_folder>/
│           ├── recipe.yaml       # Recipe definition
│           └── image.png         # Watercolour dish illustration (800×600 px, optional)
├── scripts/
│   ├── export_recipes.py         # Utility: export all recipes to plain text
│   ├── recipes_export.txt        # Output of export_recipes.py
│   ├── take_screenshots.py       # Playwright script: capture app screenshots
│   ├── make_carousel.py          # Generate LinkedIn carousel slides + PDF
│   ├── carousel_screenshots/     # Screenshots captured by take_screenshots.py
│   └── carousel_output/          # Generated carousel PNGs + carousel.pdf
├── requirements.txt
└── .gitignore
```

## Local Setup

**Requirements:** Python 3.11+

```bash
# 1. Clone the repo
git clone https://github.com/hovinh/pantry-pal.git
cd pantry-pal

# 2. Create and activate a virtual environment
python -m venv .venv
.venv\Scripts\activate        # Windows
source .venv/bin/activate     # macOS / Linux

# 3. Install dependencies
pip install -r requirements.txt

# 4. Run the app
streamlit run app.py
```

The app opens at `http://localhost:8501`.

---

## Architecture & Data Model

### Data Flow

```
data/ingredients.yaml  +  data/recipes/*/recipe.yaml
              │
              ▼
      utils/data_loader.py
      ├── load_ingredients()  →  Dict[str, Ingredient]
      ├── load_recipes()      →  List[Recipe]
      ├── recipe_nutrition()  →  Nutrition (per serving)
      └── ingredient_contributions() → per-ingredient breakdown
              │
              ▼
      pages/ (all cached with @st.cache_data)
      ├── recipe_gallery.py   — search / filter / cards / nutrition preview
      ├── ingredient_picker.py — 3-step workflow (select → suggest → checklist)
      └── nutrition.py        — bar chart + radar chart + breakdown table
```

### Data Classes (utils/data_loader.py)

| Class | Fields | Key Methods |
|---|---|---|
| `Nutrition` | calories, protein_g, fiber_g, fat_g, carbs_g | `scale(qty_g)`, `__add__()`, `per_serving(n)` |
| `Ingredient` | key, display_name, group, nutrition | — |
| `RecipeIngredient` | ingredient, quantity_g, display_qty | — |
| `Recipe` | name, cuisine, servings, tags, description, ingredients, image_path | — |

### Nutrition Calculation

- All base values stored **per 100 g** in `ingredients.yaml`
- `Nutrition.scale(qty_g)` → multiply all fields by `qty_g / 100`
- Sum all scaled ingredient nutritions, then `.per_serving(servings)`
- Ingredients without `quantity_g` (e.g. "to taste") are excluded from totals
- Ingredients with `quantity_g: 0` or missing from `ingredients.yaml` contribute 0

**Daily reference values** (used for % charts in `nutrition.py`):

| Nutrient | Reference |
|---|---|
| Calories | 2000 kcal |
| Protein | 50 g |
| Fiber | 30 g |
| Fat | 65 g |
| Carbs | 300 g |

### Multi-Unit Quantity System

Recipes support alternate display units alongside `quantity_g` (which is always required for nutrition):

```yaml
- ingredient: garlic
  quantity_cloves: 2    # display unit
  quantity_g: 10        # required for nutrition calculation
```

Supported display keys: `quantity_tsp`, `quantity_cloves`, `quantity_ml`, etc.
`_parse_quantity()` in `data_loader.py` picks the first non-`quantity_g` key for human display, and falls back to grams.

### Image Handling

- `load_recipes()` searches each recipe folder for `image.jpg`, `image.jpeg`, `image.png`, `image.webp`
- First match is stored in `Recipe.image_path`
- Pages read the file as bytes and pass directly to `st.image()`
- If no image is found, a grey placeholder is shown

### Session State & Page Navigation

- `ingredient_picker.py` uses `st.session_state` keys `step`, `selected_ingredients`, `suggested_recipes`
- The "Full breakdown →" button in `recipe_gallery.py` sets `st.session_state["nutrition_recipe_key"]` before calling `st.switch_page()` to pre-select a recipe in `nutrition.py`

---

## Current Data Summary

As of the latest commit:

- **Recipes:** 13 (Vietnamese, Japanese, Italian, Asian)
- **Ingredients in database:** 60+ across 3 groups — Proteins, Vegetables, Pantry

### Recipe List

| Folder | Display Name | Cuisine |
|---|---|---|
| `broccoli_pesto` | Broccoli Pesto Pasta | Italian |
| `canned_sardine_tomato` | Canned Sardine Tomato | Asian |
| `carrot_salad` | Carrot Salad | Asian |
| `fish_cake_tomato` | Fish Cake with Tomato | Vietnamese |
| `garlic_fish_chicken` | Fried Chicken with Garlic Fish Sauce | Vietnamese |
| `japanese_curry` | Japanese Curry | Japanese |
| `mala_noodle` | Mala Noodle | Asian |
| `okra_egg` | Okra Egg Stir-fry | Asian |
| `red_bean_sweet_soup` | Red Bean Sweet Soup | Asian |
| `sardine_egg_rolls` | Rice Paper Rolls with Sardines and Boiled Eggs | Vietnamese |
| `sushi_bake` | Sushi Bake | Japanese |
| `tempeh_rice` | Tempeh Rice Bowl | Asian |
| `tofu_egg_stir_fry` | Stir-fried Vegetables in Egg Sauce with Silky Tofu | Vietnamese |

---

## Adding Content

### Add an ingredient

Open [`data/ingredients.yaml`](data/ingredients.yaml) and append a new block. All nutrition values are **per 100 g**. Source values from [USDA FoodData Central](https://fdc.nal.usda.gov/) — use the **SR Legacy** or **Foundation Foods** entry; always use raw/uncooked values.

```yaml
salmon:
  display_name: Salmon
  group: Proteins                 # Proteins | Vegetables | Pantry
  nutrition_per_100g:
    calories: 208
    protein_g: 20.0
    fiber_g: 0.0
    fat_g: 13.0
    carbs_g: 0.0
```

### Add a recipe

1. Create a new folder under `data/recipes/` using a concise lowercase underscore-separated name (e.g. `garlic_fish_chicken`).
2. Add a `recipe.yaml` file.
3. Drop in an `image.png` (800 × 600 px, 4:3 watercolour illustration style).

```yaml
name: My Dish
cuisine: Vietnamese               # free text, used for filtering
servings: 2
tags: [main course, quick]        # free text list

description: |
  1. Step one.
  2. Step two.

ingredients:
  - ingredient: chicken_breast    # must match a key in ingredients.yaml
    quantity_g: 300
  - ingredient: garlic
    quantity_cloves: 3            # display unit (optional)
    quantity_g: 15                # always required for nutrition
  - ingredient: chili_flakes      # no quantity_g → "to taste", excluded from nutrition totals
```

**Rules:**
- `quantity_g` is always in grams (convert liquids: 1 ml ≈ 1 g for water-based; use actual density for oils)
- Any ingredient key not in `ingredients.yaml` shows in the checklist but contributes 0 to nutrition
- `description` is optional but recommended

### Generate a dish image

Use this prompt with an AI image generator (e.g. DALL·E, Midjourney, Stable Diffusion):

```
You are an illustration artist.

Task: Generate a watercolour of the dish below and make it look colourful.
The dish must be contained in one or at most 2 bowls (only if ingredients
cannot fit in one). Try to centre the composition.

Dish name: <dish name>.

Constraints:
- Include all ingredients, no additions.
- Resolution: 800 × 600 px
- Format: PNG
- No captions or text.
```

---

## Deploying to Streamlit Community Cloud

1. Push the repo to GitHub (recipe images must be committed — they need to be in git to appear on the cloud).
2. Go to [share.streamlit.io](https://share.streamlit.io) and create a new app pointing to `app.py`.
3. No secrets or environment variables are required.

---

## Dependencies

**Core app:**

| Package | Purpose |
|---|---|
| `streamlit >= 1.28` | Web app framework and UI components |
| `pyyaml >= 6.0` | Parsing YAML data files |
| `pandas >= 2.0` | Building the nutrition breakdown table |
| `pillow >= 10.0` | Image decoding for recipe photos |
| `plotly >= 5.0` | Radar chart in Nutrition Info page |

**Scripts only** (not needed to run the app):

| Package | Purpose |
|---|---|
| `playwright >= 1.60` | Headless browser for app screenshots (`take_screenshots.py`) |
| `img2pdf >= 0.4` | Combine PNG slides into a PDF carousel (`make_carousel.py`) |

---

## Known Limitations

- **Nutrition totals are estimated** — values are only as accurate as what is entered in `ingredients.yaml`.
- **All nutrition must be in grams** — `quantity_ml` and similar keys are only used for display; nutrition is always calculated from `quantity_g`.
- **No user accounts or persistence** — ingredient selections on the Picker page are session-only and reset on refresh.
- **Images are not auto-generated** — each new recipe needs a manually created image dropped into its folder.
