class ItemNotFound(Exception):
    """
    Исключения возникающее в случае отсутствия товара в БД
    """

    pass


class NoAccessToItem(Exception):
    """
    Исключение возникающее в случае, если у пользователя нет доступа к товару
    """

    pass
