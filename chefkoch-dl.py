#!/usr/bin/env python3

import os
import sys
import dominate
from bs4 import BeautifulSoup
from dominate import tags
import requests
from abc import ABC, abstractmethod

class Ingredient:
  def __init__(self, amount, substance):
    self.amount    = amount
    self.substance = substance

  def getAmount(self):
    return self.amount

  def getSubstance(self):
    return self.substance

class Recipe:
  def __init__(self):
    self.title        = ''
    self.ingredients  = []
    self.instructions = []

  def setTitle(self, title):
    self.title = title

  def addIngredient(self, amount, substance):
    self.ingredients.append( Ingredient(amount, substance) )

  def addInstruction(self, instruction):
    self.instructions.append(instruction)

  def addInstructions(self, instructions):
    self.instructions.extend(instructions)

  def getTitle(self):
    return self.title

  def getIngredients(self):
    return self.ingredients

  def getInstructions(self):
    return self.instructions

class Converter(ABC):
  def __init__(self, sourceObject, sourceType):
    if isinstance(sourceObject, sourceType):
      self.source = sourceObject
    else:
      self.source = sourceObject.get()

  def getSource(self):
    return self.source

  @abstractmethod
  def get(self):
    pass

class UrlToHTML(Converter):
  def __init__(self, url):
    self.url = url
    self.request = requests.get(url)

  def get(self):
    return self.request.text

class ChefkochHTMLToRecipe(Converter):
  def __init__(self, html):
    super().__init__(html, str)
    self.recipe = Recipe()
    self.parseHTML(self.getSource())

  def getTitle(self, soup):
    title = soup.find("meta",  property="og:title")
    return title['content']

  def getInstructions(self, soup):
    instructions = soup.find(id="rezept-zubereitung")
    instructions = instructions.text.split('\n')
    instructions = [x.strip() for x in instructions if x.strip() != ""]
    return instructions

  def addIngredients(self, soup):
    ingredients_in = soup \
      .find(id="recipe-incredients") \
      .find("table") \
      .find_all("tr")

    ingredients = []

    for ingredient in ingredients_in:
      ingredient = ingredient.find_all("td")
      self.recipe.addIngredient(
        ingredient[0].text.strip(),
        ingredient[1].text.strip()
      )

  def parseHTML(self, html):
    soup = BeautifulSoup( html, 'html.parser' )

    self.recipe.setTitle(self.getTitle(soup))
    self.recipe.addInstructions(self.getInstructions(soup))
    self.addIngredients(soup)

  def get(self):
    return self.recipe

class RecipeToDominateDocument(Converter):
  def __init__(self, recipe):
    super().__init__(recipe, Recipe)
    self.createDominateDocument(self.getSource())

  def createDominateDocument(self, recipe):
    self.document = dominate.document(recipe.getTitle())
    self.createHead()
    self.createBody(recipe)

  def createHead(self):
    with self.document.head:
      tags.meta(charset='UTF-8')
      tags.style('body{font-size: 4vmin;}')

  def createBody(self, recipe):
    with self.document:
      with tags.div(id="ingredients").add(tags.table()):
        tags.h3("Zutaten")
        for ingredient in recipe.getIngredients():
          with tags.tr():
            tags.td(ingredient.getAmount(), cls="amount")
            tags.td(ingredient.getSubstance(), cls="substance")
      with tags.div(id="instructions"):
        tags.h3("Zubereitung")
        for instruction in recipe.getInstructions():
          tags.p(instruction)

  def get(self):
    return self.document

class DominateDocumentToHTMLFile(Converter):
  def __init__(self, document):
    super().__init__(document, dominate.document)

  def getFilename(self):
    title = self.source.get_title()
    return title.lower().translate(str.maketrans(' ', '-', ','))+'.html'

  def createFolder(self, path):
    if not os.path.exists(path):
      os.makedirs(path)

  def writeFile(self):
    path = 'recipes/'
    self.createFolder(path)
    with open(path+self.getFilename(), 'w') as file:
      print(self.source, file=file)

  def get(self):
    self.writeFile()

if __name__ == "__main__":
  url = sys.argv[1]
  html = UrlToHTML(url)
  recipe = ChefkochHTMLToRecipe(html)
  document = RecipeToDominateDocument(recipe)
  html_file = DominateDocumentToHTMLFile(document)
  html_file.get()
