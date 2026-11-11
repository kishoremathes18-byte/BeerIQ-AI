from pathlib import Path
import pandas as pd
ROOT=Path(__file__).resolve().parents[1]/'data'
def test_published_system_recovery():
    r=pd.read_csv(ROOT/'official_2024_recovery.csv')
    total=r.loc[r.container_type=='Total'].iloc[0]
    assert total.returns_units==1180952679
    assert round(100*total.returns_units/(1011337204+542113278))==76

def test_channels_are_calculated_not_claimed_actual():
    c=pd.read_csv(ROOT/'official_2024_channels.csv')
    assert abs(c.share_2024_pct.sum()-99.99)<1e-8
    assert all(c.data_status.str.startswith('Calculated'))
    for row in c.itertuples():
        assert row.estimated_volume_hl_2024==round(3145896*row.share_2024_pct/100)
