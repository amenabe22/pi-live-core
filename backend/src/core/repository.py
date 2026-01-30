from redis import Redis
from datetime import datetime
from typing import Generic, Type, TypeVar, List, Any, Tuple, Optional
from sqlalchemy.orm import Session
from sqlalchemy import func
from core.const import AggregateInterval, AggregateWindow

Model = TypeVar("Model")


class BaseRepository(Generic[Model]):
    def __init__(self, session: Session, model: Type[Model], cache: Redis | None = None):
        self.session = session
        self.cache = cache
        self.model = model

    def get(self, id: Any) -> Model | None:
        return self.session.get(self.model, id)

    def get_by(self, **filters: Any) -> Model | None:
        return self.session.query(self.model).filter_by(**filters).first()

    def filter(
        self,
        *conditions: Any,
        filters: dict[str, Any] | None = None,
        skip: int = 0,
        limit: int = 100,
        order_by: Any | None = None
    ) -> Tuple[List[Model], int, int]:

        query = self.session.query(self.model)

        if filters:
            query = query.filter_by(**filters)
        if conditions:
            query = query.filter(*conditions)
        if order_by is not None:
            query = query.order_by(order_by)

        skip = max(0, skip)
        limit = max(0, limit)

        total_items = query.order_by(None).count()
        total_pages = (total_items + limit - 1) // limit if limit else 1

        items = query.offset(skip).limit(limit).all()

        return items, total_items, total_pages


    def list(
        self, 
        *, 
        skip: int = 0, 
        limit: int = 100,
        order_by: Any | None = None
    ) -> Tuple[List[Model], int, int]:

        return self.filter(skip=skip, limit=limit, order_by=order_by)

    def add(
        self, 
        obj: Model, 
        flush: bool = False
    ) -> Model:

        self.session.add(obj)
        if flush:
            self.session.flush()
        return obj

    def patch(
        self, 
        obj: Model,
        data: dict[str, Any],
        flush: bool = False
    ) -> Model:
    
        for field, value in data.items():
            if hasattr(obj, field):
                setattr(obj, field, value)
        
        if flush:
            self.session.flush()
        
        return obj

    def delete(self, obj: Model) -> None:
        self.session.delete(obj)

    # -- aggregate functions --

    def aggregate_count(
        self,
        ts_column: Any,
        *conditions: Any,
        start: datetime | None = None,
        end: datetime | None = None,
        window: AggregateWindow | None = None,
        interval: AggregateInterval = AggregateInterval.DAY,
        filters: dict[str, Any] | None = None,
        join_model: Any | None = None,
        join_condition: Any | None = None,
        join_filter: Any | None = None,
        limit: int | None = None,
    ) -> List[Tuple[Any, int]]:

        if end == None:
            end = datetime.utcnow()

        delta = window.delta if window != None else None
        if start == None and delta != None:
            start = end - delta

        bucket = func.date_trunc(interval.value, ts_column)

        query = (
            self.session.query(
                bucket.label("bucket"),
                func.count().label("count"),
            )
            .select_from(self.model)
        )

        if join_model is not None and join_condition is not None:
            query = query.join(join_model, join_condition)
        if filters:
            query = query.filter_by(**filters)
        if join_filter is not None:
            query = query.filter(join_filter)
        if conditions:
            query = query.filter(*conditions)
        if start != None:
            query = query.filter(ts_column >= start)
        if end != None:
            query = query.filter(ts_column < end)

        query = query.group_by(bucket)
        query = query.order_by(bucket.asc())

        if limit != None:
            query = query.limit(max(0, limit))

        rows = query.all()
        return [(r.bucket, r.count) for r in rows]


    def aggregate_sum(
        self,
        ts_column: Any,
        sum_column: Any,
        *conditions: Any,
        start: datetime | None = None,
        end: datetime | None = None,
        window: AggregateWindow | None = None,
        interval: AggregateInterval = AggregateInterval.DAY,
        filters: dict[str, Any] | None = None,
        joins: Optional[List[Tuple[Any, Any, Any]]] = None,
        join_filter: Any | None = None,
        limit: int | None = None,
    ) -> List[Tuple[Any, float]]:

        if end is None:
            end = datetime.utcnow()

        delta = window.delta if window is not None else None
        if start is None and delta is not None:
            start = end - delta

        bucket = func.date_trunc(interval.value, ts_column)

        query = self.session.query(
            bucket.label("bucket"),
            func.sum(sum_column).label("total"),
        ).select_from(self.model)

        if joins:
            for join_model, join_condition, join_filter in joins:
                query = query.join(join_model, join_condition)
                if join_filter is not None:
                    query = query.filter(join_filter)

        if filters:
            query = query.filter_by(**filters)

        if conditions:
            query = query.filter(*conditions)

        if start is not None:
            query = query.filter(ts_column >= start)
        if end is not None:
            query = query.filter(ts_column < end)

        query = query.group_by(bucket)
        query = query.order_by(bucket.asc())

        if limit is not None:
            query = query.limit(max(0, limit))

        rows = query.all()
        return [(r.bucket, r.total or 0) for r in rows]
