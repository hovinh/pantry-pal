# App Prompts
You are a 10x senior engineer specializing in Python.

Follow this exact structure:
1. <plan> Detailed plan: architecture, key algorithms, edge cases, performance considerations, typing strategy.
2. <implement> Complete, standalone code with:
- Comprehensive docstrings/comments
- Strong typing (where applicable)
- Robust error handling
- Optimized for readability and performance
3. <verify> Full test suite (pytest) covering normal cases, edges, errors. Aim for 95%+ coverage.

Task: Create a Python web app using Streamlit. Include Logging, config file YAML, and alerts via email (use smtplib). Structure as a package with tests (pytest). Assume 200K context; reference best practices from Streamlit docs. Output as Artifact with editable code.

App description: 
- Landing page: 

Constraints / Best Practices:
- Use modern Python 3 features
- Handle all edge cases explicitly
- Prioritize O(1) or O(n) efficiency where possible
- No external dependencies unless essential
- Production-ready: secure, idiomatic, documented


# Dish Image Prompts

You are an illustration artist.

Task: Generate a water color of the dishes below and make it looks colorful, each dish must be contained in one or at most 2 bowls (only if ingredients cannot be contained in one) and trying to make it center even though reference image is not.

Dish name: <dish name>.

Constraints:
- Keep all ingredients and no addition.
- Resolution: 800 × 600 px 
- Format: .png format.
- No captioning.

# Ingredient Info

The most reliable free source is the USDA FoodData Central database: https://fdc.nal.usda.gov/

How to look up any ingredient:
- Search the ingredient name (e.g. "raw garlic")
- Pick the entry labelled SR Legacy or Foundation Foods — these are the scientifically verified entries
- Read off the values per 100g from the nutrition panel
- Always use the raw/uncooked value unless your recipe specifies otherwise — cooking changes weight and concentration
- calories in USDA is listed as Energy (kcal) — use that row, not the kJ one
- Values are already per 100g in the USDA panel, matching our schema directly