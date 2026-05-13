import streamlit as st
import pandas as pd
import altair as alt
import plotly.graph_objects as go
from utils.data_loader import (
    load_ingredients,
    load_recipes,
    recipe_nutrition,
    ingredient_contributions,
)

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


def _nutrition_chart(n) -> None:
    # Metric cards row
    cols = st.columns(len(_DAILY))
    for col, (field, dv) in zip(cols, _DAILY.items()):
        label, unit = _LABELS[field]
        col.metric(label, f"{getattr(n, field):.1f} {unit}")

    # Build chart data — cap display at 150% so one huge value doesn't squash others
    rows = []
    for field, dv in _DAILY.items():
        label, unit = _LABELS[field]
        value = getattr(n, field)
        pct = value / dv * 100
        rows.append({
            "Nutrient": f"{label} ({unit})",
            "pct_display": min(pct, 150),
            "pct_actual": round(pct, 1),
            "over_limit": pct >= 100,
        })
    df = pd.DataFrame(rows)

    left_col, right_col = st.columns(2)

    # ── Left: horizontal bar chart ──────────────────────────────────────────
    with left_col:
        st.caption("Daily intake coverage")
        bars = (
            alt.Chart(df)
            .mark_bar(cornerRadiusEnd=4)
            .encode(
                x=alt.X(
                    "pct_display:Q",
                    scale=alt.Scale(domain=[0, 150]),
                    axis=alt.Axis(title="% of daily recommended intake", grid=True),
                ),
                y=alt.Y("Nutrient:N", sort=None, axis=alt.Axis(title="")),
                color=alt.condition(
                    alt.datum.over_limit,
                    alt.value("#e05c5c"),
                    alt.value("#4c9b6e"),
                ),
                tooltip=[
                    alt.Tooltip("Nutrient:N"),
                    alt.Tooltip("pct_actual:Q", title="% of daily value"),
                ],
            )
        )
        rule = (
            alt.Chart(pd.DataFrame({"x": [100]}))
            .mark_rule(color="#888", strokeDash=[6, 4], strokeWidth=1.5)
            .encode(x="x:Q")
        )
        st.altair_chart((bars + rule).properties(height=220), width="stretch")

    # ── Right: radar / spider chart ─────────────────────────────────────────
    with right_col:
        st.caption("Nutritional balance")
        labels = [row["Nutrient"] for row in rows]
        values = [row["pct_display"] for row in rows]
        actuals = [row["pct_actual"] for row in rows]

        fig = go.Figure(go.Scatterpolar(
            r=values + [values[0]],
            theta=labels + [labels[0]],
            fill="toself",
            fillcolor="rgba(76, 155, 110, 0.2)",
            line=dict(color="#4c9b6e", width=2),
            customdata=actuals + [actuals[0]],
            hovertemplate="%{theta}<br>%{customdata:.1f}% of daily value<extra></extra>",
        ))
        fig.add_trace(go.Scatterpolar(
            r=[100] * (len(labels) + 1),
            theta=labels + [labels[0]],
            mode="lines",
            line=dict(color="#888", width=1, dash="dot"),
            hoverinfo="skip",
            showlegend=False,
        ))
        fig.update_layout(
            polar=dict(
                radialaxis=dict(
                    visible=True,
                    range=[0, 150],
                    tickvals=[50, 100, 150],
                    ticktext=["50%", "100%", "150%"],
                    tickfont=dict(size=9),
                ),
                angularaxis=dict(tickfont=dict(size=10)),
            ),
            showlegend=False,
            margin=dict(l=50, r=50, t=30, b=30),
            height=300,
        )
        st.plotly_chart(fig, width="stretch")


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

    img_col, info_col = st.columns([1, 2])
    with img_col:
        if recipe.image_path and recipe.image_path.exists():
            try:
                st.image(recipe.image_path.read_bytes(), width="stretch")
            except Exception:
                pass
    with info_col:
        st.subheader(f"{recipe.name} — per serving")
        st.caption(f"{recipe.cuisine} · {recipe.servings} serving{'s' if recipe.servings > 1 else ''} total")
        if recipe.description:
            st.markdown(recipe.description)

    st.divider()
    _nutrition_chart(recipe_nutrition(recipe, ingredients))

    st.divider()
    st.markdown("#### Per-ingredient breakdown (per serving)")
    st.caption("Ingredients without a quantity are excluded from the nutrition totals.")

    rows = []
    for display_name, qty_display, n in ingredient_contributions(recipe, ingredients):
        rows.append({
            "Ingredient": display_name,
            "Quantity": qty_display,
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

    _nutrition_chart(ing.nutrition)
