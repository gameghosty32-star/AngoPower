from utils.angola import PROVINCIAS, MOEDA, TELEFONE_PREFIXO


def notification_count(request):
    if request.user.is_authenticated:
        return {
            'unread_count': request.user.notifications.filter(is_read=False).count(),
        }
    return {'unread_count': 0}


def angola_context(request):
    return {
        'PROVINCIAS': PROVINCIAS,
        'MOEDA': MOEDA,
        'TELEFONE_PREFIXO': TELEFONE_PREFIXO,
    }
