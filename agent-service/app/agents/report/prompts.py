"""周报生成Agent提示词 & HTML模板"""

# ── 1. 表现分析 Prompt（输出 JSON）────────────────────────────────────────────
ANALYZE_PROMPT = """你是备考督导助手，请分析用户在 {start_date} 至 {end_date} 期间的备考表现。

期间数据：
- 总完成率：{total_rate}%（完成 {total_completed}/{total_planned} 项任务）
- 打卡天数：{streak_days} 天
- 各科情况：
{subject_stats_text}
- 每日进度（计划 vs 实际）：
{daily_breakdown_text}
- 已完成任务明细：
{completed_tasks_detail}

请分析学习亮点和需要改进的地方，输出JSON格式：
{{
  "highlights": ["亮点1", "亮点2"],
  "issues": ["问题1", "问题2"]
}}

亮点判断参考：完成率≥80%的科目、连续打卡天数多、单日完成量大、某天全部完成计划。
问题判断参考：完成率<50%的科目、某天完全没有完成任务、总是跳过某类任务、某天计划很多但完成很少。
每类最多3条，若无亮点/问题则返回空列表。
"""

# ── 2. 报告文字内容 Prompt（输出 JSON，由 Python 组装进 HTML）────────────────
REPORT_TEXT_PROMPT = """你是备考督导助手"小搭"，请根据用户备考情况生成点评和后续建议。

期间：{start_date} 至 {end_date}
情况：
- 总完成率：{total_rate}%
- 完成任务：{total_completed}/{total_planned} 项
- 学习时长：{completed_hours} 小时
- 打卡天数：{streak_days} 天
- 亮点：{highlights}
- 待改进：{issues}
- 每日进度：
{daily_breakdown_text}

请根据完成率严格采用对应语气输出JSON：
{{
  "comment": "点评内容（见下方规则）",
  "suggestions": ["建议1", "建议2", "建议3"]
}}

点评语气规则（必须遵守）：
- 完成率 ≥ 90%：热情表扬。称赞自律和执行力，肯定具体科目表现，鼓励保持节奏。语气像朋友为你高兴。
- 完成率 70%~89%：肯定+轻推。先认可付出，再温和指出提升空间，比如"再冲一冲就能更稳"。
- 完成率 50%~69%：关切+鼓劲。先共情（备考确实不容易），分析可能原因（时间不够？任务太重？），给出务实建议，语气坚定但不严厉。
- 完成率 < 50%：严肃批评+打气。直接点出问题（拖延？计划不合理？），用"恨铁不成钢"的语气，但不能羞辱。最后一定要给希望——"现在调整还来得及"。
- 完成率 = 0%（期间无任何打卡/完成）：警告+督促。语气严厉，提醒备考时间在流逝，要求立即行动。同时表达愿意帮助制定更合理的计划。

禁止的表述：
- "你要加油哦" "继续努力" 等空洞套话
- 说教口吻（"你应该..." 改为 "不妨试试..."）
- 单独一句点评（至少2句，不超过5句）

建议要求：
- 针对待改进问题，具体可执行，每条≤30字
- 若无问题则给出保持现有节奏的建议
- 必须有1条关于时间管理的建议
"""

# ── 3. HTML 模板（Python 格式化字符串）────────────────
HTML_TEMPLATE = """\
<!DOCTYPE html>
<html lang="zh">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<style>
  * {{ box-sizing: border-box; margin: 0; padding: 0; }}
  body {{ background: #f5f5f5; font-family: -apple-system, BlinkMacSystemFont, 'PingFang SC', 'Helvetica Neue', sans-serif; padding: 16px; }}
  .container {{ max-width: 480px; margin: 0 auto; }}
  .card {{ background: #fff; border-radius: 12px; padding: 16px; margin-bottom: 12px; box-shadow: 0 2px 8px rgba(0,0,0,0.06); }}
  .header {{ background: linear-gradient(135deg, #667eea, #764ba2); color: #fff; border-radius: 12px; padding: 20px 16px; margin-bottom: 12px; text-align: center; }}
  .header h1 {{ font-size: 20px; font-weight: 700; margin-bottom: 4px; }}
  .header p {{ font-size: 13px; opacity: 0.85; }}
  .grade-badge {{ display: inline-block; background: rgba(255,255,255,0.2); border-radius: 20px; padding: 4px 16px; font-size: 28px; font-weight: 800; margin-top: 8px; letter-spacing: 2px; }}
  .section-title {{ font-size: 14px; font-weight: 600; color: #333; margin-bottom: 10px; }}
  .overview-grid {{ display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 8px; margin-top: 14px; }}
  .metric {{ text-align: center; }}
  .metric-value {{ font-size: 22px; font-weight: 700; color: #667eea; }}
  .metric-label {{ font-size: 11px; color: #999; margin-top: 3px; }}
  .progress-bar {{ background: #f0f0f0; border-radius: 999px; height: 8px; margin: 14px 0 4px; overflow: hidden; }}
  .progress-fill {{ height: 100%; border-radius: 999px; background: linear-gradient(90deg, #667eea, #764ba2); }}
  .progress-label {{ font-size: 12px; color: #999; text-align: right; margin-bottom: 2px; }}
  table {{ width: 100%; border-collapse: collapse; font-size: 13px; }}
  th {{ text-align: left; color: #999; font-weight: 500; padding: 4px 0 8px; border-bottom: 1px solid #f0f0f0; }}
  td {{ padding: 8px 0; border-bottom: 1px solid #f8f8f8; color: #444; }}
  .two-col {{ display: grid; grid-template-columns: 1fr 1fr; gap: 12px; }}
  .col-label {{ font-size: 12px; font-weight: 600; margin-bottom: 8px; }}
  .list-item {{ font-size: 13px; color: #555; line-height: 1.7; padding: 2px 0; }}
  .empty-hint {{ font-size: 12px; color: #bbb; }}
  .comment-text {{ font-size: 14px; color: #444; line-height: 1.9; }}
  .suggestion-item {{ font-size: 13px; color: #555; padding: 9px 12px; background: #f8f7ff; border-radius: 8px; margin-bottom: 8px; border-left: 3px solid #667eea; }}
  .tag-green {{ color: #4CAF50; font-weight: 600; }}
  .tag-orange {{ color: #FF9800; font-weight: 600; }}
  .tag-red {{ color: #F44336; font-weight: 600; }}
  .task-row {{ display: flex; align-items: center; justify-content: space-between; padding: 8px 0; border-bottom: 1px solid #f8f8f8; font-size: 13px; }}
  .task-date {{ color: #999; font-size: 12px; min-width: 80px; }}
  .task-subject {{ color: #667eea; font-weight: 500; }}
  .task-detail {{ color: #444; flex: 1; margin: 0 12px; text-align: left; }}
  .task-status-done {{ color: #4CAF50; font-size: 16px; }}
  .task-status-miss {{ color: #ddd; font-size: 16px; }}
</style>
</head>
<body>
<div class="container">

  <div class="header">
    <h1>📊 {report_title}</h1>
    <p>{start_date} &nbsp;—&nbsp; {end_date}</p>
    <div class="grade-badge">{grade}</div>
  </div>

  <div class="card">
    <div class="section-title">总览</div>
    <div class="progress-bar">
      <div class="progress-fill" style="width:{total_rate}%"></div>
    </div>
    <div class="progress-label">{total_rate}%</div>
    <div class="overview-grid">
      <div class="metric">
        <div class="metric-value">{total_completed}<span style="font-size:14px;color:#bbb">/{total_planned}</span></div>
        <div class="metric-label">完成任务</div>
      </div>
      <div class="metric">
        <div class="metric-value">{completed_hours}<span style="font-size:14px;color:#bbb">h</span></div>
        <div class="metric-label">学习时长</div>
      </div>
      <div class="metric">
        <div class="metric-value">{streak_days}<span style="font-size:14px;color:#bbb">天</span></div>
        <div class="metric-label">打卡天数</div>
      </div>
    </div>
  </div>

  <div class="card">
    <div class="section-title">每日进度</div>
    {daily_breakdown_html}
  </div>

  <div class="card">
    <div class="section-title">各科明细</div>
    <table>
      <thead>
        <tr><th>科目</th><th>计划</th><th>完成</th><th>完成率</th></tr>
      </thead>
      <tbody>
        {subject_rows}
      </tbody>
    </table>
  </div>

  <div class="card">
    <div class="section-title">已完成任务</div>
    {completed_tasks_html}
  </div>

  <div class="card">
    <div class="section-title">亮点 &amp; 待加强</div>
    <div class="two-col">
      <div>
        <div class="col-label" style="color:#4CAF50;">✅ 亮点</div>
        {highlights_html}
      </div>
      <div>
        <div class="col-label" style="color:#FF9800;">⚠️ 待加强</div>
        {issues_html}
      </div>
    </div>
  </div>

  <div class="card">
    <div class="section-title">小搭点评 🎙️</div>
    <div class="comment-text">{comment}</div>
  </div>

  <div class="card">
    <div class="section-title">后续建议 💡</div>
    {suggestions_html}
  </div>

</div>
</body>
</html>"""
