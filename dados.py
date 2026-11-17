from enviroment import enviroment
import psycopg2

DB_CONFIGURACAO = {
    "host": enviroment.get("DB_HOST"),
    "port": int(enviroment.get("DB_PORT")),
    "database": enviroment.get("DB_NAME"),
    "user": enviroment.get("DB_USER"),
    "password": enviroment.get("DB_PASSWORD")
}

conn = psycopg2.connect(**DB_CONFIGURACAO)