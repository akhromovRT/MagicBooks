# Скачивает открытые тексты книг в папку: python3 scripts/fetch_books.py books [slug ...]
# Зависимости: pip install beautifulsoup4 html2text
import sys, os, re, html2text
from bs4 import BeautifulSoup
OUT = sys.argv[1]
GG = "https://www.globalgreyebooks.com/online-ebooks/{}_complete-text.html"
GUT = "https://www.gutenberg.org/cache/epub/{0}/pg{0}.txt"
BOOKS = [
 ("01-mulford-thoughts-are-things", "gg", "prentice-mulford_thoughts-are-things"),
 ("02-allen-as-a-man-thinketh", "gut", 4507),
 ("03a-troward-edinburgh-lectures", "gut", 10390),
 ("03b-troward-dore-lectures", "gut", 1398),
 ("04-wattles-science-of-getting-rich", "gut", 59844),
 ("05-haanel-master-key-system", "gg", "charles-f-haanel_master-key-system"),
 ("06-trine-higher-powers-of-mind-and-spirit", "gut", 28163),
 ("07a-holmes-creative-mind", "gg", "ernest-s-holmes_creative-mind"),
 ("07b-holmes-creative-mind-and-success", "gg", "ernest-s-holmes_creative-mind-and-success"),
 ("08-shinn-game-of-life", "gut", 74878),
 ("09-shinn-your-word-is-your-wand", "gg", "florence-scovel-shinn_your-word-is-your-wand"),
 ("10-hill-think-and-grow-rich", "gg", "napoleon-hill_think-and-grow-rich"),
 ("11-goddard-feeling-is-the-secret", "gg", "neville-goddard_feeling-is-the-secret"),
 ("12-goddard-power-of-awareness", "gg", "neville-goddard_power-of-awareness"),
 ("14-goddard-law-and-the-promise", "gg", "neville-goddard_law-and-the-promise"),
]
def get(url):
    import subprocess
    return subprocess.run(["curl","-sSfL","--proto-redir","https","-A","Mozilla/5.0 (book-archiver)",url],check=True,capture_output=True).stdout.decode("utf-8","replace")
def strip_gutenberg(t):
    t = t.replace("\r\n", "\n")
    s = re.search(r"\*\*\* ?START OF (THE|THIS) PROJECT GUTENBERG[^\n]*\n", t)
    e = re.search(r"\*\*\* ?END OF (THE|THIS) PROJECT GUTENBERG", t)
    return t[s.end() if s else 0 : e.start() if e else len(t)].strip() + "\n"
def gg_text(h):
    soup = BeautifulSoup(h, "html.parser")
    title = soup.select_one("h1.book-title")
    art = soup.select_one("article.reading-body")
    for x in art.select("script,style,nav,aside"): x.decompose()
    conv = html2text.HTML2Text(); conv.body_width = 0; conv.ignore_images = True; conv.ignore_links = True
    md = conv.handle(str(art))
    md = re.sub(r"\n{3,}", "\n\n", md).strip() + "\n"
    return (f"# {title.get_text(strip=True)}\n\n" if title else "") + md
for slug, kind, ref in BOOKS:
    if len(sys.argv) > 2 and slug not in sys.argv[2:]: continue
    url = GG.format(ref) if kind == "gg" else GUT.format(ref)
    raw = get(url)
    if kind == "gg":
        body, ext = gg_text(raw), "md"
    else:
        body, ext = strip_gutenberg(raw), "txt"
    path = os.path.join(OUT, f"{slug}.{ext}")
    with open(path, "w", encoding="utf-8") as f:
        f.write(f"<!-- Source: {url} -->\n\n" if ext == "md" else f"Source: {url}\n\n")
        f.write(body)
    print(f"{slug}\t{len(body.split())} words\t{url}", flush=True)
