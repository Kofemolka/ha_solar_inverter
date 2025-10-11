from .qpigs import QPIGS

QUERIES = {
    "QPIGS": QPIGS()
}


def get_user_queries(config):
    selected_queries = []
    for user_q in config:
        if user_q in QUERIES:
            selected_queries.append(QUERIES[user_q])

    return selected_queries