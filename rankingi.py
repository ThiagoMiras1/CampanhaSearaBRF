import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from fpdf import FPDF
import os

st.set_page_config(layout="wide")

# Carregar a planilha
@st.cache_data
def carregar_dados():
    df = pd.read_excel("Ranking_Consolidado_LIMPO.xlsx", sheet_name="Sheet1")
    return df

df = carregar_dados()

# Campo para edição dos pontos de Junho (agrupado por representante)
st.sidebar.header("Atualizar Pontos de Junho")

representantes = df["REPRESENTANTE"].unique()
for rep in representantes:
    st.sidebar.subheader(f"{rep}")
    linhas_rep = df[df["REPRESENTANTE"] == rep].index

    # Calcular somas atuais para sugestões (opcional)
    brf_val = df.loc[linhas_rep, "PONTOS_BRF_JUNHO"].sum()
    seara_val = df.loc[linhas_rep, "PONTOS_SEARA_JUNHO"].sum()

    novo_brf = st.sidebar.number_input(f"Pontos BRF para {rep}", min_value=0, value=int(brf_val), step=1, key=f"brf_{rep}")
    novo_seara = st.sidebar.number_input(f"Pontos SEARA para {rep}", min_value=0, value=int(seara_val), step=1, key=f"seara_{rep}")

    # Aplicar nova pontuação para todas as linhas do representante
    df.loc[linhas_rep, "PONTOS_BRF_JUNHO"] = novo_brf / len(linhas_rep)
    df.loc[linhas_rep, "PONTOS_SEARA_JUNHO"] = novo_seara / len(linhas_rep)

# Recalcular totais
if "TOTAL_BRF_COM_JUNHO" not in df.columns or "TOTAL_SEARA_COM_JUNHO" not in df.columns:
    df["TOTAL_BRF_COM_JUNHO"] = 0
    df["TOTAL_SEARA_COM_JUNHO"] = 0

df["TOTAL_BRF_COM_JUNHO"] = df["TOTAL_BRF"] + df["PONTOS_BRF_JUNHO"]
df["TOTAL_SEARA_COM_JUNHO"] = df["TOTAL_SEARA"] + df["PONTOS_SEARA_JUNHO"]

# Continue com o restante da lógica de exibição, gráficos, PDFs, etc.
