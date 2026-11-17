import pandas as pd
import io
from enviroment import enviroment
import psycopg2

ARQUIVO_ESCOLA = "dados/Tabela_Escola_2025_V2.csv" 
ARQUIVO_MATRICULA = "dados/Tabela_Matricula_2025_V2.csv"
NOME_TABELA = "tb_instituicao_ensino"

DB_CONFIGURACAO = {
    "host": enviroment.get("DB_HOST"),
    "port": int(enviroment.get("DB_PORT")),
    "database": enviroment.get("DB_NAME"),
    "user": enviroment.get("DB_USER"),
    "password": enviroment.get("DB_PASSWORD")
}

lista_colunas = [
    "co_entidade",
    "nu_ano_censo",
    "no_entidade",
    "co_uf",
    "sg_uf",
    "no_uf",
    "co_municipio",
    "no_municipio",
    "qt_mat_bas",
    "qt_mat_inf",
    "qt_mat_fund",
    "qt_mat_med",
    "qt_mat_prof",
    "qt_mat_eja",
    "qt_mat_esp",
]
campos_mat = [col for col in lista_colunas if col.startswith("qt_mat_")]
colunas_escolas = [col for col in lista_colunas if col not in campos_mat] + ["no_regiao"]
colunas_matriculas = ["co_entidade"] + campos_mat

print("lendo tabela de Escolas...")
escolas = pd.read_csv(ARQUIVO_ESCOLA, encoding="latin-1", sep=";",usecols=lambda c: c.lower() in colunas_escolas, low_memory=False,).rename(columns=str.lower)

print("filtrano as regiões Nordeste e Sudeste...")
escolas = escolas[escolas["no_regiao"].str.lower().isin(["nordeste", "sudeste"])]

print("lendo tabela de Matriculas....")
matriculas = pd.read_csv(ARQUIVO_MATRICULA, encoding="latin-1", sep=";", usecols=lambda c: c.lower() in colunas_matriculas, low_memory=False,).rename(columns=str.lower)

print("juntando as tabelas escolas e matriculas....")
instituicao = pd.merge(escolas, matriculas, on="co_entidade")[lista_colunas]

print("colocando valores nulos com 0....")
instituicao[campos_mat] = instituicao[campos_mat].fillna(0).astype(int)

print(f"salvando no postgres()...")
conn = psycopg2.connect(**DB_CONFIGURACAO)
curso = conn.cursor()
try:
    curso.execute(f"DROP TABLE IF EXISTS {NOME_TABELA};")
    curso.execute(f"""CREATE TABLE {NOME_TABELA} (
        id SERIAL PRIMARY KEY,
        co_entidade INTEGER,
        nu_ano_censo INTEGER,
        no_entidade VARCHAR(255),
        co_uf INTEGER,
        sg_uf VARCHAR(2),
        no_uf VARCHAR(255),
        co_municipio INTEGER,
        no_municipio VARCHAR(255),
        qt_mat_bas INTEGER,
        qt_mat_inf INTEGER,
        qt_mat_fund INTEGER,
        qt_mat_med INTEGER,
        qt_mat_prof INTEGER,
        qt_mat_eja INTEGER,
        qt_mat_esp INTEGER,
        ativo BOOLEAN DEFAULT TRUE,
        created TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );""")
    dados = io.StringIO()
    instituicao.to_csv(dados,header=False, index=False)
    dados.seek(0)
    colunaDos = ','.join(lista_colunas)
    curso.copy_expert(f"COPY {NOME_TABELA} ({colunaDos}) FROM STDIN WITH (FORMAT CSV) ", dados)
    conn.commit()
    print(f"\nconcluido com sucesso tem:{len(instituicao)} registros, migração para postgres concluida!!!!")
except Exception as e:
    print(f"erro na criação da tabela: {e}")
    conn.rollback()
    
