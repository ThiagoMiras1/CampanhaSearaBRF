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

# Lista de representantes
representantes = sorted(df["REPRESENTANTE"].unique())
rep_selecionado = st.sidebar.selectbox("Selecione o Representante:", representantes)

# Obter índice das linhas correspondentes
linhas_rep = df[df["REPRESENTANTE"] == rep_selecionado].index

# Valores atuais para sugestão
brf_val = df.loc[linhas_rep, "PONTOS_BRF_JUNHO"].sum()
seara_val = df.loc[linhas_rep, "PONTOS_SEARA_JUNHO"].sum()

# Campos de input para pontos
novo_brf = st.sidebar.number_input(f"Pontos BRF para {rep_selecionado}", min_value=0, value=int(brf_val), step=1)
novo_seara = st.sidebar.number_input(f"Pontos SEARA para {rep_selecionado}", min_value=0, value=int(seara_val), step=1)

# Botão para salvar os pontos
if st.sidebar.button("Salvar Pontos"):
    df.loc[linhas_rep, "PONTOS_BRF_JUNHO"] = novo_brf / len(linhas_rep)
    df.loc[linhas_rep, "PONTOS_SEARA_JUNHO"] = novo_seara / len(linhas_rep)
    st.sidebar.success(f"Pontos atualizados para {rep_selecionado}")

# Recalcular totais
if "TOTAL_BRF_COM_JUNHO" not in df.columns or "TOTAL_SEARA_COM_JUNHO" not in df.columns:
    df["TOTAL_BRF_COM_JUNHO"] = 0
    df["TOTAL_SEARA_COM_JUNHO"] = 0

df["TOTAL_BRF_COM_JUNHO"] = df["PONTOS_BRF_ABRIL"] + df["PONTOS_BRF_MAIO"] + df["PONTOS_BRF_JUNHO"]
df["TOTAL_SEARA_COM_JUNHO"] = df["PONTOS_SEARA_ABRIL"] + df["PONTOS_SEARA_MAIO"] + df["PONTOS_SEARA_JUNHO"]

# Seletor de regional
regional = st.selectbox("Escolha uma regional", sorted(df['REGIONAL'].unique()))
df_regional = df[df['REGIONAL'] == regional]

# Função para mostrar top 5
def exibir_top(df_filtrado, titulo, coluna_pontos):
    st.subheader(titulo)
    df_top = df_filtrado.sort_values(by=coluna_pontos, ascending=False).head(5).copy()
    df_top.reset_index(drop=True, inplace=True)
    df_top.index = df_top.index + 1
    st.dataframe(df_top[["CODIGO", "REPRESENTANTE", coluna_pontos]], height=250)

    # Gráfico Top 3 com medalhas
    top3 = df_top.head(3)
    fig, ax = plt.subplots(figsize=(8, 4))
    bars = ax.bar(top3["REPRESENTANTE"], top3[coluna_pontos], color=["#FFD700", "#C0C0C0", "#CD7F32"])
    ax.set_title(f"Top 3 - {titulo}")
    ax.set_ylabel("Pontos")
    ax.tick_params(axis='x', labelrotation=20, labelsize=9)
    st.pyplot(fig)

# Exibir ranking regional
exibir_top(df_regional, f"Ranking Regional BRF - {regional}", "TOTAL_BRF_COM_JUNHO")
exibir_top(df_regional, f"Ranking Regional SEARA - {regional}", "TOTAL_SEARA_COM_JUNHO")

# Exibir ranking geral
st.subheader("Ranking Geral")
exibir_top(df, "Ranking Geral BRF", "TOTAL_BRF_COM_JUNHO")
exibir_top(df, "Ranking Geral SEARA", "TOTAL_SEARA_COM_JUNHO")

# Função para exportar PDF
class PDF(FPDF):
    def header(self):
        self.set_font("Arial", "B", 14)
        self.cell(0, 10, f"Ranking da Regional - {regional}", ln=True, align="C")
        self.ln(5)

    def chapter_title(self, title):
        self.set_font("Arial", "B", 12)
        self.cell(0, 10, title, ln=True)

    def chapter_body(self, df, coluna):
        self.set_font("Arial", "", 10)
        self.set_fill_color(200, 220, 255)
        self.cell(20, 8, "Cod", 1, 0, "C", True)
        self.cell(80, 8, "Nome", 1, 0, "C", True)
        self.cell(30, 8, "Pontos", 1, 1, "C", True)

        top5 = df.sort_values(by=coluna, ascending=False).head(5)
        for _, row in top5.iterrows():
            self.cell(20, 8, str(row['CODIGO']), 1)
            self.cell(80, 8, str(row['REPRESENTANTE']), 1)
            self.cell(30, 8, str(int(row[coluna])), 1, 1)

# Botão para exportar PDF
if st.button("Exportar Ranking da Regional para PDF"):
    pdf = PDF()
    pdf.add_page()
    pdf.chapter_title("Ranking BRF")
    pdf.chapter_body(df_regional, "TOTAL_BRF_COM_JUNHO")
    pdf.chapter_title("Ranking SEARA")
    pdf.chapter_body(df_regional, "TOTAL_SEARA_COM_JUNHO")
    pdf_path = f"ranking_{regional.replace(' ', '_')}.pdf"
    pdf.output(pdf_path)
    with open(pdf_path, "rb") as f:
        st.download_button(
            label="Clique para baixar o PDF",
            data=f,
            file_name=pdf_path,
            mime="application/pdf"
        )
    os.remove(pdf_path)
