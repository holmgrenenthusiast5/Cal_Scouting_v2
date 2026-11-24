"""Single-season college adaptation of LUMA Held-Out Adjusted Plus-Minus."""
import numpy as np
import pandas as pd
from scipy.sparse import diags
from scipy.sparse.linalg import cg
from deliver.fit import design
from pathlib import Path

def calculate(trips, players):
    offense = trips[[f'o{i}' for i in range(5)]].to_numpy()
    defense = trips[[f'd{i}' for i in range(5)]].to_numpy()
    X, ids = design(offense, defense, trips.side.eq('home').to_numpy())
    y = 100 * trips.points.to_numpy(float)
    penalty = np.full(X.shape[1], 1000.)
    penalty[-2:] = 0
    gram = (X.T @ X + diags(penalty)).tocsr()
    rhs = X.T @ y
    columns = X.tocsc()
    scores = []
    for player in players:
        j = np.searchsorted(ids, player)
        assert ids[j] == player
        off, defense_rows = [columns.indices[columns.indptr[k]:columns.indptr[k+1]] for k in (j,j+len(ids))]
        held = np.r_[off, defense_rows]
        assert len(np.unique(held)) == len(held)
        test = X[held]
        train_gram = gram - test.T @ test
        coef, status = cg(train_gram, rhs-test.T@y[held], M=diags(1/train_gram.diagonal()),rtol=1e-8)
        assert status == 0 and abs(coef[j])+abs(coef[j+len(ids)]) < 1e-7
        residual = y[held] - test @ coef
        # Fixed zero center and 500 pseudo-possessions per side for small samples.
        scores.append([residual[:len(off)].sum()/(len(off)+500), -residual[len(off):].sum()/(len(defense_rows)+500),len(off),len(defense_rows)])
    return np.array(scores)

if __name__ == '__main__':
    board=pd.read_csv('limited/limited.csv').iloc[:,:5]
    roster=pd.read_csv('deliver/all_player_estimates.csv')
    roster=roster[~roster.name.duplicated(False)]
    board=board.merge(roster[['id','name']],on='name',validate='one_to_one')
    assert len(board)==419
    board[['Off HAPM','Def HAPM','Rated off trips','Rated def trips']]=calculate(pd.read_csv('work/trips.csv.gz'),board.id)
    board['Total HAPM']=board['Off HAPM']+board['Def HAPM']
    board.drop(columns='id').sort_values('Total HAPM',ascending=False).to_csv('/workspace/shared/hapm/limited.csv',index=False,float_format='%.2f')
