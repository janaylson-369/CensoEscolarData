import sqlite3
import pandas as pd

ARQUIVO_ESCOLA = "Tabela_Escola_2025_V2.csv" 
ARQUIVO_MATRICULA = "Tabela_Matricula_2025_V2.csv" 
BANCO_SQL = "censoescolar.db"
NOME_TABELA = "tb_instituicao_ensino"

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

print("lendo tabela de Escolas...")
escolas = pd.read_csv(ARQUIVO_ESCOLA,encoding="latin-1", sep=";",low_memory=False).rename(columns=str.lower)

print("lendo tabela de Matriculas....")
matriculas = pd.read_csv(ARQUIVO_MATRICULA, encoding="latin-1",sep=";",low_memory=False).rename(columns=str.lower)

print("juntando as tabelas...")
junto = pd.merge(escolas, matriculas,on="co_entidade")

print("filtrando as regiões nordeste e sudeste....")
filtrado = junto[junto["no_regiao"].astype(str).str.strip().str.lower().isin(["nordeste", "sudeste"])].copy()

print("colocando valores nulos com 0 e convertendo para int....")
campos_mat = [col for col in lista_colunas if col.startswith("qt_mat_")]
for col in campos_mat:
    if col in filtrado.columns:
        filtrado[col] = filtrado[col].fillna(0).astype(int)

instituicao = filtrado[lista_colunas]

print(f"salvando no banco sqlite({BANCO_SQL})...")
conn = sqlite3.connect(BANCO_SQL)
instituicao.to_sql(NOME_TABELA, con=conn,if_exists="replace", index=False)
conn.close()

print(f"\nconcluido com sucesso{len(instituicao)}migração para sqlite concluida!!!!")