import pandas_datareader
pandas_datareader.__version__
import pandas_datareader as web
import datetime as dt
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

start = dt.datetime(2020,1,1)
end = dt.datetime.now()
eth = web.DataReader('ETH-USD', 'yahoo', start, end)
sol = web.DataReader('SOL-USD', 'yahoo', start, end)
ada = web.DataReader('ADA-USD', 'yahoo', start, end)

# Eth
eth['9-day'] = eth['Close'].rolling(9).mean() 
eth['21-day'] = eth['Close'].rolling(21).mean() 
eth['signal'] = np.where(eth['9-day'] > eth['21-day'], 1, 0)
eth['signal'] = np.where(eth['9-day'] < eth['21-day'], -1, eth['signal'])
eth['eth return'] = eth['Adj Close'].pct_change().dropna()
eth['system return'] = eth['signal'] * eth['eth return']
eth['entry'] = eth.signal.diff()
eth['entry'][0] = 1
# Sol
sol['9-day'] = sol['Close'].rolling(9).mean() 
sol['21-day'] = sol['Close'].rolling(21).mean()
sol['signal'] = np.where(sol['9-day'] > sol['21-day'], 1, 0)
sol['signal'] = np.where(sol['9-day'] < sol['21-day'], -1, sol['signal'])
sol['sol return'] = sol['Adj Close'].pct_change().dropna()
sol['system return'] = sol['signal'] * sol['sol return']
sol['entry'] = sol.signal.diff()
sol['entry'][0] = 1
# Ada
ada['9-day'] = ada['Close'].rolling(9).mean() 
ada['21-day'] = ada['Close'].rolling(21).mean() 
ada['signal'] = np.where(ada['9-day'] > ada['21-day'], 1, 0)
ada['signal'] = np.where(ada['9-day'] < ada['21-day'], -1, ada['signal'])
ada['ada return'] = ada['Adj Close'].pct_change().dropna()
ada['system return'] = ada['signal'] * ada['ada return']
ada['entry'] = ada.signal.diff()
ada['entry'][0] = 1


# Organize Database
def engine(eth,sol,ada):
    eth=eth.loc[:, ['eth return', 'signal', 'system return']].dropna()
    sol=sol.loc[:, ['sol return', 'signal', 'system return']].dropna()
    ada=ada.loc[:, ['ada return', 'signal', 'system return']].dropna()
    merged=pd.merge(eth,pd.merge(sol,ada,on="Date"),on="Date")
    merged.rename(columns={"signal":"signal eth","entry":"entry eth","signal_x":"signal sol", 'entry_x': 'entry sol', "signal_y":"signal ada", 'entry_y': 'entry ada'} ,inplace=True)
    return merged[22:]
df = engine(eth,sol,ada).dropna()

weight_eth = 1/3
weight_sol = 1/3
weight_ada = 1/3

df['returns per weight eth'] = weight_eth * df['system return']
df['returns per weight sol'] = weight_sol * df['system return_x']
df['returns per weight ada'] = weight_ada * df['system return_y']
df['portfolio returns'] = df['returns per weight eth'] + df['returns per weight sol'] + df['returns per weight ada']
df['market return'] = (df['eth return'] + df['sol return'] + df['ada return']) / 3
# df.to_excel(r"C:\Users\João Saraiva\Desktop\portfolio.xlsx", sheet_name = 'returns')


ptf_ret = pd.DataFrame()
ptf_ret['ptf ret'] = df['portfolio returns'][608:]
ptf_ret['cum ptf return'] = (ptf_ret['ptf ret'] + 1).cumprod()
a = ptf_ret['ptf ret']

mkt_ret = pd.DataFrame()
mkt_ret['mkt ret'] = df['market return'][608:]
mkt_ret['cum mkt return'] = (mkt_ret['mkt ret'] + 1).cumprod()
b = mkt_ret['mkt ret']

a.plot(kind = 'hist', figsize = (12, 8), bins = 50, alpha = 0.5, legend = 'Portfolio Returns ')
b.plot(kind = 'hist', figsize = (12, 8), bins = 50, alpha = 0.5, legend = 'Market Returns')
plt.legend(fontsize = 18)
# random.normal(a)
# random.normal(b)

# Summary Statistics

ptf_stats = a.describe()[1:]
ptf_stats.loc['skewness'] = a.skew()
ptf_stats.loc['kurtosis'] = a.kurtosis()
ptf_stats.loc['VaR 90%'] = a.quantile(0.1).round(4)
ptf_stats.loc['VaR 99%'] = a.quantile(0.01).round(4)
ptf_stats.loc['Sharpe Ratio'] = ptf_stats.loc['mean'] / ptf_stats.loc['std']

mkt_stats = b.describe()[1:]
mkt_stats.loc['skewness'] = b.skew()
mkt_stats.loc['kurtosis'] = b.kurtosis()
mkt_stats.loc['VaR 90%'] = b.quantile(0.1).round(4)
mkt_stats.loc['VaR 99%'] = b.quantile(0.01).round(4)
mkt_stats.loc['Sharpe Ratio'] = mkt_stats.loc['mean'] / mkt_stats.loc['std']

all_stats = pd.concat([ptf_stats, mkt_stats], axis = 1)
all_stats.to_excel(r"C:\Users\João Saraiva\Desktop\all stats.xlsx")


sharpe_ratio_ptf_testing = ptf_ret['ptf ret'].mean()/(ptf_ret['ptf ret'].std())
sharpe_ratio_mkt_testing = mkt_ret['mkt ret'].mean()/(mkt_ret['mkt ret'].std())



fig, ax = plt.subplots(figsize=(16,9))

ax.plot(a.index, a, label='MA strategy')
ax.plot(b.index, b, label='Buy and hold')

ax.set_ylabel('Total cumulative relative returns (%)')
ax.legend(loc='best', prop = {'size': 20})

plt.rcParams['figure.figsize'] = 12, 6
plt.grid(True, alpha = .3)
plt.plot(a, label = 'MA Strategy Cumulative Returns')
plt.plot(b, label = 'Buy & Hold Cumulative Returns')
plt.ylabel('Cumulative Returns', size = 15)
plt.legend(loc=2);

# Plots - Testing

plt.rcParams['figure.figsize'] = 12, 6
plt.grid(True, alpha = .3)
plt.plot(eth.iloc[0:365]['Close'], label = 'eth')
plt.plot(eth.iloc[0:365]['9-day'], label = '10MA')
plt.plot(eth.iloc[0:365]['21-day'], label = '30MA')
plt.plot(eth[0:365].loc[eth.entry == 2].index, eth[0:365]['9-day'][eth.entry == 2], '^',
         color = 'g', markersize = 12, label = 'long')
plt.plot(eth[0:365].loc[eth.entry == -2].index, eth[0:365]['21-day'][eth.entry == -2], 'v',
         color = 'r', markersize = 12, label = 'short')
plt.legend(loc=2);

plt.rcParams['figure.figsize'] = 12, 6
plt.grid(True, alpha = .3)
plt.plot(sol.iloc[:-280]['Close'], label = 'sol')
plt.plot(sol.iloc[:-280]['9-day'], label = '9-day')
plt.plot(sol.iloc[:-280]['21-day'], label = '21-day')
plt.plot(sol[:-280].loc[sol.entry == 2].index, sol[:-280]['9-day'][sol.entry == 2], '^',
         color = 'g', markersize = 12, label = 'long')
plt.plot(sol[:-280].loc[sol.entry == -2].index, sol[:-280]['21-day'][sol.entry == -2], 'v',
         color = 'r', markersize = 12, label = 'short')
plt.legend(loc=2);


plt.rcParams['figure.figsize'] = 12, 6
plt.grid(True, alpha = .3)
plt.plot(ada.iloc[:-280]['Close'], label = 'ada')
plt.plot(ada.iloc[:-280]['9-day'], label = '9-day')
plt.plot(ada.iloc[:-280]['21-day'], label = '21-day')
plt.plot(ada[:-280].loc[ada.entry == 2].index, ada[:-280]['9-day'][ada.entry == 2], '^',
         color = 'g', markersize = 12)
plt.plot(ada[:-280].loc[ada.entry == -2].index, ada[:-280]['21-day'][ada.entry == -2], 'v',
         color = 'r', markersize = 12)
plt.legend(loc=2);


# Plots - 2022

plt.rcParams['figure.figsize'] = 12, 6
plt.grid(True, alpha = .3)
plt.plot(eth.iloc[-252:]['Close'], label = 'eth')
plt.plot(eth.iloc[-252:]['9-day'], label = '9-day')
plt.plot(eth.iloc[-252:]['21-day'], label = '21-day')
plt.plot(eth[-252:].loc[eth.entry == 2].index, eth[-252:]['9-day'][eth.entry == 2], '^',
         color = 'g', markersize = 12)
plt.plot(eth[-252:].loc[eth.entry == -2].index, eth[-252:]['21-day'][eth.entry == -2], 'v',
         color = 'r', markersize = 12)
plt.legend(loc=2);

plt.rcParams['figure.figsize'] = 12, 6
plt.grid(True, alpha = .3)
plt.plot(sol.iloc[-252:]['Close'], label = 'sol')
plt.plot(sol.iloc[-252:]['9-day'], label = '9-day')
plt.plot(sol.iloc[-252:]['21-day'], label = '21-day')
plt.plot(sol[-252:].loc[sol.entry == 2].index, sol[-252:]['9-day'][sol.entry == 2], '^',
         color = 'g', markersize = 12)
plt.plot(sol[-252:].loc[sol.entry == -2].index, sol[-252:]['21-day'][sol.entry == -2], 'v',
         color = 'r', markersize = 12)
plt.legend(loc=2);

plt.rcParams['figure.figsize'] = 12, 6
plt.grid(True, alpha = .3)
plt.plot(ada.iloc[-252:]['Close'], label = 'ada')
plt.plot(ada.iloc[-252:]['9-day'], label = '9-day')
plt.plot(ada.iloc[-252:]['21-day'], label = '21-day')
plt.plot(ada[-252:].loc[ada.entry == 2].index, ada[-252:]['9-day'][ada.entry == 2], '^',
         color = 'g', markersize = 12)
plt.plot(ada[-252:].loc[ada.entry == -2].index, ada[-252:]['21-day'][ada.entry == -2], 'v',
         color = 'r', markersize = 12)
plt.legend(loc=2);
