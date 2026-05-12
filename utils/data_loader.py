from pathlib import Path
from dataclasses import dataclass
from typing import Optional
import yaml

DATA_DIR = Path(__file__).parent.parent / "data"
_IMAGE_EXTENSIONS = [".jpg", ".jpeg", ".png", ".webp"]


@dataclass
class Nutrition:
    calories: float = 0.0
    protein_g: float = 0.0
    fiber_g: float = 0.0
    fat_g: float = 0.0
    carbs_g: float = 0.0

    def scale(self, quantity_g: float) -> "Nutrition":
        f = quantity_g / 100.0
        return Nutrition(
            calories=self.calories * f,
            protein_g=self.protein_g * f,
            fiber_g=self.fiber_g * f,
            fat_g=self.fat_g * f,
            carbs_g=self.carbs_g * f,
        )

    def __add__(self, other: "Nutrition") -> "Nutrition":
        return Nutrition(
            calories=self.calories + other.calories,
            protein_g=self.protein_g + other.protein_g,
            fiber_g=self.fiber_g + other.fiber_g,
            fat_g=self.fat_g + other.fat_g,
            carbs_g=self.carbs_g + other.carbs_g,
        )

    def per_serving(self, servings: int) -> "Nutrition":
        return Nutrition(
            calories=self.calories / servings,
            protein_g=self.protein_g / servings,
            fiber_g=self.fiber_g / servings,
            fat_g=self.fat_g / servings,
            carbs_g=self.carbs_g / servings,
        )


@dataclass
class Ingredient:
    key: str
    display_name: str
    group: str
    nutrition: Nutrition


@dataclass
class RecipeIngredient:
    key: str
    quantity_g: Optional[float]  # None = "to taste"; excluded from nutrition calculation


@dataclass
class Recipe:
    key: str
    name: str
    cuisine: str
    servings: int
    tags: list[str]
    ingredients: list[RecipeIngredient]
    image_path: Optional[Path]
    description: str = ""


def load_ingredients() -> dict[str, Ingredient]:
    path = DATA_DIR / "ingredients.yaml"
    with open(path, encoding="utf-8") as f:
        raw = yaml.safe_load(f)

    result: dict[str, Ingredient] = {}
    for key, data in raw.items():
        n = data.get("nutrition_per_100g", {})
        result[key] = Ingredient(
            key=key,
            display_name=data.get("display_name", key.replace("_", " ").title()),
            group=data.get("group", "Other"),
            nutrition=Nutrition(
                calories=float(n.get("calories", 0)),
                protein_g=float(n.get("protein_g", 0)),
                fiber_g=float(n.get("fiber_g", 0)),
                fat_g=float(n.get("fat_g", 0)),
                carbs_g=float(n.get("carbs_g", 0)),
            ),
        )
    return result


def _find_image(folder: Path) -> Optional[Path]:
    for ext in _IMAGE_EXTENSIONS:
        p = folder / f"image{ext}"
        if p.exists():
            return p
    return None


def load_recipes() -> list[Recipe]:
    recipes_dir = DATA_DIR / "recipes"
    if not recipes_dir.exists():
        return []

    recipes: list[Recipe] = []
    for folder in sorted(recipes_dir.iterdir()):
        if not folder.is_dir():
            continue
        recipe_file = folder / "recipe.yaml"
        if not recipe_file.exists():
            continue

        with open(recipe_file, encoding="utf-8") as f:
            raw = yaml.safe_load(f)

        recipe_ingredients = [
            RecipeIngredient(
                key=ing["ingredient"],
                quantity_g=float(ing["quantity_g"]) if "quantity_g" in ing else None,
            )
            for ing in raw.get("ingredients", [])
        ]

        recipes.append(Recipe(
            key=folder.name,
            name=raw["name"],
            cuisine=raw.get("cuisine", ""),
            servings=int(raw.get("servings", 1)),
            tags=raw.get("tags", []),
            ingredients=recipe_ingredients,
            image_path=_find_image(folder),
            description=raw.get("description", ""),
        ))
    return recipes


def recipe_nutrition(recipe: Recipe, ingredients: dict[str, Ingredient]) -> Nutrition:
    total = Nutrition()
    for ri in recipe.ingredients:
        if ri.key in ingredients and ri.quantity_g is not None:
            total = total + ingredients[ri.key].nutrition.scale(ri.quantity_g)
    return total.per_serving(recipe.servings)


def ingredient_contributions(
    recipe: Recipe, ingredients: dict[str, Ingredient]
) -> list[tuple[str, Optional[float], Optional[Nutrition]]]:
    """Returns (display_name, quantity_g, nutrition_per_serving) for each recipe ingredient.

    nutrition_per_serving is None when quantity_g was not provided.
    """
    out = []
    for ri in recipe.ingredients:
        display_name = (
            ingredients[ri.key].display_name if ri.key in ingredients
            else ri.key.replace("_", " ").title()
        )
        if ri.quantity_g is None:
            out.append((display_name, None, None))
        elif ri.key in ingredients:
            n = ingredients[ri.key].nutrition.scale(ri.quantity_g).per_serving(recipe.servings)
            out.append((display_name, ri.quantity_g, n))
        else:
            out.append((display_name, ri.quantity_g, Nutrition()))
    return out
