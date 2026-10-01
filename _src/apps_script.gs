// 스타랩코딩학원 광진점 홈페이지 - 샘플클래스 신청 받기
// 사이트(sample.html)에서 보낸 신청을 '스타랩 통합관리' 구글 시트의 '명단Metadata'(상담인명부) 맨 아래에 한 줄 추가하고, 학원 메일로 알린다.
// 원장 구글 계정(script.google.com)의 프로젝트 "광진점 홈페이지 신청"에 붙여 넣어 웹앱으로 배포한다.
// 배포: 실행 계정 = 나, 액세스 = 모든 사용자. 배포 주소를 build.py의 FORM_ENDPOINT에 넣는다.

const TO = 'darren.kim@star-lab.co.kr';
const BOOK_ID = '1fF23hLKdMa_a9sF-ezPn4eOi_A1-5TSwjbKhlWgNoH0';   // 스타랩 통합관리
const TAB = '명단Metadata';
// 명단Metadata 열: 번호 | 학생이름 | 학생 나이(해당년도 기준, 세는 나이) | 전화 번호 | 날짜(9월 30일) | 접근 경로 | 특이사항

function doPost(e) {
  const lock = LockService.getScriptLock();
  try {
    const p = JSON.parse((e && e.postData && e.postData.contents) || '{}');
    if (p.website) return out({ ok: true });            // 자동 등록 차단용 숨은 칸
    const v = {
      name: clip(p.name, 30), grade: clip(p.grade, 10), phone: clip(p.phone, 13),
      exp: clip(p.exp, 60), days: clip(p.days, 30), times: clip(p.times, 80), memo: clip(p.memo, 500)
    };
    if (!v.name || !v.grade || !/^01\d-?\d{3,4}-?\d{4}$/.test(v.phone) || !p.agree || !p.confirm) {
      return out({ ok: false, error: 'invalid' });
    }
    const now = new Date();
    const date = Utilities.formatDate(now, 'Asia/Seoul', 'M월 d일');
    const note = ['홈페이지 샘플클래스 신청', v.grade, '경험: ' + v.exp, '가능 요일: ' + v.days, '희망 시간: ' + v.times]
      .concat(v.memo ? ['남기신 말씀: ' + v.memo] : []).join(', ');

    lock.waitLock(20000);
    const sh = SpreadsheetApp.openById(BOOK_ID).getSheetByName(TAB);
    sh.appendRow([nextNo(sh), v.name, age(v.grade), v.phone, date, '온라인문의', note]);
    lock.releaseLock();

    MailApp.sendEmail({
      to: TO,
      subject: '[홈페이지] 샘플클래스 신청 - ' + v.name + ' (' + v.grade + ')',
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
