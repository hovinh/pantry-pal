"""
Take screenshots of the 3 main Pantry Pal pages for use in carousel/docs.

Usage:
    streamlit run app.py --server.port 8502 &
    python scripts/take_screenshots.py [--port 8502] [--out scripts/carousel_screenshots]

Outputs (PNG, 1440x900):
    1_recipe_gallery.png   - Recipe Gallery full grid
    2_nutrition.png        - Nutrition Info page scrolled to metric cards + bar chart
    3_ingredient_picker.png - Ingredient Picker step 3: have/need checklist
"""

import asyncio
import argparse
import os
from playwright.async_api import async_playwright


async def take_screenshots(base_url: str, out_dir: str) -> None:
    os.makedirs(out_dir, exist_ok=True)

    async with async_playwright() as p:
        browser = await p.chromium.launch()

        # 1. Recipe Gallery
        page = await browser.new_page(viewport={"width": 1440, "height": 900})
        await page.goto(base_url, wait_until="networkidle")
        await page.wait_for_timeout(3000)
        path = os.path.join(out_dir, "1_recipe_gallery.png")
        await page.screenshot(path=path)
        print(f"Saved: {path}")
        await page.close()

        # 2. Nutrition Info — use tall viewport to capture charts, then crop
        page2 = await browser.new_page(viewport={"width": 1440, "height": 2400})
        await page2.goto(f"{base_url}/nutrition", wait_until="networkidle")
        await page2.wait_for_timeout(2000)
        await page2.locator("div[data-baseweb='select']").first.click()
        await page2.wait_for_timeout(500)
        await page2.keyboard.press("Enter")
        await page2.wait_for_timeout(4000)
        tmp2 = os.path.join(out_dir, "_nutrition_tall.png")
        await page2.screenshot(path=tmp2)
        await page2.close()
        from PIL import Image as _Image
        img2 = _Image.open(tmp2)
        cropped2 = img2.crop((0, 850, img2.width, 1750))
        path2 = os.path.join(out_dir, "2_nutrition.png")
        cropped2.save(path2)
        os.remove(tmp2)
        print(f"Saved: {path2}")

        # 3. Ingredient Picker — navigate to step 3 checklist
        page3 = await browser.new_page(viewport={"width": 1440, "height": 900})
        await page3.goto(f"{base_url}/ingredient_picker", wait_until="networkidle")
        await page3.wait_for_timeout(3000)
        # Check first 15 ingredients (proteins + some vegetables)
        checkboxes = page3.locator("[data-testid='stCheckbox']")
        for i in range(15):
            try:
                await checkboxes.nth(i).click()
                await page3.wait_for_timeout(80)
            except Exception:
                pass
        await page3.wait_for_timeout(800)
        # Step 1 → Step 2
        await page3.locator("[data-testid='stBaseButton-primary']").click()
        await page3.wait_for_timeout(2500)
        # Step 2 → Step 3: click "Select →" on first recipe
        select_btns = page3.get_by_role("button", name="Select →")
        if await select_btns.count() > 0:
            await select_btns.first.click()
            await page3.wait_for_timeout(2000)
        path3 = os.path.join(out_dir, "3_ingredient_picker.png")
        await page3.screenshot(path=path3)
        print(f"Saved: {path3}")
        await page3.close()

        await browser.close()
    print("Done.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--port", type=int, default=8502)
    parser.add_argument("--out", default="scripts/carousel_screenshots")
    args = parser.parse_args()
    asyncio.run(take_screenshots(f"http://localhost:{args.port}", args.out))
