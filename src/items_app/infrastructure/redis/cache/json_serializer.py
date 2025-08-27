import json
from uuid import UUID
from typing import Any
from items_app.infrastructure.redis.cache.base_serializer import BaseSerializer


class JsonSerializer(BaseSerializer):
    def dumps(self, data: Any) -> str:
        return json.dumps(data, default=self._default)

    def loads(self, data: str) -> Any:
        return json.loads(data, object_hook=self._object_hook)

    def _default(self, obj: Any) -> Any:
        if isinstance(obj, UUID):
            return {"__type__": "UUID", "value": str(obj)}
        return obj

    def _object_hook(self, obj: dict) -> Any:
        if "__type__" in obj:
            if obj["__type__"] == "UUID":
                return UUID(obj["value"])
        return obj
