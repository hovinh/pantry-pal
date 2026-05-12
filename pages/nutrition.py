import streamlit as st
import pandas as pd
from utils.data_loader import (
    load_ingredients,
    load_recipes,
    recipe_nutrition,
    ingredient_contributions,
)

# Daily reference values used for the progress bars
_DAILY = {"calories": 2000, "protein_g": 50, "fiber_g": 30, "fat_g": 65, "carbs_g": 300}
_LABELS = {
    "calories": ("Calories", "kcal"),
    "protein_g": ("Protein", "g"),
    "fiber_g": ("Fiber", "g"),
    "fat_g": ("Fat", "g"),
    "carbs_g": ("Carbs", "g"),
}


@st.cache_data
def get_data():
    return load_ingredients(), load_recipes()


def _nutrition_bars(n) -> None:
    for field, dv in _DAILY.items():
        label, unit = _LABELS[field]
        value = getattr(n, field)
        pct = min(value / dv, 1.0)
        val_col, bar_col = st.columns([1, 4])
        with val_col:
            st.metric(label, f"{value:.1f} {unit}")
        with bar_col:
            st.write("")
            st.write("")
            st.progress(pct, text=f"{pct * 100:.0f}% of daily value")


ingredients, recipes = get_data()

st.title("📊 Nutrition Info")

mode = st.radio("View nutrition for", ["Recipe", "Ingredient"], horizontal=True)
st.divider()

if mode == "Recipe":
    recipe_map = {r.name: r for r in recipes}

    # Pre-select if navigated here from another page via session state
    preselect_name = None
    if "nutrition_recipe_key" in st.session_state:
        key = st.session_state.pop("nutrition_recipe_key")
        preselect_name = next((r.name for r in recipes if r.key == key), None)

    default_idx = list(recipe_map).index(preselect_name) if preselect_name in recipe_map else 0
    selected_name = st.selectbox("Select a recipe", list(recipe_map), index=default_idx)
    recipe = recipe_map[selected_name]

    st.subheader(f"{recipe.name} — per serving")
    st.caption(f"{recipe.cuisine} · {recipe.servings} serving{'s' if recipe.servings > 1 else ''} total")

    if recipe.description:
        st.markdown(recipe.description)
        st.divider()

    _nutrition_bars(recipe_nutrition(recipe, ingredients))

    st.divider()
    st.markdown("#### Per-ingredient breakdown (per serving)")
    st.caption("Ingredients without a quantity are excluded from the nutrition totals.")

    rows = []
    for display_name, qty_g, n in ingredient_contributions(recipe, ingredients):
        rows.append({
            "Ingredient": display_name,
            "Qty (g)": str(int(qty_g)) if qty_g is not None else "—",
            "Calories (kcal)": f"{n.calories:.1f}" if n is not None else "—",
            "Protein (g)": f"{n.protein_g:.1f}" if n is not None else "—",
            "Fiber (g)": f"{n.fiber_g:.1f}" if n is not None else "—",
            "Fat (g)": f"{n.fat_g:.1f}" if n is not None else "—",
            "Carbs (g)": f"{n.carbs_g:.1f}" if n is not None else "—",
        })
    st.dataframe(pd.DataFrame(rows), width="stretch", hide_index=True)

else:  # Ingredient
    ing_map = {v.display_name: v for v in ingredients.values()}
    selected_name = st.selectbox("Select an ingredient", sorted(ing_map))
    ing = ing_map[selected_name]

    st.subheader(f"{ing.display_name} — per 100g")
    st.caption(f"Group: {ing.group}")

    _nutrition_bars(ing.nutrition)
