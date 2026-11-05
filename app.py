import streamlit as st
import pandas as pd

st.set_page_config(page_title="Kladenská Hokejová Historie", layout="wide")

st.title("🏒 Historická hokejová kalkulačka Kladna")
st.write("Analýza výsledků od sezóny 1965/66 do 2025/26")

@st.cache_data
def nacti_data():
    # Načte vaše CSV s hokejem (středník jako oddělovač)
    df = pd.read_csv("Kladno_Data.csv", sep=";")
    return df


try:
    df = nacti_data()
    df.columns = df.columns.str.strip()

    verze = st.sidebar.radio("Vyberte si funkci:", [
        "1) Kolik bodů po X zápasech?", 
        "2) Kolik zápasů na X bodů?",
        "3) Historické poznámky a pravidla"
    ])

    if verze == "1) Kolik bodů po X zápasech?":
        st.header("📊 Bodový stav po odehraných zápasech")
        max_zapasu = int(df['poradi'].max())
        pocet_zapasu = st.slider("Zadejte počet odehraných zápasů v sezóně:", 1, max_zapasu, 10)
        
        vysledek = df[df['poradi'] == pocet_zapasu][['sezona', 'kumul_rea', 'kumul_3b', 'poznamka']]
        vysledek.columns = ['Sezóna', 'Reálné body', 'Přepočtené body (3b)', 'Poznámka']
        
        st.subheader(f"Stav Kladna po {pocet_zapasu}. odehraném zápase:")
        st.dataframe(vysledek.reset_index(drop=True), use_container_width=True)
        st.bar_chart(vysledek.set_index('Sezóna')['Přepočtené body (3b)'])

    elif verze == "2) Kolik zápasů na X bodů?":
        st.header("⏱️ Rychlost dosažení bodové mety")
        cilove_body = st.number_input("Zadejte cílový počet bodů (přepočtených na 3b systém):", min_value=1, max_value=120, value=20)
        
        sezony = df['sezona'].unique()
        zaznamy = []
        
        for sezona in sezony:
            sub_df = df[(df['sezona'] == sezona) & (df['kumul_3b'] >= cilove_body)]
            if not sub_df.empty:
                prvni_zapas = sub_df['poradi'].min()
                realne_body_v_tom_zapase = sub_df[sub_df['poradi'] == prvni_zapas]['kumul_rea'].values[0]
                zaznamy.append({
                    "Sezóna": sezona, 
                    "Potřebný počet zápasů": int(prvni_zapas),
                    "Reálné body v té chvíli": int(realne_body_v_tom_zapase)
                })
            else:
                zaznamy.append({
                    "Sezóna": sezona, 
                    "Potřebný počet zápasů": "Nedosáhnuto",
                    "Reálné body v té chvíli": "-"
                })
                
        vysledne_df = pd.DataFrame(zaznamy)
        st.subheader(f"Kolik zápasů potřebovalo Kladno na získání minimálně {cilove_body} bodů:")
        st.dataframe(vysledne_df, use_container_width=True)

    elif verze == "3) Historické poznámky a pravidla":
        st.header("📝 Historický kontext a změny pravidel")
        st.markdown("""
        ### 🔄 Vývoj bodového systému
        * **Do sezóny 1999/00:** Platil klasický 2bodový systém (2 body za výhru, 1 za remízu).
        * **Od sezóny 2006/07:** Kompletní zrušení remíz. Zavedeny samostatné nájezdy (vítěz 2 body, poražený 1 bod).
        
        ### ⏱️ Zavedení prodloužení
        1. **Sezóny 1983/84 – 1985/86:** Poprvé zavedeno pětiminutové prodloužení náhlé smrti. Pokud gól nepadl, zápas skončil remízou.
        2. **1986–1993:** Prodloužení zrušeno, návrat k remízám po 60 minutách.
        3. **Od 1993/94:** Prodloužení vráceno natrvalo (nejdříve 5 na 5, od 1999/00 formát 4 na 4).
        
        ⚠️ *Poznámka k sezóně 2010/11:* V této sezóně proběhla tzv. **odpočtová aféra** (neoprávněné starty hráčů), kvůli které nesedí oficiální body s odehranými zápasy na ledě.
        """)

except Exception as e:
    st.error(f"Chyba při načítání dat: {e}")
