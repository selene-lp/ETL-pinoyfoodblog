from playwright.async_api import async_playwright, Locator, Page
from datetime import date
from dataclasses import asdict
from Models import Ingredient, Recipe, Nutrition
import asyncio
import json
import os

# region: Globals
BASE_URL = "https://panlasangpinoy.com/recipes/"
ROUTE_ABORT = "**/*.{png,jpg,jpeg,webp,css,js}"
TIME_OUT = 10 * 60000
NULL_VALUE = ""

# endregion


# region: Utilities
async def safe_inner_text(
    locator: Locator, nth: int = 0, default: str = NULL_VALUE
) -> str:
    elements = await locator.all()
    return await elements[nth].inner_text() if elements else default


async def safe_all(locator: Locator, default: list = []) -> list[Locator]:
    elements = await locator.all()
    return elements if len(elements) != 0 else default


def get_json_set(textcontent: str, typevalue: str, default: str = NULL_VALUE):
    json_data = json.loads(textcontent).get("@graph", [{}])
    set_data = [item for item in json_data if item.get("@type") == typevalue]
    return set_data[0] if len(set_data) != 0 else default


def get_json_value(set_data: dict, key: str, default: str = NULL_VALUE):
    return set_data.get(key, default) if isinstance(set_data, dict) else default


def extract_instructions(recipe_instructions: list):
    return (
        [
            step["text"]
            for step in recipe_instructions
            if step.get("@type") == "HowToStep"
        ]
        if recipe_instructions
        else recipe_instructions
    )


def extract_yield(good_for: list):
    return good_for[1] if len(good_for) >= 2 else NULL_VALUE


# endregion


class Scraper:
    # region: Built-in props
    async def __aenter__(self):
        self.playwright = await async_playwright().start()
        self.browser = await self.playwright.chromium.launch(headless=True, slow_mo=0)
        self.page = await self.browser.new_page()
        self.errors = []
        await self.page.route(ROUTE_ABORT, lambda route: route.abort())
        return self

    async def __aexit__(self, exc_type, exc_value, traceback):
        await self.browser.close()
        await self.playwright.stop()

    # endregion

    # region: Custom Methods
    async def intialize_scrape(
        self, start: int = 1, end: int = 0, instances: int = 1
    ) -> list[str]:
        try:
            pages = await self.gather_pages(start, end)
            batches = [
                pages[i : i + instances] for i in range(0, len(pages), instances)
            ]

            results = []
            for index, batch in enumerate(batches):
                print(f"Batch number: {index + 1}, Pages to scrape: {len(batch)}")

                batch_recipes = await asyncio.gather(
                    *(self.scrape_single_page(page_url) for page_url in batch)
                )

                for batch_recipe in batch_recipes:
                    results.extend(batch_recipe)

            return results

        except Exception as e:
            print(f"Error: {e}")
            return

    async def scrape_single_page(self, page_url: str) -> list[Recipe]:
        try:
            new_tab = await self.browser.new_page()
            await new_tab.route(ROUTE_ABORT, lambda route: route.abort())
            await new_tab.goto(page_url, timeout=TIME_OUT)
            recipe_urls = [
                await url.get_attribute("href")
                for url in await new_tab.locator(
                    ".content-sidebar-wrap article h2 a"
                ).all()
            ]
            recipes = []
            for recipe_url in recipe_urls:
                print(f"Scraping: {recipe_url}")
                recipes.append(await self.scrape_recipe(new_tab, recipe_url))

            return recipes
        except Exception as e:
            print(f"Error scraping page {page_url}: {e}")
        finally:
            await new_tab.close()

    async def scrape_recipe(self, page: Page, page_url: str) -> Recipe:
        await page.goto(page_url, timeout=TIME_OUT)
        app_script = await page.locator(
            "script[type='application/ld+json']"
        ).first.text_content()

        article_set = get_json_set(app_script, "Article")
        recipe_set = get_json_set(app_script, "Recipe")

        return Recipe(
            get_json_value(article_set, "headline"),
            page.url,
            get_json_value(article_set, "thumbnailUrl"),
            get_json_value(recipe_set, "description"),
            get_json_value(article_set, "datePublished"),
            get_json_value(article_set, "dateModified"),
            get_json_value(article_set, "articleSection", []),
            get_json_value(article_set, "keywords", []),
            get_json_value(recipe_set, "recipeCategory", []),
            get_json_value(recipe_set, "recipeCuisine", []),
            get_json_value(recipe_set, "prepTime"),
            get_json_value(recipe_set, "cookTime"),
            await self.scrape_custom_time(page),
            extract_yield(get_json_value(recipe_set, "recipeYield")),
            await self.scrape_ingredients(page),
            extract_instructions(get_json_value(recipe_set, "recipeInstructions", [])),
            await self.scrape_nutritions(page),
        )

    async def scrape_custom_time(self, page: Page) -> str:
        return await safe_inner_text(page.locator(".wprm-recipe-custom_time"))

    async def scrape_nutritions(self, page: Page) -> list[Nutrition]:
        base_class = ".wprm-nutrition-label-text-nutrition-"
        nutritions = await safe_all(page.locator(f"{base_class}container"))
        return [
            Nutrition(
                await safe_inner_text(nutrition.locator(f"{base_class}label")),
                await safe_inner_text(nutrition.locator(f"{base_class}value")),
                await safe_inner_text(nutrition.locator(f"{base_class}unit")),
                await safe_inner_text(nutrition.locator(f"{base_class}daily")),
            )
            for nutrition in nutritions
        ]

    async def scrape_ingredients(self, page: Page) -> list[Ingredient]:
        base_class = ".wprm-recipe-ingredient-"
        ingredients = await safe_all(page.locator(f"{base_class}group ul li"))
        return [
            Ingredient(
                await safe_inner_text(ingredient.locator(f"{base_class}amount")),
                await safe_inner_text(ingredient.locator(f"{base_class}unit")),
                await safe_inner_text(ingredient.locator(f"{base_class}name")),
                await safe_inner_text(ingredient.locator(f"{base_class}notes")),
            )
            for ingredient in ingredients
        ]

    async def gather_pages(self, start: int, end: int) -> list[str]:
        await self.page.goto(BASE_URL, timeout=TIME_OUT)
        max_page_text = await safe_inner_text(
            self.page.locator(".content-sidebar-wrap ul li"), -2
        )
        max_page = int(max_page_text.split()[-1])
        end = max_page if end == 0 else end
        self._validate_gather_page_range(start, end, max_page)
        return [f"{BASE_URL}page/{page}/" for page in range(start, end + 1)]

    def _validate_gather_page_range(self, start: int, end: int, max_page: int) -> None:
        if start < 1 or start > max_page:
            raise ValueError(f"Start page {start} must be between 1 and {max_page}.")
        if end < 1 or end > max_page:
            raise ValueError(f"End page {end} must be between 1 and {max_page}.")
        if start > end:
            raise ValueError("Start page cannot be greater than end page.")

    # endregion


async def main():
    try:
        async with Scraper() as scraper:
            recipes = await scraper.intialize_scrape(instances=10)

        recipe_dict = [asdict(recipe) for recipe in recipes]
        folder_path = "Datasets/Bronze"
        filename = f"pinoyfoodblog-{date.today()}.json"

        os.makedirs(folder_path, exist_ok=True)
        file_path = os.path.join(folder_path, filename)

        with open(file_path, "w") as json_file:
            json.dump(recipe_dict, json_file, indent=4)
        print(f"Data saved to {file_path}")

    except Exception as e:
        print(f"An error occurred: {e}")


if __name__ == "__main__":
    asyncio.run(main())
