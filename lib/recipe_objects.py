
class Ingredient:
    def __init__(self, ingredient, unit, amount, language="FI"):
        self.amount = amount
        self.unit = unit
        self.ingredient = ingredient
        self.language = language

    def get_calories(self):
        #TODO
        pass
    
    def get_string(self):
        string = self.amount + " " + self.unit + " " + self.ingredient
        return string.strip()
    
    def __repr__(self):
        return "\nIngredient instance of {0}".format(self.ingredient)

    def __str__(self):
        return "\nIngredient instance of {0}".format(self.ingredient)


class Recipe:
    def __init__(self, name, url, img_url=None, categories=None,
                 difficulty=None, language='FI'):
        self.name = name
        self.url = url
        self.img_url = img_url
        self.categories = categories
        self.difficulty = difficulty
        self.language = language
        
        # Set after get recipe
        self.ingredients = []
        self.stages = []
        self.language = None
        self.time = ""
        self.servings = ""

    def get_recipe(self, parser_instance, recipe_name):
        return parser_instance.get_recipe(recipe_name)
    
    def __repr__(self):
        return "\nRecipe instance of {0}".format(self.name)

    def __str__(self):
        return "\nRecipe instance of {0}".format(self.name)
