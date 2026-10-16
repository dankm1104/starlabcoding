// 스타랩코딩학원 광진점 - 학원 등록카드 받기 (2026-10-16)
// 사이트 register.html에서 보낸 등록카드를
//   1) 서명 PDF로 만들어 원장 드라이브 '스타랩 등록서류/연도' 폴더에 저장하고
//   2) 원장 전용 시트 '스타랩 등록서류'에 한 줄 추가한 뒤
//   3) 학원 메일로 알린다 (메일에는 이름·학년만, 연락처·서명은 넣지 않는다)
// 원장 구글 계정의 프로젝트 "광진점 등록카드"에 붙여 넣고, setup()을 한 번 실행한 뒤 웹앱으로 배포한다.
// 배포: 실행 계정 = 나, 액세스 = 모든 사용자. 배포 주소를 build.py의 REG_ENDPOINT에 넣는다.
// 고칠 때: 코드 전체 교체 → 저장 → 배포 관리 → 연필 → 버전 '새 버전' → 배포 (주소 유지). 웹앱 주소를 열어 'alive (등록카드 v1)' 확인
// 동의 문구를 고치면 CONSENT_VER를 올리고 register.html의 문구·CONSENT_VER도 같이 고친다.

const TO = 'darren.kim@star-lab.co.kr';
const ROOT_NAME = '스타랩 등록서류';
const BOOK_NAME = '스타랩 등록서류';
const CONSENT_VER = 'v1';
const GRADES = ['6세', '7세', '초등1', '초등2', '초등3', '초등4', '초등5', '초등6', '중1', '중2', '중3', '고1', '고2', '고3'];
const HEAD = ['제출 시각', '문서 번호', '학생 이름', '생년월일', '성별', '학교', '학년', '학생 휴대폰', '주소',
  '보호자 이름', '관계', '보호자 휴대폰', '비상 연락처', '수강 반', '첫 등원일', '이전 학습 경험', '참고 사항',
  '알게 된 경로', '소개해 주신 분', '교습비 반환 기준', '개인정보 수집·이용', '동의 문구', 'PDF',
  '원장 확인', '원생 탭 반영', '퇴원일', '메모', '기기'];

function doGet() {
  return ContentService.createTextOutput('alive (등록카드 ' + CONSENT_VER + ')');
}

function doPost(e) {
  const lock = LockService.getScriptLock();
  let locked = false;
  try {
    const p = JSON.parse((e && e.postData && e.postData.contents) || '{}');
    if (p.website) return out({ ok: true });                 // 자동 등록 차단용 숨은 칸
    const v = clean(p);
    if (!v) return out({ ok: false, error: 'invalid' });

    const now = new Date();
    lock.waitLock(25000); locked = true;
    const props = PropertiesService.getScriptProperties();
    const sh = SpreadsheetApp.openById(props.getProperty('BOOK_ID')).getSheets()[0];
    const no = nextNo(sh, now);
    const folder = yearFolder(DriveApp.getFolderById(props.getProperty('ROOT_ID')), now);
    const base = Utilities.formatDate(now, 'Asia/Seoul', 'yyyy-MM-dd') + '_' + v.s_name.replace(/[\\/:*?"<>|]/g, '') + '_등록';
    const file = folder.createFile(makePdf(v, no, now)).setName(freeName(folder, base) + '.pdf');
    sh.appendRow([
      Utilities.formatDate(now, 'Asia/Seoul', 'yyyy-MM-dd HH:mm'), no, v.s_name, v.s_birth, v.s_sex, v.s_school, v.s_grade, v.s_phone, v.s_addr,
      v.p_name, v.p_rel, v.p_phone, v.p_phone2, v.c_class, v.c_first, v.c_before, v.c_note,
      v.src, v.ref, '확인', '동의', CONSENT_VER, file.getUrl(), '', '', '', '', v.ua
    ].map(x => /^[=+\-@]/.test(String(x)) ? "'" + x : x));   // 입력값이 시트 수식으로 실행되지 않게
    SpreadsheetApp.flush();
    lock.releaseLock(); locked = false;

    MailApp.sendEmail({
      to: TO,
      subject: '[등록카드] ' + v.s_name + ' (' + v.s_grade + ') 제출 - ' + no,
      name: '스타랩 광진점 등록카드',
      body: [
        '학원 등록카드가 제출되었습니다.',
        '',
        '학생: ' + v.s_name + ' (' + v.s_grade + ', ' + v.s_school + ')',
        '수강 반: ' + (v.c_class || '-'),
        '첫 등원일: ' + (v.c_first || '-'),
        '문서 번호: ' + no,
        '',
        '확인 후 원생 탭에 옮겨 주세요. 원장 전용 시트 \'' + BOOK_NAME + '\':',
        SpreadsheetApp.openById(props.getProperty('BOOK_ID')).getUrl()
      ].join('\n')
    });
    return out({ ok: true, no: no });
  } catch (err) {
    if (locked) { try { lock.releaseLock(); } catch (x) {} }
    console.error(err && err.stack || err);
    return out({ ok: false, error: 'server' });
  }
}

// 입력 정리·검사. 틀리면 null
function clean(p) {
  const s = (k, n) => String(p[k] || '').replace(/[\r\n]+/g, ' ').replace(/\s+/g, ' ').trim().slice(0, n);
  const t = (k, n) => String(p[k] || '').replace(/\r/g, '').trim().slice(0, n);
  const v = {
    s_name: s('s_name', 30), s_birth: birth(s('s_birth', 10)), s_sex: ['남', '여'].indexOf(s('s_sex', 2)) >= 0 ? s('s_sex', 2) : '',
    s_school: school(s('s_school', 40)), s_grade: s('s_grade', 5), s_phone: phone(s('s_phone', 13)), s_addr: s('s_addr', 60),
    p_name: s('p_name', 30), p_rel: s('p_rel', 15), p_phone: phone(s('p_phone', 13)), p_phone2: phone(s('p_phone2', 13)),
    c_class: s('c_class', 60), c_first: /^\d{4}-\d{2}-\d{2}$/.test(s('c_first', 10)) ? s('c_first', 10) : '',
    c_before: t('c_before', 500), c_note: t('c_note', 500), src: s('src', 200), ref: s('ref', 40),
    sig: String(p.sig || ''), ua: s('ua', 200)
  };
  const bad = !v.s_name || !v.s_birth || !v.s_school || GRADES.indexOf(v.s_grade) < 0 || !v.s_addr ||
    !v.p_name || !v.p_rel || !v.p_phone || (p.s_phone && !v.s_phone) || (p.p_phone2 && !v.p_phone2) ||
    p.a_refund !== true || p.a_privacy !== true ||
    !/^data:image\/png;base64,[A-Za-z0-9+/=]+$/.test(v.sig) || v.sig.length > 2000000;
  return bad ? null : v;
}

// 휴대폰: 숫자 11자리 → 010-1234-5678. 아니면 빈칸
function phone(x) {
  const d = String(x).replace(/\D/g, '');
  return /^01\d{9}$/.test(d) ? d.slice(0, 3) + '-' + d.slice(3, 7) + '-' + d.slice(7) : '';
}
// 생년월일: 20170512 / 2017-05-12 → 2017-05-12. 3~20세 범위가 아니면 빈칸
function birth(x) {
  const d = String(x).replace(/\D/g, '');
  if (!/^\d{8}$/.test(d)) return '';
  const y = +d.slice(0, 4), m = +d.slice(4, 6), dd = +d.slice(6, 8), dt = new Date(y, m - 1, dd), now = new Date().getFullYear();
  if (dt.getMonth() !== m - 1 || dt.getDate() !== dd || y < now - 20 || y > now - 3) return '';
  return d.slice(0, 4) + '-' + d.slice(4, 6) + '-' + d.slice(6, 8);
}
// 학교: ○○초등학교→○○초, ○○중학교→○○중, ○○고등학교→○○고 (여자중·고→여중·여고, 초교→초). 규칙에 안 맞으면 그대로
function school(x) {
  const m = x.replace(/\s/g, '');
  const rules = [[/여자고등학교$/, '여고'], [/여자중학교$/, '여중'], [/고등학교$/, '고'], [/중학교$/, '중'], [/초등학교$/, '초'], [/초교$/, '초']];
  for (const [re, r] of rules) if (re.test(m)) return m.replace(re, r);
  return x;
}

// 문서 번호: REG-20261016-01 (그날 순번)
function nextNo(sh, now) {
  const pre = 'REG-' + Utilities.formatDate(now, 'Asia/Seoul', 'yyyyMMdd') + '-';
  const last = sh.getLastRow();
  let max = 0;
  if (last >= 2) {
    const n = Math.min(200, last - 1);
    sh.getRange(last - n + 1, 2, n, 1).getValues().forEach(r => {
      const s = String(r[0]);
      if (s.indexOf(pre) === 0) max = Math.max(max, Number(s.slice(pre.length)) || 0);
    });
  }
  return pre + String(max + 1).padStart(2, '0');
}

function yearFolder(root, now) {
  const y = Utilities.formatDate(now, 'Asia/Seoul', 'yyyy');
  const it = root.getFoldersByName(y);
  return it.hasNext() ? it.next() : root.createFolder(y);
}
function freeName(folder, base) {
  let name = base, i = 2;
  while (folder.getFilesByName(name + '.pdf').hasNext()) name = base + '_' + (i++);
  return name;
}

function esc(s) { return String(s == null ? '' : s).replace(/[&<>"]/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c])); }
function out(o) { return ContentService.createTextOutput(JSON.stringify(o)).setMimeType(ContentService.MimeType.JSON); }

// 서명 PDF (보관용). 구글 문서로 짠 뒤 PDF로 내보내고 임시 문서는 휴지통으로 보낸다.
// (HTML→PDF 변환은 글꼴을 고를 수 없어 Arial Unicode로 나온다. 구글 문서는 구글 폰트를 그대로 쓴다)
// 1쪽: 등록카드와 서명, 2쪽: 동의한 문구 전문
const FONT = 'IBM Plex Sans KR';
const C = { ink: '#222226', sub: '#6D6E72', line: '#CFCFD4', head: '#F4F4F6', brand: '#F7941E', ok: '#15803D' };

function makePdf(v, no, now) {
  const doc = DocumentApp.create('등록카드 임시 ' + no);
  const id = doc.getId();
  try {
    const b = doc.getBody();
    b.setPageWidth(595.28).setPageHeight(841.89).setMarginTop(40).setMarginBottom(40).setMarginLeft(48).setMarginRight(48);
    const stamp = Utilities.formatDate(now, 'Asia/Seoul', 'yyyy-MM-dd HH:mm');

    // 머리: 로고 + 제목 | 문서 번호·제출 시각
    const top = b.appendTable([['', '문서 번호 ' + no + '\n제출 ' + stamp + ' · 동의 문구 ' + CONSENT_VER]]);
    top.setBorderWidth(0);
    const t0 = top.getCell(0, 0).clear(), p0 = t0.getChild(0).asParagraph();
    p0.appendInlineImage(png(LOGO)).setHeight(26).setWidth(51);
    p0.appendText('  학원 등록카드').setFontSize(17).setBold(true).setForegroundColor(C.ink);
    const t1 = top.getCell(0, 1);
    t1.getChild(0).asParagraph().setAlignment(DocumentApp.HorizontalAlignment.RIGHT);
    t1.editAsText().setFontSize(8).setForegroundColor(C.sub);
    rule(b);

    const kv = (title, rows) => {
      label(b, title);
      const t = b.appendTable(rows.map(r => [r[0], r[1] === '' || r[1] == null ? '—' : String(r[1])]));
      grid(t); t.setColumnWidth(0, 118);
      for (let i = 0; i < t.getNumRows(); i++) t.getCell(i, 0).setBackgroundColor(C.head).editAsText().setBold(true);
      return t;
    };
    kv('학생', [['이름', v.s_name], ['생년월일', v.s_birth], ['성별', v.s_sex], ['학교·학년', v.s_school + ' · ' + v.s_grade], ['학생 휴대폰', v.s_phone], ['주소', v.s_addr]]);
    kv('보호자', [['이름·관계', v.p_name + ' · ' + v.p_rel], ['휴대폰', v.p_phone], ['비상 연락처', v.p_phone2]]);
    kv('수강', [['수강 반', v.c_class], ['첫 등원일', v.c_first], ['이전 학습 경험', v.c_before], ['참고 사항', v.c_note], ['알게 된 경로', v.src], ['소개해 주신 분', v.ref]]);
    const agree = kv('안내 확인과 동의', [['교습비 반환 기준', '확인 · 학원법 시행령 별표 4, 교재비 제외'], ['개인정보 수집·이용', '동의 · 수업 사진·영상 공유와 홍보 사용, 소식·이벤트 안내, CCTV 촬영 포함']]);
    for (let i = 0; i < 2; i++) agree.getCell(i, 1).editAsText().setForegroundColor(0, 1, C.ok).setBold(0, 1, true);

    // 서명
    const sig = b.appendTable([['보호자 ' + v.p_name + ' (서명)', '']]);
    sig.setBorderWidth(0); sig.setColumnWidth(1, 190);
    sig.getCell(0, 0).getChild(0).asParagraph().setAlignment(DocumentApp.HorizontalAlignment.RIGHT);
    sig.getCell(0, 0).setVerticalAlignment(DocumentApp.VerticalAlignment.CENTER);
    const img = sig.getCell(0, 1).getChild(0).asParagraph().appendInlineImage(png(v.sig.split(',')[1]));
    const w = 180; img.setHeight(Math.round(img.getHeight() * w / img.getWidth())).setWidth(w);
    b.appendParagraph('');

    // 2쪽: 동의한 문구
    b.appendPageBreak();
    label(b, '동의한 문구 (' + CONSENT_VER + ')');
    para(b, '[필수] 교습비 반환 기준', true);
    para(b, '학원법 시행령 별표 4 기준으로 아래와 같이 적용됩니다.');
    const rt = b.appendTable([
      ['구분', '반환 사유 발생 시점', '반환 금액'],
      ['학원 사정으로 교습 불가', '교습할 수 없게 된 날', '일할 계산'],
      ['교습 시작 전', '', '전액'],
      ['교습기간 1개월 이내', '총 교습시간 1/3 경과 전', '2/3'],
      ['', '총 교습시간 1/2 경과 전', '1/2'],
      ['', '총 교습시간 1/2 경과 후', '반환 없음'],
      ['교습기간 1개월 초과', '반환 사유가 발생한 달', '1개월 이내 기준'],
      ['', '나머지 달', '전액']]);
    grid(rt);
    for (let j = 0; j < 3; j++) rt.getCell(0, j).setBackgroundColor(C.head).editAsText().setBold(true);
    para(b, '교재비는 반환 대상이 아닙니다.', false, 8.5, C.sub);
    b.appendParagraph('');
    para(b, '[필수] 개인정보 수집·이용', true);
    const pt = b.appendTable([
      ['수집 항목', '학생: 이름, 생년월일, 성별, 학교, 학년, 주소(동까지), 휴대폰(선택)\n보호자: 이름, 관계, 휴대폰, 비상 연락처(선택)\n수업 사진·영상, 학원 내 CCTV 영상'],
      ['이용 목적', '수강 관리, 출결 연락, 교습비 청구\n수업 사진·영상 보호자 공유\n학원 홍보(홈페이지·블로그·SNS)에 수업 사진·영상 사용\n학원 소식·이벤트 안내(문자·카카오톡)\n시설 안전과 원생 보호(학원 내 CCTV 촬영)'],
      ['보관 기간', '퇴원 후 3년 / CCTV 영상 30일']]);
    grid(pt); pt.setColumnWidth(0, 90);
    for (let i = 0; i < 3; i++) pt.getCell(i, 0).setBackgroundColor(C.head).editAsText().setBold(true);
    para(b, '만 14세 미만 학생의 개인정보는 보호자 동의로 처리합니다. 동의를 거부할 수 있으며, 거부 시 등록이 불가합니다.', false, 8.5, C.sub);
    b.appendParagraph('');
    para(b, '스타랩코딩학원 광진점 · 서울 광진구 광나루로 602 대한빌딩 201호 · 02-444-1854', false, 8, C.sub);

    // 맨 앞 빈 문단 지우고, 전체 글꼴
    const first = b.getChild(0);
    try { if (first.getType() === DocumentApp.ElementType.PARAGRAPH && first.asParagraph().getText() === '') first.removeFromParent(); } catch (e) {}
    font(b);
    doc.saveAndClose();
    return DriveApp.getFileById(id).getAs(MimeType.PDF);
  } finally {
    try { DriveApp.getFileById(id).setTrashed(true); } catch (e) {}
  }
}

function png(b64) { return Utilities.newBlob(Utilities.base64Decode(b64), 'image/png', 'img.png'); }
function label(b, s) {
  const p = b.appendParagraph(s);
  p.setSpacingBefore(10).setSpacingAfter(3);
  p.editAsText().setFontSize(9.5).setBold(true).setForegroundColor(C.sub);
}
function para(b, s, bold, size, color) {
  const p = b.appendParagraph(s);
  p.setSpacingBefore(2).setSpacingAfter(2);
  p.editAsText().setFontSize(size || 10).setBold(!!bold).setForegroundColor(color || C.ink);
  return p;
}
function rule(b) {
  const p = b.appendParagraph('');
  p.setSpacingBefore(0).setSpacingAfter(0);
  b.appendHorizontalRule();
}
function grid(t) {
  t.setBorderColor(C.line).setBorderWidth(0.75);
  for (let i = 0; i < t.getNumRows(); i++) {
    const r = t.getRow(i);
    for (let j = 0; j < r.getNumCells(); j++) {
      r.getCell(j).setPaddingTop(3).setPaddingBottom(3).setPaddingLeft(6).setPaddingRight(6)
        .editAsText().setFontSize(9.5).setForegroundColor(C.ink);
    }
  }
}
// 표 안까지 모든 글자에 같은 글꼴
function font(el) {
  const t = el.getType();
  if (t === DocumentApp.ElementType.TEXT) { el.asText().setFontFamily(FONT); return; }
  if (el.getNumChildren) for (let i = 0; i < el.getNumChildren(); i++) font(el.getChild(i));
}

// 글꼴 시험: 예시 값으로 PDF를 만들어 '스타랩 등록서류' 폴더에 '글꼴 시험 (지워도 됨).pdf'로 저장
function testPdf() {
  const v = { s_name: '홍길동', s_birth: '2017-05-12', s_sex: '남', s_school: '구의초', s_grade: '초등3', s_phone: '', s_addr: '광진구 구의1동',
    p_name: '홍길순', p_rel: '어머니', p_phone: '010-1234-5678', p_phone2: '', c_class: '토-11시30-로봇코딩3', c_first: '2026-10-17',
    c_before: '스크래치 6개월', c_note: '', src: '지인 소개', ref: '', sig: 'data:image/png;base64,' + LOGO };
  const root = DriveApp.getFolderById(PropertiesService.getScriptProperties().getProperty('ROOT_ID'));
  const f = root.createFile(makePdf(v, 'REG-TEST-00', new Date())).setName('글꼴 시험 (지워도 됨).pdf');
  Logger.log(f.getUrl());
}

// 처음 한 번 실행: 드라이브 폴더와 원장 전용 시트를 만들고(이미 있으면 그대로 쓴다), 권한을 허용한다
function setup() {
  const props = PropertiesService.getScriptProperties();
  let root = null;
  if (props.getProperty('ROOT_ID')) { try { root = DriveApp.getFolderById(props.getProperty('ROOT_ID')); } catch (e) {} }
  if (!root) {
    const it = DriveApp.getRootFolder().getFoldersByName(ROOT_NAME);
    root = it.hasNext() ? it.next() : DriveApp.getRootFolder().createFolder(ROOT_NAME);
  }
  ['퇴원', '파기 대기'].forEach(n => { if (!root.getFoldersByName(n).hasNext()) root.createFolder(n); });
  yearFolder(root, new Date());

  let book = null;
  if (props.getProperty('BOOK_ID')) { try { book = SpreadsheetApp.openById(props.getProperty('BOOK_ID')); } catch (e) {} }
  if (!book) {
    book = SpreadsheetApp.create(BOOK_NAME);
    DriveApp.getFileById(book.getId()).moveTo(root);
  }
  const sh = book.getSheets()[0];
  sh.setName('등록카드');
  sh.getRange(1, 1, sh.getMaxRows(), HEAD.length).setNumberFormat('@');   // 전화번호·날짜가 숫자로 바뀌지 않게 전부 글자로
  sh.getRange(1, 1, 1, HEAD.length).setValues([HEAD]).setFontWeight('bold').setBackground('#FEF1E2');
  sh.setFrozenRows(1);
  props.setProperties({ ROOT_ID: root.getId(), BOOK_ID: book.getId() });
  Logger.log('폴더: ' + root.getUrl());
  Logger.log('시트: ' + book.getUrl());
  Logger.log('메일 남은 하루 발송량: ' + MailApp.getRemainingDailyQuota());
}

const LOGO = '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';
