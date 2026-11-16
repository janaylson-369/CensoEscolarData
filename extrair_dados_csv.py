import pandas as pd
from sqlalchemy import create_engine
from enviroment import enviroment

ARQUIVO_ESCOLA = "dados/Tabela_Escola_2025_V2.csv" 
ARQUIVO_MATRICULA = "dados/Tabela_Matricula_2025_V2.csv"
NOME_TABELA = "tb_instituicao_ensino"

DB_USER = enviroment.get("DB_USER")
DB_PASSWORD = enviroment.get("DB_PASSWORD")
DB_HOST = enviroment.get("DB_HOST")
DB_PORT = enviroment.get("DB_PORT")
DB_NAME = enviroment.get("DB_NAME")

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
conexao = f"postgresql+psycopg2://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
engine = create_engine(conexao)
instituicao.to_sql(NOME_TABELA, con=engine, if_exists="replace", index=False)

print(f"\nconcluido com sucesso tem:{len(instituicao)} registros, migração para postgres concluida!!!!")