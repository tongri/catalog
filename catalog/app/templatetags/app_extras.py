from django import template

register = template.Library()


def indexer(value, arg):
    value = [int(x) for x in value]
    return value[arg]


def mult(value, arg):
    return int(value) * int(arg)


register.filter('indexer', indexer)
register.filter('mult', mult)
