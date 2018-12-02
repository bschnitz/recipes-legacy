#!/usr/bin/env python3

class Ingredient:
  def __init__(self, substance, amount):
    self.amount    = amount
    self.substance = substance

  def getAmount(self):
    return self.amount

  def getSubstance(self):
    return self.substance

class RecipeIngredientSection:
  def __init__(self, title=''):
    self.title=title
    self.ingredients = []

  def addIngredient(self, substance, amount):
    self.ingredients.append(Ingredient(substance, amount))

  def getTitle(self):
    return self.title

  def getIngredients(self):
    return self.ingredients

class RecipeIngredients:
  def __init__(self):
    self.sections = []

  def addSection(self, title=''):
    self.sections.append(RecipeIngredientSection(title))
    return self

  def addIngredient(self, substance, amount):
    self.sections[-1].addIngredient(substance, amount)

  def getSections(self):
    return self.sections

class Recipe:
  def __init__(self):
    self.title        = ''
    self.ingredients  = RecipeIngredients()
    self.instructions = []

  def setTitle(self, title):
    self.title = title

  def addIngredientSection(self, title=''):
    self.ingredients.addSection(title)

  def addIngredient(self, amount, substance):
    self.ingredients.addIngredient(substance, amount)

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
