import json
from uuid import UUID
from typing import Any
from items_app.infrastructure.redis.cache.base_serializer import BaseSerializer
from sqlalchemy.orm import DeclarativeBase
from items_app.infrastructure.postgres import models


class JsonSerializer(BaseSerializer):
    def dumps(self, data: Any) -> str:
        return json.dumps(data, default=self._default)

    def loads(self, data: str) -> Any:
        return json.loads(data, object_hook=self._object_hook)

    def _default(self, obj: Any) -> Any:
        if isinstance(obj, UUID):
            return {"__type__": "UUID", "value": str(obj)}
        
        if isinstance(obj, DeclarativeBase):
            mapper = obj.__mapper__
            data = {col.key: getattr(obj, col.key) for col in mapper.column_attrs}
            data["__type__"] = obj.__class__.__name__
            return data
        return obj

    def _object_hook(self, obj: dict) -> Any:
        if "__type__" in obj:
            if obj["__type__"] == "UUID":
                return UUID(obj["value"])
            if "__type__" in obj and hasattr(models, obj["__type__"]):
                model_cls = getattr(models, obj["__type__"])
                return model_cls(**{k: v for k, v in obj.items() if k != "__type__"})
        return obj
