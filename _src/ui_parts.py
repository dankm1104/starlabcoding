# 사진 대신 넣는 수업 화면 UI (파이썬·AI 로보틱스, 앱인벤터, AX, 파이썬 알고리즘, 경진대회 준비반)
# 상자 폭에 맞춰 커지고 작아지도록 글자 크기를 cqw(상자 폭 기준)로 잡는다

UI_CSS = r'''
.ui{position:relative;width:100%;height:100%;container-type:inline-size;background:linear-gradient(155deg,#FEF1E2 0%,#FBD9AE 100%);display:flex;align-items:center;justify-content:center;overflow:hidden}
.ui *{box-sizing:border-box}
.win{position:relative;background:#fff;border-radius:2cqw;box-shadow:0 2.2cqw 6cqw rgba(166,86,5,.22),0 .3cqw .8cqw rgba(0,0,0,.06);overflow:hidden;font-size:2.3cqw;line-height:1.5;color:#1C1C1E}
.win .tbar{height:6.2cqw;display:flex;align-items:center;gap:1.1cqw;padding:0 2.4cqw;background:#F6F5F4;border-bottom:1px solid rgba(0,0,0,.06)}
.win .tbar i{width:1.5cqw;height:1.5cqw;border-radius:50%;background:#E2DED9}
.win .tbar b{margin-left:1.4cqw;font-weight:600;font-size:2.1cqw;color:#5E5F63}
.win .tbar em{margin-left:auto;font-style:normal;font-size:1.9cqw;font-weight:600;color:#A65605;background:#FEF1E2;border-radius:3cqw;padding:.4cqw 1.6cqw}
.code{font-family:ui-monospace,"SF Mono",Menlo,Consolas,monospace;font-size:2.2cqw;line-height:1.75;padding:2.2cqw 2.6cqw;white-space:pre;letter-spacing:0}
.code .n{color:#BDB7AE;display:inline-block;width:3.6cqw;user-select:none}
.code .k{color:#A65605;font-weight:700}.code .s{color:#2E7D32}.code .c{color:#9A958E}.code .f{color:#1F5FBF}.code .d{color:#C2410C}
.code .hl{display:block;background:rgba(247,148,30,.14);margin:0 -2.6cqw;padding:0 2.6cqw}
.code .del{display:block;background:rgba(220,38,38,.09);margin:0 -2.6cqw;padding:0 2.6cqw;color:#9B2C2C}
.code .add{display:block;background:rgba(22,163,74,.10);margin:0 -2.6cqw;padding:0 2.6cqw;color:#166534}
.split{display:grid;grid-template-columns:62% 38%}
.side{background:#FAF9F7;border-left:1px solid rgba(0,0,0,.06);padding:2.2cqw;display:flex;flex-direction:column;gap:1.6cqw}
.side h6{margin:0;font-size:1.9cqw;font-weight:700;color:#5E5F63}
/* 파이썬·AI 로보틱스: 코드 + 카메라 인식 화면 */
.cam{position:relative;border-radius:1.4cqw;overflow:hidden;aspect-ratio:4/3;background:linear-gradient(180deg,#3B3F45 0%,#2A2D31 55%,#5B5148 56%,#4A423B 100%)}
.cam .ball{position:absolute;left:38%;top:52%;width:22%;aspect-ratio:1;border-radius:50%;background:radial-gradient(circle at 35% 35%,#FF8A80,#D32F2F 60%,#8E1B1B)}
.cam .box{position:absolute;left:33%;top:46%;width:32%;aspect-ratio:1;border:.45cqw solid #F7941E;border-radius:.6cqw}
.cam .box b{position:absolute;left:-.45cqw;top:-3.4cqw;background:#F7941E;color:#1C1C1E;font-size:1.7cqw;font-weight:700;padding:.2cqw 1cqw;border-radius:.5cqw .5cqw .5cqw 0;white-space:nowrap}
.cam .rec{position:absolute;left:1.4cqw;top:1.2cqw;font-size:1.6cqw;color:#fff;display:flex;align-items:center;gap:.8cqw}
.cam .rec::before{content:"";width:1.2cqw;height:1.2cqw;border-radius:50%;background:#EF4444}
.out{font-family:ui-monospace,Menlo,monospace;font-size:1.8cqw;background:#1C1C1E;color:#E7E5E4;border-radius:1.2cqw;padding:1.4cqw 1.6cqw;line-height:1.6}
.out span{color:#FBC489}
/* 앱인벤터: 블록 + 휴대폰 */
.ws{position:relative;padding:3cqw;min-height:46cqw;background-color:#FBFAF8;background-image:radial-gradient(rgba(0,0,0,.08) .25cqw,transparent .26cqw);background-size:3cqw 3cqw}
.ab{display:inline-flex;align-items:center;gap:1cqw;color:#fff;font-weight:600;font-size:2.1cqw;border-radius:.8cqw;padding:1cqw 1.6cqw;white-space:nowrap}
.ab .pl{background:rgba(255,255,255,.22);border-radius:.6cqw;padding:.2cqw 1cqw}
.ab .tx{background:#B6316C;border-radius:.6cqw;padding:.3cqw 1.1cqw}
.ab.ev{background:#D69A12;border-radius:.8cqw .8cqw .8cqw 0}
.ab.set{background:#3C9A3C}.ab.call{background:#6A3FA0}
.abody{border-left:2.4cqw solid #D69A12;padding:1cqw 0 1cqw 1.2cqw;display:flex;flex-direction:column;align-items:flex-start;gap:1cqw}
.abend{width:20cqw;height:2.4cqw;background:#D69A12;border-radius:0 0 .8cqw .8cqw}
.phone{position:absolute;right:5%;bottom:7%;width:27%;aspect-ratio:9/18.5;background:#1C1C1E;border-radius:3.4cqw;padding:1cqw;box-shadow:0 2cqw 5cqw rgba(0,0,0,.22)}
.phone .scr{width:100%;height:100%;background:#fff;border-radius:2.6cqw;overflow:hidden;display:flex;flex-direction:column;align-items:center;gap:2.4cqw}
.phone .tb{width:100%;background:#F7941E;color:#1C1C1E;font-weight:700;font-size:1.9cqw;padding:2.6cqw 1.6cqw 1.4cqw}
.phone .pb{margin-top:5cqw;background:#1C1C1E;color:#fff;font-size:1.8cqw;font-weight:600;border-radius:2cqw;padding:1.2cqw 2.4cqw}
.phone .pt{font-size:2.2cqw;font-weight:700}
/* AX: 코드 리뷰 */
.bub{border-radius:1.4cqw;padding:1.4cqw 1.6cqw;font-size:1.85cqw;line-height:1.55}
.bub.ai{background:#fff;border:1px solid rgba(0,0,0,.08)}
.bub.ai b{display:flex;align-items:center;gap:.8cqw;font-size:1.7cqw;color:#A65605;margin-bottom:.6cqw}
.bub.ai b::before{content:"";width:1.6cqw;height:1.6cqw;border-radius:50%;background:#F7941E}
.bub.me{background:#1C1C1E;color:#fff;align-self:flex-end;max-width:90%}
/* 파이썬 알고리즘: 그래프 + 테스트 결과 */
.graph{width:100%;aspect-ratio:1.15}
.graph line{stroke:#C9C3BB;stroke-width:1.6}
.graph circle{fill:#fff;stroke:#1C1C1E;stroke-width:1.6}
.graph circle.v{fill:#F7941E;stroke:#A65605}
.graph text{font:600 9px ui-monospace,Menlo,monospace;text-anchor:middle;dominant-baseline:central;fill:#1C1C1E}
.pass{display:flex;flex-direction:column;gap:.7cqw;font-size:1.8cqw}
.pass div{display:flex;align-items:center;gap:1cqw}
.pass div::before{content:"✓";width:2.4cqw;height:2.4cqw;border-radius:50%;background:#16A34A;color:#fff;font-size:1.5cqw;font-weight:700;display:grid;place-items:center}
/* 경진대회 준비반 */
.plist{display:flex;flex-direction:column;padding:1cqw 3cqw 2.4cqw}
.plist div{display:grid;grid-template-columns:6.4cqw 1fr auto;align-items:center;gap:2cqw;padding:2.2cqw 0;border-bottom:1px solid rgba(0,0,0,.07)}
.plist div:last-child{border-bottom:0}
.plist i{width:6.4cqw;height:6.4cqw;border-radius:50%;display:grid;place-items:center;font-style:normal;font-size:2.6cqw;font-weight:700;color:#1C1C1E}
.plist b{font-size:2.6cqw;font-weight:700;display:block}.plist small{font-size:1.9cqw;color:#5E5F63}
.plist span{font-size:1.8cqw;font-weight:600;color:#A65605;background:#FEF1E2;border-radius:3cqw;padding:.5cqw 1.6cqw}
'''

def _code(lines, start=1):
    return ''.join(f'<span class="n">{start + k}</span>{l}\n' if not l.startswith('<span class="') or 'class="n"' in l else l for k, l in enumerate(lines))

def ln(k, s, cls=''):
    body = f'<span class="n">{k}</span>{s}'
    return f'<span class="{cls}">{body}</span>' if cls else body + '\n'

def ui_python():
    k, s, c, f, d = (lambda t: f'<span class="k">{t}</span>'), (lambda t: f'<span class="s">{t}</span>'), (lambda t: f'<span class="c">{t}</span>'), (lambda t: f'<span class="f">{t}</span>'), (lambda t: f'<span class="d">{t}</span>')
    code = ''.join([
        ln(1, f'{k("from")} robot {k("import")} Robot, Camera'),
        ln(2, ''),
        ln(3, f'bot = {f("Robot")}()'),
        ln(4, f'cam = {f("Camera")}()'),
        ln(5, ''),
        ln(6, f'{k("while")} {k("True")}:'),
        ln(7, f'    obj = cam.{f("detect")}()   {c("# 물체 인식")}', 'hl'),
        ln(8, f'    {k("if")} obj.color == {s(chr(34) + "red" + chr(34))}:'),
        ln(9, f'        bot.{f("turn_to")}(obj.x)'),
        ln(10, f'        bot.{f("forward")}({d("30")})'),
        ln(11, f'    {k("else")}:'),
        ln(12, f'        bot.{f("stop")}()'),
    ])
    return (f'<div class="ui"><div class="win" style="width:90%"><div class="tbar"><i></i><i></i><i></i><b>robot_camera.py</b><em>파이썬</em></div>'
            f'<div class="split"><div class="code">{code}</div><div class="side"><h6>카메라</h6>'
            f'<div class="cam"><span class="rec">LIVE</span><span class="ball"></span><span class="box"><b>red 0.94</b></span></div>'
            f'<div class="out">&gt; detect: <span>red</span><br>&gt; turn_to(212)<br>&gt; forward(30)</div></div></div></div></div>')

def ui_appinventor():
    blocks = ('<div><span class="ab ev">when <span class="pl">Button1</span>.Click do</span>'
              '<div class="abody"><span class="ab set">set <span class="pl">Label1</span>.Text to <span class="tx">"안녕하세요!"</span></span>'
              '<span class="ab call">call <span class="pl">TextToSpeech1</span>.Speak message <span class="tx">"반가워요"</span></span></div>'
              '<div class="abend"></div></div>')
    phone = ('<div class="phone"><div class="scr"><div class="tb">나의 첫 앱</div><div class="pb">눌러 보세요</div><div class="pt">안녕하세요!</div></div></div>')
    return (f'<div class="ui"><div class="win" style="width:90%"><div class="tbar"><i></i><i></i><i></i><b>Screen1 · 블록</b><em>앱인벤터</em></div>'
            f'<div class="ws">{blocks}</div></div>{phone}</div>')

def ui_ax():
    k, s, f, c = (lambda t: f'<span class="k">{t}</span>'), (lambda t: f'<span class="s">{t}</span>'), (lambda t: f'<span class="f">{t}</span>'), (lambda t: f'<span class="c">{t}</span>')
    code = ''.join([
        ln(1, f'{k("def")} {f("count_words")}(lines):'),
        ln(2, '    result = {}'),
        ln(3, f'    {k("for")} line {k("in")} lines:'),
        ln(4, f'        words = line.{f("split")}()'),
        ln(5, f'        stop = [{s(chr(34) + "the" + chr(34))}, {s(chr(34) + "a" + chr(34))}]', 'del'),
        ln(5, f'    stop = {{{s(chr(34) + "the" + chr(34))}, {s(chr(34) + "a" + chr(34))}}}  {c("# 밖으로")}', 'add'),
        ln(6, f'        {k("for")} w {k("in")} words:'),
        ln(7, f'            {k("if")} w {k("not in")} stop:'),
        ln(8, '                result[w] = result.get(w, 0) + 1'),
        ln(9, f'    {k("return")} result'),
    ])
    side = ('<div class="side"><h6>AI 리뷰</h6>'
            '<div class="bub ai"><b>리뷰</b>5번째 줄의 목록을 반복문 안에서 매번 새로 만들고 있어요. 밖으로 빼고 집합으로 바꾸면 더 빨라져요.</div>'
            '<div class="bub me">집합으로 바꾸면 왜 더 빨라요?</div>'
            '<div class="bub ai"><b>리뷰</b>집합은 찾는 시간이 목록 길이와 상관없이 거의 일정해요.</div></div>')
    return (f'<div class="ui"><div class="win" style="width:92%"><div class="tbar"><i></i><i></i><i></i><b>count_words.py</b><em>코드 리뷰</em></div>'
            f'<div class="split"><div class="code" style="font-size:1.95cqw">{code}</div>{side}</div></div></div>')

def ui_algo():
    k, f, c = (lambda t: f'<span class="k">{t}</span>'), (lambda t: f'<span class="f">{t}</span>'), (lambda t: f'<span class="c">{t}</span>')
    code = ''.join([
        ln(1, f'{k("from")} collections {k("import")} deque'),
        ln(2, ''),
        ln(3, f'{k("def")} {f("bfs")}(graph, start):'),
        ln(4, '    visited = [start]'),
        ln(5, f'    q = {f("deque")}([start])'),
        ln(6, f'    {k("while")} q:'),
        ln(7, f'        node = q.{f("popleft")}()', 'hl'),
        ln(8, f'        {k("for")} nxt {k("in")} graph[node]:'),
        ln(9, f'            {k("if")} nxt {k("not in")} visited:'),
        ln(10, f'                visited.{f("append")}(nxt)'),
        ln(11, f'                q.{f("append")}(nxt)'),
        ln(12, f'    {k("return")} visited'),
    ])
    pos = {1: (50, 14), 2: (22, 46), 3: (78, 46), 4: (10, 82), 5: (36, 82), 6: (64, 82), 7: (90, 82)}
    edges = [(1, 2), (1, 3), (2, 4), (2, 5), (3, 6), (3, 7)]
    svg = ''.join(f'<line x1="{pos[a][0]}" y1="{pos[a][1]}" x2="{pos[b][0]}" y2="{pos[b][1]}"/>' for a, b in edges)
    svg += ''.join(f'<circle class="{"v" if n <= 4 else ""}" cx="{x}" cy="{y}" r="8"/><text x="{x}" y="{y}">{n}</text>' for n, (x, y) in pos.items())
    side = (f'<div class="side"><h6>탐색 순서</h6><svg class="graph" viewBox="0 0 100 96" aria-hidden="true">{svg}</svg>'
            '<div class="pass"><div>예제 1 통과</div><div>예제 2 통과</div><div>예제 3 통과</div></div></div>')
    return (f'<div class="ui"><div class="win" style="width:92%"><div class="tbar"><i></i><i></i><i></i><b>bfs.py</b><em>알고리즘</em></div>'
            f'<div class="split"><div class="code">{code}</div>{side}</div></div></div>')

def ui_prep():
    rows = [('로', '#FBC489', '로봇대회', 'FLL · WRO · 로보컵 · 로보텍스'), ('경', '#FDDDB8', '경시대회', '정보올림피아드 · 청소년 IT 경시대회'),
            ('공', '#F9AB57', '공모전', '임베디드SW경진대회 · 한국코드페어'), ('영', '#FEF1E2', '영재원', '영재원 준비'), ('자', '#F7941E', '자격증', 'COS · COS Pro')]
    body = ''.join(f'<div><i style="background:{bg}">{ch}</i><p style="margin:0"><b>{t}</b><small>{d}</small></p>{"<span>대회반 Lv6부터</span>" if t == "로봇대회" else ""}</div>' for ch, bg, t, d in rows)
    return (f'<div class="ui"><div class="win" style="width:82%"><div class="tbar"><i></i><i></i><i></i><b>경진대회 준비반</b><em>초2~고3</em></div>'
            f'<div class="plist">{body}</div></div></div>')

UI = {'python': ui_python, 'appinventor': ui_appinventor, 'ax': ui_ax, 'algo': ui_algo, 'prep': ui_prep}
