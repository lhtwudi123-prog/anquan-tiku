#!/usr/bin/env python3
"""
安管人员题库练习工具 - 做完一题立即显示答案
运行方式: python3 anquan_tiku.py
然后在浏览器打开 http://localhost:8765
"""

import json
import re
import urllib.request
import urllib.parse
from http.server import HTTPServer, BaseHTTPRequestHandler

REAL_HOST = "http://px.hebsjx.org.cn"

# 所有试卷列表 (ID -> 名称)
PAPERS = {
    36: "考核模拟（新）——单选题（1）",
    37: "考核模拟（新）——单选题（2）",
    38: "考核模拟（新）——单选题（3）",
    39: "考核模拟（新）——单选题（4）",
    40: "考核模拟（新）——单选题（5）",
    41: "考核模拟（新）——单选题（6）",
    42: "考核模拟（新）——单选题（7）",
    43: "考核模拟（新）——单选题（8）",
    44: "考核模拟（新）——单选题（9）",
    45: "考核模拟（新）——单选题（10）",
    46: "考核模拟（新）——多选题（1）",
    47: "考核模拟（新）——多选题（2）",
    49: "考核模拟（新）——多选题（4）",
    50: "考核模拟（新）——多选题（5）",
    51: "考核模拟（新）——判断题（1）",
    53: "考核模拟（新）——判断题（2）",
    54: "考核模拟（新）——判断题（3）",
    55: "考核模拟（新）——判断题（4）",
    56: "考核模拟（新）——判断题（5）",
    57: "考核模拟（新）——判断题（6）",
}


def proxy_post(path, params):
    url = REAL_HOST + path
    data = urllib.parse.urlencode(params).encode()
    req = urllib.request.Request(url, data=data, method="POST")
    req.add_header("Content-Type", "application/x-www-form-urlencoded")
    req.add_header("User-Agent", "Mozilla/5.0")
    with urllib.request.urlopen(req, timeout=10) as resp:
        return resp.read()


def get_topic_ids(subject_id, exercise_type, paper_id=None, total=100):
    params = {"subjectId": subject_id, "total": total, "exerciseType": exercise_type}
    if paper_id:
        params["paperId"] = paper_id
    html = proxy_post("/tikuUserBatch/loadNoLogInTopicLeft", params).decode("utf-8", errors="replace")
    return re.findall(r'topicId="(\d+)"', html)


def get_topic_info(topic_id):
    data = proxy_post("/tikuUserBatch/loadTopicInfo", {"topicId": topic_id})
    return json.loads(data.decode("utf-8"))


HTML = r"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>安管人员题库练习</title>
<style>
* { box-sizing: border-box; margin: 0; padding: 0; }
body { font-family: "PingFang SC", "Microsoft YaHei", sans-serif; background: #f0f2f5; color: #333; min-height: 100vh; }

.header { background: #1a6fc4; color: #fff; padding: 16px 24px; font-size: 20px; font-weight: bold; }

.container { max-width: 1200px; margin: 24px auto; padding: 0 16px; }
.exam-layout { display: grid; grid-template-columns: 340px 1fr; gap: 16px; align-items: start; }
@media (max-width: 768px) {
  .exam-layout { grid-template-columns: 1fr; }
}

.card { background: #fff; border-radius: 12px; padding: 24px; box-shadow: 0 2px 8px rgba(0,0,0,.08); margin-bottom: 16px; }

/* 首页选择 */
.mode-list { display: grid; gap: 12px; }
.mode-btn { background: #f7f9fc; border: 2px solid #d0dce8; border-radius: 8px; padding: 14px 18px;
  cursor: pointer; text-align: left; font-size: 15px; transition: all .2s; }
.mode-btn:hover { border-color: #1a6fc4; background: #eaf2ff; }
.mode-btn .tag { font-size: 12px; background: #1a6fc4; color: #fff; border-radius: 4px; padding: 2px 6px; margin-right: 8px; }
.mode-btn .tag.green { background: #27ae60; }
.mode-btn .tag.orange { background: #e67e22; }

h2 { font-size: 17px; margin-bottom: 16px; color: #1a6fc4; }

/* 进度 */
.progress-bar { background: #e0e8f0; border-radius: 8px; height: 8px; overflow: hidden; margin-bottom: 8px; }
.progress-fill { background: #1a6fc4; height: 100%; transition: width .3s; }
.progress-text { font-size: 13px; color: #666; display: flex; justify-content: space-between; }
.score-badge { background: #1a6fc4; color: #fff; border-radius: 20px; padding: 4px 12px; font-size: 13px; }

/* 题目 */
.question-type { font-size: 12px; background: #eaf2ff; color: #1a6fc4; border-radius: 4px; padding: 2px 8px; display: inline-block; margin-bottom: 12px; }
.question-text { font-size: 17px; line-height: 1.7; margin-bottom: 20px; }

/* 选项 */
.options { display: grid; gap: 10px; }
.option { display: flex; align-items: flex-start; gap: 12px; border: 2px solid #d0dce8; border-radius: 8px;
  padding: 12px 16px; cursor: pointer; transition: all .2s; font-size: 15px; line-height: 1.5; }
.option:hover:not(.disabled) { border-color: #1a6fc4; background: #eaf2ff; }
.option .letter { flex-shrink: 0; width: 28px; height: 28px; border-radius: 50%; border: 2px solid #aab;
  display: flex; align-items: center; justify-content: center; font-weight: bold; font-size: 13px; }

.option.selected { border-color: #1a6fc4; background: #eaf2ff; }
.option.selected .letter { background: #1a6fc4; color: #fff; border-color: #1a6fc4; }

.option.correct { border-color: #27ae60; background: #eafaf1; }
.option.correct .letter { background: #27ae60; color: #fff; border-color: #27ae60; }

.option.wrong { border-color: #e74c3c; background: #fdedec; }
.option.wrong .letter { background: #e74c3c; color: #fff; border-color: #e74c3c; }

.option.disabled { cursor: not-allowed; }

/* 判断题 */
.tf-options { display: flex; gap: 12px; }
.tf-btn { flex: 1; padding: 14px; border: 2px solid #d0dce8; border-radius: 8px;
  cursor: pointer; font-size: 16px; text-align: center; transition: all .2s; }
.tf-btn:hover:not(.disabled) { border-color: #1a6fc4; background: #eaf2ff; }
.tf-btn.selected { border-color: #1a6fc4; background: #eaf2ff; font-weight: bold; }
.tf-btn.correct { border-color: #27ae60; background: #eafaf1; color: #27ae60; font-weight: bold; }
.tf-btn.wrong { border-color: #e74c3c; background: #fdedec; color: #e74c3c; font-weight: bold; }
.tf-btn.disabled { cursor: not-allowed; }

/* 多选提交按钮 */
.submit-multi { display: none; margin-top: 14px; padding: 10px 24px; background: #1a6fc4; color: #fff;
  border: none; border-radius: 8px; font-size: 15px; cursor: pointer; }
.submit-multi:hover { background: #155fa0; }

/* 结果提示 */
.result-box { display: none; margin-top: 16px; padding: 14px 16px; border-radius: 8px; font-size: 15px; }
.result-box.correct { background: #eafaf1; border: 1px solid #82e0aa; color: #1e8449; }
.result-box.wrong { background: #fdedec; border: 1px solid #f1948a; color: #c0392b; }
.result-icon { font-size: 20px; margin-right: 8px; }

/* 解析 */
.analysis-box { margin-top: 12px; padding: 14px 16px; background: #fffbe6; border: 1px solid #ffe58f;
  border-radius: 8px; font-size: 14px; line-height: 1.7; display: none; }
.analysis-box .label { font-weight: bold; color: #b7791f; margin-bottom: 6px; }

/* 下一题 */
.next-btn { display: none; margin-top: 16px; width: 100%; padding: 14px; background: #1a6fc4; color: #fff;
  border: none; border-radius: 8px; font-size: 16px; cursor: pointer; font-weight: bold; }
.next-btn:hover { background: #155fa0; }

/* 结果页 */
.result-page { text-align: center; }
.big-score { font-size: 56px; font-weight: bold; color: #1a6fc4; margin: 20px 0; }
.result-stats { display: flex; justify-content: center; gap: 32px; margin: 16px 0; font-size: 15px; }
.stat-item { text-align: center; }
.stat-num { font-size: 28px; font-weight: bold; }
.stat-num.green { color: #27ae60; }
.stat-num.red { color: #e74c3c; }
.restart-btn { margin-top: 20px; padding: 12px 32px; background: #1a6fc4; color: #fff;
  border: none; border-radius: 8px; font-size: 16px; cursor: pointer; }
.restart-btn:hover { background: #155fa0; }

.loading { text-align: center; color: #888; padding: 40px; font-size: 16px; }

/* 多选提示 */
.multi-hint { font-size: 13px; color: #888; margin-bottom: 12px; }

/* 答题卡侧栏 */
.sidebar-title { font-size: 14px; color: #444; text-align: center; margin-bottom: 14px; }
.sidebar-title b { color: #1a6fc4; }
.legend { display: flex; gap: 18px; justify-content: center; margin-bottom: 16px;
  padding-bottom: 14px; border-bottom: 1px solid #eef1f5; flex-wrap: wrap; font-size: 13px; color: #888; }
.legend .item { display: flex; align-items: center; gap: 6px; }
.legend .num { display: inline-flex; width: 26px; height: 26px; border-radius: 4px;
  border: 1.5px solid #d8dde3; align-items: center; justify-content: center; font-size: 12px; color: #888; }
.legend .num.cur { border-color: #1a6fc4; color: #1a6fc4; font-weight: bold; }
.legend .num.ok { border-color: #27ae60; color: #fff; background: #27ae60; }
.legend .num.bad { border-color: #e74c3c; color: #fff; background: #e74c3c; }
.section-tag { display: inline-block; background: #1a6fc4; color: #fff; padding: 6px 14px;
  border-radius: 6px; font-size: 13px; margin-bottom: 12px; }
.nav-grid { display: grid; grid-template-columns: repeat(7, 1fr); gap: 8px; }
.nav-cell { aspect-ratio: 1; display: flex; align-items: center; justify-content: center;
  border: 1.5px solid #d8dde3; border-radius: 4px; font-size: 13px; cursor: pointer;
  background: #fff; color: #888; transition: all .15s; user-select: none; }
.nav-cell:hover { border-color: #1a6fc4; }
.nav-cell.correct { background: #27ae60; color: #fff; border-color: #27ae60; }
.nav-cell.wrong { background: #e74c3c; color: #fff; border-color: #e74c3c; }
.nav-cell.current { border-color: #1a6fc4; color: #1a6fc4; font-weight: bold; }
.nav-cell.current.correct, .nav-cell.current.wrong { color: #fff; box-shadow: 0 0 0 2px #1a6fc4; }
.sidebar-actions { margin-top: 16px; padding-top: 14px; border-top: 1px solid #eef1f5;
  display: flex; gap: 8px; }
.sidebar-actions button { flex: 1; padding: 9px; border-radius: 6px; border: 1px solid #1a6fc4;
  background: #fff; color: #1a6fc4; cursor: pointer; font-size: 13px; }
.sidebar-actions button:hover { background: #eaf2ff; }
.redo-btn { margin-top: 10px; padding: 8px 14px; background: #fff; color: #1a6fc4;
  border: 1px solid #1a6fc4; border-radius: 6px; cursor: pointer; font-size: 13px; }
.redo-btn:hover { background: #eaf2ff; }

/* 错题本 */
.mode-btn .tag.red { background: #e74c3c; }
.wrong-actions { display: flex; gap: 10px; margin-top: 12px; flex-wrap: wrap; }
.wrong-actions button { flex: 1; min-width: 120px; padding: 10px; border-radius: 8px; border: 1px solid #d0dce8;
  background: #fff; cursor: pointer; font-size: 14px; }
.wrong-actions button:hover { border-color: #1a6fc4; color: #1a6fc4; }
.wrong-actions .danger { color: #e74c3c; border-color: #f5b7b1; }
.wrong-actions .danger:hover { background: #fdedec; border-color: #e74c3c; }
.empty-tip { text-align: center; color: #888; padding: 30px; font-size: 15px; }
.remove-wrong-btn { margin-top: 10px; padding: 8px 14px; background: #fff; color: #e74c3c;
  border: 1px solid #f5b7b1; border-radius: 6px; cursor: pointer; font-size: 13px; }
.remove-wrong-btn:hover { background: #fdedec; }
</style>
</head>
<body>
<div class="header">安管人员题库练习</div>
<div class="container" id="app"></div>

<script>
const PAPERS = """ + json.dumps({str(k): v for k, v in PAPERS.items()}, ensure_ascii=False) + r""";

let topicIds = [];
let currentIdx = 0;
let currentTopic = null;
let correctCount = 0;
let wrongCount = 0;
let selectedAnswers = [];
let practiceMode = 'normal'; // 'normal' or 'wrong'
let wrongQueue = []; // 错题本模式下使用的完整题目数据数组
let answerStatus = []; // 每题状态：{userAnswer, isCorrect} 或 undefined
let topicCache = []; // 每题完整数据缓存，跳转时无需重新请求

function resetSession() {
  currentIdx = 0; correctCount = 0; wrongCount = 0;
  answerStatus = []; topicCache = [];
}
function recomputeCounts() {
  correctCount = 0; wrongCount = 0;
  for (const s of answerStatus) {
    if (!s) continue;
    if (s.isCorrect) correctCount++; else wrongCount++;
  }
}

const WRONG_KEY = 'anquan_wrong_questions_v1';
function getWrongList() {
  try { return JSON.parse(localStorage.getItem(WRONG_KEY) || '[]'); }
  catch (e) { return []; }
}
function setWrongList(list) {
  localStorage.setItem(WRONG_KEY, JSON.stringify(list));
}
function addWrong(topicData, tid) {
  const list = getWrongList();
  const key = String(tid);
  if (list.some(x => String(x._tid) === key)) return;
  list.push({ _tid: key, topic: topicData.topic, option: topicData.option || [], _addedAt: Date.now() });
  setWrongList(list);
}
function removeWrong(topicId) {
  const key = String(topicId);
  setWrongList(getWrongList().filter(x => String(x._tid) !== key));
}

function render(html) {
  document.getElementById('app').innerHTML = html;
}

function showHome() {
  topicIds = []; wrongQueue = []; resetSession();
  practiceMode = 'normal';
  const wrongCountTotal = getWrongList().length;
  let paperOptions = Object.entries(PAPERS).map(([id, name]) =>
    `<button class="mode-btn" onclick="startPaper(${id})">
      <span class="tag orange">试卷</span>${name}
    </button>`
  ).join('');

  render(`
    <div class="card">
      <h2>选择练习模式</h2>
      <div class="mode-list">
        <button class="mode-btn" onclick="startRandom()">
          <span class="tag green">随机</span>随机练习 15 题（无需登录）
        </button>
        <button class="mode-btn" onclick="startWrongBook()">
          <span class="tag red">错题</span>错题本练习（${wrongCountTotal} 题）
        </button>
      </div>
      ${wrongCountTotal > 0 ? `
        <div class="wrong-actions">
          <button class="danger" onclick="clearWrongBook()">清空错题本</button>
        </div>` : ''}
    </div>
    <div class="card">
      <h2>按试卷练习</h2>
      <div class="mode-list">${paperOptions}</div>
    </div>
  `);
}

function startWrongBook() {
  const list = getWrongList();
  if (list.length === 0) {
    alert('错题本为空，先去刷几道题吧！');
    return;
  }
  practiceMode = 'wrong';
  wrongQueue = list.slice();
  topicIds = wrongQueue.map(x => x._tid);
  resetSession();
  // 错题本模式预填缓存（题目数据已经存在 localStorage 里）
  topicCache = wrongQueue.map(x => ({ topic: x.topic, option: x.option }));
  loadQuestion();
}

function clearWrongBook() {
  if (!confirm('确定清空全部错题吗？此操作无法撤销。')) return;
  setWrongList([]);
  showHome();
}

async function startRandom() {
  practiceMode = 'normal'; wrongQueue = [];
  render('<div class="loading">加载题目中...</div>');
  const resp = await fetch('/api/topics?exerciseType=EXERCISE_TYPE_15&subjectId=19&total=15');
  topicIds = await resp.json();
  resetSession();
  loadQuestion();
}

async function startPaper(paperId) {
  practiceMode = 'normal'; wrongQueue = [];
  render('<div class="loading">加载题目中...</div>');
  const resp = await fetch(`/api/topics?exerciseType=EXERCISE_TYPE_PAPER&subjectId=19&total=200&paperId=${paperId}`);
  topicIds = await resp.json();
  resetSession();
  loadQuestion();
}

async function loadQuestion() {
  if (currentIdx >= topicIds.length) { showResult(); return; }
  selectedAnswers = [];
  // 优先使用缓存（错题本模式或已访问过的题）
  if (topicCache[currentIdx]) {
    currentTopic = topicCache[currentIdx];
    renderQuestion();
    return;
  }
  render('<div class="loading">加载题目中...</div>');
  const resp = await fetch('/api/topic-info?topicId=' + topicIds[currentIdx]);
  currentTopic = await resp.json();
  topicCache[currentIdx] = currentTopic;
  renderQuestion();
}

function jumpTo(idx) {
  if (idx < 0 || idx >= topicIds.length) return;
  currentIdx = idx;
  loadQuestion();
}

function renderQuestion() {
  const t = currentTopic.topic;
  const opts = currentTopic.option || [];
  const total = topicIds.length;
  const pct = Math.round((currentIdx / total) * 100);

  const typeMap = {
    'TOPIC_TYPE_RADIO': '单选题',
    'TOPIC_TYPE_MULTI': '多选题',
    'TOPIC_TYPE_TRUEFALSE': '判断题',
    'TOPIC_TYPE_ANSWER': '简答题',
    'TOPIC_TYPE_FILLING': '填空题',
  };
  const typeName = typeMap[t.topicType] || t.topicType;
  const isMulti = t.topicType === 'TOPIC_TYPE_MULTI';
  const isTF = t.topicType === 'TOPIC_TYPE_TRUEFALSE';

  let optionsHtml = '';
  if (isTF) {
    optionsHtml = `
      <div class="tf-options">
        <div class="tf-btn" id="tf-A" onclick="selectTF('A')">✔ 正确</div>
        <div class="tf-btn" id="tf-B" onclick="selectTF('B')">✘ 错误</div>
      </div>`;
  } else {
    optionsHtml = `<div class="options">` +
      opts.map(o => `
        <div class="option" id="opt-${o.optionNo}" onclick="selectOption('${o.optionNo}')">
          <div class="letter">${o.optionNo}</div>
          <div>${o.optionName}</div>
        </div>`).join('') +
      `</div>`;
  }

  const multiHint = isMulti ? '<div class="multi-hint">（多选题，请选择所有正确答案，然后点击"确认提交"）</div>' : '';
  const multiBtn = isMulti ? '<button class="submit-multi" id="submitMultiBtn" onclick="submitMulti()">确认提交</button>' : '';

  // 题号网格
  let gridHtml = '';
  for (let i = 0; i < total; i++) {
    let cls = 'nav-cell';
    const s = answerStatus[i];
    if (s) cls += s.isCorrect ? ' correct' : ' wrong';
    if (i === currentIdx) cls += ' current';
    gridHtml += `<div class="${cls}" onclick="jumpTo(${i})">${i+1}</div>`;
  }
  const doneCount = correctCount + wrongCount;

  render(`
    <div class="exam-layout">
      <div class="card">
        <div class="sidebar-title">共 <b>${total}</b> 题，已答 <b>${doneCount}</b> 题</div>
        <div class="legend">
          <div class="item"><span class="num cur">${currentIdx+1}</span>当前</div>
          <div class="item"><span class="num ok">✓</span>正确 ${correctCount}</div>
          <div class="item"><span class="num bad">✗</span>错误 ${wrongCount}</div>
        </div>
        <div class="section-tag">${typeName}（${total}题）</div>
        <div class="nav-grid">${gridHtml}</div>
        <div class="sidebar-actions">
          <button onclick="showResult()">查看成绩</button>
          <button onclick="showHome()">返回首页</button>
        </div>
      </div>
      <div class="card">
        <div class="progress-bar"><div class="progress-fill" style="width:${pct}%"></div></div>
        <div class="progress-text" style="margin-bottom:16px;">
          <span>第 ${currentIdx+1} / ${total} 题</span>
          <span class="score-badge">✓ ${correctCount} &nbsp; ✗ ${wrongCount}</span>
        </div>
        <div class="question-type">${typeName}</div>
        <div class="question-text">${currentIdx+1}. ${t.topicName}</div>
        ${multiHint}
        ${optionsHtml}
        ${multiBtn}
        <div class="result-box" id="resultBox"></div>
        <div class="analysis-box" id="analysisBox">
          <div class="label">解析</div>
          <div id="analysisText"></div>
        </div>
        <div style="display:flex; gap:10px; margin-top:16px;">
          <button class="next-btn" style="flex:1; margin-top:0; display:${currentIdx > 0 ? 'block' : 'none'}; background:#fff; color:#1a6fc4; border:1px solid #1a6fc4;" onclick="prevQuestion()">← 上一题</button>
          <button class="next-btn" id="nextBtn" style="flex:2; margin-top:0; display:block;" onclick="nextQuestion()">
            ${currentIdx + 1 < total ? '下一题 →' : '查看成绩'}
          </button>
        </div>
      </div>
    </div>
  `);

  // 如果这题已答过，重放结果（锁定状态）
  if (answerStatus[currentIdx]) {
    replayAnswer();
  }
}

function replayAnswer() {
  const s = answerStatus[currentIdx];
  if (!s) return;
  showResultUI(s.userAnswer, s.isCorrect);
  // 加一个"重答此题"按钮
  const resultBox = document.getElementById('resultBox');
  if (resultBox) {
    resultBox.innerHTML += `<br><button class="redo-btn" onclick="redoCurrent()">重答此题</button>`;
  }
}

function redoCurrent() {
  answerStatus[currentIdx] = undefined;
  recomputeCounts();
  selectedAnswers = [];
  renderQuestion();
}

function selectOption(no) {
  const t = currentTopic.topic;
  const isMulti = t.topicType === 'TOPIC_TYPE_MULTI';

  if (document.getElementById('opt-' + no).classList.contains('disabled')) return;

  if (isMulti) {
    const el = document.getElementById('opt-' + no);
    const idx = selectedAnswers.indexOf(no);
    if (idx === -1) {
      selectedAnswers.push(no);
      el.classList.add('selected');
    } else {
      selectedAnswers.splice(idx, 1);
      el.classList.remove('selected');
    }
    // Show submit button when at least one selected
    const btn = document.getElementById('submitMultiBtn');
    if (btn) btn.style.display = selectedAnswers.length > 0 ? 'inline-block' : 'none';
  } else {
    // Single select - answer immediately
    checkAnswer(no);
  }
}

function selectTF(no) {
  if (document.getElementById('tf-A').classList.contains('disabled')) return;
  checkAnswer(no);
}

function submitMulti() {
  if (selectedAnswers.length === 0) return;
  const userAnswer = selectedAnswers.slice().sort().join('');
  checkAnswer(userAnswer);
}

function checkAnswer(userAnswer) {
  const t = currentTopic.topic;
  const correctAnswer = t.answer;
  const userSorted = userAnswer.split('').sort().join('');
  const correctSorted = correctAnswer.split('').sort().join('');
  const isCorrect = userSorted === correctSorted;

  // 记录答题状态
  answerStatus[currentIdx] = { userAnswer, isCorrect };
  recomputeCounts();

  const curTid = topicIds[currentIdx];
  if (isCorrect) {
    if (practiceMode === 'wrong') removeWrong(curTid);
  } else {
    if (practiceMode === 'normal') addWrong(currentTopic, curTid);
  }

  // 重新渲染整个题目以同步侧边栏状态，再回放结果UI
  renderQuestion();
}

function showResultUI(userAnswer, isCorrect) {
  const t = currentTopic.topic;
  const opts = currentTopic.option || [];
  const correctAnswer = t.answer;
  const isTF = t.topicType === 'TOPIC_TYPE_TRUEFALSE';

  // Disable all options
  if (isTF) {
    ['A','B'].forEach(x => {
      const el = document.getElementById('tf-' + x);
      if (el) el.classList.add('disabled');
    });
    const userEl = document.getElementById('tf-' + userAnswer);
    const correctEl = document.getElementById('tf-' + correctAnswer);
    if (correctEl) correctEl.classList.add('correct');
    if (!isCorrect && userEl) userEl.classList.add('wrong');
  } else {
    opts.forEach(o => {
      const el = document.getElementById('opt-' + o.optionNo);
      if (!el) return;
      el.classList.add('disabled');
      el.onclick = null;
    });
    // Mark correct options green
    correctAnswer.split('').forEach(c => {
      const el = document.getElementById('opt-' + c);
      if (el) { el.classList.remove('selected'); el.classList.add('correct'); }
    });
    // Mark wrong selected options red
    userAnswer.split('').forEach(c => {
      if (correctAnswer.indexOf(c) === -1) {
        const el = document.getElementById('opt-' + c);
        if (el) { el.classList.remove('selected'); el.classList.add('wrong'); }
      }
    });
  }

  // Hide multi submit button
  const submitBtn = document.getElementById('submitMultiBtn');
  if (submitBtn) submitBtn.style.display = 'none';

  // Show result box
  const resultBox = document.getElementById('resultBox');
  if (resultBox) {
    resultBox.style.display = 'block';
    resultBox.className = 'result-box ' + (isCorrect ? 'correct' : 'wrong');
    const correctLabel = isTF
      ? (correctAnswer === 'A' ? '正确' : '错误')
      : correctAnswer;
    resultBox.innerHTML = isCorrect
      ? `<span class="result-icon">✓</span>回答正确！答案：<strong>${correctLabel}</strong>`
      : `<span class="result-icon">✗</span>回答错误！正确答案：<strong>${correctLabel}</strong>`;
  }

  // Show analysis
  if (t.analyseWord && t.analyseWord.trim()) {
    const analysisBox = document.getElementById('analysisBox');
    const analysisText = document.getElementById('analysisText');
    if (analysisBox && analysisText) {
      analysisBox.style.display = 'block';
      analysisText.innerHTML = t.analyseWord;
    }
  }

  // Show next button
  const nextBtn = document.getElementById('nextBtn');
  if (nextBtn) nextBtn.style.display = 'block';

  // 错题本模式：在结果框旁加一个"已掌握，移除"按钮
  if (practiceMode === 'wrong' && resultBox) {
    const tid = topicIds[currentIdx];
    resultBox.innerHTML += `<br><button class="remove-wrong-btn" onclick="markMastered('${tid}')">已掌握，从错题本移除</button>`;
  }
}

function markMastered(topicId) {
  removeWrong(topicId);
  const btn = event.target;
  btn.disabled = true;
  btn.textContent = '✓ 已移除';
  btn.style.color = '#27ae60';
  btn.style.borderColor = '#82e0aa';
}

function nextQuestion() {
  currentIdx++;
  loadQuestion();
}

function prevQuestion() {
  if (currentIdx > 0) { currentIdx--; loadQuestion(); }
}

function showResult() {
  const total = topicIds.length;
  const pct = total > 0 ? Math.round((correctCount / total) * 100) : 0;
  render(`
    <div class="card result-page">
      <h2>练习完成！</h2>
      <div class="big-score">${pct}%</div>
      <div class="result-stats">
        <div class="stat-item">
          <div class="stat-num green">${correctCount}</div>
          <div>正确</div>
        </div>
        <div class="stat-item">
          <div class="stat-num red">${wrongCount}</div>
          <div>错误</div>
        </div>
        <div class="stat-item">
          <div class="stat-num">${total}</div>
          <div>总计</div>
        </div>
      </div>
      <button class="restart-btn" onclick="showHome()">返回首页</button>
    </div>
  `);
}

showHome();
</script>
</body>
</html>
"""


class Handler(BaseHTTPRequestHandler):
    def log_message(self, fmt, *args):
        pass  # 静默日志

    def do_GET(self):
        if self.path == "/" or self.path == "/index.html":
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.end_headers()
            self.wfile.write(HTML.encode("utf-8"))

        elif self.path.startswith("/api/topics"):
            parsed = urllib.parse.urlparse(self.path)
            qs = urllib.parse.parse_qs(parsed.query)
            exercise_type = qs.get("exerciseType", ["EXERCISE_TYPE_15"])[0]
            subject_id = qs.get("subjectId", ["19"])[0]
            total = int(qs.get("total", ["200"])[0])
            paper_id = qs.get("paperId", [None])[0]
            try:
                ids = get_topic_ids(subject_id, exercise_type, paper_id, total)
                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self.end_headers()
                self.wfile.write(json.dumps(ids).encode())
            except Exception as e:
                self.send_response(500)
                self.end_headers()
                self.wfile.write(str(e).encode())

        elif self.path.startswith("/api/topic-info"):
            parsed = urllib.parse.urlparse(self.path)
            qs = urllib.parse.parse_qs(parsed.query)
            topic_id = qs.get("topicId", [None])[0]
            try:
                data = get_topic_info(topic_id)
                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self.end_headers()
                self.wfile.write(json.dumps(data, ensure_ascii=False).encode())
            except Exception as e:
                self.send_response(500)
                self.end_headers()
                self.wfile.write(str(e).encode())
        else:
            self.send_response(404)
            self.end_headers()


if __name__ == "__main__":
    import os, socket
    port = int(os.environ.get("PORT", 8765))
    server = HTTPServer(("0.0.0.0", port), Handler)
    # 本地运行时显示局域网地址
    if port == 8765:
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            local_ip = s.getsockname()[0]
            s.close()
        except Exception:
            local_ip = "127.0.0.1"
        print(f"✅ 题库练习工具已启动")
        print(f"👉 本机访问:  http://localhost:{port}")
        print(f"👉 手机访问:  http://{local_ip}:{port}  （手机需与电脑在同一 Wi-Fi）")
        print(f"   按 Ctrl+C 停止服务")
    else:
        print(f"✅ 服务已启动，端口 {port}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n已停止")
