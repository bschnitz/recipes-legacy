#!/usr/bin/env python3

from recipe.converters import *

import sys

url = sys.argv[1]
html = UrlToHTML(url)
recipe = ChefkochHTMLToRecipe(html)
document = RecipeToDominateDocument(recipe)
DominateDocumentToHTMLFile(document)
