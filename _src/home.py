# 첫 페이지(index.html) — 2026-10-03 원장 컨펌한 시안 D 15차를 실제 사이트로 옮긴 것
# 홈 / 커리큘럼(수업 방식 포함) / 대회·실적 / 학원 소식 / 샘플클래스를 한 문서 안에 두고 #주소로 화면을 바꾼다
# 사진·영상·로고는 저장소 img/d/ 에 있다 (펙셀스 색감 보정본, 히어로 영상은 우리 영상 4K 복원 + 펙셀스 무료 영상)
# build.py가 set_posts(글 목록)를 부르고 page(HEAD, ENDPOINT)로 문서를 받는다
import re, pathlib, json

HERE = pathlib.Path(__file__).resolve().parent
SITE = HERE.parent
lines = (SITE / '_src/body.html').read_text(encoding='utf-8').split('\n')
def L(a, b): return '\n'.join(lines[a - 1:b])
def D(name):
    assert (SITE / 'img' / 'd' / name).exists(), name
    return 'img/d/' + name
IMG = {'logo.png': 'img/logo.png', 'hero.jpg': D('hero.jpg'), 'method.jpg': D('method.jpg'), 'essential.jpg': D('essential.jpg'),
       'embedded.jpg': D('embedded.jpg'), 'expo.jpg': D('expo.jpg')}
import sys; sys.path.insert(0, str(HERE)); from ui_parts import UI, UI_CSS
GEN = {'steam': D('steam.jpg'), 'prime': D('prime.jpg')}
# 프로그램 화면은 실제 캡처
SHOT = {k: D(f'ui-{k}.jpg') for k in ['python', 'appinventor', 'ax', 'algo']}
SHOT['prep'] = D('prep.jpg')
SHOT_ALT = {'python': '스파이크 앱 파이썬 편집기에서 거리 센서로 장애물을 피하는 주행 코드를 작성한 화면',
            'appinventor': '앱 인벤터 블록 편집기에서 스위치와 슬라이더로 조명 앱을 만드는 화면',
            'ax': '클로드 코드 터미널에서 AI에게 테스트 점검을 맡기고 진행 과정을 확인하는 화면',  # 앤트로픽 공식 깃허브 소개 영상의 한 장면
            'algo': '프로그래머스 코딩테스트 연습 문제를 파이썬 깊이 우선 탐색으로 푸는 화면',
            'prep': '학원에 진열된 FLL 대회 트로피와 메달'}
LG = {k: D('logo-' + f) for k, f in [('koi', 'koi.png'), ('fll', 'fll.svg'), ('robocup', 'robocup.png'), ('robotex', 'robotex.png'),
                   ('wro', 'wro.png'), ('vexiq', 'viqrc.png'), ('iro', 'iro_s.png'),
                   ('esw', 'esw.png'), ('kcf', 'kcf.png'), ('nypc', 'nypc_k.png'), ('itc', 'it_logo.png')]}

def fix(s):
    s = re.sub(r'@@A@@img/([\w.-]+)', lambda m: IMG[m.group(1)], s)
    return (s.replace('@@A@@sample.html', '#sample').replace('@@H@@#', '#')
             .replace(' loading="lazy"', ''))
TRACK = fix(L(337, 364)); MORE = L(372, 408); FAQ = fix(L(473, 481)); INFO = fix(L(490, 509))
assert TRACK.strip().startswith('<div class="trackbox"') and FAQ.strip().startswith('<div class="faq">') and INFO.strip().startswith('<div class="info">')
n = [0]
def _d(m):
    n[0] += 1
    return m.group(0).replace('style="', f'style="--d:{n[0]};', 1)
TRACK = re.sub(r'<div class="bar[^>]*>', _d, TRACK)
INFO = INFO.replace('class="btn" href="tel', 'class="pill" href="tel').replace('class="btn ghost"', 'class="pill ghost"')
POSTS = ''
def set_posts(items):
    '''build.py의 글 목록(최신 3편)으로 학원 소식 칸을 만든다. img/d/post-<slug>.jpg 가 있으면 글 옆에 붙인다
    (블로그 대표 이미지. 사진은 펙셀스 색감으로 맞추고, 버튼 배너뿐인 글은 본문 사진을 쓴다)'''
    global POSTS
    rows = []
    for p in items:
        t = SITE / 'img' / 'd' / f"post-{p['slug']}.jpg"
        th = f'<span class="th"><img src="img/d/post-{p["slug"]}.jpg" alt="" loading="lazy" decoding="async"></span>' if t.exists() else ''
        c = '' if p['category'] in ('스타랩 이야기', '학원 소식') else f"<span>{p['category']}</span>"
        rows.append(f'<li><a href="posts/{p["slug"]}.html"><span class="tx"><span class="meta"><time datetime="{p["date"]}">{p["date"].replace("-", ".")}</time>{c}</span>'
                    f'<b>{p["title"]}</b><span class="sum">{p["summary"]}</span></span>{th}</a></li>')
    POSTS = '<ul class="posts">\n      ' + '\n      '.join(rows) + '\n    </ul>'

# 과정표(지금 사이트 '과정별 자세히 보기')에서 과정·대상·설명·세부 항목을 그대로 읽는다
COURSES = []
for m in re.finditer(r'<tr><td>([^<]+)</td><td class="who">([^<]+)</td><td>\s*<p>(.*?)</p>\s*<ul class="cl">(.*?)</ul>', MORE, re.S):
    items = re.findall(r'<li><b>(.*?)</b>(.*?)</li>', m.group(4))
    COURSES.append((m.group(1), m.group(2), m.group(3), items))
OPTS = re.findall(r'<tr><td>([^<]+)</td><td class="who">([^<]+)</td><td>([^<]+)</td></tr>', MORE)
assert len(COURSES) == 6 and len(OPTS) == 4, (len(COURSES), len(OPTS))
SLUG = ['steam', 'essential', 'prime', 'python', 'embedded', 'project']
# 커리큘럼 지도와 커리큘럼 페이지를 다섯 단계로만 나눈다. 과정별 정확한 시작 학년은 과정 태그(초1~, 초3~)에 남긴다
STAGES = [('kinder', '유치부', [0], []), ('lower', '초등 저학년', [1], []), ('upper', '초등 고학년', [2, 3], [0]),
          ('middle', '중등부', [4], [1, 2]), ('high', '고등부', [5], [])]
SHORT = ['기초 로봇공학 · 언플러그드 코딩', '블록코딩 · 컴퓨터 사이언스', '센서 제어 · 대회 프로젝트',
         '문법과 알고리즘 · 머신러닝 기초', 'C 문법과 자료구조 · MCU 제어', '심화탐구 보고서 · 포트폴리오']
SHADE = ['s1', 's2', 's3', 's5', 's6', 's7']
OPT_IMG = ['appinventor', 'ax', 'algo', 'prep']
OPT_NOTE = ['', '', '', '대회반은 Lv6부터 편성']
MEDIA = {  # 과정별 사진: 실제 수업 사진이 있으면 그것, 없으면 생성 이미지
    0: ('gen', 'steam', '얼리 심플머신으로 만든 레버 장치를 손으로 돌려 보는 유치부 수업'),
    1: ('img', 'essential.jpg', '스파이크 에센셜 로봇을 태블릿 블록코딩으로 움직이는 수업'),
    2: ('gen', 'prime', '스파이크 프라임 비행기 시뮬레이터를 움직이며 노트북 스파이크 앱의 선 그래프로 센서 값을 확인하는 모습'),
    3: ('ui', 'python', ''),
    4: ('img', 'embedded.jpg', '아두이노로 만든 로봇카를 노트북으로 코딩하는 수업'),
    5: ('img', 'expo.jpg', '2023 대한민국 산업기술 R&amp;D대전에 전시된 학생 임베디드 작품'),
}
# 주요 수상: 2026 학부모 소개자료 11쪽의 네 칸 그대로 (표기는 소개자료 우선, 연도는 마스터파일)
AWARDS = [
    ('2025', '정보올림피아드(KOI)', '금상', '초등부 1차·2차대회'),
    ('2022', 'FLL 퓨처 디자이너', '종합 1위', '챌린지 · 로봇 퍼포먼스 1위'),
    ('2023', '로보컵 코리아 오픈', '1위 · 3위', '레스큐 프라이머리'),
    ('2024', '로보텍스 아시아 챔피언십', '3위', '로봇 스모 1kg'),
]
# 그 밖의 수상: 마스터파일 수상실적 탭 (학생 이름·주관 기관 상 이름 없이, 위 네 칸 제외)
MORE = [
    ('2025', [('로보텍스 전국대회', '로봇 스모 1kg', '4위, 장려상 3팀 (세계대회 진출권)'),
              ('청소년 IT 경시대회', '파이썬 부문', '동상, 장려상'),
              ('FLL 전국대회', '익스플로어', 'Innovative Idea Award, Effective Solution Award'),
              ('NYPC', '', '본선 진출')]),
    ('2024', [('로보텍스 전국대회', '로봇 스모 1kg', 'Best Team Award 2팀 (월드·아시아 챔피언십 진출권)'),
              ('임베디드 SW 경진대회', '메이커 히어로즈', '장려상, 아이디어상, 입선'),
              ('FLL 전국대회', '익스플로어', 'Excellent PT Award, Effective Solution Award, Innovative Idea Award'),
              ('FLL 퓨처 디자이너', '', 'Creator Award')]),
    ('2023', [('WRO 코리아 오픈', '프렌드십 챌린지', '동상, 장려상 2팀'),
              ('임베디드 SW 경진대회', '주니어 메이커', '우수상, 특별상')]),
    ('2022', [('FLL 전국대회', '익스플로어', 'Smart Solution Award (세계대회 진출권), Excellent PT Award')]),
    ('2021', [('FLL 전국대회', '챌린지', 'Rising Star Award 신인상 (세계대회 진출권)'),
              ('FLL 전국대회', '익스플로어', 'Best Teamwork, Brilliant Story, Innovative Research Award')]),
    ('2020', [('FLL 전국대회', '주니어', 'Smart Solution, Brilliant Story, Outstanding Building Award')]),
]
# 출전했거나 출전 예정인 대회 전부 (로고 파일이 없는 곳은 자리만)
LOGOS = [('FIRST LEGO League', 'fll', 'h', 40), ('로보컵 코리아 오픈', 'robocup', 'h', 52), ('로보텍스', 'robotex', 'h', 36),
         ('WRO', 'wro', 'h', 38), ('VEX IQ 로보틱스 컴피티션', 'vexiq', 'h', 50), ('국제로봇올림피아드(IRO)', 'iro', 'h', 58),
         ('임베디드 소프트웨어 경진대회', 'esw', 'w', 150), ('한국코드페어', 'kcf', 'w', 138), ('정보올림피아드(KOI)', 'koi', 'h', 50),
         ('청소년 IT 경시대회', 'itc', 'h', 58), ('NYPC', 'nypc', 'w', 138)]

TOOLS = [('브릭큐', '에센셜'), ('VEX123', ''), ('얼리', '심플머신'), ('스파이크', '에센셜'), ('스파이크', '프라임'), ('엔트리', ''),
         ('앱인벤터', ''), ('파이썬', ''), ('C언어', ''), ('MCU', ''), ('Git', ''), ('COS', ''), ('COS Pro', ''), ('아두이노', '')]
POS = [(4, 8), (14, 2), (23, 11), (5, 37), (15, 31), (4, 65), (16, 63),
       (70, 10), (79, 2), (88, 9), (74, 35), (86, 33), (73, 63), (86, 62)]
PREP = [('로봇대회', ''), ('공모전', ''), ('경시대회', ''), ('영재원', ''), ('자격증', 'COS · COS Pro'), ('대회반', 'Lv6부터 편성')]
FIVE = [('도입', 'Engage', '오늘의 미션과 질문으로 수업을 엽니다'), ('탐색', 'Explore', '직접 만들고 코딩하며 답을 찾아봅니다'),
        ('설명', 'Explain', '왜 그렇게 움직였는지 원리를 정리합니다'), ('확장', 'Elaborate', '배운 원리를 더 어려운 미션에 적용합니다'),
        ('평가', 'Evaluate', '결과를 돌아보고 다음 목표를 정합니다')]

ICON = {
 'robot': '<path d="M7 9h10v9H7z M12 5v4 M9.5 13h.01 M14.5 13h.01 M5 13h2 M17 13h2"/>',
 'code': '<path d="M9 8l-4 4 4 4 M15 8l4 4-4 4"/>',
 'chip': '<path d="M8 8h8v8H8z M10 4v4 M14 4v4 M10 16v4 M14 16v4 M4 10h4 M4 14h4 M16 10h4 M16 14h4"/>',
 'doc': '<path d="M6 3h7l4 4v14H6z M13 3v4h4 M9 12h6 M9 16h6"/>',
 'spark': '<path d="M12 3v4 M12 17v4 M3 12h4 M17 12h4 M6 6l2.5 2.5 M15.5 15.5L18 18 M6 18l2.5-2.5 M15.5 8.5L18 6"/>',
 'search': '<path d="M11 5a6 6 0 1 1 0 12a6 6 0 0 1 0-12z M15.5 15.5L20 20"/>',
 'bulb': '<path d="M9 18h6 M10 21h4 M12 3a6 6 0 0 0-3.5 10.9V16h7v-2.1A6 6 0 0 0 12 3z"/>',
 'up': '<path d="M5 19L19 5 M10 5h9v9"/>',
 'flag': '<path d="M6 21V4 M6 4h11l-2 4 2 4H6"/>',
 'star': '<path d="M12 4l2.4 5 5.4.6-4 3.7 1.1 5.4L12 16l-4.9 2.7 1.1-5.4-4-3.7 5.4-.6z"/>',
 'chart': '<path d="M5 19V9 M10 19V5 M15 19v-7 M20 19v-4"/>',
 'cert': '<path d="M5 4h14v11H5z M9 15l-1 5 4-2 4 2-1-5"/>',
}
def svg(k): return f'<svg viewBox="0 0 24 24" aria-hidden="true">{ICON[k]}</svg>'

def ph(what, note='', cls='', style=''):
    nn = f'<span class="ph-note">{note}</span>' if note else ''
    st = f' style="{style}"' if style else ''
    return f'<div class="ph {cls}"{st}><b>자리 비워 둠</b><span class="ph-what">{what}</span>{nn}</div>'

def pill(text, href, cls=''): return f'<a class="pill {cls}" href="{href}">{text}</a>'
SAMPLE = pill('샘플클래스 신청', '#sample')
def go(text, href, cls='ghost'): return f'<a class="pill {cls}" href="{href}">{text}<span class="ar" aria-hidden="true">→</span></a>'
def btns(*b): return '<div class="btns">' + ''.join(b) + '</div>'
def head(eye, title, sub='', b='', tag='h2'):
    e = f'<p class="eye">{eye}</p>' if eye else ''
    s = f'<p class="sub">{sub}</p>' if sub else ''
    return f'<div class="head appear">{e}<{tag} class="h2">{title}</{tag}>{s}{b}</div>'
def h1w(s):
    out, k = [], 0
    for t in s.replace('<br>', ' <br> ').split():
        if t == '<br>':
            out.append('<br>'); continue
        out.append(f'<span class="w" style="--k:{k}">{t}</span>'); k += 1
    return '<h1 class="h1">' + ' '.join(out) + '</h1>'
def phero(eye, title, sub='', b=''):
    s = f'<p class="sub">{sub}</p>' if sub else ''
    return f'<div class="head"><p class="eye">{eye}</p>{h1w(title)}{s}{b}</div>'

PAGES = {  # 이어서 보기 카드에 쓰는 페이지 소개
    'curriculum': ('커리큘럼', '유치부터 대입까지, 끊김 없는 로드맵', '유치부부터 고등부까지 단계별 과정과 선택 과정'),
    'method': ('수업 방식', '설명을 듣고 따라 만드는 수업이 아닙니다', '도입부터 평가까지 다섯 단계로 진행하는 수업'),
    'record': ('대회·실적', '실적으로 증명합니다', '출전 대회와 대회별 수상·진출 기록'),
    'stories': ('학원 소식', '상담에서 자주 받는 질문과 수업 이야기', '학원 블로그 글 모음'),
}
def nexts(a, b):
    cards = ''
    for k in (a, b):
        eye, title, desc = PAGES[k]
        cards += (f'<a class="nx appear" href="#{k}"><span class="eye">{eye}</span><b>{title}</b>'
                  f'<span class="nx-b"><span>{desc}</span><i aria-hidden="true">→</i></span></a>')
    return f'<section class="next"><div class="cols"><p class="lbl appear">이어서 보기</p><div class="nxs">{cards}</div></div></section>'

def band():
    return (f'<section class="band"><div class="cols"><div class="head appear"><p class="eye">샘플클래스</p>'
            f'<h2 class="h2">처음이라면,<br>샘플클래스로 먼저 경험해 보세요</h2>'
            f'<p class="sub">정규수업과 같은 교구와 방식으로 직접 만들고, 코딩하고, 고쳐 가며 완성해 봅니다.</p>'
            f'{btns(pill("샘플클래스 신청", "#sample", "white"), pill("전화 02-444-1854", "tel:024441854", "line"))}</div></div></section>')

def roadmap():
    cols = ''
    for k, (sid, label, mains, opts) in enumerate(STAGES):
        blocks = ''.join(f'<a class="blk {SHADE[c]}" href="#c-{SLUG[c]}" style="--d:{k * 2 + n}"><strong>{COURSES[c][0]}</strong><small>{SHORT[c]}</small></a>'
                         for n, c in enumerate(mains))
        blocks += ''.join(f'<span class="blk xo" style="--d:{k * 2 + 2}"><strong>{OPTS[o][0]}</strong><small>{OPTS[o][2]}</small></span>' for o in opts)
        cols += f'<div class="mc"><div class="st"><i></i><b>{label}</b></div>{blocks}</div>'
    prep = f'<div class="blk prepbar" style="--d:11"><strong>{OPTS[3][0]}</strong><small>{OPTS[3][2]}</small></div>'
    return f'<div class="map" id="map">{cols}{prep}</div>'

CSS = UI_CSS + r'''
:root{--ink:#1C1C1E;--g5:rgba(28,28,30,.56);--g3:rgba(28,28,30,.3);--line:rgba(28,28,30,.1);--sand:#F6F5F4;--o:#F7941E;--oh:#FFA43C;--oi:#A65605;--em:#EE8410;--tint:#FEF1E2;
  --s1:#FEF1E2;--s2:#FDDDB8;--s3:#FBC489;--s4:#F9AB57;--s5:#F7941E;--s6:#D97A12;--s7:#A65605;
  --ease:cubic-bezier(.83,0,.17,1);--easeOut:cubic-bezier(.16,1,.3,1);
  --sans:"Pretendard Variable",Pretendard,-apple-system,"Apple SD Gothic Neo","Malgun Gothic",system-ui,sans-serif;color-scheme:light}
*{box-sizing:border-box}
html{-webkit-text-size-adjust:100%}
body{margin:0;background:#fff;color:var(--ink);font-family:var(--sans);font-size:16px;line-height:1.5;letter-spacing:-.01em;-webkit-font-smoothing:antialiased;word-break:keep-all;overflow-wrap:break-word}
img{max-width:100%;height:auto;display:block}
p{margin:0}h1,h2,h3{margin:0;text-wrap:balance}
a{color:inherit;text-decoration:none}
.cols{max-width:1496px;margin-inline:auto;padding-inline:32px}
a:focus-visible,button:focus-visible,summary:focus-visible{outline:2px solid var(--o);outline-offset:3px}

/* 버튼: 사나 알약 크기(36px) 그대로, 색은 스타랩 주황 */
.pill{display:inline-flex;align-items:center;gap:6px;height:36px;padding:0 16px;border-radius:36px;background:var(--o);color:var(--ink);font-size:14px;font-weight:600;white-space:nowrap;transition:background .2s ease,box-shadow .2s ease}
.pill:hover{background:var(--oh)}
.pill.ghost{background:#fff;font-weight:500;box-shadow:inset 0 0 0 1px rgba(28,28,30,.16)}
.pill.ghost:hover{background:var(--sand)}
.pill.white{background:#fff}.pill.white:hover{background:var(--tint)}
.pill.line{background:transparent;font-weight:500;box-shadow:inset 0 0 0 1.5px rgba(28,28,30,.55)}
.pill.line:hover{background:rgba(255,255,255,.25)}
.pill .ar{transition:transform .3s var(--easeOut)}.pill:hover .ar{transform:translateX(3px)}
.btns{display:flex;flex-wrap:wrap;justify-content:center;gap:8px}

/* 상단 */
.top{position:sticky;top:0;z-index:40;background:rgba(255,255,255,.96);-webkit-backdrop-filter:blur(12px);backdrop-filter:blur(12px);border-bottom:1px solid transparent}
.top .cols{display:flex;align-items:center;height:56px;gap:8px}
.brand{display:flex;align-items:center;gap:8px;margin-right:16px}
.brand img{height:24px;width:auto}
.brand b{font-size:15px;font-weight:600;letter-spacing:-.02em;white-space:nowrap}
.nav{display:flex}
.nav a,.top .tel{font-size:14px;padding:8px 12px;border-radius:6px;transition:background .2s;position:relative;white-space:nowrap}
.nav a:hover,.top .tel:hover{background:rgba(28,28,30,.05)}
.nav a[aria-current]{font-weight:600}
.nav a[aria-current]::after{content:"";position:absolute;left:12px;right:12px;bottom:2px;height:2px;border-radius:2px;background:var(--o)}
.top .right{margin-left:auto;display:flex;align-items:center;gap:4px}
.top .tel{font-variant-numeric:tabular-nums}
.menu{all:unset;display:none;cursor:pointer;width:36px;height:36px;border-radius:50%;place-items:center}
.menu svg{width:20px;height:20px;fill:none;stroke:var(--ink);stroke-width:1.8;stroke-linecap:round}
.mnav{display:none}

/* 페이지 전환 */
.view{display:none}
.view.on{display:block;animation:viewIn .45s var(--easeOut)}
@keyframes viewIn{from{opacity:0}to{opacity:1}}

/* 섹션 공통 */
section{padding-block:100px}
.sand{background:var(--sand)}
.head{text-align:center;display:flex;flex-direction:column;align-items:center;gap:20px;margin-bottom:56px}
.eye{font-size:16px;line-height:1.4;color:var(--oi)}
.h2{font-size:48px;font-weight:500;line-height:1.08;letter-spacing:-.035em}
.sub{font-size:16px;line-height:1.5;max-width:34rem;color:rgba(28,28,30,.8)}
.ph-t{color:var(--g3)}
.lbl{text-align:center;font-size:14px;color:var(--g5);margin-bottom:24px}
.center{text-align:center;margin-top:32px;display:flex;justify-content:center}

/* 첫 제목 (모든 페이지 공통): 단어가 0.1초 간격으로 2초 동안 나타남 */
.h1{font-size:clamp(2rem,6.4vw,4.2rem);font-weight:400;line-height:1.08;letter-spacing:-.04em}
.h1 em{font-style:normal;color:var(--em)}
.h1 .w{display:inline-block}
.js .h1 .w{opacity:0}
.js .h1.go .w{animation:wordIn 2s var(--easeOut) forwards;animation-delay:calc(var(--k)*.1s)}
@keyframes wordIn{to{opacity:1}}
.phero{padding-block:96px 64px}
.phero .head{gap:22px;margin-bottom:0}

/* 홈 첫 화면 */
.hero{padding-block:88px 24px}
.hero .head{gap:22px;margin-bottom:48px}
.hero-media{border-radius:16px;overflow:hidden;aspect-ratio:16/9;max-width:100%}
.hero-video{display:block;width:100%;height:100%;object-fit:cover}
.ph.dark{height:100%;border-radius:16px;border-color:rgba(255,255,255,.16);background:repeating-linear-gradient(-45deg,#24221F 0 14px,#1E1C1A 14px 28px);color:rgba(255,255,255,.66)}
.ph.dark .ph-what{color:#fff;font-size:18px}.ph.dark b{color:var(--o)}
.ph.dark .play{width:64px;height:64px;border-radius:50%;background:var(--o);display:grid;place-items:center;margin-bottom:10px}
.ph.dark .play svg{width:22px;height:22px;fill:var(--ink);margin-left:3px}
.logos{display:grid;grid-template-columns:repeat(6,1fr);column-gap:20px;margin-top:8px}
.logos .slot{height:110px;display:flex;align-items:center;justify-content:center;transition:opacity 1s ease}
.logos .slot.hide{opacity:0}
.logos img{width:auto;max-width:150px}
.logos .wm{font-size:28px;font-weight:800;letter-spacing:-.02em;color:#1C1C1E}

/* 홈 제품 블록 (사나 홈의 Sana Learn / Sana 블록) */
.prod .head{margin-bottom:40px}
.feats{list-style:none;margin:0 auto 56px;padding:0;display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:24px;max-width:960px;text-align:center}
.feats.five5{grid-template-columns:repeat(5,minmax(0,1fr));max-width:1100px}
.feats li{display:flex;flex-direction:column;align-items:center;gap:4px;font-size:14px;line-height:1.4}
.feats svg{width:18px;height:18px;fill:none;stroke:var(--oi);stroke-width:1.7;stroke-linecap:round;stroke-linejoin:round;margin-bottom:6px}
.feats b{font-weight:600}.feats span{color:var(--g5)}
.feats i{font-style:normal;font-size:12px;color:var(--oi);font-variant-numeric:tabular-nums}
.card{background:#fff;border-radius:24px;padding:48px 40px 40px;max-width:1144px;margin-inline:auto}
.prod-card{border-radius:24px;padding:88px 40px 40px}
.prod-card .pm{margin:0;border-radius:16px;overflow:hidden}
.prod-card .pm img{width:100%;aspect-ratio:16/8;object-fit:cover}

/* 홈 실적 카드 (사나 홈의 고객 인용 카드 자리) */
.proofsec{padding-block:16px}
.proof{position:relative;border-radius:24px;overflow:hidden;min-height:560px;background:#222 center 62%/cover no-repeat;display:flex;align-items:flex-end}
.proof::before{content:"";position:absolute;inset:0;background:linear-gradient(90deg,rgba(14,12,10,.86) 0%,rgba(14,12,10,.55) 45%,rgba(14,12,10,.05) 80%)}
.proof .pt{position:relative;padding:56px;display:flex;flex-direction:column;align-items:flex-start;gap:18px;color:#fff;max-width:640px}
.proof .eye{color:var(--s3)}
.proof h3{font-size:40px;font-weight:500;line-height:1.15;letter-spacing:-.035em}
.proof .cap{font-size:14px;color:rgba(255,255,255,.7)}
.proof.r{justify-content:flex-end}
.proof.r::before{background:linear-gradient(270deg,rgba(14,12,10,.86) 0%,rgba(14,12,10,.55) 34%,rgba(14,12,10,0) 62%)}
.proof.r .pt{max-width:470px}

/* 커리큘럼 지도 (지금 사이트와 같은 막대) */
.track{display:grid;grid-template-columns:minmax(96px,1.3fr) repeat(12,minmax(70px,1fr));row-gap:10px;min-width:980px}
.trackbox{overflow-x:auto}
.station{grid-row:1;display:flex;flex-direction:column;align-items:center;gap:6px;position:relative;padding-bottom:8px}
.station::before{content:"";position:absolute;top:6px;left:0;right:0;height:3px;background:var(--ink)}
.station:first-child::before{left:50%}.station:last-child::before{right:50%}
.station i{position:relative;width:15px;height:15px;border-radius:50%;background:#fff;border:3px solid var(--ink)}
.station b{font-size:13px;font-weight:500;font-variant-numeric:tabular-nums}
.bar{position:relative;border-radius:12px;padding:10px 12px;min-height:50px;display:flex;flex-direction:column;justify-content:center;line-height:1.35;min-width:0}
.bar strong{font-size:14.5px;font-weight:600;white-space:nowrap}
.bar small{font-size:12.5px;color:rgba(28,28,30,.65);white-space:nowrap}
.bar.main{min-height:72px;border-radius:0;justify-content:flex-start;gap:3px}
.bar.main strong{white-space:normal}.bar.main small span{display:block}
.bar.main.first{border-radius:12px 0 0 12px}.bar.main.last{border-radius:0 12px 12px 0}
.bar.main+.bar.main{box-shadow:inset 1px 0 0 rgba(255,255,255,.55)}
.s1{background:var(--s1)}.s2{background:var(--s2)}.s3{background:var(--s3)}.s4{background:var(--s4)}.s5{background:var(--s5)}.s6{background:var(--s6)}
.s7{background:var(--s7);color:#fff}.s7 small{color:rgba(255,255,255,.88)}
.bar.single{background:var(--sand);margin-right:4px}
.bar.prep{background:transparent;outline:1px dashed rgba(28,28,30,.35);outline-offset:-1px}
.bar.gap{margin-top:12px}
.js .trackbox .bar{opacity:0;transform:translateX(-12px);transition:opacity .8s var(--ease),transform .8s var(--ease);transition-delay:calc(var(--d,0)*.08s)}
.js .trackbox.in .bar{opacity:1;transform:none}

/* 커리큘럼 페이지 */
.chips{display:flex;flex-wrap:wrap;justify-content:center;gap:8px;margin-top:48px}
.chip{display:inline-flex;align-items:center;gap:8px;height:40px;padding:0 16px;border-radius:40px;background:var(--sand);font-size:14px;font-weight:500;transition:background .2s}
.chip:hover{background:var(--tint)}
.chip i{font-style:normal;font-size:12.5px;color:var(--oi);font-variant-numeric:tabular-nums}
.courses{padding-block:24px 80px}
.course{display:grid;grid-template-columns:5fr 7fr;gap:64px;align-items:center;padding-block:56px;border-top:1px solid var(--line);scroll-margin-top:64px}
.course:first-child{border-top:0}
.course.flip{grid-template-columns:7fr 5fr}.course.flip .cm{order:-1}
.course .ct{display:flex;flex-direction:column;align-items:flex-start;gap:18px}
.range{display:inline-flex;align-items:center;height:28px;padding:0 12px;border-radius:28px;background:var(--tint);color:var(--oi);font-size:13px;font-weight:600;font-variant-numeric:tabular-nums}
.course h3{font-size:36px;font-weight:500;line-height:1.12;letter-spacing:-.035em}
.course .desc{font-size:18px;line-height:1.5}
.course ul{list-style:none;margin:6px 0 0;padding:0;display:flex;flex-direction:column;gap:14px;width:100%}
.course li{display:grid;grid-template-columns:auto 1fr;column-gap:14px;padding-top:14px;border-top:1px solid var(--line)}
.course li::before{content:"";width:8px;height:8px;border-radius:50%;background:var(--o);margin-top:7px;grid-row:1/span 2}
.course li b{font-weight:600}.course li span{color:var(--g5);font-size:15px}
.course .cm{border-radius:24px;overflow:hidden;aspect-ratio:4/3;max-width:100%}
.course .cm img{width:100%;height:100%;object-fit:cover}
.course .cm .ph{height:100%;border-radius:24px}
.course .acts{display:flex;gap:8px;flex-wrap:wrap;margin-top:6px}
.opt{display:grid;grid-template-columns:repeat(3,1fr);gap:16px;max-width:1144px;margin-inline:auto}
.opt div{background:#fff;border-radius:16px;padding:24px;display:flex;flex-direction:column;gap:8px}
.opt b{font-size:20px;font-weight:500;letter-spacing:-.02em}
.opt span{color:var(--g5)}
.panel{position:relative;background:var(--sand);border-radius:24px;height:540px;overflow:hidden}
.panel .pc{position:absolute;inset:0;display:flex;flex-direction:column;align-items:center;justify-content:center;gap:16px;text-align:center}
.panel .pc h3{font-size:32px;font-weight:500;letter-spacing:-.03em;line-height:1.1}
.panel .pc p{color:var(--g5)}
.bubble{position:absolute;width:104px;height:104px;border-radius:50%;background:#fff;display:flex;flex-direction:column;align-items:center;justify-content:center;text-align:center;font-size:13.5px;font-weight:600;line-height:1.25;letter-spacing:-.02em;left:var(--x);top:var(--y);box-shadow:0 1px 2px rgba(28,28,30,.04)}
.bubble small{font-size:12px;font-weight:400;color:var(--g5)}
.js .bubble{opacity:0;transform:scale(.6);transition:opacity .8s var(--easeOut),transform .8s var(--easeOut);transition-delay:calc(var(--i)*.05s)}
.js .panel.in .bubble{opacity:1;transform:none}

/* 수업 방식 페이지 */
.device{margin:0;border-radius:16px;overflow:hidden}
.device img{width:100%;aspect-ratio:16/8;object-fit:cover}
.five{display:grid;grid-template-columns:repeat(5,1fr);margin-top:16px;border-radius:16px;overflow:hidden}
.five div{padding:20px;display:flex;flex-direction:column;gap:4px}
.five b{font-weight:600}.five i{font-style:normal;font-size:12.5px;color:rgba(28,28,30,.6)}
.five span{font-size:14px;color:rgba(28,28,30,.85)}
.five .f5{background:var(--s5)}
.five-p{text-align:center;max-width:40rem;margin:28px auto 0;color:var(--g5)}
.cmp{display:grid;grid-template-columns:3fr 4fr 4fr;column-gap:20px;position:relative;max-width:1144px;margin-inline:auto}
.cmp>div{padding:18px 0;border-bottom:1px solid var(--line)}
.cmp .hd{color:var(--g5);padding-top:0}.cmp .hd.on{color:var(--oi);font-weight:600}
.cmp .sk{height:12px;border-radius:6px;background:rgba(28,28,30,.07);margin:6px 0}
.cmp .sk.o{background:rgba(247,148,30,.22)}
.cmp-note{position:absolute;inset:48px 0 0;display:flex;align-items:center;justify-content:center}
.cmp-note .ph{background:rgba(255,255,255,.92);max-width:560px}
.data{display:grid;grid-template-columns:repeat(3,1fr);gap:16px;max-width:1144px;margin-inline:auto}
.data .ph{min-height:220px;border-radius:24px}
.reviews{padding-block:40px}
.rail{display:flex;gap:16px;overflow-x:auto;scroll-snap-type:x mandatory;scrollbar-width:none;padding-inline:32px;scroll-padding-inline:32px;max-width:100vw}
.rail::-webkit-scrollbar{display:none}
.rail>*{scroll-snap-align:start;flex:none}
.ctrl{display:flex;justify-content:center;align-items:center;gap:8px;margin-top:32px}
.prog{height:28px;border-radius:28px;background:rgba(28,28,30,.05);display:flex;align-items:center;gap:6px;padding-inline:12px}
.prog .bar2{width:64px;height:3px;border-radius:3px;background:rgba(28,28,30,.12);overflow:hidden}
.prog .bar2::before{content:"";display:block;height:100%;width:var(--p,0%);background:var(--o)}
.prog .dot{width:4px;height:4px;border-radius:50%;background:rgba(28,28,30,.25)}
.ctrl button{all:unset;cursor:pointer;width:28px;height:28px;border-radius:50%;background:rgba(28,28,30,.05);display:grid;place-items:center}
.ctrl button svg{width:10px;height:10px;fill:var(--ink)}
.quote{width:min(470px,80vw);background:#fff;border-radius:24px;padding:16px;display:flex;flex-direction:column;gap:56px}
.quote .q{background:var(--sand);border-radius:16px;padding:28px;min-height:170px;display:flex;flex-direction:column;justify-content:center;gap:6px}
.quote .q b{font-size:12px;letter-spacing:.06em;color:var(--oi)}
.quote .q span{color:var(--g5)}
.quote .who{display:flex;flex-direction:column;gap:2px;padding:0 28px 12px}
.quote .who i{width:44px;height:44px;border-radius:50%;border:1.5px dashed rgba(28,28,30,.25);margin-bottom:16px}
.quote .who span{color:var(--g5)}

/* 대회·실적 페이지 */
.stats{display:grid;grid-template-columns:repeat(4,1fr);margin:0 auto;padding:0;list-style:none;max-width:1144px}
.stats li{padding:4px 24px 0;border-left:1px solid var(--line);display:flex;flex-direction:column;gap:8px}
.stats li:first-child{border-left:0;padding-left:0}
.stats b{font-size:48px;font-weight:400;letter-spacing:-.04em;line-height:1;font-variant-numeric:tabular-nums}
.stats b .cu{color:var(--em)}
.walls{display:flex;flex-direction:column;gap:40px}
.wg{display:flex;flex-direction:column;gap:16px}
.wg-h{display:flex;align-items:center;gap:10px;font-size:20px;font-weight:500;letter-spacing:-.02em}
.wg-h::before{content:"";width:10px;height:10px;border-radius:50%;background:var(--o)}
.wall{display:grid;grid-template-columns:repeat(6,minmax(0,1fr));gap:12px}
.cell{background:var(--sand);border-radius:16px;height:156px;display:flex;flex-direction:column;align-items:center;justify-content:center;gap:14px;padding:16px;text-align:center}
.cell img{max-width:88%;max-height:72px;object-fit:contain}
.cell small{font-size:13px;color:var(--g5);line-height:1.3}
.cell.need{background:transparent;border:1.5px dashed rgba(28,28,30,.18)}
.cell.need b{font-size:12px;letter-spacing:.06em;color:var(--oi)}
.cell.need span{font-weight:600;font-size:15px}
.story{width:min(440px,80vw);display:flex;flex-direction:column;gap:14px}
.story .m{position:relative;height:420px;border-radius:24px;overflow:hidden}
.story .m .ph{height:100%;border-radius:24px;background:repeating-linear-gradient(-45deg,#3A3836 0 14px,#33312F 14px 28px);border-color:rgba(255,255,255,.18);color:rgba(255,255,255,.7)}
.story .m .ph .ph-what{color:#fff}.story .m .ph b{color:var(--s3)}
.story .lgc{position:absolute;left:20px;top:20px;height:52px;padding:0 14px;border-radius:12px;background:#fff;display:flex;align-items:center;font-weight:600;font-size:15px}
.story .lgc img{height:30px;width:auto;max-width:150px;object-fit:contain}
.story p strong{font-weight:500}
.partner{display:grid;grid-template-columns:1fr 1fr;gap:16px}
.partner>.ph{border-radius:24px;min-height:440px}
.pcards{display:grid;grid-template-columns:1fr 1fr;gap:16px}
.pcard{background:var(--sand);border-radius:16px;padding:20px 24px;min-height:120px;display:flex;flex-direction:column;justify-content:space-between;gap:16px}
.pcard .ico{width:32px;height:32px;border-radius:50%;background:#fff;display:grid;place-items:center}
.pcard .ico svg{width:16px;height:16px;fill:none;stroke:var(--oi);stroke-width:1.7;stroke-linecap:round;stroke-linejoin:round}
.pcard b{font-weight:500;font-size:17px}.pcard small{display:block;color:var(--g5);font-size:13.5px;margin-top:2px}
.pcard.o{grid-column:1/-1;min-height:96px;background:var(--o);justify-content:flex-end;transition:background .2s}
.pcard.o:hover{background:var(--oh)}
.pcard.o b{font-weight:600;display:flex;justify-content:space-between;align-items:center}

/* 이어서 보기 + 주황 신청 띠 (모든 페이지 끝) */
.next{padding-block:40px 100px}
.nxs{display:grid;grid-template-columns:1fr 1fr;gap:16px;max-width:1144px;margin-inline:auto}
.nx{background:var(--sand);border-radius:24px;padding:32px;min-height:220px;display:flex;flex-direction:column;gap:12px;transition:background .25s}
.nx:hover{background:var(--tint)}
.nx b{font-size:28px;font-weight:500;letter-spacing:-.03em;line-height:1.15}
.nx-b{margin-top:auto;display:flex;align-items:flex-end;justify-content:space-between;gap:16px;color:var(--g5)}
.nx-b i{flex:none;width:44px;height:44px;border-radius:50%;background:var(--o);color:var(--ink);font-style:normal;font-size:18px;display:grid;place-items:center;transition:transform .3s var(--easeOut)}
.nx:hover .nx-b i{transform:translateX(4px)}
.band{background:var(--o);padding-block:104px}
.band .head{margin-bottom:0}
.band .eye{color:var(--ink);opacity:.75}
.band .sub{color:var(--ink)}
.facts{display:flex;flex-wrap:wrap;justify-content:center;gap:8px;margin:0}
.facts div{display:flex;gap:8px;align-items:baseline;background:rgba(255,255,255,.35);border-radius:36px;padding:8px 16px;font-size:14px}
.facts dt{opacity:.7}.facts dd{margin:0;font-weight:600}.facts small{font-weight:400;opacity:.75}

/* 샘플클래스 페이지 */
.mission{position:relative;border-radius:24px;overflow:hidden;min-height:520px;display:grid;grid-template-columns:1fr 1fr}
.mission>.ph{border-radius:24px;grid-column:1/-1;grid-row:1;align-items:flex-start;text-align:left;padding:48px}
.mission>.ph .ph-what,.mission>.ph .ph-note{max-width:16rem}
.mission .txt{grid-column:2;grid-row:1;position:relative;align-self:center;margin:24px;padding:40px;background:#fff;border-radius:16px;display:flex;flex-direction:column;gap:18px;font-size:20px;font-weight:500;letter-spacing:-.03em;line-height:1.35}
.mission .txt dl{margin:8px 0 0;display:grid;grid-template-columns:auto 1fr;gap:8px 18px;font-size:16px;font-weight:400;letter-spacing:-.01em;line-height:1.45}
.mission .txt dt{color:var(--g5)}.mission .txt dd{margin:0}
.mission .txt dd small{color:var(--g5);margin-left:6px}
.faq{max-width:1144px;margin-inline:auto}
.faq details{border-bottom:1px solid var(--line)}
.faq details:first-child{border-top:1px solid var(--line)}
.faq summary{list-style:none;cursor:pointer;padding:22px 40px 22px 0;font-weight:500;position:relative}
.faq summary::-webkit-details-marker{display:none}
.faq summary::after{content:"";position:absolute;right:8px;top:27px;width:8px;height:8px;border-right:1.5px solid;border-bottom:1.5px solid;transform:rotate(45deg);transition:transform .3s var(--easeOut)}
.faq details[open] summary::after{transform:rotate(225deg)}
.faq details p{padding:0 0 22px;color:var(--g5);max-width:60rem}
.visit{display:grid;grid-template-columns:1fr 1fr;gap:16px}
/* 오시는 길 지도: 구글 지도 (확대·이동·길찾기 가능) */
.mapbox{border-radius:16px;overflow:hidden;min-height:380px;background:var(--sand);position:relative}
.mapbox iframe{position:absolute;inset:0;width:100%;height:100%;border:0;display:block}
.info{background:var(--sand);border-radius:24px;padding:40px;display:flex;flex-direction:column;gap:28px}
.addr,.time{display:flex;flex-direction:column;gap:10px}
.addr p:first-child b{font-size:22px;font-weight:500;letter-spacing:-.03em}
.addr p+p{color:var(--g5)}
.maps{display:flex;flex-wrap:wrap;gap:6px;margin-top:8px}
.hours{margin:0;display:grid;grid-template-columns:auto 1fr;gap:6px 22px}.hours dt{font-weight:500}.hours dd{margin:0;font-variant-numeric:tabular-nums}
.note{color:var(--g5);font-size:14px}
.visit>.ph{border-radius:24px;min-height:420px}

/* 학원 소식 */
.posts{list-style:none;margin:0 auto;padding:0;display:grid;grid-template-columns:1fr;gap:16px;max-width:1000px}
.posts a{display:flex;align-items:center;gap:32px;height:100%;background:var(--sand);border-radius:24px;padding:20px 20px 20px 36px;transition:background .25s}
.posts .tx{display:flex;flex-direction:column;gap:12px;flex:1;min-width:0}
.posts .th{flex:none;width:300px;max-width:42%;aspect-ratio:16/10;border-radius:16px;overflow:hidden;background:var(--line)}
.posts .th img{width:100%;height:100%;object-fit:cover;transition:transform .5s var(--easeOut)}
.posts a:hover .th img{transform:scale(1.03)}
.hmethod{padding-block:56px 100px}
.posts a:hover{background:var(--tint)}
.posts .meta{display:flex;gap:10px;font-size:14px;color:var(--g5);font-variant-numeric:tabular-nums}
.posts b{font-size:20px;font-weight:500;line-height:1.35;letter-spacing:-.025em}
.posts .sum{color:var(--g5)}

/* 아래 전체 메뉴 (사나식 큰 바닥글) */
footer{border-top:1px solid var(--line);padding-block:64px 40px;font-size:14px}
footer .cols{display:grid;grid-template-columns:2fr 1fr 1fr 1fr 1fr;gap:24px}
footer .col{display:flex;flex-direction:column;gap:8px}
footer .fh{color:var(--g5);margin-bottom:6px}
footer a:hover{color:var(--oi)}
footer img{height:24px;width:auto;align-self:flex-start;margin-bottom:12px}
footer .copy{grid-column:1/-1;display:flex;justify-content:space-between;color:var(--g5);padding-top:48px}

/* 커리큘럼 지도: 다섯 단계 */
.map{display:grid;grid-template-columns:repeat(5,minmax(0,1fr));column-gap:10px;row-gap:10px}
.mc{display:flex;flex-direction:column;gap:8px;min-width:0}
.st{display:flex;flex-direction:column;align-items:center;gap:8px;position:relative;padding-bottom:10px}
.st::before{content:"";position:absolute;top:7px;left:-5px;right:-5px;height:3px;background:var(--ink)}
.mc:first-child .st::before{left:50%}.mc:nth-child(5) .st::before{right:50%}
.st i{position:relative;width:17px;height:17px;border-radius:50%;background:#fff;border:3px solid var(--ink)}
.st b{font-size:15px;font-weight:600}
.blk{display:flex;flex-direction:column;gap:4px;border-radius:12px;padding:14px 16px;min-height:84px;line-height:1.35;transition:transform .25s var(--easeOut),box-shadow .25s}
a.blk:hover{transform:translateY(-2px);box-shadow:0 6px 16px rgba(28,28,30,.08)}
.blk strong{font-size:15px;font-weight:600}.blk small{font-size:13px;color:rgba(28,28,30,.68)}
.blk.s7 small{color:rgba(255,255,255,.85)}
.blk.xo{background:var(--sand);min-height:0}
.blk.prepbar{grid-column:2/6;background:transparent;outline:1.5px dashed rgba(28,28,30,.32);outline-offset:-1.5px;min-height:0;flex-direction:row;align-items:baseline;gap:12px;margin-top:6px}
.js .map .blk{opacity:0;transform:translateY(12px);transition:opacity .8s var(--ease),transform .8s var(--ease);transition-delay:calc(var(--d,0)*.08s)}
.js .map.in .blk{opacity:1;transform:none}
/* 커리큘럼 페이지: 단계 묶음 */
.stage{padding-top:40px}
.stage-h{display:flex;align-items:center;gap:12px;font-size:28px;font-weight:600;letter-spacing:-.03em;padding-bottom:8px}
.stage-h i{width:12px;height:12px;border-radius:50%;background:var(--o)}
.ocs{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:16px;max-width:1300px;margin-inline:auto}
.oc{background:#fff;border-radius:24px;padding:12px 12px 24px;display:flex;flex-direction:column;align-items:flex-start;gap:8px;scroll-margin-top:72px}
.oc .om{width:100%;aspect-ratio:4/3;border-radius:16px;overflow:hidden;margin-bottom:8px}
.oc .om img{width:100%;height:100%;object-fit:cover}
/* 실제 화면 캡처: 흰 화면이 배경에 묻히지 않게 얇은 테두리 */
.course .cm:has(img.shot),.oc .om:has(img.shot){outline:1px solid rgba(28,28,30,.14);outline-offset:-1px}.oc .om .ph{height:100%}
.oc>.range,.oc>b,.oc>.od,.oc>.note2{margin-inline:12px}
.oc>b{font-size:20px;font-weight:600;letter-spacing:-.02em}.oc .od{color:var(--g5)}
.oc .note2{font-size:13px;color:var(--oi);font-weight:500}
/* 대회 로고 한데 모으기 (파트너 로고 띠처럼) */
.mqsec{padding-block:8px 0}
.mq{overflow:hidden;-webkit-mask-image:linear-gradient(90deg,transparent,#000 10%,#000 90%,transparent);mask-image:linear-gradient(90deg,transparent,#000 10%,#000 90%,transparent)}
.mq-t{display:flex;width:max-content;animation:mq 45s linear infinite}
.mq:hover .mq-t{animation-play-state:paused}
.mq .lg{flex:none;height:96px;display:flex;align-items:center;margin-right:72px}
.mq img{object-fit:contain}
@keyframes mq{to{transform:translateX(-50%)}}
/* 주요 수상: 소개자료처럼 네 칸 강조 카드 */
.aw{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:16px;max-width:1144px;margin-inline:auto}
.aw article{border-radius:24px;padding:32px 36px;min-height:248px;display:flex;flex-direction:column;gap:6px;background:#fff}
.aw article:nth-child(1){background:var(--o)}
.aw article:nth-child(2){background:#FBE9CF}
.aw article:nth-child(3){background:#FFD7C4}
.aw article:nth-child(4){background:#FFC24A}
.aw .ae{font-size:17px;font-weight:600;letter-spacing:-.01em;display:flex;gap:10px;align-items:baseline}
.aw .ae i{font-style:normal;font-weight:500;font-variant-numeric:tabular-nums;opacity:.6}
.aw .ar2{font-size:clamp(56px,6.4vw,88px);font-weight:700;letter-spacing:-.045em;line-height:1.05;margin-top:auto}
.aw .as{font-size:16px;font-weight:500;opacity:.78}
.aw-sum{text-align:center;margin-top:40px;display:flex;flex-direction:column;gap:6px}
.aw-sum b{font-size:26px;font-weight:600;letter-spacing:-.03em;text-wrap:balance}
.aw-sum span{color:var(--g5);font-size:16px}
/* 그 밖의 수상: 양이 보이게 글로 */
.more{max-width:1144px;margin-inline:auto;border-top:1px solid var(--ink)}
.more .yr{display:grid;grid-template-columns:120px minmax(0,1fr);gap:24px;padding:20px 0;border-bottom:1px solid var(--line)}
.more .yr>b{font-size:28px;font-weight:500;letter-spacing:-.03em;line-height:1.2;font-variant-numeric:tabular-nums;color:var(--oi)}
.more ul{list-style:none;margin:0;padding:0;display:flex;flex-direction:column}
.more li{display:grid;grid-template-columns:minmax(0,5fr) minmax(0,7fr);gap:24px;padding:7px 0;font-size:16px;line-height:1.5}
.more li+li{border-top:1px dashed var(--line)}
.more li b{font-weight:600}.more li b small{font-size:inherit;font-weight:400;color:var(--g5)}
.more li span{color:var(--ink)}
@media (max-width:700px){.aw{grid-template-columns:1fr}.aw article{min-height:200px;padding:26px 24px}.aw-sum b{font-size:21px}
  .more .yr{grid-template-columns:1fr;gap:4px}.more li{grid-template-columns:1fr;gap:0;padding:9px 0}.more li span{color:var(--g5)}}
/* 신청 페이지 */
input,select,textarea,button{font:inherit;color:inherit}
.apply{display:grid;grid-template-columns:minmax(0,7fr) minmax(0,4fr);gap:16px;align-items:start;max-width:1144px;margin-inline:auto}
.formcard{background:#fff;border:1px solid var(--line);border-radius:24px;padding:40px}
.af{display:flex;flex-direction:column;gap:26px}
.frow2{display:grid;grid-template-columns:1fr 1fr;gap:16px}
.fd{display:flex;flex-direction:column;gap:10px;min-width:0}
.fl{font-size:14px;font-weight:600}.fl em,.ck em{font-style:normal;font-size:12px;font-weight:500;color:var(--oi);margin-left:6px}
.af input[type=text],.af input[type=tel],.af select,.af textarea{height:48px;border:1px solid rgba(28,28,30,.18);border-radius:10px;padding:0 14px;background:#fff;font-size:16px;width:100%;transition:border-color .2s,box-shadow .2s}
.af textarea{height:112px;padding:12px 14px;resize:vertical}
.af input:focus,.af select:focus,.af textarea:focus{outline:none;border-color:var(--o);box-shadow:0 0 0 3px rgba(247,148,30,.18)}
.tg{display:flex;flex-wrap:wrap;gap:8px}
.t{position:relative;cursor:pointer}
.t input{position:absolute;opacity:0;pointer-events:none}
.t span{display:inline-flex;align-items:center;height:40px;padding:0 16px;border-radius:40px;background:var(--sand);font-size:14.5px;font-weight:500;transition:background .2s,box-shadow .2s}
.t:hover span{background:#EFEDEA}
.t input:checked+span{background:var(--tint);box-shadow:inset 0 0 0 1.5px var(--o);color:var(--oi)}
.t input:focus-visible+span{outline:2px solid var(--o);outline-offset:2px}
.hint{font-size:13px;color:var(--g5)}
.agree{background:var(--sand);border-radius:16px;padding:20px 22px;display:flex;flex-direction:column;gap:12px;font-size:14px}
.agree ul{margin:0;padding-left:18px;color:rgba(28,28,30,.8);display:flex;flex-direction:column;gap:4px}
.agree dl{margin:0;display:grid;grid-template-columns:auto 1fr;gap:6px 16px}.agree dt{color:var(--g5)}.agree dd{margin:0}
.ck{display:flex;align-items:center;gap:10px;font-weight:500;cursor:pointer}
.ck input{width:20px;height:20px;accent-color:var(--o)}
.ferr{color:#C2410C;font-size:14px;min-height:1px}
.hp{position:absolute;left:-9999px;width:1px;height:1px;overflow:hidden}
.fsub{display:flex;align-items:center;gap:16px;flex-wrap:wrap;color:var(--g5);font-size:14px}
.pill.big{height:48px;padding:0 28px;font-size:16px;border:0;cursor:pointer}
.done{background:#fff;border:1px solid var(--line);border-radius:24px;padding:56px 40px;display:flex;flex-direction:column;align-items:center;text-align:center;gap:14px}
.done .dk{width:56px;height:56px;border-radius:50%;background:var(--o);display:grid;place-items:center;font-size:24px;font-weight:700}
.done h3{font-size:28px;font-weight:600;letter-spacing:-.03em}.done p{color:var(--g5)}
.done[hidden],.af[hidden]{display:none}
.formcard .done{border:0;padding:32px 0}
.aside{background:var(--sand);border-radius:24px;padding:32px;display:flex;flex-direction:column;align-items:flex-start;gap:18px;position:sticky;top:76px}
.aside h3{font-size:20px;font-weight:600}
.ad{margin:0;display:grid;grid-template-columns:auto 1fr;gap:10px 18px;width:100%}
.ad dt{color:var(--g5)}.ad dd{margin:0;font-weight:500}.ad dd small{display:block;font-weight:400;color:var(--g5);font-size:13px}
.ad.hrs{padding-top:18px;border-top:1px solid var(--line);font-variant-numeric:tabular-nums}
.aside p{color:var(--g5);font-size:14px}

/* 수업 방식: 사진 + 다섯 단계 나란히 */
.mx{display:grid;grid-template-columns:minmax(0,1fr) minmax(0,1fr);gap:64px;align-items:center}
.mx-img{margin:0;border-radius:24px;overflow:hidden;aspect-ratio:4/5;max-width:100%}
.mx-img img{width:100%;height:100%;object-fit:cover}
.mx-t{display:flex;flex-direction:column;gap:20px}
.steps{list-style:none;margin:0;padding:0;display:flex;flex-direction:column}
.steps li{display:grid;grid-template-columns:44px 1fr;gap:18px;align-items:start;padding:20px 0;border-top:1px solid var(--line)}
.steps li:last-child{border-bottom:1px solid var(--line)}
.sn{width:44px;height:44px;border-radius:50%;display:grid;place-items:center;font-weight:700;font-size:16px;font-variant-numeric:tabular-nums}
.steps b{display:flex;align-items:baseline;gap:10px;font-size:22px;font-weight:600;letter-spacing:-.03em}
.steps b i{font-style:normal;font-size:14px;font-weight:500;color:var(--g5);letter-spacing:0}
.steps li span:not(.sn){display:block;margin-top:4px;color:rgba(28,28,30,.75)}
.mx-p{color:var(--g5);max-width:34rem}

/* 빈 자리 */
.ph{display:flex;flex-direction:column;align-items:center;justify-content:center;text-align:center;gap:6px;padding:24px;border-radius:16px;border:1.5px dashed rgba(28,28,30,.18);
  background:repeating-linear-gradient(-45deg,#F8F7F5 0 12px,#F1EFEC 12px 24px);color:var(--g5)}
.ph b{font-size:12px;font-weight:700;letter-spacing:.06em;color:var(--oi)}
.ph-what{font-size:15px;font-weight:600;color:var(--ink);max-width:28rem}
.ph-note{font-size:13px;max-width:28rem}

/* 등장 효과 (사나 값) */
.js .appear{opacity:0;transform:translateY(20px);transition:opacity .8s var(--ease),transform .8s var(--ease);transition-delay:calc(var(--i,0)*.08s)}
.js .appear.seen{opacity:1;transform:none}

@media (max-width:1100px){.h2{font-size:40px}.panel{height:620px}.bubble{width:88px;height:88px;font-size:12.5px}.course{gap:40px}.wall{grid-template-columns:repeat(4,minmax(0,1fr))}}
@media (max-width:980px){
  .nav,.top .tel{display:none}.menu{display:grid}.top .pill{height:34px;padding:0 13px;font-size:13.5px}
  .mnav{position:absolute;left:0;right:0;top:56px;background:#fff;border-bottom:1px solid var(--line);padding:8px 20px 20px;flex-direction:column}
  .menu-open .mnav{display:flex}
  .mnav a{padding:14px 0;font-size:17px;font-weight:500;border-bottom:1px solid var(--line)}
  .mnav a[aria-current]{color:var(--oi)}
  .mnav a.tel2{border-bottom:0;color:var(--g5);font-size:15px;font-variant-numeric:tabular-nums}
  .cols{padding-inline:20px}.rail{padding-inline:20px;scroll-padding-inline:20px}
  section{padding-block:64px}.h2{font-size:32px}.head{margin-bottom:36px;gap:16px}
  .phero{padding-block:64px 40px}.hero{padding-block:56px 16px}.hero .head{margin-bottom:32px}
  .logos{grid-template-columns:repeat(3,1fr)}.logos .slot{height:76px}.logos .slot:nth-child(n+4){display:none}.logos img{max-width:96px;transform:scale(.8)}
  .card{padding:28px 18px}.prod-card{padding:56px 18px 18px}
  .feats{grid-template-columns:1fr 1fr;row-gap:22px;margin-bottom:36px}.feats.five5{grid-template-columns:repeat(5,minmax(0,1fr));gap:4px}.feats.five5 span,.feats.five5 i{display:none}
  .prod-card .pm img{aspect-ratio:4/3}
  .proof{min-height:520px}.proof::before{background:linear-gradient(0deg,rgba(14,12,10,.9) 0%,rgba(14,12,10,.6) 50%,rgba(14,12,10,.1) 100%)}.proof .pt{padding:28px}.proof h3{font-size:28px}
  .course,.course.flip{grid-template-columns:1fr;gap:24px;padding-block:40px}.course.flip .cm{order:0}.course .cm{order:-1}.course h3{font-size:28px}.course .desc{font-size:16px}
  .opt{grid-template-columns:1fr}
  .panel{height:auto;padding:28px 16px;display:flex;flex-wrap:wrap;gap:8px;justify-content:center}
  .panel .pc{position:static;width:100%;margin-bottom:12px;order:-1}.panel .pc h3{font-size:24px}
  .bubble{position:static;width:78px;height:78px}
  .device img{aspect-ratio:4/3}.five{grid-template-columns:1fr}
  .cmp{grid-template-columns:2fr 3fr 3fr;column-gap:12px}.data{grid-template-columns:1fr}.data .ph{min-height:140px}
  .stats{grid-template-columns:1fr 1fr;row-gap:28px}.stats li:nth-child(3){border-left:0;padding-left:0}.stats b{font-size:36px}
  .map{grid-template-columns:1fr;row-gap:14px}.st{flex-direction:row;justify-content:flex-start;padding-bottom:0}.st::before{display:none}.blk.prepbar{grid-column:1;flex-direction:column;gap:2px}
  .ocs{grid-template-columns:1fr 1fr}.mq .lg{height:72px;margin-right:44px;transform:scale(.82)}
  .proof.r{justify-content:flex-start}.mx{grid-template-columns:1fr;gap:28px}.mx-img{aspect-ratio:4/3}.steps b{font-size:19px}
  .apply{grid-template-columns:1fr}.formcard{padding:22px}.frow2{grid-template-columns:1fr}.aside{position:static}.stage-h{font-size:24px}
  .story .m{height:340px}
  .partner,.visit{grid-template-columns:1fr}.partner>.ph{min-height:260px}.visit>.ph{min-height:240px}.mapbox{min-height:320px}
  .nxs{grid-template-columns:1fr}.nx{min-height:180px;padding:24px}.nx b{font-size:24px}
  .band{padding-block:72px}
  .mission{display:flex;flex-direction:column;min-height:0;overflow:visible}.mission>.ph{min-height:240px}.mission .txt{margin:16px 0 0;padding:24px;background:var(--sand);font-size:18px}
  .posts{grid-template-columns:1fr}.posts a{flex-direction:column;align-items:stretch;gap:16px;padding:16px 16px 24px}.posts .th{order:-1;width:100%;max-width:100%}.posts .tx{padding-inline:8px}.info{padding:24px}
  footer .cols{grid-template-columns:1fr 1fr}footer .col:first-child{grid-column:1/-1}
}
@media (max-width:560px){.ocs{grid-template-columns:1fr}}
@media (max-width:700px){
  .trackbox{overflow:visible}.track{display:flex;flex-direction:column;gap:8px;min-width:0}.station{display:none}
  .bar{display:grid;grid-template-columns:4.4rem minmax(0,1fr);column-gap:10px;align-items:center;min-height:0!important;padding:11px 14px!important;border-radius:12px!important}
  .bar::before{content:attr(data-range);grid-row:1/span 2;font-size:.8rem;font-weight:500}
  .bar strong,.bar small{grid-column:2;white-space:normal}.bar.single{margin-right:0}.bar.gap{margin-top:6px}
  .bar.main{border-radius:0!important;margin-top:-8px}.bar.main.first{border-radius:12px 12px 0 0!important;margin-top:0}.bar.main.last{border-radius:0 0 12px 12px!important}
  .bar.main+.bar.main{box-shadow:inset 0 1px 0 rgba(255,255,255,.55)}
  .pcards{grid-template-columns:1fr}
  .brand b{font-size:14px}
}
@media (max-width:380px){.brand b{display:none}}
@media (prefers-reduced-motion:reduce){.mq-t{animation:none;flex-wrap:wrap;width:auto;justify-content:center}.mq-t .lg:nth-child(n+11){display:none}.view.on{animation:none}.js .appear,.js .trackbox .bar,.js .bubble,.js .h1 .w{opacity:1!important;transform:none!important;transition:none!important;animation:none!important}}
'''

JS = r'''
(function(){
  var reduce = window.matchMedia && matchMedia('(prefers-reduced-motion: reduce)').matches, hasIO = 'IntersectionObserver' in window;
  var views = {}, cur = null, T0 = document.title;  /* 첫 화면 제목은 검색용 제목 그대로 */
  Array.prototype.forEach.call(document.querySelectorAll('.view'), function(v){ views[v.dataset.view] = v; });

  /* 숫자 카운트업 2초 */
  function countUp(el){
    if (reduce) return; var to = +el.dataset.to, t0 = null;
    (function step(t){ if (!t0) t0 = t; var p = Math.min(1, (t - t0) / 2000); el.textContent = Math.round(to * (p >= 1 ? 1 : 1 - Math.pow(2, -10 * p))); if (p < 1) requestAnimationFrame(step); })(performance.now());
  }
  /* 등장 효과: 20px 아래에서 0.8초, 같은 순간에 들어온 것끼리 0.08초 간격 */
  var io = (hasIO && !reduce) ? new IntersectionObserver(function(ents){
    var k = 0;
    ents.forEach(function(en){
      if (!en.isIntersecting) return; var t = en.target;
      if (t.classList.contains('appear')) { t.style.setProperty('--i', k++); t.classList.add('seen'); }
      if (t.classList.contains('trackbox') || t.classList.contains('panel') || t.classList.contains('map')) t.classList.add('in');
      if (t.classList.contains('cu')) countUp(t);
      io.unobserve(t);
    });
  }, { rootMargin: '0px 0px -12% 0px' }) : null;
  function arm(v){
    Array.prototype.forEach.call(v.querySelectorAll('.appear,.trackbox,.panel,.map,.cu'), function(e){
      if (io) { e.classList.remove('seen'); e.classList.remove('in'); if (e.classList.contains('cu')) e.textContent = '0'; io.observe(e); }
      else { e.classList.add('seen'); e.classList.add('in'); }
    });
    var h = v.querySelector('.h1'); if (h) { h.classList.remove('go'); void h.offsetWidth; h.classList.add('go'); }
  }
  /* 페이지 바꾸기: #주소가 페이지 이름이면 그 페이지, 페이지 안의 칸 이름이면 그 페이지를 열고 그 칸으로 */
  function show(name){
    if (cur === name) return false;
    Object.keys(views).forEach(function(k){ views[k].classList.toggle('on', k === name); });
    Array.prototype.forEach.call(document.querySelectorAll('[data-nav]'), function(a){
      if (a.dataset.nav === name) a.setAttribute('aria-current', 'page'); else a.removeAttribute('aria-current');
    });
    cur = name; arm(views[name]); document.title = name === 'home' ? T0 : views[name].dataset.title;
    return true;
  }
  function route(){
    var h = decodeURIComponent(location.hash.slice(1)) || 'home', name = h, target = null;
    if (!views[h]) { var el = document.getElementById(h); if (el && el.closest('.view')) { name = el.closest('.view').dataset.view; target = el; } else name = 'home'; }
    var changed = show(name);
    document.body.classList.remove('menu-open');
    requestAnimationFrame(function(){
      if (target) window.scrollTo({ top: target.getBoundingClientRect().top + window.scrollY - 72, behavior: changed ? 'auto' : 'smooth' });
      else window.scrollTo(0, 0);
    });
  }
  window.addEventListener('hashchange', route); route();

  /* 신청서: 필수 항목을 확인하고 학원 구글 시트(Apps Script)로 보낸다 */
  var form = document.getElementById('applyForm');
  if (form) {
    form.elements['phone'].addEventListener('input', function(){
      var d = this.value.replace(/\D/g, '').slice(0, 11);
      this.value = d.length > 7 ? d.replace(/(\d{3})(\d{3,4})(\d{4})/, '$1-$2-$3') : d.length > 3 ? d.slice(0, 3) + '-' + d.slice(3) : d;
    });
    form.addEventListener('change', function(e){
      var t = e.target; if (t.name !== 'exp' || !t.checked) return;
      Array.prototype.forEach.call(form.querySelectorAll('input[name=exp]'), function(i){ if (i !== t && (t.value === '처음이에요' || i.value === '처음이에요')) i.checked = false; });
    });
    form.addEventListener('submit', function(e){
      e.preventDefault();
      var f = form.elements, err = document.getElementById('ferr'), btn = document.getElementById('fsubmit'), miss = [];
      function picked(n){ return Array.prototype.map.call(form.querySelectorAll('input[name=' + n + ']:checked'), function(i){ return i.value; }).join(', '); }
      var d = { name: f['name'].value.trim(), grade: f['grade'].value, phone: f['phone'].value.trim(), exp: picked('exp'), days: picked('days'), times: picked('times'),
                memo: f['memo'].value.trim(), website: f['website'].value, confirm: f['confirm'].checked, agree: f['agree'].checked, page: location.pathname + '#sample' };
      if (!d.name) miss.push('학생 이름'); if (!d.grade) miss.push('학년');
      if (!/^01\d-?\d{3,4}-?\d{4}$/.test(d.phone)) miss.push('보호자 연락처');
      if (!d.exp) miss.push('코딩·로봇 경험'); if (!d.days) miss.push('가능한 요일'); if (!d.times) miss.push('희망 시간대');
      if (!d.confirm) miss.push('안내 확인'); if (!d.agree) miss.push('개인정보 동의');
      if (miss.length) { err.textContent = '아래 항목을 확인해 주세요: ' + miss.join(', '); return; }
      err.textContent = ''; btn.disabled = true; btn.textContent = '보내는 중…';
      fetch(window.FORM_ENDPOINT, { method: 'POST', body: JSON.stringify(d) })
        .then(function(r){ return r.json(); })
        .then(function(res){
          if (!res || !res.ok) throw new Error('fail');
          form.hidden = true; document.getElementById('applyDone').hidden = false;
          if (window.gtag) gtag('event', 'generate_lead', { form_name: 'sample_class' });
        })
        .catch(function(){
          btn.disabled = false; btn.textContent = '신청하기';
          err.textContent = '신청을 보내지 못했습니다. 잠시 후 다시 시도하시거나 02-444-1854로 전화 주세요.';
        });
    });
  }
  /* 작은 화면 메뉴 */
  document.querySelector('.menu').addEventListener('click', function(){
    var o = document.body.classList.toggle('menu-open'); this.setAttribute('aria-expanded', o ? 'true' : 'false');
  });

  /* 대회 로고: 보이는 칸보다 많으면 2초마다 한 칸씩 1초 동안 교체 (사나 첫 화면 값) */
  var pool = window.LOGO_POOL || [], slots = Array.prototype.slice.call(document.querySelectorAll('#logos .slot'));
  function key(h){ var m = /(?:alt|data-alt)="([^"]*)"/.exec(h); return m ? m[1] : h; }
  if (!reduce) setInterval(function(){
    var vis = slots.filter(function(s){ return s.offsetParent !== null; });
    var shown = vis.map(function(s){ return key(s.innerHTML); });
    var rest = pool.filter(function(h){ return shown.indexOf(key(h)) < 0; });
    if (!vis.length || !rest.length) return;
    var s = vis[Math.floor(Math.random() * vis.length)]; s.classList.add('hide');
    setTimeout(function(){ s.innerHTML = rest[Math.floor(Math.random() * rest.length)]; s.classList.remove('hide'); }, 1000);
  }, 2000);

  /* 카드 슬라이더: 진행 막대가 차면 한 장 넘김 */
  Array.prototype.forEach.call(document.querySelectorAll('.slider'), function(sl){
    var rail = sl.querySelector('.rail'), bar = sl.querySelector('.bar2'), btn = sl.querySelector('.toggle');
    var D = +sl.dataset.auto || 5000, playing = !reduce, inView = false, acc = 0, last = performance.now();
    var PAUSE = btn.innerHTML, PLAY = '<svg viewBox="0 0 10 10"><path d="M2 1l7 4-7 4z"/></svg>';
    function set(){ btn.innerHTML = playing ? PAUSE : PLAY; btn.setAttribute('aria-label', playing ? '자동 넘김 멈춤' : '자동 넘김 시작'); }
    btn.addEventListener('click', function(){ playing = !playing; set(); });
    rail.addEventListener('pointerdown', function(){ playing = false; set(); });
    if (hasIO) new IntersectionObserver(function(e){ inView = e[0].isIntersecting; }).observe(sl);
    function next(){
      var items = Array.prototype.slice.call(rail.children), x = rail.scrollLeft, target = 0;
      for (var k = 0; k < items.length; k++) { var off = items[k].offsetLeft - rail.firstElementChild.offsetLeft; if (off > x + 4) { target = off; break; } }
      if (rail.scrollLeft + rail.clientWidth >= rail.scrollWidth - 4) target = 0;
      rail.scrollTo({ left: target, behavior: 'smooth' });
    }
    (function tick(now){
      if (playing && inView) { acc += now - last; if (acc >= D) { acc = 0; next(); } }
      last = now; bar.style.setProperty('--p', (acc / D * 100).toFixed(1) + '%');
      requestAnimationFrame(tick);
    })(performance.now());
  });
})();
'''

def ctrl():
    return ('<div class="ctrl"><span class="prog"><span class="bar2"></span>' + '<i class="dot"></i>' * 3 + '</span>'
            '<button type="button" class="toggle" aria-label="자동 넘김 멈춤"><svg viewBox="0 0 10 10"><rect x="1.5" y="1" width="2.4" height="8"/><rect x="6.1" y="1" width="2.4" height="8"/></svg></button></div>')

def photo_card(img_key, fallback, eye, title, sub, more_text, more_href, pos='center', side=''):
    bg = f' style="background-image:url({GEN[img_key]});background-position:{pos}"' if img_key in GEN else (f' style="background-image:url({IMG[fallback]});background-position:{pos}"' if fallback else '')
    return (f'<div class="proof{" r" if side else ""} appear"{bg}><div class="pt"><p class="eye">{eye}</p><h3>{title}</h3>'
            f'<p class="cap">{sub}</p>{btns(SAMPLE, go(more_text, more_href, "white"))}</div></div>')

def home():
    items = [f'<img src="{LG["koi"]}" alt="정보올림피아드" style="height:46px">',
             f'<img src="{LG["fll"]}" alt="FIRST LEGO League" style="height:36px">',
             f'<img src="{LG["robocup"]}" alt="로보컵" style="height:50px">',
             f'<img src="{LG["robotex"]}" alt="로보텍스" style="height:34px">',
             f'<img src="{LG["wro"]}" alt="WRO" style="height:36px">',
             f'<img src="{LG["vexiq"]}" alt="VEX IQ 로보틱스 컴피티션" style="height:46px">',
             f'<img src="{LG["iro"]}" alt="국제로봇올림피아드(IRO)" style="height:60px">',
             f'<img src="{LG["nypc"]}" alt="NYPC" style="width:132px">',
             f'<img src="{LG["esw"]}" alt="임베디드 소프트웨어 경진대회" style="width:140px">',
             f'<img src="{LG["kcf"]}" alt="한국코드페어" style="width:132px">',
             f'<img src="{LG["itc"]}" alt="청소년 IT 경시대회" style="height:56px">']
    logos = ''.join(f'<div class="slot">{t}</div>' for t in items[:6])
    five = ''.join(f'<div class="f{k+1}" style="background:var(--s{k+1})"><i>{e}</i><b>{a}</b><span>{d}</span></div>' for k, (a, e, d) in enumerate(FIVE))
    play = '<span class="play"><svg viewBox="0 0 24 24"><path d="M6 4l14 8-14 8z"/></svg></span>'
    # 히어로 영상: 우리 NAS 영상 + 펙셀스(무료 라이선스) 영상을 펙셀스 색감으로 맞춰 이어 붙인 것 (2026-10-03)
    video = ('<video class="hero-video" autoplay muted loop playsinline preload="auto" poster="img/d/hero-poster.jpg" '
             'aria-label="유치부 코딩 로봇부터 아두이노와 대회까지 이어지는 수업 장면">'
             '<source src="img/d/hero-720.mp4" type="video/mp4" media="(max-width: 700px)"><source src="img/d/hero.mp4" type="video/mp4"></video>')
    return f'''
<div class="view" data-view="home" data-title="스타랩코딩학원 광진점">
<section class="hero"><div class="cols">
  <div class="head">
    <p class="eye">스타랩코딩학원 광진점</p>
    {h1w('<em>피지컬</em> <em>AI</em> <em>시대</em>,<br>준비는 지금부터입니다.')}
    <p class="sub">로봇코딩부터 파이썬·C언어, 입시 준비까지<br>하나의 과정으로 이어집니다.</p>
    {btns(SAMPLE, go('커리큘럼 보기', '#curriculum'))}
  </div>
  <div class="hero-media appear">{video}</div>
  <div class="logos" id="logos" aria-label="출전·수상 대회">{logos}</div><script>window.LOGO_POOL={json.dumps(items)};</script>
</div></section>

<section class="sand prod"><div class="cols">
  {head('커리큘럼', '유치부터 대입까지,<br>끊김 없는 로드맵', '600차시에 달하는 빈틈없는 커리큘럼으로<br>언제, 어떤 수준으로 와도 딱 맞는 자리에서 소수정예로 시작합니다.', btns(SAMPLE, go('커리큘럼 보기', '#curriculum')))}
  <div class="card appear">{roadmap()}</div>
</div></section>

<section class="proofsec" style="padding-top:16px"><div class="cols">
  {photo_card('', 'hero.jpg', '대회·실적', '6년 연속 전국대회 수상,<br>10회 이상 세계대회 진출', '2025 로보텍스·MRC 코리아 인터내셔널 대회에 출전한 스타랩 선수단', '대회·실적 보기', '#record', 'center 62%')}
</div></section>

<section class="hmethod"><div class="cols">
  {head('수업 방식', '설명을 듣고 따라 만드는<br>수업이 아닙니다', '학생이 직접 코드를 짜고, 로봇을 돌려 보고,<br>틀린 곳을 스스로 고칩니다.')}
  <figure class="device appear"><img src="{IMG['method.jpg']}" alt="스파이크 에센셜로 만든 로봇을 태블릿 블록코딩으로 움직이는 수업"></figure>
  <div class="five appear">{five}</div>
  <p class="five-p appear">생각을 코드로 옮기고 결과를 보고 다시 판단하는 연습으로, 창의력과 끝까지 풀어내는 문제해결력, 함께 완성하는 협업능력을 기릅니다.</p>
  <div class="center appear">{btns(SAMPLE, go('커리큘럼 보기', '#curriculum'))}</div>
</div></section>

{band()}
</div>'''

def course_row(k, flip):
    name, who, desc, items = COURSES[k]
    kind, a, b = MEDIA[k]
    if kind == 'ui' and a in SHOT:
        media = f'<img class="shot" src="{SHOT[a]}" alt="{SHOT_ALT[a]}" style="object-position:left top">'
    elif kind == 'ui':
        media = UI[a]()
    elif kind == 'img':
        media = f'<img src="{IMG[a]}" alt="{b}"' + (' style="object-position:center 45%"' if a == 'expo.jpg' else '') + '>'
    elif a in GEN:
        media = f'<img src="{GEN[a]}" alt="{b}">'
    else:
        media = ph(b)
    lis = ''.join(f'<li><b>{t}</b><span>{d}</span></li>' for t, d in items)
    return (f'<article class="course{" flip" if flip else ""}" id="c-{SLUG[k]}">'
            f'<div class="ct appear"><span class="range">{who}</span><h3>{name}</h3><p class="desc">{desc}</p><ul>{lis}</ul>'
            f'<div class="acts">{SAMPLE}</div></div><div class="cm appear">{media}</div></article>')

def curriculum():
    five = ''.join(f'<div class="f{k+1}" style="background:var(--s{k+1})"><i>{e}</i><b>{a}</b><span>{d}</span></div>' for k, (a, e, d) in enumerate(FIVE))
    chips = ''.join(f'<a class="chip" href="#s-{sid}">{label}</a>' for sid, label, _, _ in STAGES)
    groups, n = '', 0
    for sid, label, mains, _ in STAGES:
        rows = ''
        for c in mains:
            rows += course_row(c, n % 2 == 1); n += 1
        groups += f'<div class="stage" id="s-{sid}"><h2 class="stage-h appear"><i></i>{label}</h2>{rows}</div>'
    opts = ''
    for k, (a, w, d) in enumerate(OPTS):
        key = OPT_IMG[k]
        m = (f'<img src="{SHOT[key]}" alt="{SHOT_ALT[key]}"' + (' class="shot" style="object-position:left top"' if key != 'prep' else '') + '>') if key in SHOT else UI[key]()
        note = f'<span class="note2">{OPT_NOTE[k]}</span>' if OPT_NOTE[k] else ''
        opts += f'<article class="oc appear" id="c-opt{k}"><div class="om">{m}</div><span class="range">{w}</span><b>{a}</b><span class="od">{d}</span>{note}</article>'
    return f'''
<div class="view" data-view="curriculum" data-title="커리큘럼 · 스타랩코딩학원 광진점">
<section class="phero"><div class="cols">
  {phero('커리큘럼', '유치부터 대입까지,<br>끊김 없는 로드맵', '600차시에 달하는 빈틈없는 커리큘럼으로<br>언제, 어떤 수준으로 와도 딱 맞는 자리에서 소수정예로 시작합니다.', btns(SAMPLE))}
  <nav class="chips appear" aria-label="단계 바로가기">{chips}</nav>
</div></section>
<section class="courses"><div class="cols">{groups}</div></section>
<section class="sand" id="optional"><div class="cols">
  {head('', '선택 과정', '', btns(SAMPLE))}
  <div class="ocs">{opts}</div>
</div></section>
<section id="method" style="scroll-margin-top:56px"><div class="cols">
  {head('수업 방식', '설명을 듣고 따라 만드는<br>수업이 아닙니다', '학생이 직접 코드를 짜고, 로봇을 돌려 보고,<br>틀린 곳을 스스로 고칩니다.', btns(SAMPLE))}
  <figure class="device appear"><img src="{IMG['method.jpg']}" alt="스파이크 에센셜로 만든 로봇을 태블릿 블록코딩으로 움직이는 수업"></figure>
  <div class="five appear">{five}</div>
  <p class="five-p appear">생각을 코드로 옮기고 결과를 보고 다시 판단하는 연습으로, 창의력과 끝까지 풀어내는 문제해결력, 함께 완성하는 협업능력을 기릅니다.</p>
</div></section>
{nexts('record', 'stories')}
{band()}
</div>'''

def method():
    five = ''.join(f'<div class="f{k+1}" style="background:var(--s{k+1})"><i>{e}</i><b>{a}</b><span>{d}</span></div>' for k, (a, e, d) in enumerate(FIVE))
    sk = lambda w, o='': f'<div class="sk {o}" style="width:{w}%"></div>'
    cmp_rows = ''.join(f'<div>{sk(55)}</div><div>{sk(90)}{sk(60)}</div><div>{sk(85, "o")}{sk(70, "o")}</div>' for _ in range(5))
    quotes = ''.join(f'<article class="quote"><div class="q"><b>자리 비워 둠</b><span>학부모 후기 문장 — 실제 후기에서 발췌, 게재 동의 받은 것만</span></div>'
                     f'<div class="who"><i></i><span>이름 자리 (예: ○학년 학부모)</span><span>수강 과정 자리</span></div></article>' for _ in range(4))
    data = (ph('설문 데이터 ①', '레고 에듀케이션 교사 설문 보고서에서 고른 수치 · 출처 함께 표기')
            + ph('설문 데이터 ②', '어느 항목을 넣을지는 원장님이 정한 뒤 채움')
            + ph('설문 데이터 ③', '숫자는 크게, 설명은 한 줄'))
    return f'''
<div class="view" data-view="method" data-title="수업 방식 · 스타랩코딩학원 광진점">
<section class="phero"><div class="cols">
  {phero('수업 방식', '설명을 듣고 따라 만드는<br>수업이 아닙니다', '학생이 직접 코드를 짜고, 로봇을 돌려 보고,<br>틀린 곳을 스스로 고칩니다.', btns(SAMPLE))}
</div></section>
<section style="padding-top:0"><div class="cols">
  <figure class="device appear"><img src="{IMG['method.jpg']}" alt="스파이크 에센셜로 만든 로봇을 태블릿 블록코딩으로 움직이는 수업"></figure>
  <div class="five appear">{five}</div>
  <p class="five-p appear">생각을 코드로 옮기고 결과를 보고 다시 판단하는 연습으로, 창의력과 끝까지 풀어내는 문제해결력, 함께 완성하는 협업능력을 기릅니다.</p>
</div></section>
<section style="padding-top:40px"><div class="cols">
  {head('비교', '<span class="ph-t">제목 자리 · 따라 만드는 수업과 다른 점</span>', '', btns(SAMPLE))}
  <div class="cmp appear" aria-hidden="true">
    <div class="hd"></div><div class="hd">따라 만드는 수업</div><div class="hd on">스타랩 수업</div>
    {cmp_rows}
    <div class="cmp-note">{ph('비교표: 흔한 "설명 듣고 따라 만드는 수업"과 스타랩 수업을 항목별로 나란히', '항목 4~5줄 (예: 수업 시작, 막혔을 때, 수업이 끝나면). 문구는 원장님과 정해서 채움')}</div>
  </div>
</div></section>
<section class="sand"><div class="cols">
  {head('데이터', '<span class="ph-t">제목 자리 · 왜 이런 수업이어야 하는지</span>', '<span class="ph-t">설명 자리 · 한두 줄</span>')}
  <div class="data appear">{data}</div>
</div></section>
<section style="padding-bottom:0"><div class="cols">{head('학부모 후기', '<span class="ph-t">제목 자리 · 후기 섹션 문구</span>', '', btns(SAMPLE))}</div></section>
<section class="sand reviews"><div class="slider appear" data-auto="6000"><div class="rail">{quotes}</div>{ctrl()}</div></section>
{nexts('record', 'stories')}
{band()}
</div>'''

def record():
    one = ''.join(f'<div class="lg"><img src="{LG[lg]}" alt="{name}" style="{"height" if d == "h" else "width"}:{v}px"></div>' for name, lg, d, v in LOGOS)
    two = one.replace('alt="', 'aria-hidden="true" alt="')
    logos = f'<div class="mq" aria-label="출전 대회"><div class="mq-t">{one}{two}</div></div>'
    cards = ''.join(f'<article><p class="ae">{n}<i>{y}</i></p><p class="ar2">{r}</p><p class="as">{d}</p></article>'
                    for y, n, r, d in AWARDS)
    more = ''
    for y, rows in MORE:
        lis = ''.join(f'<li><b>{n}' + (f' <small>· {p}</small>' if p else '') + f'</b><span>{r}</span></li>' for n, p, r in rows)
        more += f'<div class="yr"><b>{y}</b><ul>{lis}</ul></div>'
    return f'''
<div class="view" data-view="record" data-title="대회·실적 · 스타랩코딩학원 광진점">
<section class="phero"><div class="cols">
  {phero('대회·실적', '실적으로 증명합니다', '로봇대회, 공모전, 경시대회까지<br>스타랩 학생들이 직접 거둔 성과입니다.', btns(SAMPLE))}
</div></section>
<section class="mqsec appear">{logos}</section>
<section style="padding-top:48px;padding-bottom:72px"><div class="cols">
  <ul class="stats appear" aria-label="한눈에 보기">
    <li><b><span class="cu" data-to="6">6</span>년 연속</b><span>전국대회 수상</span></li>
    <li><b><span class="cu" data-to="10">10</span>회+</b><span>세계대회 진출</span></li>
    <li><b><span class="cu" data-to="600">600</span>차시</b><span>유치부터 고3까지 잇는 커리큘럼</span></li>
    <li><b><span class="cu" data-to="400">400</span>명+</b><span>누적 수강생</span></li>
  </ul>
</div></section>
<section class="sand" style="padding-bottom:80px"><div class="cols">
  {head('', '주요 수상 이력', '', btns(SAMPLE))}
  <div class="aw appear">{cards}</div>
  <p class="aw-sum appear"><b>2021–2026, 6개년 연속 세계대회 진출</b></p>
</div></section>
<section style="padding-bottom:72px"><div class="cols">
  {head('', '그 밖의 수상 내역', '')}
  <div class="more appear">{more}</div>
</div></section>
{nexts('stories', 'curriculum')}
{band()}
</div>'''

def stories():
    return f'''
<div class="view" data-view="stories" data-title="학원 소식 · 스타랩코딩학원 광진점">
<section class="phero"><div class="cols">
  {phero('학원 소식', '학원 소식', '상담에서 자주 받는 질문과 수업 이야기를 정리합니다.')}
</div></section>
<section style="padding-top:24px"><div class="cols">
  <div class="appear">{POSTS}</div>
  <p class="center">{go('전체 글 보기', 'posts/')}</p>
</div></section>
{nexts('curriculum', 'record')}
{band()}
</div>'''

def chk(name, items, cls=''):
    return '<div class="tg">' + ''.join(f'<label class="t"><input type="checkbox" name="{name}" value="{v}"><span>{v}</span></label>' for v in items) + '</div>'

def sample():
    grades = ''.join(f'<option>{g}</option>' for g in ['초1', '초2', '초3', '초4', '초5', '초6', '중1', '중2', '중3'])
    form = f'''<form class="af" id="applyForm" novalidate>
      <div class="frow2">
        <label class="fd"><span class="fl">학생 이름<em>필수</em></span><input type="text" name="name" maxlength="30" autocomplete="off" required></label>
        <label class="fd"><span class="fl">학년<em>필수</em></span><select name="grade" required><option value="">선택해 주세요</option><option value="7세">유치부</option>{grades}</select></label>
      </div>
      <label class="fd"><span class="fl">보호자 연락처<em>필수</em></span><input type="tel" name="phone" inputmode="numeric" placeholder="010-0000-0000" maxlength="13" required></label>
      <div class="fd"><span class="fl">코딩·로봇 경험<em>필수</em></span>{chk('exp', ['처음이에요', '엔트리·스크래치', '로봇코딩', '파이썬·C언어'])}<p class="hint">해 본 것을 모두 골라 주세요.</p></div>
      <div class="fd"><span class="fl">가능한 요일<em>필수</em></span>{chk('days', ['화', '수', '목', '금', '토'])}<p class="hint">여러 요일을 고를 수 있습니다. 일요일과 월요일에는 샘플클래스를 하지 않습니다.</p></div>
      <div class="fd"><span class="fl">희망 시간대<em>필수</em></span>{chk('times', ['오전 10~12시', '오후 1~3시', '오후 3~5시', '오후 5~7시', '저녁 7시 이후'])}<p class="hint">오전은 토요일, 저녁 7시 이후는 평일만 가능합니다.</p></div>
      <label class="fd"><span class="fl">남기실 말씀</span><textarea name="memo" maxlength="500" placeholder="궁금한 점이나 미리 알려 주실 내용을 적어 주세요."></textarea></label>
      <div class="agree">
        <ul><li>샘플클래스는 초등·중등 90분, 유치부 60분이며, 참가비는 30,000원입니다. 정규과정에 등록하시면 수강료에서 전액 차감합니다.</li>
        <li>수업 시간 조율을 위해 남겨 주신 학부모님 연락처로 전화나 문자를 드릴 수 있습니다.</li></ul>
        <label class="ck"><input type="checkbox" name="confirm"><span>위 내용을 확인했습니다 <em>필수</em></span></label>
      </div>
      <div class="agree">
        <dl><dt>수집 항목</dt><dd>학생 이름, 학년, 보호자 연락처, 코딩·로봇 경험, 가능한 요일과 시간대, 남기신 말씀</dd>
        <dt>이용 목적</dt><dd>샘플클래스 일정 안내, 상담과 상담 이력 관리</dd>
        <dt>보유 기간</dt><dd>상담 이력으로 보관하며, 삭제를 요청하시면 바로 파기합니다</dd></dl>
        <p class="hint">동의하지 않으셔도 됩니다. 이 경우 온라인 신청은 어렵고, 전화(02-444-1854)로 신청하실 수 있습니다.</p>
        <label class="ck"><input type="checkbox" name="agree"><span>개인정보 수집·이용에 동의합니다 <em>필수</em></span></label>
      </div>
      <div class="hp" aria-hidden="true"><label>웹사이트<input type="text" name="website" tabindex="-1" autocomplete="off"></label></div>
      <p class="ferr" id="ferr" role="alert"></p>
      <div class="fsub"><button class="pill big" type="submit" id="fsubmit">신청하기</button><span>확인 후 남겨 주신 번호로 전화드립니다.</span></div>
    </form>
    <div class="done" id="applyDone" hidden><span class="dk" aria-hidden="true">✓</span><h3>신청이 접수되었습니다</h3><p>확인 후 남겨 주신 번호로 전화드려 수업 시간을 안내해 드립니다.<br>급하시면 02-444-1854로 전화 주세요.</p>{go('첫 페이지로', '#home')}</div>'''
    aside = '''<aside class="aside"><h3>샘플클래스 안내</h3>
      <dl class="ad"><dt>대상</dt><dd>유치부 · 초등학생 · 중학생<small>코딩 경험이 없어도 됩니다</small></dd><dt>시간</dt><dd>90분<small>유치부는 60분</small></dd>
      <dt>참가비</dt><dd>30,000원<small>정규과정 등록 시 수강료에서 전액 차감</small></dd></dl>
      <dl class="ad hrs"><dt>화~금</dt><dd>13:00 ~ 20:30</dd><dt>토</dt><dd>10:00 ~ 17:00</dd><dt>일·월</dt><dd>샘플클래스 없음</dd></dl>
      <p>전화로 신청하셔도 됩니다.</p><a class="pill ghost" href="tel:024441854">전화 02-444-1854</a></aside>'''
    return f'''
<div class="view" data-view="sample" data-title="샘플클래스 신청 · 스타랩코딩학원 광진점">
<section class="phero"><div class="cols">
  {phero('샘플클래스', '처음이라면,<br>샘플클래스로 먼저 경험해 보세요', '신청을 남겨 주시면 확인 후 전화로 수업 시간을 안내해 드립니다.')}
</div></section>
<section style="padding-top:0"><div class="cols"><div class="apply appear"><div class="formcard">{form}</div>{aside}</div></div></section>
<section id="faq" style="padding-top:40px;scroll-margin-top:56px"><div class="cols">
  {head('', '자주 묻는 질문')}
{FAQ}
</div></section>
<section id="visit" style="padding-top:40px;scroll-margin-top:56px"><div class="cols">
  {head('', '오시는 길')}
  <div class="visit appear">
{INFO}
    <div class="mapbox"><iframe title="스타랩코딩학원 광진점 위치 지도" src="https://maps.google.com/maps?q=%EC%8A%A4%ED%83%80%EB%9E%A9%EC%BD%94%EB%94%A9%ED%95%99%EC%9B%90%20%EA%B4%91%EC%A7%84%EC%A0%90&amp;z=17&amp;hl=ko&amp;output=embed" loading="lazy" referrerpolicy="no-referrer-when-downgrade" allowfullscreen></iframe></div>
  </div>
</div></section>
</div>'''

def page(HEAD, ENDPOINT):
    nav = [('curriculum', '커리큘럼'), ('record', '대회·실적'), ('stories', '학원 소식')]
    navh = ''.join(f'<a href="#{k}" data-nav="{k}">{t}</a>' for k, t in nav) + '<a href="#visit">오시는 길</a>'
    mnav = ''.join(f'<a href="#{k}" data-nav="{k}">{t}</a>' for k, t in nav) + '<a href="#sample" data-nav="sample">샘플클래스</a><a href="#visit">오시는 길</a><a class="tel2" href="tel:024441854">전화 02-444-1854</a>'
    fcur = ''.join(f'<a href="#c-{SLUG[k]}">{c[0]}</a>' for k, c in enumerate(COURSES))
    return f'''<!doctype html>
<html lang="ko">
<head>
{HEAD}
<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/pretendard@1.3.9/dist/web/variable/pretendardvariable-dynamic-subset.min.css">
<script>document.documentElement.className+=' js';window.FORM_ENDPOINT={json.dumps(ENDPOINT)}</script>
<style>{CSS}</style>
</head>
<body>
<header class="top"><div class="cols">
  <a class="brand" href="#home"><img src="{IMG['logo.png']}" alt=""><b>스타랩코딩학원</b></a>
  <nav class="nav" aria-label="주요 메뉴">{navh}</nav>
  <div class="right"><a class="tel" href="tel:024441854">02-444-1854</a>{SAMPLE}
    <button type="button" class="menu" aria-label="메뉴" aria-expanded="false"><svg viewBox="0 0 24 24"><path d="M4 7h16 M4 12h16 M4 17h16"/></svg></button></div>
</div><nav class="mnav" aria-label="메뉴">{mnav}</nav></header>
<main>
{home()}
{curriculum()}
{record()}
{stories()}
{sample()}
</main>
<footer><div class="cols">
  <div class="col"><img src="{IMG['logo.png']}" alt="스타랩코딩학원"><p>스타랩코딩학원 광진점</p><p style="color:var(--g5)">서울특별시 광진구 광나루로 602 대한빌딩 2층 201호</p><p style="color:var(--g5)">학원등록번호 제2310호 · 서울특별시광진교육지원청</p></div>
  <div class="col"><p class="fh">커리큘럼</p>{fcur}</div>
  <div class="col"><p class="fh">학원</p><a href="#method">수업 방식</a><a href="#record">대회·실적</a><a href="#c-opt3">경진대회 준비반</a><a href="#stories">학원 소식</a></div>
  <div class="col"><p class="fh">문의</p><a href="#sample">샘플클래스 신청</a><a href="#faq">자주 묻는 질문</a><a href="#visit">오시는 길</a><a href="tel:024441854">02-444-1854</a></div>
  <div class="col"><p class="fh">채널</p><a href="https://blog.naver.com/starlab_gwangjin">스타랩 광진 블로그</a><a href="http://pf.kakao.com/_jixhQG">카카오톡 채널</a><a href="https://star-lab.co.kr">스타랩 본사</a></div>
  <p class="copy"><span>© 스타랩코딩학원 광진점</span><span>02-444-1854</span></p>
</div></footer>
<script>{JS}</script>
</body>
</html>
'''

