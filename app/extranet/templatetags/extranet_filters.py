from django import template

register = template.Library()


@register.filter
def get_nb_days(leave):
    """Return 0.5 if half-day (am/pm), otherwise the number of calendar days
    between start_date and end_date inclusive.
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
def dict_get(dictionary, key):
    """
    Récupère un élément d'un dictionnaire par sa clé.
    Alias pour get_item pour plus de clarté.
    """
    return dictionary.get(key)


@register.filter
def get_balance_attr(user_balances, user_and_attr):
    """Get an attribute from a user's leave balance.

    Expected format: user_balances|get_balance_attr:"user_id,attr_name"
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


@register.filter
def french_decimal(value, decimal_places=1):
    """
    Affiche un nombre décimal avec des virgules au lieu des points.
    Usage: {{ value|french_decimal:1 }}
    """
    if value is None:
        return "0"
    
    try:
        # Convertir en float si c'est un Decimal
        float_value = float(value)
        
        # Formater avec le nombre de décimales spécifié
        if decimal_places == 0:
            formatted = f"{float_value:.0f}"
        else:
            formatted = f"{float_value:.{decimal_places}f}"
        
        # Remplacer le point par une virgule
        return formatted.replace('.', ',')
    except (ValueError, TypeError):
        return str(value)


@register.filter
def days_display(value):
    """
    Affiche les jours avec virgule française et le bon pluriel.
    Usage: {{ value|days_display }}
    """
    if value is None:
        return "0 jour"
    
    try:
        float_value = float(value)
        formatted = french_decimal(value, 1)
        
        # Gestion du pluriel
        if float_value <= 1:
            return f"{formatted} jour"
        else:
            return f"{formatted} jours"
    except (ValueError, TypeError):
        return f"{value} jour"
