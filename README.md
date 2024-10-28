# ETL-pinoyfoodblog

This ETL project for PinoyFoodBlog demonstrates an ETL process with <b>Medallion Architecture</b>, <b>Web Scraping</b>, <b>Data Modeling</b>, <b>Pandas</b>, <b>Python</b>, <b>SQL</b>, and <b>Jupyter Notebook</b>. The project includes three stages: Bronze, Silver, and Gold, each with specific data processing and storage methods.

- Bronze Stage:

    - <b>File:</b> `extract.py`
    - <b>Process:</b> Web scraping is performed asynchronously using `playwright` and `asyncio`, with an object-oriented structure provided by `dataclasses`. The raw data is saved in `datasets/bronze` for initial processing.

- Silver Stage:

    - <b>File:</b> `transform.ipynb`
    - <b>Process:</b> Data is cleaned and normalized in `Jupyter` using `pandas`, with spelling corrections by `thefuzz` and unit standardization by `pint`. The structured data is saved in `datasets/silver` as a cleaned dataset and `pinoyfoodblog.db` file.

- Gold Stage:

    - <b>File:</b> `load.ipynb`
    - <b>Process:</b> Using `sqlalchemy`, the analytics-ready data is loaded from the Silver database. Aggregated insights are saved as a Parquet file in `datasets/gold`, providing analytics on cooking times, nutritional content, and servings.
 
### Installation Process

You need to install Jupyter Notebook or VS Code jupyter extension to view or run the .ipynb files.

For the installation of python libraries:

```
pip install pandas thefuzz pint sqlalchemy playwright
pip install playwright
```

### Final Output

From extraction, It will saved a .json file with a filename of pinoyfoodblog.json. and will be transformed and load using the .ipynb files.

For your references, here are the expected outputs from raw data to analytics:

<b>Raw json file from extraction</b> - `pinoyfoodblog.json`

```
[
  {
		"name": "Batchoy Tagalog",
		"link": "https://samplelink.com/batchoy-tagalog/",
		"thumbnail": "https://samplelink.com/wp-content/uploads/2024/09/How-to-cook-batchoy.jpg",
		"description": "Filipino noodle soup composed of pork tenderloin and innards.",
		"publish": "2024-09-23T13:52:48+00:00",
		"modified": "2024-09-23T14:15:35+00:00",
		"categories": [
			"Lunch Recipes",
			"Noodle Recipes",
			"Pork Recipes",
			"Recipes",
			"Soup Recipes"
		],
		"tags": ["asian noodle recipe", "batchoy", "Pork Recipes"],
		"courses": ["Main Course"],
		"cuisines": ["Filipino"],
		"prep_time": "PT10M",
		"cook_time": "PT45M",
		"custom_time": "",
		"good_for": "4 people",
		"ingredients": [
			{
				"amount": "1",
				"unit": "lb.",
				"name": "pork loin",
				"notes": ""
			}
		],
		"instructions": [
			"Heat 3 tablespoons cooking oil in a cooking pot.",
			"Add 1 lb. pork loin, stirring until the outer part turns light brown, which should take around 2 minutes",

		],
		"nutritions": [
			{
				"label": "Calories: ",
				"value": "1986",
				"unit": "kcal",
				"daily": " (99%)"
			}
		]
	}
]
```

<b>Normalized database structure</b> - `pinoyfoodblog.db`

![ERD](https://github.com/user-attachments/assets/449755a3-00a5-461a-87b3-3471249647d5)

<b>Analytics</b> - `load.ipynb`

![analytics](https://github.com/user-attachments/assets/7073ed5b-7bd0-440c-95de-6e7a18062a25)


