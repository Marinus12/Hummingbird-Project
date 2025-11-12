import pandas as pd

def simple_momentum(data: pd.DataFrame):
    """
    A trivial example: iterate 1-min bars, go long when close > previous close, exit next bar.
    Yields trade dicts.
    """
    data = data.sort_values('timestamp').reset_index(drop=True)
    for i in range(1, len(data)):
        prev = data.loc[i-1]
        cur = data.loc[i]
        if cur['close'] > prev['close']:
            # buy at next bar open (approx)
            yield {'time': cur['timestamp'], 'side': 'buy', 'price': cur['open'], 'size': 1}
            # exit on next bar close if available
            if i+1 < len(data):
                nxt = data.loc[i+1]
                yield {'time': nxt['timestamp'], 'side': 'sell', 'price': nxt['close'], 'size': 1}