import streamlit as st
import pandas as pd
import plotly.express as px
from io import BytesIO
import datetime




def show():
    menu = st.sidebar.radio("Aller à :", ["📁 Upload de fichier", "📋 Tableau des Contrats", "📊 Statistiques"])

    if menu == "📁 Upload de fichier":
        uploaded_file = st.file_uploader(
            "Uploader un fichier (Parquet ou Excel) pour Agence_LAATAOUIA_SIDI RAHAL_TAMELLALT",
            type=["parquet", "xlsx"])
        if uploaded_file is not None:
            df = load_data(uploaded_file)
            st.session_state.agency_data["Agence_LAATAOUIA_SIDI RAHAL_TAMELLALT"] = df
            st.success(f"Fichier chargé avec succès ✅ ({len(df)} contrats)")
        else:
            st.info("Veuillez charger un fichier pour commencer.")

    if "Agence_LAATAOUIA_SIDI RAHAL_TAMELLALT" in st.session_state.agency_data:
        data = st.session_state.agency_data["Agence_LAATAOUIA_SIDI RAHAL_TAMELLALT"]

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
def filter_data(df, search_params, categorie_filter, etat_contrat_filter):
    filtered_df = df.copy()
    if not filtered_df.empty:
        filtered_df["État Contrat"] = filtered_df["Date resiliation du contrat"].apply(lambda x: "Résilié" if pd.notna(x) else "En service")
        if search_params["search_code_agence"] and "Code Agence (Abonnement)" in filtered_df.columns:
            filtered_df = filtered_df[filtered_df["Code Agence (Abonnement)"].astype(str).str.contains(search_params["search_code_agence"], case=False, na=False)]
        if search_params["search_nom_agence"] and "Nom Agence (Abonnement)" in filtered_df.columns:
            filtered_df = filtered_df[filtered_df["Nom Agence (Abonnement)"].str.contains(search_params["search_nom_agence"], case=False, na=False)]
        if search_params["search_num_tournee"] and "Numéro de tournée" in filtered_df.columns:
            filtered_df = filtered_df[filtered_df["Numéro de tournée"].astype(str).str.contains(search_params["search_num_tournee"], na=False)]
        if search_params["search_num_contrat"] and "Numéro contrat" in filtered_df.columns:
            filtered_df = filtered_df[filtered_df["Numéro contrat"].astype(str).str.contains(search_params["search_num_contrat"], na=False)]
        if search_params["search_nom_client"] and "Nom / raison sociale du client tit." in filtered_df.columns:
            filtered_df = filtered_df[filtered_df["Nom / raison sociale du client tit."].str.contains(search_params["search_nom_client"], case=False, na=False)]
        if search_params["search_prenom_client"] and "Prenom du client titulaire" in filtered_df.columns:
            filtered_df = filtered_df[filtered_df["Prenom du client titulaire"].str.contains(search_params["search_prenom_client"], case=False, na=False)]
        if search_params["search_nom_commune"] and "Nom commune" in filtered_df.columns:
            filtered_df = filtered_df[filtered_df["Nom commune"].str.contains(search_params["search_nom_commune"], case=False, na=False)]
        if categorie_filter != "Tous" and "Libelle categorie facturation" in filtered_df.columns:
            filtered_df = filtered_df[filtered_df["Libelle categorie facturation"] == categorie_filter]
        if etat_contrat_filter != "Tous" and "État Contrat" in filtered_df.columns:
            filtered_df = filtered_df[filtered_df["État Contrat"] == etat_contrat_filter]
    return filtered_df

def show_table(data):
    st.subheader("🔍 Recherche et Filtrage - Agence_LAATAOUIA_SIDI RAHAL_TAMELLALT")

    with st.expander("🔍 Filtres de base"):
        col1, col2, col3 = st.columns(3)
        search_code_agence = col1.text_input("Code Agence")
        search_nom_agence = col2.selectbox("Nom Agence", options=["Tous"] + ["BE-AS LAATAOUIA", "BE-AS SIDI RAHAL", "BE-AS TAMELLALT"])
        search_num_contrat = col3.text_input("Numéro contrat")

    with st.expander("🔍 Filtres avancés"):
        col1, col2 = st.columns(2)
        search_num_tournee = col1.text_input("Numéro de tournée")
        search_nom_client = col2.text_input("Nom client")
        search_prenom_client = st.text_input("Prénom client")
        search_nom_commune = st.text_input("Nom commune")

    search_params = {
        "search_code_agence": search_code_agence,
        "search_nom_agence": search_nom_agence if search_nom_agence != "Tous" else "",
        "search_num_tournee": search_num_tournee,
        "search_num_contrat": search_num_contrat,
        "search_nom_client": search_nom_client,
        "search_prenom_client": search_prenom_client,
        "search_nom_commune": search_nom_commune,
    }

    if "Libelle categorie facturation" in data.columns:
        categorie_filter = st.selectbox("Catégorie d'abonnement", options=["Tous"] + list(data["Libelle categorie facturation"].dropna().unique()))
    else:
        categorie_filter = "Tous"
        st.warning("La colonne 'Libelle categorie facturation' n'existe pas.")

    etat_contrat_filter = st.selectbox("État du contrat", options=["Tous", "En service", "Résilié"])

    filtered_data = filter_data(data, search_params, categorie_filter, etat_contrat_filter)

    if not filtered_data.empty:
        page_size = 10
        total_pages = max(1, (len(filtered_data) + page_size - 1) // page_size)
        
        col1, col2 = st.columns([1, 3])
        with col1:
            page_number = st.number_input("Page:", min_value=1, max_value=total_pages, value=1)
        
        start_idx = (page_number - 1) * page_size
        end_idx = min(start_idx + page_size, len(filtered_data))
        
        sort_column = "Date creation abonnement" if "Date creation abonnement" in filtered_data.columns else None
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
        
        





def show_stats(data):
    st.subheader("📊 Statistiques sur les Contrats - Agence_LAATAOUIA_SIDI RAHAL_TAMELLALT")
    
    regions = ["Toutes", "BE-AS LAATAOUIA", "BE-AS SIDI RAHAL", "BE-AS TAMELLALT"]
    selected_region = st.selectbox("Filtrer par région :", regions)
    
    # Filtrer les données selon la région sélectionnée
    filtered_data = data if selected_region == "Toutes" else data[data["Nom Agence (Abonnement)"] == selected_region]
    
    # Afficher le nombre total de contrats pour la région sélectionnée
    st.markdown(f"### Statistiques pour: {selected_region if selected_region != 'Toutes' else 'Toutes les régions'}")
    st.markdown(f"**Nombre total de contrats:** {len(filtered_data)}")
    
    # Créer des onglets pour chaque type de visualisation
    tab1, tab2, tab3, tab4 = st.tabs(["Répartition Catégorie/État", "Répartition géographique", "Évolution temporelle", "Tableaux récapitulatifs"])
    
    with tab1:
        st.markdown("#### Répartition par Catégorie et État")
        col1, col2 = st.columns(2)
        
        with col1:
            if "Libelle categorie facturation" in filtered_data.columns:
                fig1 = px.pie(filtered_data, names="Libelle categorie facturation", 
                             title=f"Répartition par Catégorie ({selected_region})")
                st.plotly_chart(fig1, use_container_width=True)
            else:
                st.warning("La colonne 'Libelle categorie facturation' n'existe pas.")
        
        with col2:
            filtered_data["État Contrat"] = filtered_data["Date resiliation du contrat"].apply(
                lambda x: "Résilié" if pd.notna(x) else "En service")
            fig2 = px.pie(filtered_data, names="État Contrat", 
                         title=f"État des Contrats ({selected_region})", 
                         color="État Contrat", hole=0.3)
            st.plotly_chart(fig2, use_container_width=True)
    
    with tab2:
        st.markdown("#### Répartition géographique")
        
        if "Nom commune" in filtered_data.columns:
            col1, col2 = st.columns(2)
            
            with col1:
                # Répartition par agence (utile seulement si "Toutes" est sélectionnée)
                if selected_region == "Toutes":
                    nom_agence_counts = filtered_data["Nom Agence (Abonnement)"].value_counts().reset_index()
                    nom_agence_counts.columns = ["Nom Agence", "Nombre"]
                    fig_agence = px.bar(nom_agence_counts, x="Nom Agence", y="Nombre",
                                      title="Répartition par Agence")
                    st.plotly_chart(fig_agence, use_container_width=True)
                
            with col2:
                # Répartition par commune
                commune_counts = filtered_data["Nom commune"].value_counts().reset_index()
                commune_counts.columns = ["Commune", "Nombre"]
                fig_commune = px.bar(commune_counts, x="Commune", y="Nombre",
                                    title=f"Répartition par Commune ({selected_region})")
                st.plotly_chart(fig_commune, use_container_width=True)
    
    with tab3:
        st.markdown("#### Évolution temporelle")
        
        if "Date creation abonnement" in filtered_data.columns:
            # Évolution annuelle
            filtered_data['Année'] = pd.to_datetime(filtered_data['Date creation abonnement']).dt.year
            annual_data = filtered_data['Année'].value_counts().sort_index().reset_index()
            annual_data.columns = ['Année', 'Nombre']
            
            fig_annual = px.line(annual_data, x='Année', y='Nombre',
                                title=f"Évolution annuelle ({selected_region})")
            st.plotly_chart(fig_annual, use_container_width=True)
            
            # Évolution mensuelle (pour la dernière année)
            if not filtered_data.empty:
                latest_year = filtered_data['Année'].max()
                monthly_data = filtered_data[filtered_data['Année'] == latest_year].copy()
                monthly_data['Mois'] = pd.to_datetime(monthly_data['Date creation abonnement']).dt.month_name()
                monthly_counts = monthly_data['Mois'].value_counts().reset_index()
                monthly_counts.columns = ['Mois', 'Nombre']
                
                fig_monthly = px.bar(monthly_counts, x='Mois', y='Nombre',
                                    title=f"Répartition mensuelle ({latest_year}, {selected_region})")
                st.plotly_chart(fig_monthly, use_container_width=True)
    
    with tab4:
        st.markdown("#### Tableaux récapitulatifs")
        
        if "Libelle categorie facturation" in filtered_data.columns:
            # Tableau croisé Catégorie × État
            pivot_etat = pd.crosstab(filtered_data["Libelle categorie facturation"], 
                                    filtered_data["État Contrat"])
            st.markdown("##### Répartition Catégorie × État")
            st.dataframe(pivot_etat, use_container_width=True)
            
        if "Nom commune" in filtered_data.columns and "Libelle categorie facturation" in filtered_data.columns:
            # Tableau croisé Commune × Catégorie
            pivot_commune = pd.crosstab(filtered_data["Nom commune"], 
                                      filtered_data["Libelle categorie facturation"])
            st.markdown("##### Répartition Commune × Catégorie")
            st.dataframe(pivot_commune, use_container_width=True)
    
    # Métriques clés
    st.markdown("### Métriques clés")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        total = len(filtered_data)
        st.metric("Total contrats", total)
    
    with col2:
        en_service = len(filtered_data[filtered_data["État Contrat"] == "En service"])
        st.metric("Contrats en service", f"{en_service} ({en_service/total*100:.1f}%)" if total > 0 else "0")
    
    with col3:
        resilies = len(filtered_data[filtered_data["État Contrat"] == "Résilié"])
        st.metric("Contrats résiliés", f"{resilies} ({resilies/total*100:.1f}%)" if total > 0 else "0")