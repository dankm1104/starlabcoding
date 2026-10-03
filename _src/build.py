"""광진점 사이트 빌드
body.html(첫 페이지) + posts_src/*.html(스타랩 이야기 글) -> dist/ (실제 사이트), preview/ (검토용 아티팩트)
도메인이 정해지면 DOMAIN만 바꿔 다시 실행한다. 예: DOMAIN = "https://starlabgj.kr"
사진은 저장소 맨 위 img/ 폴더에 둔다.
"""
import glob, html, json, os, re, shutil
from datetime import date

DOMAIN = "https://starlabcoding.co.kr"
OUT, PREV = "..", "preview"  # 사이트는 저장소 맨 위에 만든다. _src 안에서 실행

FONTS = ('<link rel="preconnect" href="https://fonts.googleapis.com">\n'
         '<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>\n'
         '<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;500'
         '&family=IBM+Plex+Sans+KR:wght@400;500;700&display=swap">')

# 구글 애널리틱스 (속성: 스타랩코딩학원 광진점 홈페이지, 스트림: 광진점 홈페이지)
# 실제 도메인에서만 켜진다. 미리보기·로컬에서는 기록하지 않음
GA_ID = "G-SXYG0R5WMM"
# 샘플클래스 신청을 받는 구글 Apps Script 웹앱 주소 (신청 → 구글 시트 + 메일)
FORM_ENDPOINT = "https://script.google.com/macros/s/AKfycby6k2TKL4GjP-XzRct7w_7yKdNAslZeJEhDgeK1nBIh6rZuuf9nP146p9yayOhi58ch_g/exec"
ANALYTICS = """<script>
if (/(^|\\.)starlabcoding\\.co\\.kr$/.test(location.hostname)) {
  var s = document.createElement('script'); s.async = true;
  s.src = 'https://www.googletagmanager.com/gtag/js?id=@@GA@@';
  document.head.appendChild(s);
  window.dataLayer = window.dataLayer || [];
  window.gtag = function () { dataLayer.push(arguments); };
  gtag('js', new Date());
  gtag('config', '@@GA@@');
  // 버튼 클릭 기록: 전화, 샘플클래스 신청, 카카오톡, 지도
  document.addEventListener('click', function (e) {
    var a = e.target.closest && e.target.closest('a');
    if (!a) return;
    var h = a.getAttribute('href') || '';
    var name = h.indexOf('tel:') === 0 ? 'phone_click'
      : /sub01-03-04|sample\\.html|^#sample$/.test(h) ? 'sample_class_click'
      : h.indexOf('pf.kakao.com') > -1 ? 'kakao_click'
      : /map\\.kakao|map\\.naver/.test(h) ? 'map_click' : '';
    if (name) gtag('event', name, { link_url: h, transport_type: 'beacon' });
  });
}
</script>""".replace("@@GA@@", GA_ID)
# 네이버 광고 전환 추적 (프리미엄 로그 분석 공통 스크립트 + 신청 완료 'lead')
# 키(네이버공통키 na_account_id)는 검색광고시스템 [도구 > 프리미엄 로그 분석]에서 확인. 비어 있으면 아무것도 넣지 않는다
# 안내: https://naver.github.io/conversion-tracking/pages/01_script_guide_wcstrans/
NAVER_WA = ""
if NAVER_WA:
    ANALYTICS += """
<script src="https://wcs.naver.net/wcslog.js"></script>
<script>
if (window.wcs && /(^|\\.)starlabcoding\\.co\\.kr$/.test(location.hostname)) {
  if (!window.wcs_add) window.wcs_add = {};
  wcs_add["wa"] = "@@WA@@";
  wcs.inflow("starlabcoding.co.kr");
  wcs_do();
  window.naverLead = function () { wcs.trans({ type: "lead" }); };
}
</script>""".replace("@@WA@@", NAVER_WA)

PHOTO_ALT = {
    1: "광진구 구의동 스타랩코딩학원 광진점 교실",
    2: "유치부 STEAM 수업 교구 VEX123과 레고 에듀케이션 얼리 심플머신",
    3: "레고 에듀케이션 스파이크로 만든 로봇코딩 작품",
    4: "파이썬·C언어·임베디드 수업",
    5: "학생이 로봇을 조립하고 코딩하는 수업 장면",
    6: "스타랩코딩학원 광진점 대회 수상 트로피와 상장",
    7: "광나루로 602 대한빌딩(아트박스 건물) 입구",
}

body = open("body.html", encoding="utf-8").read()
STYLE = re.search(r"<style>.*?</style>", body, re.S).group(0)
HEADER = re.search(r'<header class="top">.*?</header>', body, re.S).group(0)
FOOTER_RAW = re.search(r"<footer>.*?</footer>", body, re.S).group(0)
FOOTER = FOOTER_RAW.replace("@@A@@", "../")


def strip(t):
    return html.unescape(re.sub(r"<[^>]+>", "", t)).strip()


def ld(o):
    return '<script type="application/ld+json">\n' + json.dumps(o, ensure_ascii=False, indent=1) + "\n</script>"


def photos(s, prefix):
    """photos/N.jpg 가 있으면 사진 자리를 실제 사진으로 바꾼다"""
    def sub(m):
        n = int(m.group(1))
        for ext in ("jpg", "jpeg", "png", "webp"):
            if os.path.exists(f"photos/{n}.{ext}"):
                return (f'data-photo="{n}"{m.group(2)}><img src="{prefix}photos/{n}.{ext}" '
                        f'alt="{PHOTO_ALT[n]}" loading="lazy" decoding="async">')
        return m.group(0)
    return re.sub(r'data-photo="(\d)"([^>]*)><div class="ph-slot">.*?</div>', sub, s, flags=re.S)


def links(s, home, posts, assets=""):
    return s.replace("@@H@@", home).replace("@@P@@", posts).replace("@@A@@", assets)


# ── 글 읽기 ──
posts = []
for f in sorted(glob.glob("posts_src/*.html")):
    raw = open(f, encoding="utf-8").read()
    head, content = raw.split("\n---\n", 1)
    meta = dict(line.split(": ", 1) for line in head.strip().splitlines())
    meta["content"] = content.strip()
    posts.append(meta)
posts.sort(key=lambda p: p["date"], reverse=True)


def cat(p, pre="", a="", b=""):
    """분류가 '스타랩 이야기'(섹션 이름과 같음)면 표시하지 않는다"""
    c = p["category"]
    return "" if c in ("스타랩 이야기", "학원 소식") else f"{pre}{a}{c}{b}"


def dot(d):
    return d.replace("-", ".")


def post_list(items, prefix):
    rows = []
    for p in items:
        rows.append(
            f'<li><a href="{prefix}{p["slug"]}.html"><span class="meta"><time datetime="{p["date"]}">{dot(p["date"])}</time>'
            f'{cat(p, "", "<span>", "</span>")}</span><b>{p["title"]}</b><span class="sum">{p["summary"]}</span></a></li>')
    return '<ul class="posts">\n      ' + "\n      ".join(rows) + "\n    </ul>"


def page(title, desc, canon_path, extra_head, inner, og_type="website"):
    canon = (f'<link rel="canonical" href="{DOMAIN}/{canon_path}">\n'
             f'<meta property="og:url" content="{DOMAIN}/{canon_path}">\n') if DOMAIN else ""
    return f"""<!doctype html>
<html lang="ko">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>{title}</title>
<meta name="description" content="{html.escape(desc)}">
<meta name="robots" content="index, follow, max-snippet:-1">
{canon}<meta property="og:type" content="{og_type}">
<meta property="og:locale" content="ko_KR">
<meta property="og:site_name" content="스타랩코딩학원 광진점">
<meta property="og:title" content="{html.escape(title)}">
<meta property="og:description" content="{html.escape(desc)}">
<meta name="format-detection" content="telephone=no">
<meta name="naver-site-verification" content="a8d50ad0e07dc6b774fd50e51b22d8a8fe8e33a2">
<link rel="icon" href="/favicon.ico" sizes="any">
<link rel="icon" type="image/png" sizes="32x32" href="/img/favicon-32.png">
<link rel="apple-touch-icon" href="/img/apple-touch-icon.png">
{('<link rel="alternate" type="application/rss+xml" title="학원 소식" href="' + DOMAIN + '/rss.xml">') if DOMAIN else ""}
{('<meta property="og:image" content="' + DOMAIN + '/img/hero.jpg">') if DOMAIN else ""}
{FONTS}
{extra_head}
{ANALYTICS}
</head>
<body>
{inner}
</body>
</html>
"""


# ── 첫 페이지 ──
faq = re.findall(r"<details><summary>(.*?)</summary><p>(.*?)</p></details>", body, re.S)
assert len(faq) >= 6, len(faq)

org = {
    "@context": "https://schema.org",
    "@type": ["LocalBusiness", "EducationalOrganization"],
    "name": "스타랩코딩학원 광진점",
    "alternateName": ["스타랩 광진점", "스타랩코딩학원 광진센터"],
    "description": "광진구 구의동, 실적으로 증명하는 스타랩코딩학원입니다. 6년 연속 전국대회 수상 세계대회 진출 10회. "
                   "유치부 첫 코딩부터 고등 심화 프로젝트까지, 로봇코딩으로 시작해 파이썬 C언어 임베디드로 이어집니다.",
    "telephone": "+82-2-444-1854",
    "address": {"@type": "PostalAddress", "streetAddress": "광나루로 602 대한빌딩 2층 201호",
                "addressLocality": "광진구", "addressRegion": "서울특별시", "postalCode": "05034", "addressCountry": "KR"},
    "areaServed": ["광진구", "구의동", "광장동"],
    "openingHoursSpecification": [
        {"@type": "OpeningHoursSpecification", "dayOfWeek": ["Tuesday", "Wednesday", "Thursday", "Friday"], "opens": "13:00", "closes": "20:30"},
        {"@type": "OpeningHoursSpecification", "dayOfWeek": "Saturday", "opens": "10:00", "closes": "17:00"},
        {"@type": "OpeningHoursSpecification", "dayOfWeek": "Sunday", "opens": "13:00", "closes": "17:00"},
    ],
    "sameAs": ["https://blog.naver.com/starlab_gwangjin", "https://pf.kakao.com/_jixhQG", "https://place.map.kakao.com/1836797483"],
    "parentOrganization": {"@type": "Organization", "name": "스타랩코딩학원", "url": "https://star-lab.co.kr"},
    "knowsAbout": ["로봇코딩", "피지컬 AI", "AI 로보틱스", "파이썬", "C언어", "아두이노", "MCU", "임베디드", "머신러닝", "정보올림피아드", "로봇대회", "COS", "COS Pro"],
}
if DOMAIN:
    org["url"] = DOMAIN + "/"
    org["logo"] = DOMAIN + "/img/logo.png"
    org["image"] = [DOMAIN + "/img/hero.jpg", DOMAIN + "/img/method.jpg"]
faqld = {"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": [
    {"@type": "Question", "name": strip(q), "acceptedAnswer": {"@type": "Answer", "text": strip(a)}} for q, a in faq]}

home = body.replace("@@LATEST@@", post_list(posts[:3], "posts/"))
home = links(home, "", "posts/", "")

TITLE = "광진구 구의동 코딩학원 스타랩 | 유치~고등 로봇코딩·파이썬·C언어"
# 네이버 서치어드바이저 기준: 설명문은 80자 이내 (2026-10-03)
DESC = "광진구 구의동 스타랩코딩학원 광진점. 6년 연속 전국대회 수상, 세계대회 진출 10회. 유치부 로봇코딩부터 파이썬·C언어까지 600차시 과정."

# ── 글 페이지 ──
def article(p):
    others = [o for o in posts if o["slug"] != p["slug"]][:3]
    return f"""{links(HEADER, "../index.html", "", "../")}
<main id="top">
  <div class="wrap">
    <article class="article">
      <p class="crumb"><a href="index.html">학원 소식</a>{cat(p, " · ")}</p>
      <h1>{p["title"]}</h1>
      <p class="byline"><time datetime="{p["date"]}">{dot(p["date"])}</time> · 스타랩코딩학원 광진점</p>
      <div class="answer"><span>짧게 답하면</span><p>{p["answer"]}</p></div>
      <div class="prose">
{p["content"]}
      </div>
      <p class="source">사진과 함께 보는 원문: <a href="{p["source"]}">스타랩 광진 블로그</a></p>
      <div class="ask">
        <h2>어디서부터 시작할지 궁금하다면</h2>
        <p>학년과 코딩 경험을 알려 주시면 레벨테스트와 상담으로 시작 단계를 함께 정합니다. 전화문의 <span class="num">02-444-1854</span></p>
        <div class="cta"><a class="btn" href="../sample.html">샘플클래스 신청</a><a class="btn ghost" href="http://pf.kakao.com/_jixhQG/chat">카카오톡 상담</a></div>
      </div>
    </article>
    <section class="article" style="padding-top:0" aria-label="다른 글">
      <h2 style="font-size:1.2rem">다른 글</h2>
      {post_list(others, "")}
    </section>
  </div>
</main>
{FOOTER}"""


def article_ld(p):
    o = {"@context": "https://schema.org", "@type": "BlogPosting", "headline": p["title"],
         "description": p["summary"], "datePublished": p["date"], "inLanguage": "ko",
         "author": {"@type": "Organization", "name": "스타랩코딩학원 광진점"},
         "publisher": {"@type": "Organization", "name": "스타랩코딩학원 광진점"},
         "dateModified": p["date"],
         "isBasedOn": p["source"], "articleSection": p["category"]}
    if DOMAIN:
        o["mainEntityOfPage"] = f"{DOMAIN}/posts/{p['slug']}.html"
        o["image"] = DOMAIN + "/img/hero.jpg"
        o["publisher"]["logo"] = {"@type": "ImageObject", "url": DOMAIN + "/img/logo.png"}
    return ld(o)


LIST_INNER = f"""{links(HEADER, "../index.html", "", "../")}
<main id="top">
  <div class="wrap">
    <div class="article" style="max-width:52rem">
      <h1>학원 소식</h1>
      <p style="color:var(--sub)">상담에서 자주 받는 질문과 수업 이야기를 정리합니다. 사진이 담긴 원문은 스타랩 광진 블로그에 있습니다.</p>
      {post_list(posts, "")}
    </div>
  </div>
</main>
{FOOTER}"""


def write(path, text):
    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    open(path, "w", encoding="utf-8").write(text)


shutil.rmtree(PREV, ignore_errors=True)
shutil.rmtree(f"{OUT}/posts", ignore_errors=True)  # 글 페이지만 새로 만든다 (OUT 전체를 지우면 저장소가 날아감)

# 실제 사이트
# 첫 페이지: 2026-10-03 원장 컨펌 시안 D (home.py). 검색·통계 태그는 이 파일의 page()와 같은 것을 쓴다
import home as homepage
homepage.set_posts(posts[:3])
_full = page(TITLE, DESC, "", ld(org) + "\n" + ld(faqld), "")
HEAD = re.search(r"<head>\n(.*)\n</head>", _full, re.S).group(1).replace(FONTS + "\n", "")
INDEX = homepage.page(HEAD, FORM_ENDPOINT)
write(f"{OUT}/index.html", INDEX)
for p in posts:
    write(f"{OUT}/posts/{p['slug']}.html",
          page(f"{p['title']} | 스타랩코딩학원 광진점", p["summary"], f"posts/{p['slug']}.html",
               STYLE + "\n" + article_ld(p), article(p), "article"))
write(f"{OUT}/posts/index.html", page("학원 소식 | 스타랩코딩학원 광진점",
      "광진구 구의동 스타랩코딩학원 광진점 학원 소식. 학부모가 자주 묻는 질문과 수업 이야기, 로봇대회·정보올림피아드·자격증 소식을 정리합니다.", "posts/", STYLE, LIST_INNER))

# 샘플클래스 신청 페이지
sf = open("sample_form.html", encoding="utf-8").read().replace("@@ENDPOINT@@", FORM_ENDPOINT)
SAMPLE_STYLE = re.search(r"<style>.*?</style>", sf, re.S).group(0)
SAMPLE_BODY = sf.replace(SAMPLE_STYLE, "").strip()
SAMPLE_INNER = links(HEADER, "index.html", "posts/", "") + "\n" + SAMPLE_BODY.replace("</main>", "</main>\n" + FOOTER_RAW.replace("@@A@@", ""), 1)
write(f"{OUT}/sample.html", page("샘플클래스 신청 | 스타랩코딩학원 광진점",
      "스타랩코딩학원 광진점 샘플클래스 신청. 유치부·초등·중학생 로봇·코딩 수업(초등·중등 90분, 유치부 60분). 참가비 30,000원.",
      "sample.html", STYLE + "\n" + SAMPLE_STYLE, SAMPLE_INNER))

# 없는 주소로 들어왔을 때 (GitHub Pages가 404.html을 보여 준다. 어느 깊이에서든 열리므로 링크는 절대 경로)
NF_INNER = links(HEADER, "/", "/posts/", "/") + """
<main id="top">
  <div class="wrap">
    <div class="article">
      <h1>페이지를 찾을 수 없습니다</h1>
      <p>주소가 바뀌었거나 없어진 페이지입니다.</p>
      <p><a class="btn" href="/">첫 화면으로</a> <a class="btn ghost" href="/posts/">학원 소식</a> <a class="btn ghost" href="/sample.html">샘플클래스 신청</a></p>
    </div>
  </div>
</main>
""" + FOOTER_RAW.replace("@@A@@", "/")
nf = page("페이지를 찾을 수 없습니다 | 스타랩코딩학원 광진점", "스타랩코딩학원 광진점", "", STYLE, NF_INNER)
nf = re.sub(r'<link rel="canonical"[^>]*>\n', "", nf).replace('<meta charset="utf-8">', '<meta charset="utf-8">\n<meta name="robots" content="noindex">', 1)
write(f"{OUT}/404.html", nf)

bots = ["Googlebot", "Google-Extended", "Yeti", "GPTBot", "OAI-SearchBot", "ChatGPT-User",
        "ClaudeBot", "Claude-SearchBot", "Claude-User", "PerplexityBot", "Perplexity-User", "Bingbot", "Daumoa"]
robots = "".join(f"User-agent: {b}\nAllow: /\n\n" for b in bots) + "User-agent: *\nAllow: /\n"
if DOMAIN:
    robots += f"\nSitemap: {DOMAIN}/sitemap.xml\n"
    urls = [("", date.today().isoformat()), ("sample.html", date.today().isoformat()), ("posts/", posts[0]["date"])] + [(f"posts/{p['slug']}.html", p["date"]) for p in posts]
    write(f"{OUT}/sitemap.xml", '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
          + "".join(f"  <url><loc>{DOMAIN}/{u}</loc><lastmod>{m}</lastmod></url>\n" for u, m in urls) + "</urlset>\n")
write(f"{OUT}/robots.txt", robots)

# RSS: 네이버 서치어드바이저 등에 새 글을 알리는 용도
if DOMAIN:
    from email.utils import format_datetime
    from datetime import datetime, timezone, timedelta
    KST = timezone(timedelta(hours=9))
    def rfc(d):
        return format_datetime(datetime.fromisoformat(d).replace(hour=9, tzinfo=KST))
    items = "".join(
        f"  <item>\n    <title>{html.escape(p['title'])}</title>\n    <link>{DOMAIN}/posts/{p['slug']}.html</link>\n"
        f"    <guid isPermaLink=\"true\">{DOMAIN}/posts/{p['slug']}.html</guid>\n"
        f"    <description>{html.escape(p['summary'])}</description>\n    <category>{html.escape(p['category'])}</category>\n"
        f"    <pubDate>{rfc(p['date'])}</pubDate>\n  </item>\n" for p in posts)
    write(f"{OUT}/rss.xml", '<?xml version="1.0" encoding="UTF-8"?>\n<rss version="2.0">\n<channel>\n'
          f"  <title>학원 소식 | 스타랩코딩학원 광진점</title>\n  <link>{DOMAIN}/posts/</link>\n"
          "  <description>광진구 구의동 스타랩코딩학원 광진점의 코딩 교육 이야기와 학부모 질문 정리</description>\n"
          f"  <language>ko</language>\n  <lastBuildDate>{rfc(posts[0]['date'])}</lastBuildDate>\n" + items + "</channel>\n</rss>\n")
write(f"{OUT}/CNAME", "starlabcoding.co.kr\n")  # 깃허브 페이지 도메인 연결용

# 검토용 아티팩트: 첫 페이지는 뼈대 없이, 글 페이지는 완전한 문서로
write(f"{PREV}/index.html", INDEX)
for p in posts:
    write(f"{PREV}/posts/{p['slug']}.html", open(f"{OUT}/posts/{p['slug']}.html", encoding="utf-8").read())
write(f"{PREV}/posts/index.html", open(f"{OUT}/posts/index.html", encoding="utf-8").read())
write(f"{PREV}/sample.html", open(f"{OUT}/sample.html", encoding="utf-8").read())
shutil.copy(f"{PREV}/index.html", "preview.html")  # Claude 미리보기용, 저장소에 올리지 않음  # 아티팩트 주소를 유지하려고 같은 파일 경로로 게시
print("ok:", len(posts), "posts,", len(faq), "faq")
