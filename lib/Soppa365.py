import re
try:
    from lib.recipe_objects import Ingredient, Recipe
except ModuleNotFoundError:
    from recipe_objects  import Ingredient, Recipe
from multiprocessing.pool import Pool
import sys; sys.setrecursionlimit(10000)
from HTML.reader import parse_url


class Soppa365Parser:
    # For search recipes
    re_ajax_recipes = re.compile(r'recipe-card-horizontal')
    # For recipe items ands instructions building
    re_recipe_sheet = re.compile(r'region main2')
    re_stages = 'field field-name-field-recipe-instructions field-type-text-long field-label-hidden'
    re_ingredients = re.compile(r'recipe-items__item')
    re_items_instructions = re.compile(r'group-recipe-ingredients')
    re_multiple_newline = re.compile('\n\n\n\n\n\n\n')

    def __init__(self):
        self.recipes = {}
        self.log = []
    
    def search(self, search, category="", difficulty="", max_page=10):
        self.latest_search = search, category, difficulty
        self.recipes = {}
        
        # Build urls for multiprocess map
        urls = []
        search = "&".join(search.split(" "))
        for page in range(max_page):
            url = ("https://www.soppa365.fi/ajax/sbase-cloud-search-recipe?"
                   "page={page}&keyword={search}&category={category}&"
                   "difficulty={difficulty}").format(page=page, search=search,
                                                     category=category,
                                                     difficulty=difficulty)
            urls.append(url)
        #### For standalone
        # responses = Pool(5).map(parse_url, urls) 
        #### For spyder run
        responses = []
        for url in urls:
            responses.append(parse_url(url))
        # Use multiprocessing if applicable
    
        for response in responses:
            self._parse_page(response)
            
    def _parse_page(self, response):
        recipe_page = response.find_all("article", class_=self.re_ajax_recipes)
        for recipe in recipe_page:
            self._parse_recipe(recipe)
            
    def _parse_recipe(self, recipe_sheet):
        # Set recipe name
        temp = recipe_sheet.div.div.next_sibling.next_sibling.div.div.div.a
        name = temp.text.strip().capitalize()

        # Set url to recipe
        temp = recipe_sheet.div.a
        url = "https://www.soppa365.fi" + temp.attrs['href']

        # Add numeric index if recipe name already in recipe dict for unique
        if name in self.recipes:
            if self.recipes[name].url == url:
                if name[-1].isdigit():
                    last_num = int(name[-1])
                    name[-1] = str(last_num + 1)
                else:
                    name += " 2"

        # Get image url
        try:
            temp = temp.div.div.div.div.div.img
            img_url = temp.attrs['data-src']
        except AttributeError:
            img_url = None
        
        # Set category
        categories = []
        temp = recipe_sheet.div.next_sibling.next_sibling.div
        try:
            for cat in temp.div.div.next_sibling.next_sibling.div:
                if not cat == ", ":
                    categories.append(cat.text)
        except AttributeError:
            categories = None

        # Set difficulty
        try:
            temp = temp.next_sibling.next_sibling.div.div.next_sibling
            temp = temp.next_sibling.div
            difficulty = cat.text
        except (AttributeError, UnboundLocalError):
            difficulty = None
        
        # Add recipe to recipe book and print warnings
        recipe_obj = Recipe(name, url, img_url, categories, difficulty, "FI") 
        self.recipes[recipe_obj.name] = recipe_obj

    def get_recipe(self, recipe_name):
        if self.recipes[recipe_name].ingredients:
            return self.recipes[recipe_name]

        url = self.recipes[recipe_name].url
        soup = parse_url(url)
        # Get recipe sheet pointer
        recipe_sheet = soup.find('div', class_=self.re_recipe_sheet)
        
        # Build ingredients and stages
        self.recipes[recipe_name].ingredients = self._build_ingredients(recipe_sheet)
        self.recipes[recipe_name].stages = self._build_stages(soup)
        return self.recipes[recipe_name]

    def _build_ingredients(self, recipe_sheet):
        # Ingredient parser
        def create_ingr_obj(ingr_list):
            icount = len(ingr_list)
            if icount == 3:
                return Ingredient(ingr_list[2], ingr_list[1], ingr_list[0])
            elif icount == 2:
                return Ingredient(ingr_list[1], "", ingr_list[0])
            elif icount == 1:
                return Ingredient(ingr_list[0], "", "")

        # Path to ingredients
        ingredient = recipe_sheet.find('div', class_=self.re_ingredients)
        items = []
        while ingredient:  # Containers
            item = ingredient.div
            lingr = []
            while item:  # Items in ingredient container
                # Append ingredient data to list
                lingr.append(item.text.strip())
                item = item.next_sibling.next_sibling
            items.append( create_ingr_obj(lingr) )
            ingredient = ingredient.next_sibling.next_sibling # Next ingredient
        return items
    
    def _build_stages(self, recipe_sheet):
        temp = recipe_sheet.find('div', class_=self.re_stages)
        stages = []
        # Get stages
        temp = temp.div.div
        for item in temp:
            try:
                txt = item.text.strip()
            except AttributeError:
                continue
            stages.append(txt)
        return stages


if __name__ == '__main__':
    def profile(function, *args, **kwargs):
        """ Returns performance statistics (as a string) for the given function.
        """
        def _run():
            function(*args, **kwargs)
        import cProfile as profile
        import pstats
        import os
        import sys; sys.modules['__main__'].__profile_run__ = _run
        id_ = function.__name__ + '()'
        profile.run('__profile_run__()', id_)
        p = pstats.Stats(id_)
        p.stream = open(id_, 'w')
        p.sort_stats('cumulative').print_stats(30)
        p.stream.close()
        s = open(id_).read()
        os.remove(id_)
        return s
    
    def test():
        soppa = Soppa365Parser()
        soppa.search("omena")
        return soppa

    #print(profile(test))
    soppa = Soppa365Parser()
    soppa.search('omena')
    recipe = soppa.get_recipe('Omena-kauravuokaleipä')



