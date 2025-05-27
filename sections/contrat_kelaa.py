import streamlit as st
import pandas as pd
import plotly.express as px
from io import BytesIO
import datetime

def show():
    menu = st.sidebar.radio("Aller à :", ["📁 Upload de fichier", "📋 Tableau des Contrats", "📊 Statistiques"])

    if menu == "📁 Upload de fichier":
        uploaded_file = st.file_uploader("Uploader un fichier (Parquet ou Excel) pour Agence_El Kelaa Des Sraghna",
                                         type=["parquet", "xlsx"])
        if uploaded_file is not None:
            df = load_data(uploaded_file)
            st.session_state.agency_data["Agence_El Kelaa Des Sraghna"] = df
            st.success(f"Fichier chargé avec succès ✅ ({len(df)} contrats) pour Agence_El Kelaa Des Sraghna")
        else:
            st.info("Veuillez charger un fichier pour commencer.")

    if "Agence_El Kelaa Des Sraghna" in st.session_state.agency_data:
        data = st.session_state.agency_data["Agence_El Kelaa Des Sraghna"]

        if menu == "📋 Tableau des Contrats":
            show_table(data)
        elif menu == "📊 Statistiques":
            show_stats(data)

@st.cache_data(show_spinner="Chargement des données...", ttl=3600)
def load_data(file_path):
    try:
        if file_path.name.endswith('.xlsx'):
            return pd.read_excel(file_path)
        else:
            return pd.read_parquet(file_path)
    except Exception as e:
        st.error(f"Erreur lors du chargement du fichier: {str(e)}")
        return pd.DataFrame()

# Reste du code...


@st.cache_data(show_spinner=True)
def filter_data(df, search_nom, search_contrat, search_CIN, search_ancienne_ref, search_num_compteur, search_commune,
                categorie_filter, etat_contrat_filter):
    filtered_df = df.copy()
    if not filtered_df.empty:
        filtered_df["État Contrat"] = filtered_df["Date resiliation du contrat"].apply(
            lambda x: "Résilié" if pd.notna(x) else "En service")
        if search_nom and "Nom de client titulaire" in filtered_df.columns:
            filtered_df = filtered_df[
                filtered_df["Nom de client titulaire"].str.contains(search_nom, case=False, na=False)]
        if search_contrat and "N° de contrat" in filtered_df.columns:
            filtered_df = filtered_df[filtered_df["N° de contrat"].astype(str).str.contains(search_contrat, na=False)]
        if search_CIN and "cin" in filtered_df.columns:
            filtered_df = filtered_df[filtered_df["cin"].astype(str).str.contains(search_CIN, na=False)]
        if search_ancienne_ref and "ex contrat SA" in filtered_df.columns:
            filtered_df = filtered_df[
                filtered_df["ex contrat SA"].astype(str).str.contains(search_ancienne_ref, na=False)]
        if search_num_compteur and "Numéro contrat" in filtered_df.columns:
            filtered_df = filtered_df[
                filtered_df["Numéro contrat"].astype(str).str.contains(search_num_compteur, na=False)]
        if search_commune and "Commune" in filtered_df.columns:
            filtered_df = filtered_df[filtered_df["Commune"].str.contains(search_commune, case=False, na=False)]
        if categorie_filter != "Tous" and "Catégorie d'abonnement" in filtered_df.columns:
            filtered_df = filtered_df[filtered_df["Catégorie d'abonnement"] == categorie_filter]
        if etat_contrat_filter != "Tous" and "État Contrat" in filtered_df.columns:
            filtered_df = filtered_df[filtered_df["État Contrat"] == etat_contrat_filter]
    return filtered_df


def show_table(data):
    st.subheader("🔍 Recherche et Filtrage - Agence_El Kelaa Des Sraghna")

    with st.expander("🔍 Filtres de base"):
        col1, col2, col3 = st.columns(3)
        search_nom = col1.text_input("Nom de client")
        search_contrat = col2.text_input("Numéro de contrat")
        search_commune = col3.text_input("Commune")

    with st.expander("🔍 Filtres avancés"):
        col1, col2 = st.columns(2)
        search_CIN = col1.text_input("CIN")
        search_ancienne_ref = col2.text_input("Ancienne référence")
        search_num_compteur = st.text_input("Numéro de compteur")

    if "Catégorie d'abonnement" in data.columns:
        categorie_filter = st.selectbox("Catégorie d'abonnement",
                                        options=["Tous"] + list(data["Catégorie d'abonnement"].dropna().unique()))
    else:
        categorie_filter = "Tous"
        st.warning("La colonne 'Catégorie d'abonnement' n'existe pas. Le filtre de catégorie est désactivé.")

    etat_contrat_filter = st.selectbox("État du contrat", options=["Tous", "En service", "Résilié"])

    filtered_data = filter_data(data, search_nom, search_contrat, search_CIN, search_ancienne_ref, search_num_compteur,
                                search_commune, categorie_filter, etat_contrat_filter)

    if not filtered_data.empty:
        page_size = 10
        total_pages = max(1, (len(filtered_data) + page_size - 1) // page_size)

        col1, col2 = st.columns([1, 3])
        with col1:
            page_number = st.number_input("Page:", min_value=1, max_value=total_pages, value=1)

        start_idx = (page_number - 1) * page_size
        end_idx = min(start_idx + page_size, len(filtered_data))

        sort_column = "Date de début" if "Date de début" in filtered_data.columns else None
        if sort_column:
            display_data = filtered_data.sort_values(by=sort_column, ascending=False).iloc[start_idx:end_idx]
        else:
            display_data = filtered_data.iloc[start_idx:end_idx]

        st.dataframe(display_data, use_container_width=True)

        output = BytesIO()
        filtered_data.to_excel(output, index=False)
        st.download_button("📥 Télécharger les résultats filtrés",
                           data=output.getvalue(),
                           file_name="contrats_filtres.xlsx",
                           mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")

        st.warning("Aucune donnée à afficher avec les filtres actuels.")


def show_stats(data):
    st.subheader("📊 Statistiques sur les Contrats - Agence_El Kelaa Des Sraghna")

    tab1, tab2, tab3, tab4 = st.tabs(
        ["Répartition par Catégorie", "Répartition par État", "Évolution des Abonnements", "Tableaux récapitulatifs"])

    with tab1:
        st.markdown("#### Répartition par Catégorie d'Abonnement")
        if "Catégorie d'abonnement" in data.columns:
            fig1 = px.pie(data, names="Catégorie d'abonnement", title="Répartition des Contrats")
            st.plotly_chart(fig1, use_container_width=True)
        else:
            st.warning("La colonne 'Catégorie d'abonnement' n'existe pas.")

    with tab2:
        st.markdown("#### Répartition par État")
        data["État Contrat"] = data["Date resiliation du contrat"].apply(
            lambda x: "Résilié" if pd.notna(x) else "En service")
        fig2 = px.pie(data_frame=data, names="État Contrat", title="Contrats (Résiliés vs En Service)",
                      color="État Contrat", hole=0.3)
        st.plotly_chart(fig2, use_container_width=True)

    with tab3:
        st.markdown("#### Évolution des Abonnements par Années")
        if "Date de début" in data.columns:
            data['Date de début'] = pd.to_datetime(data['Date de début'], errors='coerce')
            data['Année'] = data['Date de début'].dt.year
            abonnement_par_annee = data['Année'].value_counts().sort_index()
            fig_abonnement = px.line(abonnement_par_annee, x=abonnement_par_annee.index, y=abonnement_par_annee.values,
                                     labels={'x': 'Année', 'y': "Nombre d'Abonnements"},
                                     title="Évolution des Abonnements")
            st.plotly_chart(fig_abonnement, use_container_width=True)

    with tab4:
        st.markdown("#### Tableaux récapitulatifs")

        

        if "Commune" in data.columns and "Catégorie d'abonnement" in data.columns:
            # Tableau croisé Commune × Catégorie
            pivot_commune = pd.crosstab(data["Commune"],
                                        data["Catégorie d'abonnement"])
            st.markdown("##### Répartition Commune × Catégorie")
            st.dataframe(pivot_commune, use_container_width=True)

    st.markdown("---")
    st.subheader("🚨 Alertes : Contrats Proches de la Fin")
    if "Date de fin" in data.columns:
        data['Date de fin'] = pd.to_datetime(data['Date de fin'], errors='coerce')
        today = pd.Timestamp(datetime.date.today())
        prochain_mois = today + pd.DateOffset(months=1)
        alertes = data[
            (data["Date de fin"].notnull()) & (data["Date de fin"] >= today) & (data["Date de fin"] <= prochain_mois)]
        if not alertes.empty:
            st.warning(f"⚠ {len(alertes)} contrats arrivent à échéance dans le mois à venir !")
            st.dataframe(alertes[["Numéro contrat", "Nom de client titulaire", "Date de fin"]],
                         use_container_width=True)
            alert_output = BytesIO()
            alertes.to_excel(alert_output, index=False)
            st.download_button("📥 Télécharger les alertes", data=alert_output.getvalue(),
                               file_name="alertes_echeances.xlsx",
                               mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
        else:
            st.success("✅ Aucun contrat n'arrive à échéance dans le mois à venir.")
    else:
        st.info("Pas de date de fin disponible pour cette agence.")