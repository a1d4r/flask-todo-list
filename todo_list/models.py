from datetime import datetime
from typing import Literal, Optional

from pydantic import BaseModel

from . import db


class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    description = db.Column(db.String(100), nullable=False)
    active = db.Column(db.Boolean, default=True, nullable=False, index=True)
    created_at = db.Column(
        db.DateTime, default=datetime.utcnow, nullable=False, index=True
    )

    def __repr__(self):
        return f'<Task {self.description}>'


class TodoListQuery(BaseModel):
    status: Optional[Literal['all', 'active', 'completed']] = None
    page: int = 1
    filter: Optional[str] = None
