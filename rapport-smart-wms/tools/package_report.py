"""Package the compiled report and its active editable sources."""
from pathlib import Path
import json
import shutil
import zipfile
import pymupdf

root = Path(__file__).resolve().parents[1]
build = root / 'build'
audit = json.loads((root / 'audit/revision_complete/verification.json').read_text(encoding='utf-8'))
assert not audit['overfull_warnings']
assert not audit['undefined_references']
assert not audit['missing_characters']
assert all(t['pass'] for t in audit['tables'])
assert all(s['report_page'] is not None for s in audit['sections'])
assert all(not p.get('text_crossing_diagram_box') for p in audit['pages'])
shutil.copy2(build / 'main.pdf', build / 'Rapport_Stage_FERHAN_Abdelali_Complet_Corrige.pdf')
# The earlier abbreviated PDF remains preserved in archive/version_abregee.
shutil.copy2(build / 'main.pdf', build / 'Rapport_Stage_FERHAN_Abdelali_Smart_WMS_Revu.pdf')
document = pymupdf.open(build / 'main.pdf')
assert all(abs(p.rect.width - 595.276) < 1 and abs(p.rect.height - 841.89) < 1 for p in document), 'All report pages must be A4 portrait'
fresh_name = 'Rapport_FERHAN_SmartWMS_Complet_Chapitres_1_5_Final.pdf'
shutil.copy2(build / 'main.pdf', root.parent / fresh_name)
shutil.copy2(build / 'main.pdf', build / fresh_name)
page_number = next(i for i, p in enumerate(document)
                   if 'FIGURE 4.1' in p.get_text().upper() and p.get_images(full=True))
architecture = pymupdf.open()
architecture.insert_pdf(document, from_page=page_number, to_page=page_number)
architecture.save(build / 'Architecture_Fonctionnelle_Smart_WMS_Originale.pdf')
document[page_number].get_pixmap(dpi=240, alpha=False).save(build / 'Architecture_Fonctionnelle_Smart_WMS.png')
with zipfile.ZipFile(build / 'Rapport_Smart_WMS_Sources_LaTeX.zip', 'w', zipfile.ZIP_DEFLATED) as bundle:
    files = [root / p for p in ['main.tex', 'README.md', 'CORRECTIONS.md', 'CORRESPONDANCE.md',
                                'config/revision.tex', 'bibliography/revision.bib']]
    for directory in ['chapters/revision', 'figures/revision', 'figures/uml', 'figures/uml-source', 'figures/uml-split', 'figures/uml-quad', 'uml', 'tables', 'tools']:
        files.extend(p for p in (root / directory).rglob('*') if p.is_file() and p.suffix in {'.tex', '.png', '.webp', '.puml', '.py', '.ps1'})
    files.extend(p for p in (root / 'figures').glob('*') if p.is_file() and p.suffix in {'.png', '.webp'})
    for path in files:
        bundle.write(path, path.relative_to(root))
    originals = root.parent / 'diagramms'
    for path in originals.glob('*.puml'):
        bundle.write(path, Path('uml/original') / path.name)
print(f'Packaged {len(document)} pages; architecture PDF page {page_number + 1}.')
