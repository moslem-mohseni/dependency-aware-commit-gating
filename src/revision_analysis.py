"""Measured extraction quality and fresh-stream policy results."""
from pathlib import Path
import sys
import pandas as pd
sys.path.insert(0,str(Path(__file__).resolve().parent))
from stats_utils import wilson,paired_diff_ci
ROOT=Path(__file__).resolve().parents[1]

def main():
    d=pd.read_csv(ROOT/'results/dependency_extraction.csv');rows=[]
    for (policy,kind),g in d.groupby(['policy','kind']):
        row=dict(policy=policy,kind=kind,n=len(g),checks=g.checks.mean(),first_commit=g.executed_irrev.mean())
        for metric in ('harm','done','stopped'):
            row[metric],row[metric+'_lo'],row[metric+'_hi']=wilson(int(g[metric].sum()),len(g))
        for prefix in ('edge','reach'):
            if prefix+'_tp' in g and g[prefix+'_tp'].notna().any():
                row[prefix+'_precision']=g[prefix+'_tp'].sum()/g[prefix+'_pred'].sum()
                row[prefix+'_recall']=g[prefix+'_tp'].sum()/g[prefix+'_true'].sum()
        rows.append(row)
    pd.DataFrame(rows).to_csv(ROOT/'results/extraction_summary.csv',index=False)
    contrasts=[]
    for kind,metric in [('DOWN','harm'),('act','done'),('INDEP','executed_irrev'),('act','checks')]:
        pivot=d[d.kind==kind].pivot(index='base',columns='policy',values=metric)
        for policy in ('gate_text','gate_shared'):
            effect,lo,hi,dz=paired_diff_ci(pivot[policy],pivot.gate,n_boot=1000,seed=71)
            contrasts.append(dict(policy=policy,kind=kind,metric=metric,diff=effect,lo=lo,hi=hi,dz=dz))
    pd.DataFrame(contrasts).to_csv(ROOT/'results/extraction_contrasts.csv',index=False)
    print('Fresh extraction summaries and nominal intervals saved')

if __name__=='__main__':main()
