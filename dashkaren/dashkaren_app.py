import pandas as pd
import plotly.express as px
import streamlit as st
from collections import Counter
from wordcloud import WordCloud
import matplotlib.pyplot as plt

st.set_page_config(page_title="Dashboard Bienestar Escolar", layout="wide")

FILE = "dashkaren/Ruta de fortalecimiento académico y bienestar – Grado 11  (respuestas).xlsx"

@st.cache_data
def cargar():
    return pd.read_excel(FILE)

df = cargar()

grado_col = "Grado"
org_col = [c for c in df.columns if "organizada tienes actualmente tu rutina" in c.lower()][0]
prep_col = [c for c in df.columns if "preparado te sientes" in c.lower()][0]
estrategias_col = [c for c in df.columns if "estrategias utilizas cuando estudias" in c.lower()][0]
efec_col = [c for c in df.columns if "efectivas consideras" in c.lower()][0]
dificultad_col = [c for c in df.columns if "qué es lo que más se te dificulta" in c.lower()][0]
afront_col = [c for c in df.columns if "qué sueles hacer" in c.lower()][0]
apoyo_fam_col = [c for c in df.columns if "percibes el apoyo de tu familia" in c.lower()][0]
texto_col = df.columns[-1]

st.title("📊 Ruta de Fortalecimiento Académico y Bienestar")

grado = st.sidebar.multiselect(
    "Filtrar grado",
    sorted(df[grado_col].dropna().unique()),
    default=sorted(df[grado_col].dropna().unique())
)

df = df[df[grado_col].isin(grado)]

def resumen(variable):

    serie = pd.to_numeric(df[variable], errors="coerce")

    if serie.notna().sum() > 0:

        c1,c2,c3,c4,c5,c6 = st.columns(6)

        c1.metric("N", int(serie.count()))
        c2.metric("Media", round(serie.mean(),2))
        c3.metric("Mediana", round(serie.median(),2))
        c4.metric("DE", round(serie.std(),2))
        c5.metric("Mín", round(serie.min(),2))
        c6.metric("Máx", round(serie.max(),2))

    else:
        st.info("Variable categórica. Se muestran distribuciones y porcentajes.")

def porcentajes(variable):

    conteos = df[variable].value_counts().sort_index()
    total = conteos.sum()

    t = pd.DataFrame({
        "Respuesta": conteos.index,
        "Frecuencia": conteos.values
    })

    t["Porcentaje"] = t["Frecuencia"] / total * 100

    t["Etiqueta"] = (
        t["Porcentaje"].round(2).astype(str)
        + "% (n="
        + t["Frecuencia"].astype(str)
        + ")"
    )

    fig = px.bar(
        t,
        x="Respuesta",
        y="Porcentaje",
        text="Etiqueta"
    )

    fig.update_traces(textposition="outside")
    st.plotly_chart(fig, use_container_width=True)

def contar_multiple(serie):
    conteo=Counter()

    for x in serie.dropna():
        for item in str(x).split(","):
            item=item.strip()
            if item:
                conteo[item]+=1

    out=pd.DataFrame(conteo.items(),columns=["Categoría","Frecuencia"])
    out["Porcentaje"]=out["Frecuencia"]/len(df)*100

    return out.sort_values("Frecuencia",ascending=False)

tab1,tab2,tab3,tab4,tab5 = st.tabs(
    ["📊 Resumen","📚 Académico","🧠 Bienestar","🚦 Riesgo","💬 Respuestas abiertas"]
)

with tab1:

    k1,k2,k3,k4=st.columns(4)

    k1.metric("Estudiantes",len(df))
    k2.metric("Media organización",round(df[org_col].mean(),2))
    k3.metric("Media efectividad",round(df[efec_col].mean(),2))
    k4.metric("Correlación",round(df[[org_col,efec_col]].corr().iloc[0,1],2))

with tab2:

    for var in [org_col, prep_col, efec_col]:

        st.header(var)
        resumen(var)

        porcentajes(var)

        st.divider()

    st.header("Relación entre organización y efectividad")

    corr=df[[org_col,efec_col]].corr().iloc[0,1]

    st.metric("Correlación de Pearson",round(corr,3))

    for titulo,columna in [
        ("📚 Estrategias de estudio utilizadas", estrategias_col),
        ("⚠️ Dificultades académicas reportadas", dificultad_col)
    ]:

        st.header(titulo)

        tabla=contar_multiple(df[columna])

        tabla["Etiqueta"]=(
            tabla["Porcentaje"].round(2).astype(str)
            + "% (n="
            + tabla["Frecuencia"].astype(str)
            + ")"
        )

        fig=px.bar(
            tabla,
            x="Porcentaje",
            y="Categoría",
            orientation="h",
            text="Etiqueta"
        )

        fig.update_layout(height=800,margin=dict(l=250,r=40,t=60,b=50))

        st.plotly_chart(fig,use_container_width=True)

with tab3:

    st.header(afront_col)

    tabla=contar_multiple(df[afront_col])

    tabla["Etiqueta"]=(
        tabla["Porcentaje"].round(2).astype(str)
        + "% (n="
        + tabla["Frecuencia"].astype(str)
        + ")"
    )

    fig=px.bar(
        tabla,
        x="Porcentaje",
        y="Categoría",
        orientation="h",
        text="Etiqueta"
    )

    fig.update_layout(height=800,margin=dict(l=250,r=40,t=60,b=50))

    st.plotly_chart(fig,use_container_width=True)

    st.header(apoyo_fam_col)

    try:
        resumen(apoyo_fam_col)
    except:
        pass

    porcentajes(apoyo_fam_col)

with tab4:

    st.info("""
Metodología:

🔴 Rojo:
Organización ≤ 2
o Efectividad ≤ 2

🟡 Amarillo:
Organización > 2 y ≤ 3
o Efectividad > 2 y ≤ 3

🟢 Verde:
Organización > 3
y Efectividad > 3
""")

    riesgo=pd.DataFrame()
    riesgo["Nombre"]=df["Nombre completo"]
    riesgo["Nivel"]="Verde"

    riesgo.loc[(df[org_col]<=3)|(df[efec_col]<=3),"Nivel"]="Amarillo"
    riesgo.loc[(df[org_col]<=2)|(df[efec_col]<=2),"Nivel"]="Rojo"

    st.dataframe(riesgo,use_container_width=True)

    r=riesgo["Nivel"].value_counts().reset_index()

    fig=px.pie(r,names="Nivel",values="count",hole=.5)

    st.plotly_chart(fig,use_container_width=True)

with tab5:

    st.header(texto_col)

    texto=" ".join(df[texto_col].fillna("").astype(str))

    stop={"que","para","con","los","las","una","uno","del","por","más",
          "muy","sus","sea","como","pero","porque","eso","este","esta",
          "me","de","la","el","y","en","un"}

    wc=WordCloud(
        width=1600,
        height=800,
        background_color="white",
        stopwords=stop,
        collocations=False,
        max_words=100
    ).generate(texto)

    fig,ax=plt.subplots(figsize=(16,8))
    ax.imshow(wc,interpolation="bilinear")
    ax.axis("off")

    st.pyplot(fig)

    st.subheader("Comentarios registrados")
    st.dataframe(df[[texto_col]],use_container_width=True)
