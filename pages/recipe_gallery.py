import streamlit as st
from utils.data_loader import load_ingredients, load_recipes, recipe_nutrition


@st.cache_data
def get_data():
    return load_ingredients(), load_recipes()


ingredients, recipes = get_data()

st.title("🥘 Recipe Gallery")

search_col, cuisine_col = st.columns([3, 1])
with search_col:
    query = st.text_input("Search", placeholder="Search recipes...", label_visibility="collapsed")
with cuisine_col:
    cuisines = ["All"] + sorted({r.cuisine for r in recipes if r.cuisine})
    cuisine_filter = st.selectbox("Cuisine", cuisines, label_visibility="collapsed")

filtered = [
    r for r in recipes
    if (not query or query.lower() in r.name.lower())
    and (cuisine_filter == "All" or r.cuisine == cuisine_filter)
]

if not filtered:
    st.info("No recipes match your search.")
else:
    COLS = 3
    for i in range(0, len(filtered), COLS):
        cols = st.columns(COLS)
        for col, recipe in zip(cols, filtered[i : i + COLS]):
            with col:
                with st.container(border=True):
                    _showed_image = False
                    if recipe.image_path and recipe.image_path.exists():
                        try:
                            st.image(recipe.image_path.read_bytes(), use_container_width=True)
                            _showed_image = True
                        except Exception:
                            pass
                    if not _showed_image:
                        st.markdown(
                            "<div style='height:160px;background:#f5f5f5;display:flex;"
                            "align-items:center;justify-content:center;border-radius:8px;"
                            "color:#bbb;font-size:13px'>No image</div>",
                            unsafe_allow_html=True,
                        )

                    st.subheader(recipe.name)

                    meta_parts = []
                    if recipe.cuisine:
                        meta_parts.append(recipe.cuisine)
                    meta_parts.append(
                        f"{recipe.servings} serving{'s' if recipe.servings > 1 else ''}"
                    )
                    st.caption(" · ".join(meta_parts))

                    if recipe.tags:
                        st.markdown(" ".join(f"`{t}`" for t in recipe.tags))

                    ing_names = [
                        ingredients[ri.key].display_name if ri.key in ingredients
                        else ri.key.replace("_", " ").title()
                        for ri in recipe.ingredients
                    ]
                    st.markdown("**Ingredients:** " + ", ".join(ing_names))

                    if recipe.description:
                        with st.expander("Instructions"):
                            st.markdown(recipe.description)

                    with st.expander("Nutrition per serving"):
                        n = recipe_nutrition(recipe, ingredients)
                        c1, c2, c3 = st.columns(3)
                        c1.metric("Calories", f"{n.calories:.0f} kcal")
                        c2.metric("Protein", f"{n.protein_g:.1f} g")
                        c3.metric("Fiber", f"{n.fiber_g:.1f} g")

                        if st.button("Full breakdown →", key=f"nutr_{recipe.key}"):
                            st.session_state["nutrition_recipe_key"] = recipe.key
                            st.switch_page("pages/nutrition.py")
