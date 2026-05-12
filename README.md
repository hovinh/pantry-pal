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
│   └── data_loader.py            # Data models and loading logic
├── data/
│   ├── ingredients.yaml          # Ingredient nutrition database
│   └── recipes/
│       └── <recipe_folder>/
│           ├── recipe.yaml       # Recipe definition
│           └── image.jpg         # Dish photo (optional)
├── requirements.txt
└── .gitignore
```

## Local Setup

**Requirements:** Python 3.11+

```bash
# 1. Clone the repo
git clone https://github.com/<your-username>/pantry-pal.git
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

## Adding Content

### Add an ingredient

Open [`data/ingredients.yaml`](data/ingredients.yaml) and append a new block. All nutrition values are **per 100 g**.

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

For factually accurate values, look up the ingredient on [USDA FoodData Central](https://fdc.nal.usda.gov/) and use the **SR Legacy** or **Foundation Foods** entry.

### Add a recipe

1. Create a new folder under `data/recipes/` using a lowercase, underscore-separated name.
2. Add a `recipe.yaml` file (see schema below).
3. Optionally drop in an `image.jpg`, `image.png`, or `image.webp` (recommended size: 800 × 600 px, 4:3 ratio).

```yaml
# data/recipes/my_dish/recipe.yaml

name: My Dish
cuisine: Italian                  # free text, used for filtering
servings: 2
tags: [vegetarian, quick]         # free text list

description: |                    # optional — step-by-step instructions
  1. Do this first.
  2. Then do this.

ingredients:
  - ingredient: pasta             # must match a key in ingredients.yaml
    quantity_g: 200
  - ingredient: olive_oil
    quantity_g: 20
  - ingredient: chili_flakes      # omit quantity_g to mark as "to taste"
                                  # → shown in checklist, excluded from nutrition
```

> **Note:** `quantity_g` is always in grams. Liquid ingredients should also be entered in grams (assume 1 ml ≈ 1 g for water-based liquids; use the actual density for oils if precision matters).

> **Unknown ingredients** (keys not found in `ingredients.yaml`) are shown in the checklist and ingredient list but contribute 0 to the nutrition totals. Add them to `ingredients.yaml` to enable nutrition tracking.

## Deploying to Streamlit Community Cloud

1. Push the repo to GitHub (make sure recipe images are committed — they must be in git to appear on the cloud).
2. Go to [share.streamlit.io](https://share.streamlit.io) and create a new app pointing to `app.py`.
3. No secrets or environment variables are required.

## Dependencies

| Package | Purpose |
|---|---|
| `streamlit >= 1.28` | Web app framework and UI components |
| `pyyaml >= 6.0` | Parsing YAML data files |
| `pandas >= 2.0` | Building the nutrition breakdown table |
| `pillow >= 10.0` | Image decoding for recipe photos |

## Known Limitations

- **Nutrition totals are estimated** — values are only as accurate as what is entered in `ingredients.yaml`. Cross-check against [USDA FoodData Central](https://fdc.nal.usda.gov/).
- **All quantities must be in grams** — the `quantity_g` key is the only unit the loader reads. A `quantity_ml` key is silently ignored; convert to grams before entering.
- **No user accounts or persistence** — ingredient selections on the Picker page are session-only and reset on refresh.
