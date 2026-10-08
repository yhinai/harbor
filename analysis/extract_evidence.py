"""Extract published notebook outputs. Does not execute notebook cells or models."""
from pathlib import Path
from html.parser import HTMLParser
from decimal import Decimal
import hashlib, json, math

ROOT = Path(__file__).resolve().parent


class Table(HTMLParser):
    def __init__(self):
        super().__init__()
        self.rows = []; self.row = None; self.cell = None

    def handle_starttag(self, tag, attrs):
        if tag == 'tr': self.row = []
        elif tag in ('td', 'th'): self.cell = [tag, '']

    def handle_data(self, data):
        if self.cell is not None: self.cell[1] += data

    def handle_endtag(self, tag):
        if tag in ('td', 'th') and self.cell is not None:
            self.row.append((self.cell[0], self.cell[1].strip())); self.cell = None
        elif tag == 'tr' and self.row is not None:
            self.rows.append(self.row); self.row = None


def table(notebook, cell):
    outputs = notebook['cells'][cell]['outputs']
    html = next(''.join(o['data']['text/html']) for o in outputs
                if 'text/html' in o.get('data', {}))
    parser = Table(); parser.feed(html)
    return parser.rows


def main():
    path = ROOT / 'sources/tb-heatmaps.ipynb'
    notebook = json.loads(path.read_text())
    revision = json.loads((ROOT/'sources/tb-experiments-tree.json').read_text())['sha']
    source = f'https://github.com/laude-institute/terminal-bench-experiments/blob/{revision}/notebooks/model_task_heatmaps.ipynb'
    rows = table(notebook, 6)
    headers = [v for _, v in rows[0]][1:]
    anchors = []; excluded = []
    for row in rows[1:]:
        record = dict(zip(headers, [v for _, v in row][1:]))
        rate = Decimal(record['p_hat']); n = int(record['n_trials'])
        assert rate*n == int(rate*n)
        item = dict(task=record['task_name'], model=record['model_display_name'],
                    scaffold=record['agent_display_name'], published_reward_mean=float(rate),
                    published_n_trials=n, derived_passes=int(rate*n),
                    published_n_errors=int(record['n_errors']), source_cell_zero_based=6)
        (excluded if item['published_n_errors'] else anchors).append(item)
    assert [(a['task'], a['derived_passes'], a['published_n_trials']) for a in anchors] == [
        ('bn-fit-modify',3,4), ('break-filter-js-from-html',0,5),
        ('build-cython-ext',4,4), ('build-pmars',5,5)]

    rows = table(notebook, 9)
    tasks = [v for _, v in rows[0]][2:]
    displayed = []; agent = None
    for row in rows[2:]:
        indexes = [v for kind,v in row if kind == 'th']
        if len(indexes) == 2: agent, model = indexes
        else: model = indexes[0]
        values = [v for kind,v in row if kind == 'td']
        assert len(tasks) == len(values)
        selected = {t:float(v) for t,v in zip(tasks,values) if t in {
            'caffe-cifar-10','train-fasttext','torch-pipeline-parallelism',
            'cancel-async-tasks','break-filter-js-from-html'}}
        displayed.append(dict(scaffold=agent, model=model, published_rates=selected,
                              n_trials=None, n_errors=None, source_cell_zero_based=9))
    assert len(displayed) == 5
    for r in displayed:
        for task in ['caffe-cifar-10','train-fasttext','torch-pipeline-parallelism']:
            assert r['published_rates'][task] == 0
    result = dict(
        interpretation='Published historical results, extracted rather than reproduced. Zero recorded exceptions is not an independent validity or trajectory audit.',
        source_url=source, source_sha256=hashlib.sha256(path.read_bytes()).hexdigest(),
        anchors=anchors, excluded_due_to_exceptions=excluded,
        limited_heatmap_evidence=displayed,
        calculations=dict(
            zero_of_five_uniform_prior_beta_1_6_equal_tail_95=[1-.975**(1/6),1-.025**(1/6)],
            binomial_n8_probability_k_le2_at_p025=sum(math.comb(8,k)*.25**k*.75**(8-k) for k in range(3)),
            binomial_n8_probability_k_le2_at_p05=sum(math.comb(8,k)*.5**8 for k in range(3)),
            illustrative_irt_p_weak_005_ability_gap_3=1/(1+math.exp(-(math.log(.05/.95)+3)))))
    (ROOT/'benchmark-evidence.json').write_text(json.dumps(result, indent=2)+'\n')
    print(f'Extracted {len(anchors)} anchors; excluded {len(excluded)} exception-bearing row; no notebook execution.')


if __name__ == '__main__': main()
