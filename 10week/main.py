import pandas as pd
import sqlite3
from fastapi import FastAPI
import gradio as gr
from datetime import datetime

# --- 데이터 처리 함수들 (기존 코드 재사용) ---

DB_FILE = "AdventureWorks.db"
EXCEL_FILE = "AdventureWorks Sales.xlsx"

def setup_database():
    try:
        xls = pd.ExcelFile(EXCEL_FILE)
        conn = sqlite3.connect(DB_FILE)
        for sheet_name in xls.sheet_names:
            table_name = sheet_name.replace('_data', '')
            df = pd.read_excel(xls, sheet_name)
            df.to_sql(table_name, conn, if_exists='replace', index=False)
        print("데이터베이스 설정이 완료되었습니다.")
        conn.close()
        return True
    except Exception as e:
        print(f"데이터베이스 설정 중 오류 발생: {e}")
        return False

def perform_rfm_analysis():
    """
    RFM 분석을 수행하고 결과를 DataFrame으로 반환하는 함수.
    """
    try:
        conn = sqlite3.connect(DB_FILE)
        query = """
        SELECT 
            c.CustomerKey,
            d."Full Date" as OrderDate,
            s.SalesOrderLineKey,
            s."Sales Amount"
        FROM Sales s
        JOIN Customer c ON s.CustomerKey = c.CustomerKey
        JOIN Date d ON s.OrderDateKey = d.DateKey
        """
        df = pd.read_sql_query(query, conn)
        conn.close()

        df['OrderDate'] = pd.to_datetime(df['OrderDate'])
        snapshot_date = df['OrderDate'].max() + pd.DateOffset(days=1)
        
        rfm = df.groupby('CustomerKey').agg({
            'OrderDate': lambda date: (snapshot_date - date.max()).days,
            'SalesOrderLineKey': 'nunique', 
            'Sales Amount': 'sum'
        })
        rfm.rename(columns={'OrderDate': 'Recency', 'SalesOrderLineKey': 'Frequency', 'Sales Amount': 'Monetary'}, inplace=True)
        
        rfm['R_score'] = pd.qcut(rfm['Recency'], 5, labels=range(5, 0, -1), duplicates='drop').astype(int)
        rfm['F_score'] = pd.qcut(rfm['Frequency'].rank(method='first'), 5, labels=range(1, 6), duplicates='drop').astype(int)
        rfm['M_score'] = pd.qcut(rfm['Monetary'], 5, labels=range(1, 6), duplicates='drop').astype(int)
        rfm['RFM_Score'] = rfm[['R_score', 'F_score', 'M_score']].sum(axis=1)

        def segment_customer(df):
            if df['RFM_Score'] >= 12: return 'VIP 고객'
            elif df['RFM_Score'] >= 9: return '충성 고객'
            elif df['RFM_Score'] >= 5: return '잠재 고객'
            else: return '이탈 가능 고객'
        rfm['Segment'] = rfm.apply(segment_customer, axis=1)

        # CustomerKey를 인덱스에서 컬럼으로 변경
        return rfm.reset_index()

    except Exception as e:
        print(f"RFM 분석 중 오류 발생: {e}")
        # 오류 발생 시 빈 DataFrame 반환
        return pd.DataFrame()

# --- Gradio 인터페이스 생성 ---

# DB 초기 설정
setup_database() 

# Gradio 앱 정의
with gr.Blocks() as demo:
    gr.Markdown("# AdventureWorks Sales 데이터 분석")
    gr.Markdown("RFM 분석을 통해 고객을 세분화하고 비즈니스 인사이트를 도출합니다.")
    
    with gr.Tab("RFM 분석 결과"):
        rfm_output = gr.DataFrame(label="고객 세그먼테이션 결과")
        # "분석 실행" 버튼을 누르면 perform_rfm_analysis 함수가 실행되고, 그 결과가 rfm_output에 표시됨
        rfm_button = gr.Button("RFM 분석 실행")
        rfm_button.click(fn=perform_rfm_analysis, inputs=None, outputs=rfm_output)

# --- FastAPI 앱에 Gradio 앱 마운트 ---

# FastAPI 앱 생성
app = FastAPI()

# Gradio 앱을 '/gradio' 경로에 추가
app = gr.mount_gradio_app(app, demo, path="/gradio")

# 기존 API 엔드포인트들도 그대로 유지 (선택 사항)
@app.get("/")
def read_root():
    return {"message": "FastAPI 서버가 실행 중입니다. UI는 /gradio 경로에 있습니다."}

@app.get("/rfm-json/")
def get_rfm_json():
    df = perform_rfm_analysis()
    return df.to_dict('records')

