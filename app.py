import streamlit as st

st.set_page_config(page_title="Pantry Pal", layout="wide", page_icon="🥘")

pg = st.navigation([
    st.Page("pages/recipe_gallery.py", title="Recipe Gallery", icon="🥘", default=True),
    st.Page("pages/ingredient_picker.py", title="Ingredient Picker", icon="🛒"),
    st.Page("pages/nutrition.py", title="Nutrition Info", icon="📊"),
])
pg.run()
