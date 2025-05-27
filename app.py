import streamlit as st
from sections import contrat_kelaa, autre_contrat, postes

# Configuration initiale
st.set_page_config(
    page_title="Suivi Contrats et Postes Électricité",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# =============================================
# EN-TÊTE PRINCIPAL
# =============================================
st.markdown("""
    <div style='text-align: center; padding: 1.5rem; margin-bottom: 2rem;
               background: linear-gradient(to right, #0056b3, #003366);
               border-radius: 10px; box-shadow: 0 4px 8px rgba(0,0,0,0.2);'>
        <h1 style='color: white; margin: 0;'>⚡ ElectraTrack  ⚡</h1>
        <p style='color: rgba(255,255,255,0.9); margin: 0.5rem 0 0;'>
            Suivi intelligent des contrats et des postes électriques
        </p>
    </div>
""", unsafe_allow_html=True)

# =============================================
# INITIALISATION DE SESSION
# =============================================
if "agency_data" not in st.session_state:
    st.session_state.agency_data = {}
if "postes_data" not in st.session_state:
    st.session_state.postes_data = None

# =============================================
# BARRE LATERALE - NAVIGATION
# =============================================
with st.sidebar:
    st.title("📌 Navigation")
    
    section = st.radio(
        "Menu principal :",
        ["📄 Contrats Électricité", "🏗 Postes Électriques"],
        index=0
    )

    st.markdown("---")
    
    if section == "📄 Contrats Électricité":
        st.subheader("Sélection d'agence")
        agency = st.selectbox(
            "Choisir une agence :",
            ["Agence_El Kelaa Des Sraghna", "Agence_LAATAOUIA_SIDI RAHAL_TAMELLALT"]
        )

# =============================================
# CONTENU PRINCIPAL
# =============================================
if section == "📄 Contrats Électricité":
    if agency == "Agence_El Kelaa Des Sraghna":
        contrat_kelaa.show()
    else:
        autre_contrat.show()
elif section == "🏗 Postes Électriques":
    postes.show()

# =============================================
# PIED DE PAGE (SIDEBAR)
# =============================================
with st.sidebar:
    st.markdown("---")
    st.subheader("📞 Contact")
    
    cols = st.columns(2)
    with cols[0]:
        st.markdown("""
            <a href="https://wa.me/+212639773243" target="_blank">
            <img src="https://upload.wikimedia.org/wikipedia/commons/6/6b/WhatsApp.svg" 
                 width="40" style="margin-right: 15px;"></a>
            """, unsafe_allow_html=True)
    
    with cols[1]:
        st.markdown("""
            <a href="https://www.facebook.com/profile.php?id=61575126301247" target="_blank">
            <img src="https://upload.wikimedia.org/wikipedia/commons/5/51/Facebook_f_logo_%282019%29.svg" 
                 width="40"></a>
            """, unsafe_allow_html=True)
    
    st.markdown("""
        **📧 Email**  
        elhattabnada123@gmail.com  
        
        **🕒 Horaires**  
        Lun-Ven: 8h30-17h30
    """)
