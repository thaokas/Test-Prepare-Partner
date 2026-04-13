from app.models.report import WeeklyReport


def test_report_table_name():
    assert WeeklyReport.__tablename__ == "weekly_reports"


def test_report_has_required_columns():
    cols = {c.name for c in WeeklyReport.__table__.columns}
    required = {'id', 'user_id', 'plan_id', 'week_start', 'week_end',
                'average_rate', 'summary', 'suggestions'}
    assert required.issubset(cols)


def test_report_has_index():
    index_names = {idx.name for idx in WeeklyReport.__table__.indexes}
    assert 'idx_user_week' in index_names


def test_report_defaults():
    col = WeeklyReport.__table__.columns['average_rate']
    assert col.default.arg == 0.0
