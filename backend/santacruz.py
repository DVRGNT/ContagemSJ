from flask import Flask, jsonify
from flask_cors import CORS
import gspread
from google.oauth2.service_account import Credentials
import pandas as pd
from datetime import datetime, timedelta
import os
    
app = Flask(__name__)
CORS(app, resources={r"/api/*": {"origins": "https://contagem-santacruz-sj.vercel.app"}})
    
def ler_dados_google_sheet():
        # ... (Esta função permanece a mesma da versão anterior, lendo a planilha)
        try:
            scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
            creds_path = '/home/GabrielBelo/credentials.json'
    
            if not os.path.exists(creds_path):
                print(f"ATENÇÃO: Arquivo de credenciais NÃO encontrado em: {creds_path}")
                return None
    
            creds = Credentials.from_service_account_file(creds_path, scopes=scope)
            client = gspread.authorize(creds)
    
            sheet_name = "radar_santa_cruz"
            sheet = client.open(sheet_name).sheet1
    
            data = sheet.get_all_records()
            if not data:
                print("A planilha parece estar vazia.")
                return pd.DataFrame()
    
            df = pd.DataFrame(data)
    
            required_cols = ["timestamp", "total_detected", "zone"]
            if not all(col in df.columns for col in required_cols):
                print(f"ERRO: Colunas necessárias ({required_cols}) não encontradas.")
                print(f"Colunas encontradas: {df.columns.tolist()}")
                return pd.DataFrame()
    
            # A linha mais importante, com o formato correto
            df['timestamp'] = pd.to_datetime(df['timestamp'], format='%d/%m/%Y %H:%M:%S', errors='coerce')
            df['total_detected'] = pd.to_numeric(df['total_detected'], errors='coerce').fillna(0)
            df.dropna(subset=['timestamp'], inplace=True)
    
            return df
    
        except Exception as e:
            print(f"Erro inesperado ao ler dados do Google Sheet: {e}")
            return None
    
@app.route('/api/impact-data')
def get_impact_data():
        df = ler_dados_google_sheet()
        if df is None or df.empty:
            return jsonify({
                "impactedToday": 0,
                "impactedTotal": 0,
                "peakHour": "N/D",
                "topZoneByPeople": "N/D", # Chave do JSON atualizada
                "error": "Dados não disponíveis ou planilha em formato incorreto"
            }), 500
    
        # --- Cálculos de Pessoas e Horário de Pico (permanecem os mesmos) ---
        hoje = datetime.now().date()
        df_hoje = df[df['timestamp'].dt.date == hoje]

        if not df_hoje.empty:
            impactadas_hoje = int(df_hoje['total_detected'].iloc[-1])
        else:
            impactadas_hoje = "Evento Pausado"
            
        impactadas_total = int(df['total_detected'].iloc[-1])  
    
        pico_por_hora = df.groupby(df['timestamp'].dt.hour)['total_detected'].sum()
        if not pico_por_hora.empty:
            hora_de_pico_num = pico_por_hora.idxmax()
            horario_pico_str = f"{int(hora_de_pico_num):02d}:00"
        else:
            horario_pico_str = "N/D"
    
        # --- LÓGICA ATUALIZADA: Zona com Mais Pessoas no Total ---
        # Agrupa os dados por 'Zona' e soma o número de 'Pessoas' em cada uma
        # Filtra o DataFrame para remover linhas onde 'Zona' é nula ou uma string vazia
        df_zonas = df.dropna(subset=['zone']) # Remove nulos
        df_zonas = df_zonas[df_zonas['zone'].astype(str).str.strip() != ''] # Remove strings vazias
    
        if not df_zonas.empty:
            # Agrupa os dados por 'Zona' e soma o número de 'Pessoas' em cada uma
            pessoas_por_zona = df_zonas.groupby('zone')['total_detected'].sum()
            if not pessoas_por_zona.empty:
                # Encontra a zona (index) com o maior valor de soma de pessoas
                zona_com_mais_pessoas = pessoas_por_zona.idxmax()
            else:
                zona_com_mais_pessoas = "Nenhuma"
        else:
            # Caso não haja nenhuma linha com uma zona válida
            zona_com_mais_pessoas = "Nenhuma"
    
    
        return jsonify({
            "impactedToday": impactadas_hoje,
            "impactedTotal": impactadas_total,
            "peakHour": horario_pico_str,
            "topZoneByPeople": zona_com_mais_pessoas # Retorna a nova variável com a chave atualizada
        })
    
if __name__ == '__main__':
    app.run(debug=True)