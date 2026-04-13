from app.models.task import Task
from sqlalchemy import Index

def test_task_table_name():
    assert Task.__tablename__ == "tasks"

def test_task_has_required_columns():
    cols = {c.name for c in Task.__table__.columns}
    required = {'id', 'plan_id', 'user_id', 'task_date', 'subject', 'task_content', 'status', 'keywords'}
    assert required.issubset(cols)

def test_task_has_user_date_index():
    index_names = {idx.name for idx in Task.__table__.indexes}
    assert 'idx_user_date' in index_names
