import streamlit as st
import pandas as pd

st.set_page_config(page_title="Kladenská Hokejová Historie", layout="wide")

st.title("🏒 Historická hokejová kalkulačka Kladna")
st.write("Analýza výsledků od sezóny 1965/66 do 2025/26")

@st.cache_data
def nacti_data():
    # Načte NOVÝ přejmenovaný soubor se středníkem
    df = pd.read_csv("Kladno_Cista_Data.csv", sep=";")
    
    # OPRAVNÝ MECHANISMUS PRO SLOUPCE:
    # Převede všechny názvy sloupců na malá písmena a odstraní mezery
    df.columns = df.columns.str.strip().str.lower()
    
    # Odstranění diakritiky z názvů sloupců pro jistotu (sezóna -> sezona, pořadí -> poradi)
    převodník = {
        'sezóna': 'sezona', 'pořadí': 'poradi', 'skóre': 'skore', 
        'výsledek': 'vysledek', 'poznámka': 'poznamka'
    }
    df = df.rename(columns=převodník)
    return df

try:
    df = nacti_data()

    verze = st.sidebar.radio("Vyberte si funkci:", [
        "1) Kolik bodů po X zápasech?", 
        "2) Kolik zápasů na X bodů?",
        "3) Historické poznámky a pravidla"
    ])

    if verze == "1) Kolik bodů po X zápasech?":
        st.header("📊 Bodový stav po odehraných zápasech")
        
        # Kontrola, zda sloupec existuje
        if 'poradi' in df.columns:
            max_zapasu = int(df['poradi'].max())
            pocet_zapasu = st.slider("Zadejte počet odehraných zápasů v sezóně:", 1, max_zapasu, 10)
            
            # Výběr sloupců podle toho, co v tabulce opravdu je
            dostupne_sloupce = [col for col in ['sezona', 'kumul_realne', 'kumul_3b', 'poznamka'] if col in df.columns]
            vysledek = df[df['poradi'] == pocet_zapasu][dostupne_sloupce].copy()
            
            # Přejmenování sloupců pro hezčí zobrazení uživateli
            přejmenování_zobrazení = {
                'sezona': 'Sezóna',
                'kumul_realne': 'Reálné body',
                'kumul_3b': 'Přepočtené body (3b)',
                'poznamka': 'Poznámka'
            }
            vysledek = vysledek.rename(columns=přejmenování_zobrazení)
            
            st.subheader(f"Stav Kladna po {pocet_zapasu}. odehraném zápase:")
            st.dataframe(vysledek.reset_index(drop=True), use_container_width=True)
            
            if 'Přepočtené body (3b)' in vysledek.columns and 'Sezóna' in vysledek.columns:
                # Seznam sezón v nižší soutěži (1. liga)
                nizsi_soutez = [
                    "1983/84", "1984/85", "1986/87", "2002/03", 
                    "2014/15", "2015/16", "2016/17", "2017/18", "2018/19", "2020/21"
                ]
                
                # Vytvoření barevného profilu pro každou sezónu v grafu
                vysledek['barva'] = vysledek['Sezóna'].apply(lambda x: '#FF4B4B' if str(x).strip() in nizsi_soutez else '#1F77B4')
                
                # Vykreslení pokročilejšího grafu s vlastními barvami
                st.bar_chart(
                    vysledek,
                    x="Sezóna",
                    y="Přepočtené body (3b)",
                    color="barva",
                    use_container_width=True
                )
                
                # Přidání vysvětlující poznámky (legendy) pod graf
                st.markdown("""
                🔴 **Červeně zvýrazněné sloupce** značí sezóny, ve kterých Kladno působilo v **nižší soutěži** (1. lize / tehdejší I. ČNHL). \n
                🔵 **Modré sloupce** značí sezóny v nejvyšší soutěži (Extralize / tehdejší I. lize).
                """)
        else:
            st.error(f"V souboru chybí sloupec pro pořadí zápasů. Dostupné sloupce jsou: {list(df.columns)}")

    elif verze == "2) Kolik zápasů na X bodů?":
        st.header("⏱️ Rychlost dosažení bodové mety")
        cilove_body = st.number_input("Zadejte cílový počet bodů (přepočtených na 3b systém):", min_value=1, max_value=120, value=20)
        
        if 'sezona' in df.columns and 'kumul_3b' in df.columns and 'poradi' in df.columns:
            sezony = df['sezona'].unique()
            zaznamy = []
            
            for sezona in sezony:
                sub_df = df[(df['sezona'] == sezona) & (df['kumul_3b'] >= cilove_body)]
                if not sub_df.empty:
                    prvni_zapas = sub_df['poradi'].min()
                    realne_body = int(sub_df[sub_df['poradi'] == prvni_zapas]['kumul_realne'].values[0]) if 'kumul_realne' in df.columns else "-"
                    zaznamy.append({
                        "Sezóna": sezona, 
                        "Potřebný počet zápasů": int(prvni_zapas),
                        "Reálné body v té chvíli": realne_body
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
        else:
            st.error(f"Chybí potřebné sloupce (sezona, poradi nebo kumul_3b). Dostupné sloupce: {list(df.columns)}")

    elif verze == "3) Historické poznámky a pravidla":
        st.header("📝 Historický kontext a změny pravidel")
        st.markdown("""
        ### 🔄 Vývoj bodového systému
        * **Do sezóny 1999/00:** Platil klasický 2bodový systém (2 body za výhru, 1 za remízu).
        * **Od sezóny 2006/07:** Kompletní zrušení remíz. Zavedeny samostatné nájezdy (vítěz 2 body, poražený 1 bod).
        
        ### ⏱️ Zavedení prodloužení
        1. **Sezóny 1983/84 – 1985/86:** Popvrve zavedeno pětiminutové prodloužení náhlé smrti. Pokud gól nepadl, zápas skončil remízou.
        2. **1986–1993:** Prodloužení zrušeno, návrat k remízám po 60 minutách.
        3. **Od 1993/94:** Prodloužení vráceno natrvalo (nejdříve 5 na 5, od 1999/00 formát 4 na 4).
        
        ⚠️ *Poznámka k sezóně 2010/11:* V této sezóně proběhla tzv. **odpočtová aféra** (neoprávněné starty hráčů), kvůli které nesedí oficiální body s odehranými zápasy na ledě.
        """)

except Exception as e:
    st.error(f"Chyba při načítání dat: {e}")
