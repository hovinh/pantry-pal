import streamlit as st
from collections import defaultdict
from utils.data_loader import load_ingredients, load_recipes

_GROUP_ORDER = ["Proteins", "Vegetables", "Pantry"]


@st.cache_data
def get_data():
    return load_ingredients(), load_recipes()


ingredients, recipes = get_data()

if "selected_keys" not in st.session_state:
    st.session_state.selected_keys = set()
if "picker_step" not in st.session_state:
    st.session_state.picker_step = "select"
if "picker_recipe_key" not in st.session_state:
    st.session_state.picker_recipe_key = None

st.title("🛒 Ingredient Picker")

# ── STEP 1: select ingredients ─────────────────────────────────────────────
if st.session_state.picker_step == "select":
    st.markdown("Check everything you have on hand, then click **Find Recipes**.")

    groups: dict[str, list] = defaultdict(list)
    for ing in ingredients.values():
        groups[ing.group].append(ing)

    ordered = [g for g in _GROUP_ORDER if g in groups]
    ordered += [g for g in sorted(groups) if g not in _GROUP_ORDER]

    cols = st.columns(len(ordered))
    updated: set[str] = set()

    for col, group_name in zip(cols, ordered):
        with col:
            st.markdown(f"**{group_name}**")
            for ing in sorted(groups[group_name], key=lambda x: x.display_name):
                checked = st.checkbox(
                    ing.display_name,
                    value=ing.key in st.session_state.selected_keys,
                    key=f"cb_{ing.key}",
                )
                if checked:
                    updated.add(ing.key)

    st.session_state.selected_keys = updated

    st.divider()
    n = len(updated)
    label = f"Find Recipes — {n} ingredient{'s' if n != 1 else ''} selected →"
    if st.button(label, type="primary", disabled=n == 0):
        st.session_state.picker_step = "suggest"
        st.rerun()

# ── STEP 2: recipe suggestions ─────────────────────────────────────────────
elif st.session_state.picker_step == "suggest":
    if st.button("← Change ingredients"):
        st.session_state.picker_step = "select"
        st.rerun()

    st.markdown("### Recipes you can make")
    st.caption("Sorted by how many ingredients you already have.")

    selected = st.session_state.selected_keys
    scored = []
    for recipe in recipes:
        total = len(recipe.ingredients)
        if total == 0:
            continue
        have = sum(1 for ri in recipe.ingredients if ri.key in selected)
        scored.append((recipe, have, total))
    scored.sort(key=lambda x: x[1] / x[2], reverse=True)

    for recipe, have, total in scored:
        pct = have / total
        with st.container(border=True):
            left, right = st.columns([5, 1])
            with left:
                st.markdown(f"**{recipe.name}**  `{recipe.cuisine}`")
                st.caption(f"{have} of {total} ingredients · {pct:.0%} match")
                st.progress(pct)
            with right:
                st.write("")
                st.write("")
                if st.button("Select →", key=f"sel_{recipe.key}"):
                    st.session_state.picker_recipe_key = recipe.key
                    st.session_state.picker_step = "checklist"
                    st.rerun()

# ── STEP 3: ingredient checklist ───────────────────────────────────────────
elif st.session_state.picker_step == "checklist":
    recipe = next(
        (r for r in recipes if r.key == st.session_state.picker_recipe_key), None
    )
    if recipe is None:
        st.error("Recipe not found.")
        st.session_state.picker_step = "suggest"
        st.stop()

    selected = st.session_state.selected_keys

    back_col, nutr_col, _ = st.columns([2, 2, 4])
    with back_col:
        if st.button("← Back to suggestions"):
            st.session_state.picker_step = "suggest"
            st.rerun()
    with nutr_col:
        if st.button("📊 Full nutrition →"):
            st.session_state["nutrition_recipe_key"] = recipe.key
            st.switch_page("pages/nutrition.py")

    st.markdown(f"### {recipe.name} — Shopping Checklist")
    st.divider()

    have_items, need_items = [], []
    for ri in recipe.ingredients:
        display = (
            ingredients[ri.key].display_name if ri.key in ingredients
            else ri.key.replace("_", " ").title()
        )
        if ri.key in selected:
            have_items.append(display)
        else:
            need_items.append(display)

    have_col, need_col = st.columns(2)

    with have_col:
        st.markdown("#### ✅ You have")
        if have_items:
            for name in have_items:
                st.markdown(
                    f"<div style='padding:8px 12px;margin:4px 0;background:#d4edda;"
                    f"border-radius:6px;color:#155724;font-size:15px'>✓ {name}</div>",
                    unsafe_allow_html=True,
                )
        else:
            st.markdown("*(none)*")

    with need_col:
        st.markdown("#### 🛒 Need to buy")
        if need_items:
            for name in need_items:
                st.markdown(
                    f"<div style='padding:8px 12px;margin:4px 0;background:#fff3cd;"
                    f"border-radius:6px;color:#856404;font-size:15px'>🛒 {name}</div>",
                    unsafe_allow_html=True,
                )
        else:
            st.success("You already have everything!")
