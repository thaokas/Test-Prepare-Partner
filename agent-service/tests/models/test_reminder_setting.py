from app.models.reminder_setting import ReminderSetting


def test_reminder_setting_table_name():
    assert ReminderSetting.__tablename__ == "reminder_settings"


def test_reminder_setting_has_required_columns():
    cols = {c.name for c in ReminderSetting.__table__.columns}
    required = {'id', 'user_id', 'mode', 'custom_times', 'monking_interval', 'is_active'}
    assert required.issubset(cols)


def test_reminder_setting_mode_names():
    from types import SimpleNamespace
    prop_func = ReminderSetting.mode_name.fget
    rs = SimpleNamespace(mode=0)
    assert prop_func(rs) == "静默模式"
    rs.mode = 1
    assert prop_func(rs) == "温柔模式"
    rs.mode = 2
    assert prop_func(rs) == "强化模式"
    rs.mode = 3
    assert prop_func(rs) == "唐僧模式"


def test_reminder_setting_defaults():
    col = ReminderSetting.__table__.columns['mode']
    assert col.default.arg == 1
    col2 = ReminderSetting.__table__.columns['monking_interval']
    assert col2.default.arg == 30
