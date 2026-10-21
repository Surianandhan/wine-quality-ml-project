"""
make_templates.py -- turn the format samples into empty templates (run once).

    python report/tools/make_templates.py <sample_report.docx> <sample_paper.docx>

Keeps only what defines the format -- page set-up, styles, list numbering,
footers and section breaks -- and removes every paragraph, image, link and
property of the sample, so no content of the sample stays in this project.
The SASTRA logo on the sample's title page is saved to report/assets/.
"""
import sys
import zipfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from docxkit import Doc  # noqa: E402

HERE = Path(__file__).resolve().parent.parent
OUT = HERE / "templates"
OUT.mkdir(exist_ok=True)
(HERE / "assets").mkdir(exist_ok=True)


def strip(src, dst, keep_sections):
    d = Doc(src)
    # Doc() has already emptied the body; keep the template's section breaks
    # so the build scripts can reuse them (title page / front matter / chapters).
    for sect in d.para_sects[:keep_sections]:
        d.section_break(sect)
    d.save(dst, title="", author="")
    print("wrote", dst)


report_src, paper_src = sys.argv[1], sys.argv[2]
with zipfile.ZipFile(report_src) as z:
    (HERE / "assets" / "sastra_logo.png").write_bytes(z.read("word/media/image1.png"))
strip(report_src, OUT / "report_template.docx", keep_sections=2)
strip(paper_src, OUT / "paper_template.docx", keep_sections=0)
