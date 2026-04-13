from app.models.checkin import CheckinRecord


def test_checkin_table_name():
    assert CheckinRecord.__tablename__ == "checkin_records"


def test_checkin_has_required_columns():
    cols = {c.name for c in CheckinRecord.__table__.columns}
    required = {'id', 'user_id', 'plan_id', 'checkin_date', 'content',
                'completed_task_ids', 'completion_rate', 'encouragement'}
    assert required.issubset(cols)


def test_checkin_has_index():
    index_names = {idx.name for idx in CheckinRecord.__table__.indexes}
    assert 'idx_user_plan_date' in index_names


def test_checkin_defaults():
    col_defaults = {c.name: c.default.arg for c in CheckinRecord.__table__.columns if c.default}
    assert col_defaults.get('checkin_type') == 1
    assert col_defaults.get('completion_rate') == 0.0
