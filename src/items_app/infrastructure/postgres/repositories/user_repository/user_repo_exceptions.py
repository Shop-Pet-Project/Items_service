from typing import List
from uuid import UUID


class UserHasCompaniesError(Exception):
    """Нельзя удалить пользователя, у которого есть компании."""

    def __init__(self, user_id: UUID, companies: list[str]):
        self.user_id = user_id
        self.companies = companies
        super().__init__(
            f"Невозможно удалить пользователя {user_id}: "
            f"у него есть компании ({', '.join(companies)})"
        )
