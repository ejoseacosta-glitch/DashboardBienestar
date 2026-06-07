# -*- coding: utf-8 -*-
"""
Created on Sun Jun  7 14:47:22 2026

@author: Edson Acosta
"""


import pandas as pd
import plotly.express as px
import streamlit as st
from collections import Counter
import re

st.set_page_config(page_title="Dashboard Bienestar Escolar", layout="wide")

FILE = "Ruta de fortalecimiento académico y bienestar – Grado 11  (respuestas).xlsx"

@st.cache_data
def cargar():
    return pd.read_excel(FILE)

df = cargar()

grado_col = "Grado"
org_col = [c for c in df.columns if "organizada tienes actualmente tu rutina" in c][0]
prep_col = [c for c in df.columns if "preparado te sientes" in c][0]
estrategias_col = [c for c in df.columns if "estrategias utilizas cuando estudias" in c][0]
efec_col = [c for c in df.columns if "efectivas consideras" in c][0]
dificultad_col = [c for c in df.columns if "qué es lo que más se te dificulta?" in c.lower() and "escoge" in c.lower()][0]
afront_col = [c for c in df.columns if "qué sueles hacer" in c.lower()][0]
apoyo_fam_col = [c for c in df.columns if "percibes el apoyo de tu familia" in c.lower()][0]
texto_col = df.columns[-1]

st.title("📊 Dashboard de Fortalecimiento Académico y Bienestar")

grado = st.sidebar.multiselect(
    "Filtrar grado",
    sorted(df[grado_col].dropna().unique()),
    default=sorted(df[grado_col].dropna().unique())
)

df = df[df[grado_col].isin(grado)]

# KPIs
c1,c2,c3,c4 = st.columns(4)

c1.metric("Estudiantes", len(df))
c2.metric("Media organización", round(df[org_col].mean(),2))
c3.metric("Media efectividad", round(df[efec_col].mean(),2))
c4.metric("Correlación Org.-Efectividad", round(df[[org_col,efec_col]].corr().iloc[0,1],2))

st.divider()

# Estadísticas descriptivas
with st.expander("📈 Estadísticas descriptivas"):
    st.dataframe(df[[org_col,efec_col]].describe().T)

col1,col2 = st.columns(2)

with col1:
    fig = px.histogram(df,x=org_col,title="Organización de la rutina de estudio")
    st.plotly_chart(fig,use_container_width=True)

with col2:
    fig = px.histogram(df,x=efec_col,title="Efectividad percibida de las estrategias")
    st.plotly_chart(fig,use_container_width=True)

col3,col4 = st.columns(2)

with col3:
    fig = px.histogram(df,x=prep_col,title="Preparación para grado 11")
    st.plotly_chart(fig,use_container_width=True)

with col4:
    fig = px.scatter(
        df,
        x=org_col,
        y=efec_col,
        color=grado_col,
        title="Organización vs efectividad"
    )
    st.plotly_chart(fig,use_container_width=True)

st.divider()

# Función conteo múltiples respuestas
def contar_multiple(serie):
    conteo = Counter()
    for x in serie.dropna():
        for item in str(x).split(","):
            item=item.strip()
            if item:
                conteo[item]+=1
    return pd.DataFrame(conteo.items(),columns=["Categoría","Frecuencia"]).sort_values(
        "Frecuencia",ascending=False
    )

st.subheader("📚 Estrategias de estudio utilizadas")
estr = contar_multiple(df[estrategias_col])
st.plotly_chart(
    px.bar(
        estr.head(15),
        x="Frecuencia",
        y="Categoría",
        orientation="h"
    ),
    use_container_width=True
)

st.subheader("⚠️ Dificultades académicas reportadas")
dif = contar_multiple(df[dificultad_col])
st.plotly_chart(
    px.bar(dif.head(15),x="Frecuencia",y="Categoría",orientation="h"),
    use_container_width=True
)

st.subheader("🧠 Estrategias de afrontamiento")
afr = contar_multiple(df[afront_col])
st.plotly_chart(
    px.bar(afr.head(15),x="Frecuencia",y="Categoría",orientation="h"),
    use_container_width=True
)

st.subheader("👨‍👩‍👧 Apoyo familiar")
st.plotly_chart(
    px.histogram(df,x=apoyo_fam_col),
    use_container_width=True
)

st.divider()

# Semáforo básico
st.subheader("🚦 Indicador de riesgo académico")

riesgo = pd.DataFrame()
riesgo["Nombre"] = df["Nombre completo"]

riesgo["Nivel"] = "Verde"

cond_amarillo = (df[org_col] <= 3) | (df[efec_col] <= 3)
cond_rojo = (df[org_col] <= 2) | (df[efec_col] <= 2)

riesgo.loc[cond_amarillo,"Nivel"]="Amarillo"
riesgo.loc[cond_rojo,"Nivel"]="Rojo"

st.dataframe(riesgo)

st.metric("Casos en riesgo alto (Rojo)", (riesgo["Nivel"]=="Rojo").sum())

st.divider()

# Respuestas abiertas
st.subheader(" Respuestas abiertas")

texto = " ".join(df[texto_col].fillna("").astype(str))

palabras = re.findall(r"[a-záéíóúñ]+", texto.lower())
stop = {"que","para","con","los","las","una","uno","del","por","más","muy","sus","sea","como","pero","porque","eso","este","esta","me","de","la","el","y","en","un"}
palabras = [p for p in palabras if p not in stop and len(p)>3]

freq = pd.DataFrame(Counter(palabras).most_common(20),columns=["Palabra","Frecuencia"])

st.plotly_chart(
    px.bar(freq,x="Frecuencia",y="Palabra",orientation="h",
           title="Temas más frecuentes en respuestas abiertas"),
    use_container_width=True
)

st.dataframe(df[[ "Nombre completo", texto_col ]])
