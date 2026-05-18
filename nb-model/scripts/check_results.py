import pandas as pd, numpy as np
from pathlib import Path
from scipy import stats
import statsmodels.api as sm
from statsmodels.discrete.discrete_model import NegativeBinomial, Poisson
import warnings; warnings.filterwarnings('ignore')

ROOT = Path(__file__).resolve().parents[1]
df = pd.read_csv(ROOT / 'outputs' / 'nb_model_ready.csv')
df_model = df[~df['cv_split_flagged']].copy()

BASELINE_VARS = ['dim_type_4p','intensity_major','dim_priority_VRI','dim_priority_voorrang']
X      = sm.add_constant(df_model[BASELINE_VARS].copy())
y      = df_model['crash_count'].values.astype(float)
offset = np.log(df_model['exposure'].values)

pois = Poisson(y, X, offset=offset).fit(disp=False, maxiter=200)
print(f'=== POISSON (converged: {pois.mle_retvals["converged"]}) ===')
print(f'AIC={pois.aic:.2f}, LL={pois.llf:.3f}')
ci = pois.conf_int()
for var in pois.params.index:
    irr = np.exp(pois.params[var])
    lo  = np.exp(ci.loc[var].iloc[0])
    hi  = np.exp(ci.loc[var].iloc[1])
    p   = pois.pvalues[var]
    star = '***' if p<0.001 else '**' if p<0.01 else '*' if p<0.05 else '.' if p<0.1 else ''
    print(f'  {var:<25} IRR={irr:.3f}  [{lo:.3f},{hi:.3f}]  p={p:.3f} {star}')

nb = NegativeBinomial(y, X, loglike_method='nb2', offset=offset).fit(disp=False, maxiter=200)
print(f'\n=== NB2 (converged: {nb.mle_retvals["converged"]}) ===')
print(f'AIC={nb.aic:.2f}, LL={nb.llf:.3f}')
print(f'All params: {dict(nb.params.round(4))}')
print(f'All BSE:    {dict(nb.bse.round(4))}')
if 'alpha' in nb.params.index:
    a = nb.params['alpha']
    print(f'alpha param: {a:.4f} -> actual alpha = exp({a:.4f}) = {np.exp(a):.4f}')
