import streamlit as st
from pykrx import stock
from datetime import datetime
from pytz import timezone, utc
import pandas as pd
import numpy as np
import plotly.express as px


KST = timezone('Asia/Seoul')
now = datetime.utcnow()

SeoulTime = utc.localize(now).astimezone(KST)

df = stock.get_index_ohlcv("19890701", SeoulTime, "1001")

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
df4
fig = px.scatter(df4, x='2nd half', y='1st half', color='year', text='year', width=800, height=800)
fig.update_traces(textposition='bottom right', textfont_size=8)
fig.update_xaxes(tickformat=',.1%')
fig.update_yaxes(tickformat=',.1%')
fig.update_layout(showlegend=False)
fig.add_vline(x=0, line_width=0.5)
fig.add_hline(y=0, line_width=0.5)
#fig.show()

st.plotly_chart(fig)
