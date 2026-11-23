import json,html
from pathlib import Path
import pandas as pd,numpy as np
from sklearn.pipeline import make_pipeline
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import Ridge
import sys
sys.path.insert(0,'star_model')
from fit import key
s=pd.read_csv('star_model/season_features.csv').dropna(subset=['O','D']);rates=['boxO','boxD','usage','efg','three_rate','ft_rate','shots40']
s=s.drop(columns=rates).merge(pd.read_csv('opponent_update/adjusted.csv')[['id','year']+rates],on=['id','year'],validate='one_to_one')
s['poss']=np.expm1(s.volume).round();later=s[['id','year','O','D','poss']].copy();later.year-=1
d=s.merge(later,on=['id','year'],suffixes=('','_next')).query('500<=poss<1500 and poss_next>=1000')
features=['O','D','volume','team_strength']+rates
def fit(t):return make_pipeline(SimpleImputer(),StandardScaler(),Ridge(alpha=100)).fit(t[features],t[['O_next','D_next']])
v=d[d.year==2025].copy();v['forecast']=fit(d[d.year<2025]).predict(v[features]).sum(1);actual=v.O_next+v.D_next
rho=v.forecast.corr(actual,method='spearman');base=(v.O+v.D).corr(actual,method='spearman')
low=pd.read_csv('opponent_update/low-possession-board.csv');low=low[low[['off_possessions','def_possessions']].min(axis=1)>=250].copy();low['key']=low.name.map(key);latest=s[s.year==2026];q=low.merge(latest[~latest.key.duplicated(False)],on='key',validate='one_to_one',suffixes=('','_s'))
pred=fit(d).predict(q[features]);q['Projected offense']=pred[:,0];q['Projected defense']=pred[:,1];q['Projected total']=pred.sum(1)
cols=['name','Current school','Current class','off_possessions','def_possessions','Projected offense','Projected defense','Projected total'];q=q.sort_values('Projected total',ascending=False)[cols].round(2);q.to_csv('limited/limited.csv',index=False)
source=Path('opponent_update/live/index.html').read_text();section=f"""<section id="limited"><div class="eyebrow">2026–27 scouting classes</div><h2>Limited-possession projections</h2><p>{len(q)} juniors and sophomores with at least 250 possessions on each side and fewer than 750 on one or both. Offensive and defensive projections sum to expected next-season national total RAPM, in points per 100 possessions.</p><details><summary>Model and transferability</summary><p>A separate ridge regression uses prior offensive and defensive RAPM, exposure, team strength and opponent-adjusted box statistics. Historical training uses 500–1,499 combined possessions and requires 1,000 observed the following season. The cohort includes returning players and transfers across Division I. In a held-out 2025–26 test across {len(v):,} players, projected and actual next-season impact had a rank correlation of {rho:.3f}. Ranking those players by prior RAPM alone yielded {base:.3f}.</p></details><label>Find a player or school <input id="lowfilter" type="search"></label><div class="tablebox" style="max-height:32rem;overflow:auto"><table><thead><tr>"""+''.join('<th>'+h+'</th>' for h in ['Player','Current school','Class','Off poss','Def poss','Proj O','Proj D','Proj total'])+'</tr></thead><tbody id="lowrows">'+''.join('<tr>'+''.join('<td>'+html.escape(str(x))+'</td>' for x in row)+'</tr>' for row in q.itertuples(index=False,name=None))+'</tbody></table></div></section>'
source=source.replace('<a href="#method">','<a href="#limited">Limited possessions</a><a href="#method">',1).replace('<section id="method">',section+'<section id="method">').replace('</html>',"""<script>document.getElementById('lowfilter').oninput=function(){for(const row of document.getElementById('lowrows').rows){row.hidden=!row.textContent.toLowerCase().includes(this.value.toLowerCase())}}</script></html>""")
Path('limited/index.html').write_text(source);print(len(q),len(v),rho,base,q.head(3))
