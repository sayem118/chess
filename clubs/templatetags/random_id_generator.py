from django import template
import random

register = template.Library()

idsSoFar = []

@register.simple_tag
def randomIdNumber():
    number = random.randint(10000,99999)

    initialLength = len(idsSoFar)

    while ( len(idsSoFar) != initialLength+1):
        try:
            idsSoFar.index(number)
            number = random.randint(10000,99999)
        except ValueError:
            idsSoFar.append(number)

    return number
