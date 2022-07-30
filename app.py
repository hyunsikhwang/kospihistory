import streamlit as st
from pykrx import stock
from datetime import datetime
from pytz import timezone, utc
import pandas as pd
import numpy as np
import plotly.express as px
import requests
import json


st.header("KOSPI Analysis Charts")

KST = timezone('Asia/Seoul')
now = datetime.utcnow()

SeoulTime = utc.localize(now).astimezone(KST)

df = stock.get_index_ohlcv("19890701", SeoulTime, "1001")

tab1, tab2, tab3 = st.tabs(["Fig1", "Fig2", "Fig3"])

# figure 1

with tab1:
    st.subheader("Figure 1")

    df1 = df.reset_index()[['날짜', '종가']].copy()
    df2 = df1[~df1['날짜'].dt.strftime('%Y-%m').duplicated()].copy()
    df3 = df2[(df2['날짜'].astype(str).str[5:7]).isin(['01', '07'])].copy()

    # 가장 최근 날짜의 레코드를 추가해서 가장 최근 반기가 종료되기 전에도 현재 기준 수익률을 확인할 수 있도록 함
    df3 = pd.concat([df3, df1.tail(1)])

    df3['change'] = df3['종가'].pct_change(periods=1, axis=0)
    df3['change'] = df3['change'].shift(-1)
    df3['change'] = df3['change'].fillna(0)
    df3['half'] = np.where(df3['날짜'].astype(str).str[5:7]=='01', '1st half', '2nd half')
    df3['year'] = df3['날짜'].astype(str).str[:4]
    df3 = df3[:-1]

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

    st.plotly_chart(fig, unsafe_allow_html=True)

with tab2:
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

    st.plotly_chart(fig_1, unsafe_allow_html=True)

with tab3:
    # figure 3 - CPI vs PER

    st.subheader("Figure 3 - CPI vs PER")

    #소비자물가지수
    ECOS_API_KEY = st.secrets["ECOS_API_KEY"]
    url = f'http://ecos.bok.or.kr/api/StatisticSearch/{ECOS_API_KEY}/json/kr/1/10000/901Y009/M/199901/202207/0'

    res = requests.get(url)
    resJsn = json.loads(res.text)['StatisticSearch']['row']
    df_cpi = pd.DataFrame(resJsn)

    df_cpi['DATA_VALUE'] = df_cpi['DATA_VALUE'].astype(float)
    df_cpi['DATA_VALUE_pct'] = df_cpi['DATA_VALUE'].pct_change(periods=12)
    #df_cpi['TIME'] = pd.to_datetime(df_cpi['TIME'], format='%Y%m', errors='coerce').dropna()
    df_cpi['TIME'] = df_cpi['TIME'].astype(str)

    df_111 = df_1.reset_index()[['날짜', '종가', 'PER', 'PBR', '배당수익률']]
    df_1111 = df_111[~df_111['날짜'].dt.strftime('%Y-%m').duplicated()].copy()
    df_1111['날짜'] = df_1111['날짜'].astype(str).str[:7].str.replace('-', '')

    df_cpi_per = pd.merge(df_cpi, df_1111, how='left', left_on='TIME', right_on='날짜')[['TIME', 'DATA_VALUE_pct', 'PER']].dropna()
    df_cpi_per = df_cpi_per[(df_cpi_per['DATA_VALUE_pct'] > 0)]
    df_cpi_per['TIME'] = df_cpi_per['TIME'].astype(str).str[:7]
    df_cpi_per['year'] = df_cpi_per['TIME'].str[:4]

    fig_cpi_per = px.scatter(df_cpi_per, x='DATA_VALUE_pct', y='PER', text='TIME', trendline="ols", trendline_options=dict(log_x=True),
                            width=800, height=800, trendline_scope="overall", trendline_color_override="red", color='year')
    fig_cpi_per.update_traces(textposition="top right")
    fig_cpi_per.update_layout(
        font=dict(
            size=7
        )
    )

    st.plotly_chart(fig_cpi_per, unsafe_allow_html=True)
