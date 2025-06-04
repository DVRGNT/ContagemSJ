from flask import Flask, jsonify
from flask_cors import CORS
import gspread
from google.oauth2.service_account import Credentials # Para google-auth
import pandas as pd
from datetime import datetime
import os # Para variáveis de ambiente

app = Flask(__name__)
# Configure CORS para seu domínio Vercel
CORS(app, resources={r"/api/*": {"origins": "https://SEU_DOMINIO_DO_VERCEL.vercel.app"}})

def ler_dados_google_sheet():
    try:
        # Escopo da API do Google Sheets
        scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']

        # CAMINHO DIRETO PARA SEU ARQUIVO DE CREDENCIAIS NO PYTHONANYWHERE
        creds_path = '/home/GabrielBelo/credentials.json' # <--- ALTERAÇÃO PRINCIPAL AQUI

        # Verifica se o arquivo de credenciais existe no caminho especificado
        if not os.path.exists(creds_path):
            print(f"ATENÇÃO: Arquivo de credenciais NÃO encontrado em: {creds_path}")
            print("Verifique se o arquivo foi carregado corretamente para este local no PythonAnywhere.")
            return None # Falha ao carregar credenciais se o arquivo não existir

        # Carrega as credenciais do arquivo JSON especificado
        creds = Credentials.from_service_account_file(creds_path, scopes=scope)

        # Autoriza o cliente gspread com as credenciais carregadas
        client = gspread.authorize(creds)

        # Abra a planilha pelo nome ou URL
        # Substitua 'NomeDaSuaPlanilha' pelo nome exato ou ID da sua planilha
        # Certifique-se que a conta de serviço (do credentials.json) tem permissão para acessar esta planilha
        sheet_name = "GraficoTeste" # COLOQUE O NOME DA SUA PLANILHA AQUI
        try:   
            sheet = client.open(sheet_name).worksheet("pagina1") # Abre a primeira aba (sheet1)
        except gspread.exceptions.SpreadsheetNotFound:
            print(f"ERRO: Planilha '{sheet_name}' não encontrada. Verifique o nome e se a conta de serviço tem permissão.")
            return None
        except Exception as e_open:
            print(f"Erro ao abrir a planilha '{sheet_name}': {e_open}")
            return None

        # Extrai todos os valores como uma lista de dicionários
        data = sheet.get_all_records()
        if not data: # Se a planilha estiver vazia ou get_all_records() retornar vazio
            print("A planilha parece estar vazia ou não foi possível ler os registros.")
            # Retorna um DataFrame vazio com as colunas esperadas para evitar erros posteriores
            return pd.DataFrame(columns=['Data', 'PessoasImpactadas'])

        df = pd.DataFrame(data)

        # Verificações e conversões de colunas
        # Certifique-se que os nomes das colunas ('Data', 'PessoasImpactadas')
        # correspondem EXATAMENTE aos cabeçalhos da sua planilha Google.
        if 'Data' not in df.columns or 'PessoasImpactadas' not in df.columns:
            print("ERRO: As colunas 'Data' ou 'PessoasImpactadas' não foram encontradas na planilha.")
            print(f"Colunas encontradas: {df.columns.tolist()}")
            # Retorna um DataFrame vazio com as colunas esperadas para evitar erros posteriores
            return pd.DataFrame(columns=['Data', 'PessoasImpactadas'])

        df['Data'] = pd.to_datetime(df['Data'], errors='coerce')
        df['PessoasImpactadas'] = pd.to_numeric(df['PessoasImpactadas'], errors='coerce').fillna(0)

        return df

    except gspread.exceptions.APIError as e_api:
        print(f"Erro de API do Google Sheets: {e_api}")
        print("Verifique as cotas da API, permissões da conta de serviço e se a API está habilitada no Google Cloud Console.")
        return None
    except Exception as e:
        print(f"Erro inesperado ao ler dados do Google Sheet: {e}")
        return None

@app.route('/api/impact-data')
def get_impact_data():
    df = ler_dados_google_sheet() # LÊ OS DADOS FRESCOS A CADA CHAMADA
    if df is None or df.empty:
        return jsonify({"impactedToday": 0, "impactedTotal": 0, "error": "Dados não disponíveis"}), 500

    hoje = datetime.now().date()
    df_hoje = df[df['Data'].dt.date == hoje]
    impactadas_hoje = int(df_hoje['PessoasImpactadas'].sum())
    impactadas_total = int(df['PessoasImpactadas'].sum())

    return jsonify({
        "impactedToday": impactadas_hoje,
        "impactedTotal": impactadas_total
    })

if __name__ == '__main__':
    # Este modo de execução é para desenvolvimento local,
    # o PythonAnywhere usará um servidor WSGI como Gunicorn.
    app.run(debug=True)