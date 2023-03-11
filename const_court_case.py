# impport packages
import requests
from bs4 import BeautifulSoup
import pandas as pd
import streamlit as st
import time

st.set_page_config(
    page_title="헌법재판소 결과 파인더",
    page_icon=":open_book:",
    layout="wide",
)

# funtion def
def get_case(casenum):

    url = 'http://openapi.ccourt.go.kr/openapi/services/PrecedentSearchSvc/getPrcdntSearchInfo'
    params ={    
        'serviceKey': st.secrets["API_KEY"], 
        'eventNo': casenum
    }

    colnames = ['사건번호', '사건명', '재판부', '종국일자', '종국결과']

    resp = requests.get(url, params)
    soup = BeautifulSoup(resp.content, features="xml")
    items = soup.find_all('item')
    print(items)
    # assert(len(items)==1)
    try:
        item = items[0]
        
        df_result = pd.DataFrame([
            # item.find('eventNum').text,  # 판례번호
            item.find('eventNo').text,  # 사건번호
            item.find('eventNm').text,  # 사건명
            item.find('jgdmtCort').text,  # 재판부
            item.find('rstaDate').text,  # 종국일자
            item.find('rstaRsta').text  # 종국결과
        ], index=colnames).T

        return df_result

    except:
        pass


st.markdown("<h1 style='text-align: left; color: #1E90FF;'>헌법재판소 종국결과 파인더</h1>", unsafe_allow_html=True)

cases = st.text_area(
    '사건번호를 입력하세요.   다수의 사건번호는 쉼표(,)로 분리하세요.'
)

# @st.experimental_memo
@st.cache_data
def convert_df(df):
   return df.to_csv().encode('utf-8')

if st.button('요청'):
    st.write('요청을 받았습니다.')
    st.write(cases)

    case_list = cases.replace(' ', '').split(',')
    if all([len(case_list) >= 1, case_list[0] != '']):
        print(case_list)
        df_result = pd.DataFrame(columns=['사건번호', '사건명', '재판부', '종국일자', '종국결과'])    
        for case in case_list:            
            df_tmp = get_case(case)
            if df_tmp is None:
                st.write('결과가 없습니다: ', case)
                continue
            df_result = pd.concat([df_result, df_tmp])
            time.sleep(0.1)
        st.write(df_result.reset_index(drop=True))   
    
        st.download_button(
            label='다운로드 테이블',
            data=convert_df(df_result),
            file_name="file.csv",
            mime="text/csv",
            key='download-csv'
        )

    else:
        st.write('사건번호를 입력하세요.')

