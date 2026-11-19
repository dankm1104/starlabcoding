// 스타랩코딩학원 광진점 홈페이지 - 샘플클래스 신청 받기
// 사이트(sample.html)에서 보낸 신청을 '스타랩 통합관리' 구글 시트의 '명단Metadata'(상담인명부) 맨 아래에 한 줄 추가하고, 학원 메일로 알린다.
// 원장 구글 계정(script.google.com)의 프로젝트 "광진점 홈페이지 신청"에 붙여 넣어 웹앱으로 배포한다.
// 배포: 실행 계정 = 나, 액세스 = 모든 사용자. 배포 주소를 build.py의 FORM_ENDPOINT에 넣는다.

const TO = 'darren.kim@star-lab.co.kr';
const BOOK_ID = '1fF23hLKdMa_a9sF-ezPn4eOi_A1-5TSwjbKhlWgNoH0';   // 스타랩 통합관리
const TAB = '명단Metadata';
const REF_BOOK_ID = '1I1aI4I5FTgV6jH2TurtAYZt45jmIZKr-POmOguZE4t4';   // 스타랩 소개 링크 (원장 전용: 링크 값 | 소개한 분)
// 명단Metadata 열: 번호 | 학생이름 | 학생 나이(해당년도 기준, 세는 나이) | 전화 번호 | 날짜(9월 30일) | 접근 경로 | 특이사항
// 유입(2026-11-19 원장): 사이트가 방문 경로(p.src)를 같이 보내면 특이사항 끝에 '유입: …', 메일에 '유입 경로: …'로 적는다. 신청자가 적는 칸은 없다

function doPost(e) {
  const lock = LockService.getScriptLock();
  try {
    const p = JSON.parse((e && e.postData && e.postData.contents) || '{}');
    if (p.website) return out({ ok: true });            // 자동 등록 차단용 숨은 칸
    const v = {
      name: clip(p.name, 30), grade: clip(p.grade, 10), phone: clip(p.phone, 13),
      exp: clip(p.exp, 60), days: clip(p.days, 30), times: clip(p.times, 80), memo: clip(p.memo, 500),
      ref: String(p.ref || '').replace(/[^A-Za-z0-9_-]/g, '').slice(0, 20), refname: clip(p.refname, 40)
    };
    if (!v.name || !v.grade || !/^01\d-?\d{3,4}-?\d{4}$/.test(v.phone) || !p.agree || !p.confirm) {
      return out({ ok: false, error: 'invalid' });
    }
    v.refwho = who(v.ref);
    const now = new Date();
    const from = source(p.src, now);
    const date = Utilities.formatDate(now, 'Asia/Seoul', 'M월 d일');
    const note = ['홈페이지 샘플클래스 신청', v.grade, '경험: ' + v.exp, '가능 요일: ' + v.days, '희망 시간: ' + v.times]
      .concat(v.memo ? ['남기신 말씀: ' + v.memo] : []).concat(intro(v) ? ['소개: ' + intro(v)] : []).concat(from ? ['유입: ' + from] : []).join(', ');

    lock.waitLock(20000);
    const sh = SpreadsheetApp.openById(BOOK_ID).getSheetByName(TAB);
    sh.appendRow([nextNo(sh), v.name, age(v.grade), v.phone, date, '온라인문의', note]);
    lock.releaseLock();

    MailApp.sendEmail({
      to: TO,
      subject: '[홈페이지] ' + (intro(v) ? '소개 ' : '') + '샘플클래스 신청 - ' + v.name + ' (' + v.grade + ')',
      name: '스타랩 광진점 홈페이지',
      body: [
        '광진점 홈페이지로 샘플클래스 신청이 들어왔습니다.',
        '',
        '학생 이름: ' + v.name,
        '학년: ' + v.grade,
        '보호자 연락처: ' + v.phone,
        '코딩·로봇 경험: ' + v.exp,
        '가능한 요일: ' + v.days,
        '희망 시간대: ' + v.times,
        '남기신 말씀: ' + (v.memo || '-'),
        '소개해 주신 분: ' + (intro(v) || '-'),
        '유입 경로: ' + (from || '-'),
        '',
        '신청 시각: ' + Utilities.formatDate(now, 'Asia/Seoul', 'yyyy-MM-dd HH:mm'),
        '스타랩 통합관리 > 명단Metadata 맨 아래에 기록했습니다.'
      ].join('\n')
    });
    return out({ ok: true });
  } catch (err) {
    try { lock.releaseLock(); } catch (x) {}
    return out({ ok: false, error: 'server' });
  }
}

// 소개: 소개 링크로 왔으면 '소개한 분 (링크 값)', 직접 적었으면 적은 이름
function intro(v) {
  const link = v.ref ? (v.refwho ? v.refwho + ' (링크 ' + v.ref + ')' : '링크 ' + v.ref) : '';
  return [link, v.refname].filter(String).join(' / ');
}

// 링크 값 → 소개한 분. '스타랩 소개 링크' 시트 첫 탭의 A열(링크 값)·B열(소개한 분)에서 찾는다. 못 찾으면 빈칸
function who(ref) {
  if (!ref) return '';
  try {
    const rows = SpreadsheetApp.openById(REF_BOOK_ID).getSheets()[0].getDataRange().getValues();
    for (let i = 1; i < rows.length; i++) {
      if (String(rows[i][0]).trim().toLowerCase() === ref.toLowerCase()) return String(rows[i][1]).trim();
    }
  } catch (e) {}
  return '';
}

// 유입 경로: 사이트가 보낸 방문 기록을 읽기 쉬운 말로. l = 마지막으로 들어온 길, f = 처음 들어온 길(다를 때만 덧붙임).
// 사이트가 안 보냈으면(옛 화면) 빈칸, 보냈는데 길을 모르면 '확인 안 됨'. 신청한 날과 다른 날의 방문이면 날짜를 붙인다
function source(src, now) {
  if (!src || typeof src !== 'object') return '';
  const l = touch(src.l), f = touch(src.f);
  if (!l) return '확인 안 됨';
  let s = l.label + (l.unknown ? '' : when(l, now));
  if (f && !f.unknown && f.label !== l.label) s += ' / 첫 방문 ' + f.label + when(f, now);
  return s.slice(0, 200);
}

// 방문 기록 하나 → 이름. 주소 꼬리표(utm)가 있으면 그것, 없으면 직전 사이트, 없으면 앱 표시
function touch(t) {
  if (!t || typeof t !== 'object') return null;
  const s = tidy(t.s), h = tidy(t.h).toLowerCase(), a = tidy(t.a).toLowerCase();
  let label = '';
  if (s) {
    const tag = [s, tidy(t.m), tidy(t.c), tidy(t.n)].filter(String).join('/');
    const known = { 'daangn': '당근 광고', 'naver_blog': '네이버 블로그 버튼', 'chatgpt': '챗GPT 광고', 'chatgpt.com': '챗GPT' }[s.toLowerCase()];
    label = known ? known + ' [' + tag + ']' : '꼬리표 ' + tag;
  } else if (h) {
    label = site(h);
  } else if (a) {
    label = { kakaotalk: '카카오톡으로 받은 링크', naver: '네이버 앱', daum: '다음 앱', instagram: '인스타그램 앱', facebook: '페이스북 앱', daangn: '당근 앱' }[a] || '';
  }
  if (!label) return t.d ? { label: '확인 안 됨(주소 입력·문자 링크 등)', t: 0, unknown: true } : null;
  return { label: label, t: Number(t.t) || 0 };
}

// 직전 사이트 주소 → 이름
function site(h) {
  const rules = [
    [/(^|\.)gemini\.google\.com$/, '제미나이'], [/(^|\.)(chatgpt\.com|openai\.com)$/, '챗GPT'], [/(^|\.)perplexity\.ai$/, '퍼플렉시티'],
    [/(^|\.)claude\.ai$/, 'Claude'], [/(^|\.)copilot\.microsoft\.com$/, '코파일럿'],
    [/(^|\.)search\.naver\.com$/, '네이버 검색'], [/(^|\.)(place|map)\.naver\.com$/, '네이버 플레이스·지도'],
    [/(^|\.)blog\.naver\.com$/, '네이버 블로그'], [/(^|\.)cafe\.naver\.com$/, '네이버 카페'], [/(^|\.)naver\.com$/, '네이버'],
    [/(^|\.)google\.[a-z.]+$/, '구글 검색'], [/(^|\.)bing\.com$/, '빙 검색'], [/(^|\.)daum\.net$/, '다음'],
    [/(^|\.)map\.kakao\.com$/, '카카오맵'], [/(^|\.)kakao\.com$/, '카카오'],
    [/(^|\.)star-lab\.co\.kr$/, '스타랩 본사 홈페이지'], [/(^|\.)daangn\.com$/, '당근'],
    [/(^|\.)instagram\.com$/, '인스타그램'], [/(^|\.)facebook\.com$/, '페이스북'], [/(^|\.)threads\.(net|com)$/, '스레드'],
    [/(^|\.)(youtube\.com|youtu\.be)$/, '유튜브']
  ];
  for (let i = 0; i < rules.length; i++) if (rules[i][0].test(h)) return rules[i][1] + ' (' + h + ')';
  return h;
}

// 신청한 날과 다른 날에 들어온 길이면 ' (11/18 방문)'
function when(x, now) {
  if (!x.t) return '';
  const d = Utilities.formatDate(new Date(x.t), 'Asia/Seoul', 'M/d');
  return d === Utilities.formatDate(now, 'Asia/Seoul', 'M/d') ? '' : ' (' + d + ' 방문)';
}

// 사이트가 보낸 값 다듬기: 쉼표·줄바꿈은 빈칸으로, 60자까지
function tidy(x) { return String(x == null ? '' : x).replace(/[,\r\n]+/g, ' ').trim().slice(0, 60); }

// 학년 → 세는 나이 (7세=7, 초1=8 … 초6=13, 중1=14 … 중3=16). 명단Metadata 기존 기록과 같은 기준
function age(grade) {
  if (grade === '7세') return '7';
  const m = /^(초|중)(\d)$/.exec(grade);
  if (!m) return grade;
  return String(Number(m[2]) + (m[1] === '초' ? 7 : 13));
}

// 맨 아래 기록의 번호 + 1
function nextNo(sh) {
  const last = sh.getLastRow();
  const col = sh.getRange(Math.max(1, last - 30), 1, Math.min(31, last), 1).getValues();
  for (let i = col.length - 1; i >= 0; i--) {
    const n = Number(String(col[i][0]).trim());
    if (n > 0) return n + 1;
  }
  return '';
}

function clip(s, n) { return String(s || '').replace(/[\r\n]+/g, ' ').trim().slice(0, n); }
function out(o) { return ContentService.createTextOutput(JSON.stringify(o)).setMimeType(ContentService.MimeType.JSON); }

// 처음 한 번 실행: 권한 허용 확인 (시트에는 아무것도 쓰지 않음)
function setup() {
  const sh = SpreadsheetApp.openById(BOOK_ID).getSheetByName(TAB);
  Logger.log('명단Metadata 마지막 줄: ' + sh.getLastRow() + ', 다음 번호: ' + nextNo(sh));
  Logger.log('메일 남은 하루 발송량: ' + MailApp.getRemainingDailyQuota());
}
