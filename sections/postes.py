import streamlit as st
import pandas as pd
import plotly.express as px
import altair as alt
from io import BytesIO

def show():
    menu_postes = st.sidebar.radio("Aller à :", ["📁 Upload de fichier", "📋 Tableau des Postes", "📊 Statistiques"])

    if menu_postes == "📁 Upload de fichier":
        uploaded_file = st.file_uploader("Uploader un fichier (Parquet ou Excel) pour les postes", type=["parquet", "xlsx"])
        if uploaded_file is not None:
            postes_data = load_postes(uploaded_file)
            st.session_state.postes_data = postes_data
            st.success(f"Fichier chargé avec succès ✅ ({len(postes_data)} postes)")

    if st.session_state.postes_data is not None:
        data = st.session_state.postes_data

        if menu_postes == "📋 Tableau des Postes":
            show_table(data)
        elif menu_postes == "📊 Statistiques":
            show_stats(data)

@st.cache_data(show_spinner="Chargement des postes...", ttl=3600)
def load_postes(file_path):
    try:
        if file_path.name.endswith('.xlsx'):
            return pd.read_excel(file_path)
        else:
            return pd.read_parquet(file_path)
    except Exception as e:
        st.error(f"Erreur lors du chargement du fichier postes: {str(e)}")
        return pd.DataFrame()

def show_table(data):
    st.subheader("🔍 Recherche et Filtrage")

    with st.expander("🔍 Filtres de recherche"):
        col1, col2, col3 = st.columns(3)
        nomdepart = col1.text_input("NOMDEPART")
        nomcommune = col2.text_input("NOM COMMUNE")
        adressecivq = col3.text_input("ADRESCIVIQ")
        matricule = st.text_input("MATRICULE")
        typeposte = st.text_input("TYPEPOSTE")

    filters = {
        "NOMDEPART": nomdepart,
        "NOM COMMUNE": nomcommune,
        "ADRESCIVIQ": adressecivq,
        "MATRICULE": matricule,
        "TYPEPOSTE": typeposte
    }

    filtered_data = filter_postes(data, filters)
    st.markdown("### 📈 Statistiques sur la recherche")
    col1, col2 = st.columns(2)
    col1.metric("📄 Postes affichés", len(filtered_data))
    col2.metric("🔍 Filtres actifs", sum(bool(v) for v in filters.values()))

    if not filtered_data.empty:
        page_size = 10
        total_pages = max(1, (len(filtered_data) + page_size - 1) // page_size)

        col1, col2 = st.columns([1, 3])
        with col1:
            page_number = st.number_input("Page:", min_value=1, max_value=total_pages, value=1)

        start_idx = (page_number - 1) * page_size
        end_idx = min(start_idx + page_size, len(filtered_data))

        st.dataframe(filtered_data.iloc[start_idx:end_idx], use_container_width=True)

        output = BytesIO()
        filtered_data.to_excel(output, index=False)
        st.download_button("📥 Télécharger les résultats filtrés",
                           data=output.getvalue(),
                           file_name="postes_filtres.xlsx",
                           mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")

        selected_index = st.selectbox("Sélectionner un poste pour voir la fiche :", options=filtered_data.index)
        poste_info = filtered_data.loc[selected_index]

        st.markdown("---")
        st.markdown("### 🧾 Fiche Poste")
        st.json(poste_info.to_dict())
    else:
        st.warning("Aucune donnée à afficher avec les filtres actuels.")

@st.cache_data(show_spinner=True)
def filter_postes(df, filters):
    filtered_df = df.copy()
    if not filtered_df.empty:
        for key, value in filters.items():
            if value and key in filtered_df.columns:
                filtered_df = filtered_df[filtered_df[key].astype(str).str.contains(value, case=False, na=False)]
    return filtered_df

def show_stats(data):
    st.subheader("📊 Statistiques sur les Postes Électriques")

    if "PUISNOM" in data.columns and "NOMDEPART" in data.columns and not data.empty:
        st.markdown("#### Somme de Puissance par NOMDEPART")
        chart_data = data.groupby("NOMDEPART")["PUISNOM"].sum().reset_index()
        if not chart_data.empty:
            chart = alt.Chart(chart_data).mark_bar().encode(
                x=alt.X("NOMDEPART", sort="-y"),
                y="PUISNOM",
                tooltip=["NOMDEPART", "PUISNOM"]
            ).properties(width="container", height=400)
            st.altair_chart(chart, use_container_width=True)

    if "PUISNOM" in data.columns and "NOM COMMUNE" in data.columns and not data.empty:
        st.markdown("#### Somme de Puissance par NOM COMMUNE")
        chart_data = data.groupby("NOM COMMUNE")["PUISNOM"].sum().reset_index()
        if not chart_data.empty:
            chart = alt.Chart(chart_data).mark_bar(color='orange').encode(
                x=alt.X("NOM COMMUNE", sort="-y"),
                y="PUISNOM",
                tooltip=["NOM COMMUNE", "PUISNOM"]
            ).properties(width="container", height=400)
            st.altair_chart(chart, use_container_width=True)

    # Nombre de postes par TYPEPOSTE et NOMDEPART
    if "TYPEPOSTE" in data.columns and "NOMDEPART" in data.columns and not data.empty:
        st.markdown("#### Nombre de Postes par TYPEPOSTE et NOMDEPART")
        chart_data = data.groupby(["NOMDEPART", "TYPEPOSTE"]).size().reset_index(name="Nombre de Postes")
        if not chart_data.empty:
            chart = alt.Chart(chart_data).mark_bar().encode(
                x="NOMDEPART",
                y="Nombre de Postes",
                color="TYPEPOSTE",
                tooltip=["NOMDEPART", "TYPEPOSTE", "Nombre de Postes"]
            ).properties(width="container", height=400)
            st.altair_chart(chart, use_container_width=True)

    # Nombre de postes par TYPEPOSTE et NOM COMMUNE
    st.markdown("#### Nombre de Postes par TYPEPOSTE et NOM COMMUNE")
    if "TYPEPOSTE" in data.columns and "NOM COMMUNE" in data.columns:
        typeposte_par_commune = data.groupby(["NOM COMMUNE", "TYPEPOSTE"]).size().reset_index(name="Nombre de Postes")
        fig_typeposte_commune = px.bar(typeposte_par_commune, x="NOM COMMUNE", y="Nombre de Postes", color="TYPEPOSTE",
                                       labels={"Nombre de Postes": "Nombre de Postes", "NOM COMMUNE": "Nom Commune",
                                               "TYPEPOSTE": "Type Poste"},
                                       title="Nombre de Postes par Type de Poste et Nom Commune")
        st.plotly_chart(fig_typeposte_commune, use_container_width=True)
    else:
        st.warning("Les colonnes 'TYPEPOSTE' ou 'NOM COMMUNE' n'existent pas dans les données.")