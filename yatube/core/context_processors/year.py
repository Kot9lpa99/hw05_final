from datetime import datetime


def year(request):
    a = datetime.today().year
    return {'year': a}
