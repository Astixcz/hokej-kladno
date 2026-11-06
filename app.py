import streamlit as st
import pandas as pd

st.set_page_config(page_title="Kladenská Hokejová Historie", layout="wide")

st.title("🏒 Historická hokejová kalkulačka Kladna")
st.write("Analýza výsledků od sezóny 1965/66 do 2025/26")

@st.cache_data
def nacti_data():
    df = pd.read_csv("Kladno_Cista_Data.csv", sep=";")
    df.columns = df.columns.str.strip().str.lower()
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
        
        if 'poradi' in df.columns:
            max_zapasu = int(df['poradi'].max())
            pocet_zapasu = st.slider("Zadejte počet odehraných zápasů v sezóně:", 1, max_zapasu, 10)
            
            dostupne_sloupce = [col for col in ['sezona', 'kumul_realne', 'kumul_3b', 'poznamka'] if col in df.columns]
            vysledek = df[df['poradi'] == pocet_zapasu][dostupne_sloupce].copy()
            
            přejmenování_zobrazení = {
                'sezona': 'Sezóna', 'kumul_realne': 'Reálné body', 'kumul_3b': 'Přepočtené body (3b)', 'poznamka': 'Poznámka'
            }
            vysledek = vysledek.rename(columns=přejmenování_zobrazení)
            
            st.subheader(f"Stav Kladna po {pocet_zapasu}. odehraném zápase:")
            st.dataframe(vysledek.reset_index(drop=True), use_container_width=True)
            
            if 'Přepočtené body (3b)' in vysledek.columns and 'Sezóna' in vysledek.columns:
                nizsi_soutez = [
                    "1983/84", "1984/85", "1986/87", "2002/03", 
                    "2014/15", "2015/16", "2016/17", "2017/18", "2018/19", "2020/21"
                ]
                
                vysledek['Soutěž'] = vysledek['Sezóna'].apply(
                    lambda x: '1. liga (Nižší)' if str(x).strip() in nizsi_soutez else 'Extraliga (Nejvyšší)'
                )
                
                # OPRAVENO: Správný název parametru je color= a přijímá seznam barev
                st.bar_chart(
                    vysledek,
                    x="Sezóna",
                    y="Přepočtené body (3b)",
                    color=["#FF4B4B", "#1F77B4"],
                    use_container_width=True
                )
                
                st.markdown("""
                🔴 **Červeně zvýrazněné sloupce** značí sezóny, ve kterých Kladno působilo v **nižší soutěži** (1. lize / tehdejší I. ČNHL). \n
                🔵 **Modré sloupce** značí sezóny v nejvyšší soutěži (Extralize / tehdejší I. lize). \n
                ⚠️ *Upozornění k zobrazení:* Pokud posuvník nastavíte na více než 52 zápasů, v grafu zůstanou pouze dvě sezóny. Vlivem automatického chování grafické knihovny Streamlit se v této chvíli mohou barvy sloupců (červená a modrá) navzájem prohodit. Spolehlivé zařazení sezón vyčtete vždy z textové tabulky výše.
                """)
        else:
            st.error(f"V souboru chybí sloupec pro pořadí zápasů.")

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
                    realne_body = int(sub_df[sub_df['poradi'] == prvni_zapas]['kumul_realne'].values) if 'kumul_realne' in df.columns else "-"
                    zaznamy.append({
                        "Sezóna": sezona, "Potřebný počet zápasů": int(prvni_zapas), "Reálné body v té chvíli": realne_body
                    })
                else:
                    zaznamy.append({
                        "Sezóna": sezona, "Potřebný počet zápasů": "Nedosáhnuto", "Reálné body v té chvíli": "-"
                    })
                    
            vysledne_df = pd.DataFrame(zaznamy)
            st.subheader(f"Kolik zápasů potřebovalo Kladno na získání minimálně {cilove_body} bodů:")
            st.dataframe(vysledne_df, use_container_width=True)
        else:
            st.error(f"Chybí potřebné sloupce (sezona, poradi nebo kumul_3b).")

    elif verze == "3) Historické poznámky a pravidla":
        st.header("📝 Jak kalkulačka funguje & Historický kontext")
        st.markdown("""
        ### 💡 Návod k funkcím aplikace
        
        #### 1) Záložka: Kolik bodů po X zápasech?
        * **K čemu slouží:** Pomocí posuvníku (slideru) si zvolíte konkrétní odehraný zápas od začátku základní části (např. 10. zápas sezóny). 
        * **Co uvidíte:** Aplikace vám okamžitě porovná všechny sezóny od roku 1965 a ukáže, kolik bodů v tomto konkrétním okamžiku Kladno mělo. Můžete tak snadno porovnat historické starty do sezón. Graf dole vám vizuálně ukáže nejúspěšnější roky.
        
        #### 2) Záložka: Kolik zápasů na X bodů?
        * **K čemu slouží:** Zadáte cílové číslo (např. 20 bodů) a aplikace prohledá historii Kladna.
        * **Co uvidíte:** U každé sezóny zjistíte přesné chronologické číslo zápasu, ve kterém Kladno na tuto bodovou metu poprvé dosáhlo (při přepočtu na 3bodový systém). Pokud Kladno v daném roce takto úspěšné nebylo, uvidíte text *„Nedosáhnuto“*. Sloupec *„Reálné body v té chvíli“* ukazuje, kolik bodů svítilo v tabulce podle tehdejších historických pravidel.
        
        ---
        
        ### 🔄 Vývoj bodového systému v historii
        * **Do sezóny 1999/00:** Platil klasický 2bodový systém (2 body za výhru, 1 za remízu). V aplikaci jsou tyto sezóny pro spravedlivé srovnání matematicky přepočteny na moderní model (Výhra = 3 body, Remíza = 1 bod).
        * **Od sezóny 2006/07:** Kompletní zrušení remíz v české Extralize. Zavedeny samostatné nájezdy (vítěz bere 2 body, poražený v prodloužení/nájezdech 1 bod).
        
        ### ⏱️ Zavedení prodloužení
        1. **Sezóny 1983/84 – 1985/86:** V československé lize poprvé krátce zavedeno pětiminutové prodloužení systémem „náhlé smrti“. Pokud gól nepadl, zápas přesto skončil remízou.
        2. **1986–1993:** Prodloužení bylo zrušeno, po 60 minutách následovala okamžitá remíza.
        3. **Od 1993/94:** Prodloužení vráceno natrvalo (nejdříve v klasickém formátu 5 na 5, od sezóny 1999/00 atraktivnější formát 4 na 4).
        
        ⚠️ *Poznámka k sezóně 2010/11:* V této sezóně postihla český hokej tzv. **odpočtová aféra** za neoprávněné starty hráčů (včetně Kladna). Zápasy odehrané na ledě a body získané u zeleného stolu se proto mohou lišit.
        """)

except Exception as e:
    st.error(f"Chyba při načítání dat: {e}")
