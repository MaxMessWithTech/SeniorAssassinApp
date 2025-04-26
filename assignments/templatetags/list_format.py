from django import template

register = template.Library()

@register.filter(name='list_formatting')
def list_formatting(value):
    return ', '.join(value)

@register.filter(name='query_to_list')
def convertQueryToNameList(query) -> list:

	out = list()

	for p in query:
		out.append(p.name)

	if len(out) == 0:
		out.append("NONE")
	
	return ', '.join(out)

