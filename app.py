import streamlit as st
from pykrx import stock
from datetime import datetime
from pytz import timezone, utc
import pandas as pd
import numpy as np
import plotly.express as px


st.header("KOSPI Analysis Charts")

KST = timezone('Asia/Seoul')
now = datetime.utcnow()

SeoulTime = utc.localize(now).astimezone(KST)

df = stock.get_index_ohlcv("19890701", SeoulTime, "1001")


# figure 1

st.subheader("Figure 1")

df1 = df.reset_index()[['날짜', '종가']].copy()
df2 = df1[~df1['날짜'].dt.strftime('%Y-%m').duplicated()].copy()
df3 = df2[(df2['날짜'].astype(str).str[5:7]).isin(['01', '07'])].copy()
df3['change'] = df3['종가'].pct_change(periods=1, axis=0)
df3['change'] = df3['change'].shift(-1)
df3['change'] = df3['change'].fillna(0)
#df3 = df3[1:]
df3['half'] = np.where(df3['날짜'].astype(str).str[5:7]=='01', '1st half', '2nd half')
df3['year'] = df3['날짜'].astype(str).str[:4]
df4 = df3.pivot_table(values='change', index='year', columns='half').reset_index()
df4 = df4[1:]

fig = px.scatter(df4, x='2nd half', y='1st half', color='year', text='year', width=800, height=800)
fig.update_traces(textposition='bottom right', textfont_size=8)
fig.update_xaxes(tickformat=',.1%')
fig.update_yaxes(tickformat=',.1%')
fig.update_layout(showlegend=False)
fig.add_vline(x=0, line_width=0.5)
fig.add_hline(y=0, line_width=0.5)
#fig.show()

st.plotly_chart(fig)


# figure 2

st.subheader("Figure 2")

df_1 = stock.get_index_fundamental("20020701", SeoulTime, "1001")
df_2 = pd.merge(df_1, df3, how='inner', on='날짜')
df_2['year_half'] = df_2['year'] + ' ' + df_2['half']
df_2['year_half'] = df_2['year_half'].str.replace(' half', '')
fig_1 = px.scatter(df_2, x='PBR', y='change', color='year_half', text='year_half', width=600, height=800)
fig_1.update_traces(textposition='bottom right', textfont_size=8)
fig_1.update_xaxes(tickformat=',.2f')
fig_1.update_yaxes(tickformat=',.1%')
fig_1.update_layout(showlegend=False)
fig_1.add_vline(x=1, line_width=0.5)
fig_1.add_hline(y=0, line_width=0.5)
#fig_1.show()

st.plotly_chart(fig_1)


# figure 3

st.subheader("Figure 3")

df_111 = df_1.reset_index()[['날짜', '종가', 'PER', 'PBR', '배당수익률']]
df_112 = df_111[(df_111['날짜']>='2003-01-01')].reset_index(drop=True)

df_113 = df_112.set_index('날짜').resample('2Q', closed='left').agg(['min','max']).reset_index()
df_113.columns = np.where(df_113.columns.get_level_values(1) != '', df_113.columns.get_level_values(0) + '_' + df_113.columns.get_level_values(1), df_113.columns.get_level_values(0))
#display(df_113)

df_114 = df_111[~df_111['날짜'].dt.strftime('%Y-%m').duplicated()].copy()
df_115 = df_114[(df_114['날짜'].astype(str).str[5:7]).isin(['01', '07'])].copy()

df_116 = pd.merge_asof(df_115, df_113, on='날짜')[['날짜', '종가', 'PER', 'PBR', '배당수익률', '종가_min', '종가_max']][1:]
df_116['종가_min'] = df_116['종가_min'].shift(-1)
df_116['종가_max'] = df_116['종가_max'].shift(-1)
df_116['상승'] = df_116['종가_max'] / df_116['종가'] - 1
df_116['하락'] = df_116['종가_min'] / df_116['종가'] - 1
df_116['변동'] = np.where(df_116['상승'].abs() > df_116['하락'].abs(), df_116['상승'], df_116['하락'])
df_116['updn'] = np.where(df_116['변동'] == df_116['상승'], 'up', 'dn')
df_116 = df_116.fillna(0)
df_116['half'] = np.where(df_116['날짜'].astype(str).str[5:7]=='01', '1st half', '2nd half')
df_116['year'] = df_116['날짜'].astype(str).str[:4]
df_116['year_half'] = df_116['year'] + ' ' + df_2['half']
df_116['year_half'] = df_116['year_half'].str.replace(' half', '')

#display(df_116)

fig_2 = px.scatter(df_116, x='PBR', y='변동', color='year_half', text='year_half', width=600, height=800)
fig_2.update_traces(textposition='bottom right', textfont_size=8)
fig_2.update_xaxes(tickformat=',.2f')
fig_2.update_yaxes(tickformat=',.1%')
fig_2.update_layout(showlegend=False)
fig_2.add_vline(x=1, line_width=0.5)
fig_2.add_hline(y=0, line_width=0.5)
#fig_2.show()

st.plotly_chart(fig_2)
