import urllib.request
import tkinter as tk
from PIL import Image, ImageTk
from functools import partial
from GUI.general import (LabeledEntryNoButton, LabeledEntryWithButton,
                         FilteredSelectableList, HyperlinkManager)
import webbrowser
# From folder
from Apps.recipe_scraper.lib.Soppa365 import Soppa365Parser


font = 'calibri 14'
lfont = 'calibri 12'


class RecipeBook:
    books = [Soppa365Parser()]
    def __init__(self, search=None):
        self.soppa = self.books[0]
    
    def search(self, string_vart):
        # Search from all sites and append together
        self.soppa.search(string_vart)
        self.recipes = self.soppa.recipes

    def get_recipe(self, recipe_name):
        # Check where the recipe is and use correct parser
        url = self.recipes[recipe_name].url
        if url.startswith(r"https://www.soppa365.fi/"):
            return self.soppa.get_recipe(recipe_name)
        

class Application(tk.Frame):
    def __init__(self, master=None):
        tk.Frame.__init__(self, master)
        self.recipe_book = RecipeBook()
        self.create_widgets()

    # Create main GUI window
    def create_widgets(self):
        # Left frame for search, filter, list and picture
        # Right for recipe
        self.frame_left = tk.Frame(self)
        self.frame_left.pack(side=tk.LEFT, anchor=tk.NW, expand=tk.YES, fill=tk.X)

        # LEFT FRAME
        # Search bar (frame with label and inputbox)
        self.frame_search = LabeledEntryWithButton(self.frame_left, label_text="Search for", label_width=10)
        self.frame_search.pack(side=tk.TOP, anchor=tk.NW, expand=tk.YES, fill=tk.X)
        self.frame_search.set_callback(self.onSearchButton)

        # Filter bar (frame with label and function triggered by string variable)
        self.frame_filter = LabeledEntryNoButton(self.frame_left, label_text="Filter for", label_width=10)
        self.frame_filter.pack(side=tk.TOP, anchor=tk.NW, expand=tk.YES, fill=tk.X)
        self.frame_filter.variable.trace('w', self.filter_list)

        # List box with double click and enter binding
        self.listbox_recipes = FilteredSelectableList(self.frame_left, label_text="Filter matches in search results:", list_width=60, list_height=20)
        self.listbox_recipes.pack(side=tk.TOP, anchor=tk.NW, expand=tk.YES, fill=tk.X)
        self.listbox_recipes.set_callback(self.onGetRecipe)
        
        # Label for picture
        self.label_picture = tk.Label(self.frame_left, height=30)
        self.label_picture.pack(side=tk.TOP, anchor=tk.NW, expand=tk.YES, fill=tk.X)
        
        # RIGHT FRAME
        self.frame_recipe = tk.Frame(self, width=800)
        self.frame_recipe.pack(side=tk.RIGHT, anchor=tk.NE, expand=tk.YES, fill=tk.X)

        self.frame_recipe_general = tk.Frame(self.frame_recipe)
        
        self.label_recipe_amount = tk.Label(self.frame_recipe_general, width=20, height=3, font=14)
        self.label_recipe_time = tk.Label(self.frame_recipe_general, width=40, height=3, font=14)
        
        self.label_recipe_amount.pack(side="left", anchor=tk.NW, expand=tk.YES, fill=tk.X)
        self.label_recipe_time.pack(side="left", anchor=tk.NW, expand=tk.YES, fill=tk.X)
        self.frame_recipe_general.pack(side="top", anchor=tk.NW, expand=tk.YES, fill=tk.X)
        
        self.text_items = tk.Text(self.frame_recipe, font=14, height=30)
        self.hyperlink_items = HyperlinkManager(self.text_items)
        self.text_stages = tk.Text(self.frame_recipe, font=14)
        
        # Pack right frame
        self.text_items.pack(side="top", anchor=tk.NW, expand=tk.YES, fill=tk.X)
        self.text_stages.pack(side="top", anchor=tk.NW, expand=tk.YES, fill=tk.X)

    def onSearchButton(self, *args):
        search_term = self.frame_search.variable.get()
        self.recipe_book.search(search_term)

        self.search_hits = len(self.recipe_book.recipes)
        self.filter_list()

    def filter_list(self, *args):
        filter_term = self.frame_filter.variable.get()
        listbox = self.listbox_recipes.listbox
        recipes = self.recipe_book.recipes

        listbox.delete(0, tk.END)
        
        for item in recipes:
            if filter_term.lower() in item.lower():
                listbox.insert(tk.END, item)

    def onGetRecipe(self, event):
        # Get chosen recipe
        widget = event.widget
        selection = widget.curselection()
        if selection == ():
            return None
        # Search for recipe in recipebook
        recipe = self.recipe_book.get_recipe(widget.get(selection[0]))
        
        # Update image, if no image use troll
        img_url = recipe.img_url
        if img_url is not None:
            urllib.request.urlretrieve(img_url, 'temp//test.jpg')
            maxsize = (465, 465)
            image = Image.open('temp//test.jpg')
            image.thumbnail(maxsize, Image.ANTIALIAS)
            self.image = ImageTk.PhotoImage(image)
            self.label_picture.configure(image=self.image, height=500)
        else:
            self.image = ImageTk.PhotoImage(Image.open('data//error.png'))
            self.label_picture.configure(image=self.image, height=500)
        
        # Delete GUI contents
        self.text_items.configure(state='normal')
        self.text_items.delete(1.0, tk.END)
        self.text_stages.configure(state='normal')
        self.text_stages.delete(1.0, tk.END)
    
        # Set recipe data      
        self.label_recipe_amount.configure(text=recipe.servings)
        self.label_recipe_time.configure(text=recipe.time,
                                         wraplength=200)
        items = ""
        for ingredient in recipe.ingredients:
            items += ingredient.get_string() + "\n"
        
        stages = recipe.stages
        txt_stages = "\n\n".join(stages)
        
        # Fill boxes
        self.text_items.insert(tk.END, items)
        self.text_items.insert(tk.INSERT, "\n\n")
        self.text_items.insert(tk.INSERT, recipe.url, 
                               self.hyperlink_items.open_url(recipe.url))
        self.text_stages.insert(tk.END, txt_stages)

        # Word wrap
        self.text_items.configure(wrap='word')
        self.text_stages.configure(wrap='word')
        # Read-onnly
        self.text_items.configure(state='disabled')
        self.text_stages.configure(state='disabled')

    def click_hypertext(self, *url):
        lambda url=url: webbrowser.open(url)


if __name__ == '__main__':
    root = tk.Tk()
    root.title('Recipe selector')
    app = Application(root)
    app.pack()
    app.mainloop()

