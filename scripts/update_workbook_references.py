"""Refresh cross-volume number index from the successfully built textbook."""
from pathlib import Path
import argparse
import re
ROOT=Path(__file__).resolve().parents[1]
parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('--textbook-aux', type=Path, default=ROOT/'build/textbook/textbook.aux')
args = parser.parse_args()
aux=args.textbook_aux.read_text()
numbers=dict(re.findall(r'\\newlabel\{([^}]+)\}\{\{([^}]+)\}',aux))
keys=set()
output=ROOT/'book/workbook/tb-numbers.generated.tex'
for p in (ROOT/'book/workbook').rglob('*.tex'):
    if p == output:
        continue
    keys.update(re.findall(r'\\tb(?:object|numberref)\{([^}]+)\}',p.read_text()))
missing=keys-numbers.keys()
if missing:raise SystemExit('Missing textbook references: '+', '.join(sorted(missing)))
text='% Textbook number index; refreshed after make textbook.\n'+''.join('\\tbnumber{'+k+'}{'+numbers[k]+'}\n' for k in sorted(keys))
p=ROOT/'book/workbook/tb-numbers.generated.tex'
if not p.exists() or p.read_text()!=text:p.write_text(text)
print(f'Textbook references: {len(keys)}')
