"""
build_report.py -- the project report (Word) in the SASTRA CSE425 format.

    python report/build_report.py            # writes report/Project_Report_127018060.docx
    python report/build_report.py --pages    # also renders it (Pages) and fills in page numbers

Needs python-docx and pandoc. Every number is read from results/ (see
tools/results.py); figures come from report/build_figures.py and
results/*/figures. The document is built twice in memory: the first pass
numbers the figures, tables, equations and citations, the second writes them.
"""
import copy
import json
import re
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE / "tools"))
from docxkit import Doc, X, latex_to_omml, md, pageref, ppr, run  # noqa: E402
from refs import REFS, Citations  # noqa: E402
import report_text as TXT  # noqa: E402

TEMPLATE = HERE / "templates" / "report_template.docx"
OUT = HERE / "Project_Report_127018060.docx"
PAGES = HERE / "data" / "report_pages.json"

DUMMY_MATH = '<m:oMathPara><m:oMath><m:r><m:t>x</m:t></m:r></m:oMath></m:oMathPara>'
DUMMY_INLINE = '<m:oMath><m:r><m:t>x</m:t></m:r></m:oMath>'


class Report:
    def __init__(self, prev=None, eq_cache=None, pages=None):
        self.d = Doc(TEMPLATE)
        self.sect_title, self.sect_front = self.d.para_sects[:2]
        prev = prev or {}
        self.prev_reg = prev.get("reg", {})
        self.prev_figs = prev.get("figs", [])
        self.prev_tabs = prev.get("tabs", [])
        self.prev_toc = prev.get("toc", [])
        self.cite = Citations(prev.get("cited", set()))
        self.eq_cache = eq_cache or {}
        self.pages = pages or {}
        self.reg, self.figs, self.tabs, self.toc = {}, [], [], []
        self.cited, self.latex, self.latex_inline = set(), [], []
        self.search = {}
        self.ch = self.sec = self.sub = self.nfig = self.ntab = self.neq = 0

    # ------------------------------------------------------------ text --
    def T(self, s):
        def ref(m):
            return self.prev_reg.get(m.group(1), "?")

        def cit(m):
            keys = [k.strip() for k in m.group(1).split(",")]
            for k in keys:
                if k not in REFS:
                    raise KeyError(f"unknown reference {k}")
            self.cited.update(keys)
            return self.cite(*keys)

        s = re.sub(r"\[\[([\w:.-]+)\]\]", ref, s)
        return re.sub(r"\{c:([\w, ]+)\}", cit, s)

    def page(self, bm):
        return self.pages.get(bm, "1")

    # ------------------------------------------------------------ blocks --
    def para(self, s, after=None, keep_next=False):
        self.d.p(md(self.T(s)), ppr(jc="both", after=after, keep_next=keep_next))

    def meta(self, label, value):
        self.d.p(run(label, b=True) + md(" " + self.T(value)), ppr(after=60))

    def bullets(self, items):
        for it in items:
            self.d.p(md(self.T(it)), ppr(num=12, after=60, jc="both"))

    def numbered(self, items):
        nid = self.d.new_list(11)
        for it in items:
            self.d.p(md(self.T(it)), ppr(num=nid, after=60, jc="both"))

    def label(self, text):
        self.d.p(run(text, b=True, sz=26), ppr(keep_next=True, before=160, after=80))

    def chapter(self, title):
        if self.ch:
            self.d.page_break()
        self.ch += 1
        self.sec = self.sub = self.nfig = self.ntab = self.neq = 0
        self.d.p(run(f"CHAPTER {self.ch}"), ppr(style="Heading1", jc="center"))
        bm = f"ch_{self.ch}"
        self.d.p(self.d.bookmark(bm, run(title, b=True, sz=28)), ppr(keep_next=True, after=280, line=240, jc="center"))
        self.toc.append(["chapter", f"Chapter {self.ch}", title, bm])
        self.search[bm] = ("line", f"CHAPTER {self.ch}")

    def h2(self, title, key=None):
        self.sec += 1
        self.sub = 0
        bm = f"sec_{self.ch}_{self.sec}"
        num = f"{self.ch}.{self.sec}"
        self.d.p(self.d.bookmark(bm, run(f"{num}  {title.upper()}")), ppr(style="Heading2"))
        self.toc.append(["section", num, title, bm])
        self.search[bm] = ("start", f"{num} {title.upper()}")
        if key:
            self.reg[key] = num

    def h3(self, title):
        self.sub += 1
        self.d.p(run(f"{self.ch}.{self.sec}.{self.sub}  {title}"), ppr(style="Heading3"))

    def figure(self, key, path, caption, width=6.3):
        self.nfig += 1
        num = f"{self.ch}.{self.nfig}"
        self.reg[key] = num
        bm = f"fig_{key}"
        self.d.picture(path, width, ppr(keep_next=True, after=40, line=240, jc="center"))
        cap = run(f"Figure {num}:", b=True, sz=22) + md(" " + self.T(caption), sz=22)
        self.d.p(self.d.bookmark(bm, cap), ppr(after=240, line=240, jc="center"))
        self.figs.append([num, self.T(caption), bm])
        self.search[bm] = ("start", f"Figure {num}:")

    def table(self, key, caption, header, rows, widths, align=None, sz=20, bold_rows=(), keep_next=None):
        self.ntab += 1
        num = f"{self.ch}.{self.ntab}"
        self.reg[key] = num
        bm = f"tab_{key}"
        cap = run(f"Table {num}:", b=True, sz=22) + md(" " + self.T(caption), sz=22)
        self.d.p(self.d.bookmark(bm, cap), ppr(keep_next=True, before=120, after=80, line=240, jc="center"))
        rows = [[self.T(str(c)) for c in r] for r in rows]
        self.d.grid_table([self.T(h) for h in header], rows, widths, sz=sz, align=align,
                          bold_rows=bold_rows, keep_next=keep_next)
        self.d.p("", ppr(after=80, line=240, jc="both"))
        self.tabs.append([num, self.T(caption), bm])
        self.search[bm] = ("start", f"Table {num}:")

    def eqs(self, items):
        """items: [(key, latex)] -> one borderless equation table."""
        maths, labels = [], []
        for key, latex in items:
            self.neq += 1
            num = f"{self.ch}.{self.neq}"
            self.reg[key] = num
            self.latex.append(latex)
            el = self.eq_cache.get(("d", latex))
            maths.append(el if el is not None else X(DUMMY_MATH))
            labels.append(num)
        self.d.eq_table(maths, labels)

    def inline_math(self, latex):
        self.latex_inline.append(latex)
        el = self.eq_cache.get(("i", latex))
        return copy.deepcopy(el) if el is not None else X(DUMMY_INLINE)

    def code(self, lines):
        lines = list(lines)
        for k, line in enumerate(lines):
            pp = ppr(shd="F4F4F4", before=80 if k == 0 else None, after=160 if k == len(lines) - 1 else 0,
                     line=240, ind_left=360)
            self.d.p(run(line or " ", font="Consolas", sz=17), pp)

    # ------------------------------------------------------------ front --
    def front_heading(self, text, bm, sz=30):
        self.d.p(self.d.bookmark(bm, run(text, b=True, sz=sz)), ppr(after=360, line=240, jc="center"))
        self.search[bm] = ("line", text)

    def list_table(self, kind, items):
        head = "Figure No." if kind == "fig" else "Table No."
        rows = [[n, t, pageref(bm, self.page(bm), sz=22)] for n, t, bm in items]
        self.d.grid_table([head, "Title", "Page No."], [[n, md(t, sz=22), p] for n, t, p in rows],
                          [1584, 6624, 1296], sz=22, align=["center", "left", "center"], keep_next=False)

    def build(self):
        TXT.front_matter(self)
        TXT.chapters(self)
        self.references()
        return self

    def references(self):
        self.chapter("REFERENCES")
        nid = self.d.new_list(9)
        for k in self.cite.keys:
            pieces, url = REFS[k]
            xml = "".join(run(t, i=it) for t, it in pieces)
            if url:
                xml += run(" ") + self.d.link(url, url)
            self.d.p(xml, ppr(num=nid, after=120, jc="left"))

    def state(self):
        return {"reg": self.reg, "figs": self.figs, "tabs": self.tabs, "toc": self.toc, "cited": self.cited}


# ---------------------------------------------------------------- pages --
def roman(n):
    vals = [(10, "x"), (9, "ix"), (5, "v"), (4, "iv"), (1, "i")]
    out = ""
    for v, s in vals:
        while n >= v:
            out += s
            n -= v
    return out


def find_pages(pdf, search):
    """Page label of every bookmark, found from the rendered PDF's text."""
    n = int(re.search(r"Pages:\s+(\d+)", subprocess.run(["pdfinfo", str(pdf)], capture_output=True, text=True).stdout).group(1))
    texts = []
    for p in range(1, n + 1):
        t = subprocess.run(["pdftotext", "-f", str(p), "-l", str(p), str(pdf), "-"], capture_output=True, text=True).stdout
        texts.append([re.sub(r"\s+", " ", line).strip() for line in t.splitlines()])
    first_ch = next(i for i, lines in enumerate(texts) if "CHAPTER 1" in lines)
    toc_page = next(i for i, lines in enumerate(texts) if "Table of Contents" in lines)
    labels = {}
    for bm, (mode, key) in search.items():
        key = re.sub(r"\s+", " ", key)
        rng = range(0, toc_page + 1) if bm.startswith("fm_") else range(first_ch, n)
        for i in rng:
            hit = any(line == key for line in texts[i]) if mode == "line" else any(line.startswith(key) for line in texts[i])
            if hit:
                labels[bm] = roman(i + 1) if i < first_ch else str(i - first_ch + 1)
                break
        else:
            print("  page not found:", bm, key)
    return labels, n


def render(docx, pdf):
    script = HERE / "tools" / "docx2pdf.applescript"
    subprocess.run(["osascript", str(script), str(docx), str(pdf)], check=True)


def build_once(prev, cache, pages):
    rep = Report(prev, cache, pages).build()
    return rep


def main():
    pages = json.loads(PAGES.read_text()) if PAGES.exists() else {}
    first = build_once(None, None, pages)
    disp, inl = latex_to_omml(list(dict.fromkeys(first.latex)), list(dict.fromkeys(first.latex_inline)))
    cache = {("d", k): v for k, v in zip(dict.fromkeys(first.latex), disp)}
    cache.update({("i", k): v for k, v in zip(dict.fromkeys(first.latex_inline), inl)})
    rep = build_once(first.state(), cache, pages)
    rep.d.save(OUT, title=TXT.TITLE, author=TXT.STUDENT, subject="CSE425 Machine Learning Essentials – project report",
               keywords="wine quality, ensemble learning, class imbalance, SMOTE, feature importance")
    print("wrote", OUT)
    if "--pages" in sys.argv:
        pdf = HERE / "data" / "report_render.pdf"
        for attempt in range(2):
            render(OUT, pdf)
            labels, n = find_pages(pdf, rep.search)
            changed = labels != pages
            pages = labels
            PAGES.write_text(json.dumps(labels, indent=1))
            print(f"rendered {n} pages; page numbers {'updated' if changed else 'unchanged'}")
            if not changed:
                break
            rep = build_once(first.state(), cache, pages)
            rep.d.save(OUT, title=TXT.TITLE, author=TXT.STUDENT, subject="CSE425 Machine Learning Essentials – project report",
                       keywords="wine quality, ensemble learning, class imbalance, SMOTE, feature importance")


if __name__ == "__main__":
    main()
