#!/usr/bin/env python3

import os
import dominate
from bs4 import BeautifulSoup
from dominate import tags
import requests
from abc import ABC, abstractmethod

from .recipe import *

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

    first_ingredient = ingredients_in[0].find_all("td")
    amount    = first_ingredient[0].text.strip()
    substance = first_ingredient[1].text.strip()

    if amount != '':
      self.recipe.addIngredientSection()

    for ingredient in ingredients_in:
      ingredient = ingredient.find_all("td")
      amount    = ingredient[0].text.strip()
      substance = ingredient[1].text.strip()
      if amount == '':
        self.recipe.addIngredientSection(substance)
      else:
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
      with tags.div(id="ingredients"):
        tags.h3("Zutaten")
        for section in recipe.getIngredients().getSections():
          with tags.div(cls="section"):
            if section.getTitle() != '':
              tags.h4(section.getTitle())
            with tags.table():
              for ingredient in section.getIngredients():
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
    self.writeFile()

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
    return self.getFilename()