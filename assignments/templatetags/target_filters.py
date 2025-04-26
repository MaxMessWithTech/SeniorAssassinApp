from django import template

register = template.Library()

@register.filter(name='target_remaining')
def targetRemaining(all_p):

    if len(filtered_p) == 0:
        return ""

    filtered_p = list()

    for p in all_p:
        if p.round_eliminated is True and p.eliminated_permanently is False:
            filtered_p.append(p)

    return len(filtered_p)
