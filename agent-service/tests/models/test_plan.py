from app.models.plan import StudyPlan

def test_plan_table_name():
    assert StudyPlan.__tablename__ == "study_plans"

def test_plan_has_required_columns():
    cols = {c.name for c in StudyPlan.__table__.columns}
    required = {'id', 'user_id', 'exam_name', 'exam_type', 'exam_date', 'status', 'current_phase'}
    assert required.issubset(cols)

def test_plan_phase_name_property():
    from types import SimpleNamespace
    prop_func = StudyPlan.phase_name.fget
    plan = SimpleNamespace(current_phase=1)
    assert prop_func(plan) == "基础阶段"
    plan.current_phase = 2
    assert prop_func(plan) == "强化阶段"
    plan.current_phase = 3
    assert prop_func(plan) == "冲刺阶段"
