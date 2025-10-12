from .qpigs import QPIGS
from .qmod import QMOD

QUERIES = {
    QPIGS.cmd(): QPIGS(),
    QMOD.cmd(): QMOD()
}


def get_user_queries(config):
    selected_queries = []
    for user_q in config:
        if user_q in QUERIES:
            selected_queries.append(QUERIES[user_q])

    return selected_queries