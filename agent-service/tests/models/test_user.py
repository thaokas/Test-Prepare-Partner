from app.models.user import User

def test_user_table_name():
    assert User.__tablename__ == "users"

def test_user_has_required_columns():
    cols = {c.name for c in User.__table__.columns}
    required = {'id', 'username', 'foundation_level', 'current_streak', 'reminder_mode', 'created_at'}
    assert required.issubset(cols)

def test_user_foundation_level_default():
    col = User.__table__.columns['foundation_level']
    assert col.default.arg == 0

def test_user_reminder_mode_default():
    col = User.__table__.columns['reminder_mode']
    assert col.default.arg == 1
