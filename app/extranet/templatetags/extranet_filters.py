from django import template

register = template.Library()


@register.filter
def get_nb_days(leave):
    """
    Retourne 0.5 si demi-journée (am/pm), sinon le nombre de jours calendaires entre start_date et end_date inclus.
    """
    if leave.demi_jour in ["am", "pm"]:
        return 0.5
    return (leave.end_date - leave.start_date).days + 1


@register.filter
def get_item(dictionary, key):
    """
    Récupère un élément d'un dictionnaire par sa clé.
    """
    return dictionary.get(key)


@register.filter
def get_balance_attr(user_balances, user_and_attr):
    """
    Récupère un attribut du solde de congés pour un utilisateur donné.
    Format: user_balances|get_balance_attr:"user_id,attr_name"
    """
    try:
        user_id, attr_name = str(user_and_attr).split(",", 1)
        user_id = int(user_id)
        balance = user_balances.get(user_id, {})
        return balance.get(attr_name, 0)
    except (ValueError, AttributeError):
        return 0


@register.filter
def get_user_balance(user_balances, user_id):
    """
    Récupère le solde de congés pour un utilisateur donné.
    """
    return user_balances.get(user_id, {})
