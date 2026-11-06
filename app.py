import streamlit as st
import pandas as pd
import plotly.express as px

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

    nizsi_soutez = [
        "1983/84", "1984/85", "1986/87", "2002/03", 
        "2014/15", "2015/16", "2016/17", "2017/18", "2018/19", "2020/21"
    ]

    if verze == "1) Kolik bodů po X zápasech?":
        st.header("📊 Bodový stav po odehraných zápasech")
        
        if 'poradi' in df.columns:
            max_zapasu = int(df['poradi'].max())
            pocet_zapasu = st.slider("Zadejte počet odehraných zápasů v sezóně:", 1, max_zapasu, 17)
            
            dostupne_sloupce = [col for col in ['sezona', 'kumul_realne', 'kumul_3b', 'poznamka'] if col in df.columns]
            vysledek = df[df['poradi'] == pocet_zapasu][dostupne_sloupce].copy()
            
            přejmenování_zobrazení = {
                'sezona': 'Sezóna', 'kumul_realne': 'Reálné body', 'kumul_3b': 'Přepočtené body (3b)', 'poznamka': 'Poznámka'
            }
            vysledek = vysledek.rename(columns=přejmenování_zobrazení)
            
            if not vysledek.empty and 'Přepočtené body (3b)' in vysledek.columns:
                max_body_v_koliku = vysledek['Přepočtené body (3b)'].max()
                nej_sezony = vysledek[vysledek['Přepočtené body (3b)'] == max_body_v_koliku]['Sezóna'].tolist()
                st.info(f"🏆 **Historický rekord Kladna:** Po {pocet_zapasu} zápasech byla nejúspěšnější sezóna **{', '.join(nej_sezony)}** ({max_body_v_koliku} bodů po přepočtu na 3b systém).")

            st.subheader(f"Stav Kladna po {pocet_zapasu}. odehraném zápase:")
            st.dataframe(vysledek.reset_index(drop=True), use_container_width=True)
            
            if 'Přepočtené body (3b)' in vysledek.columns and 'Sezóna' in vysledek.columns:
                vysledek['Soutěž'] = vysledek['Sezóna'].apply(
                    lambda x: '1. liga (Nižší)' if str(x).strip() in nizsi_soutez else 'Extraliga (Nejvyšší)'
                )
                
                fig = px.bar(
                    vysledek,
                    x="Sezóna",
                    y="Přepočtené body (3b)",
                    color="Soutěž",
                    color_discrete_map={
                        "Extraliga (Nejvyšší)": "#1F77B4",
                        "1. liga (Nižší)": "#FF4B4B"
                    },
                    labels={"Přepočtené body (3b)": "Body (3b)"},
                    template="plotly_white"
                )
                
                fig.update_xaxes(categoryorder="array", categoryarray=vysledek['Sezóna'], title="Sezóna")
                fig.update_layout(
                    margin=dict(l=0, r=0, t=20, b=0),
                    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
                )
                st.plotly_chart(fig, use_container_width=True)
                
                st.markdown("""
                🔴 **Červeně zvýrazněné sloupce** značí sezóny, ve kterých Kladno působilo v **nižší soutěži** (1. lize / tehdejší I. ČNHL). \n
                🔵 **Modré sloupce** značí sezóny v nejvyšší soutěži (Extralize / tehdejší I. lize).
                """)
        else:
            st.error("V souboru chybí sloupec pro pořadí zápasů.")

    elif verze == "2) Kolik zápasů na X bodů?":
        st.header("⏱️ Rychlost dosažení bodové mety")
        cilove_body = st.number_input("Zadejte cílový počet bodů (přepočtených na 3b systém):", min_value=1, max_value=120, value=20)
        
        skryt_nedosazeno = st.checkbox("Skrýt sezóny, které na tuto metu nedosáhly", value=False)

        if 'sezona' in df.columns and 'kumul_3b' in df.columns and 'poradi' in df.columns:
            sezony = df['sezona'].unique()
            zaznamy = []
            
            for sezona in sezony:
                sub_df = df[(df['sezona'] == sezona) & (df['kumul_3b'] >= cilove_body)]
                if not sub_df.empty:
                    prvni_zapas = sub_df['poradi'].min()
                    hodnoty_realne = sub_df[sub_df['poradi'] == prvni_zapas]['kumul_realne'].values
                    realne_body = int(hodnoty_realne[0]) if len(hodnoty_realne) > 0 and 'kumul_realne' in df.columns else "-"
                    
                    zaznamy.append({
                        "Sezóna": sezona, "Potřebný počet zápasů": int(prvni_zapas), "Reálné body v té chvíli": realne_body
                    })
                else:
                    if not skryt_nedosazeno:
                        zaznamy.append({
                            "Sezóna": sezona, "Potřebný počet zápasů": "Nedosáhnuto", "Reálné body v té chvíli": "-"
                        })
                    
            vysledne_df = pd.DataFrame(zaznamy)
            st.subheader(f"Kolik zápasů potřebovalo Kladno na získání minimálně {cilove_body} bodů:")
            st.dataframe(vysledne_df, use_container_width=True)

            graf_df = vysledne_df[vysledne_df["Potřebný počet zápasů"] != "Nedosáhnuto"].copy()
            
            if not graf_df.empty:
                graf_df["Potřebný počet zápasů"] = pd.to_numeric(graf_df["Potřebný počet zápasů"])
                graf_df['Soutěž'] = graf_df['Sezóna'].apply(
                    lambda x: '1. liga (Nižší)' if str(x).strip() in nizsi_soutez else 'Extraliga (Nejvyšší)'
                )
                
                graf_df = graf_df.sort_values(by="Potřebný počet zápasů", ascending=True)

                st.subheader(f"📊 Žebříček sezón podle rychlosti dosažení {cilove_body} bodů")
                st.caption("Graf zobrazuje pouze sezóny, které na metu dosáhly, seřazené od nejrychlejších po nejpomalejší.")

                fig2 = px.bar(
                    graf_df,
                    x="Sezóna",
                    y="Potřebný počet zápasů",
                    color="Soutěž",
                    color_discrete_map={
                        "Extraliga (Nejvyšší)": "#1F77B4",
                        "1. liga (Nižší)": "#FF4B4B"
                    },
                    labels={"Potřebný počet zápasů": "Počet zápasů k metě"},
                    template="plotly_white"
                )
                
                fig2.update_xaxes(categoryorder="array", categoryarray=graf_df['Sezóna'], title="Sezóna")
                fig2.update_layout(
                    margin=dict(l=0, r=0, t=20, b=0),
                    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
                )
                st.plotly_chart(fig2, use_container_width=True)
            else:
                st.warning(f"V žádné historické sezóně Kladno nedosáhlo na hranici {cilove_body} bodů.")
        else:
            st.error("Chybí potřebné sloupce (sezona, poradi nebo kumul_3b).")

    elif verze == "3) Historické poznámky a pravidla":
        st.header("📝 Jak kalkulačka funguje & Historický kontext")
        st.markdown("""
        ### 💡 Návod k funkcím aplikace
        
        📌 **Tip pro práci s tabulkami:** Kliknutím na libovolný název záhlaví sloupce můžete data v tabulce okamžitě **vzestupně nebo sestupně seřadit**. To vám umožní bleskově najít ty historicky nejlepší a nejhorší sezóny!
        
        #### 1) Záložka: Kolik bodů po X zápasech?
        * **K čemu slouží:** Pomocí posuvníku si zvolíte konkrétní odehraný zápas od začátku základní části.
        * **Co uvidíte:** Aplikace okamžitě porovná všechny sezóny od roku 1965 a ukáže přepočtený stav bodů.
        * **Důležité upozornění:** Pokud nastavíte vyšší počet zápasů, než se tehdy odehrálo, sezóna z grafů i tabulky zmizí.
        
        #### 2) Záložka: Kolik zápasů na X bodů?
        * **K čemu slouží:** Zadáte cílové číslo a aplikace najde, jak rychle na něj Kladno dosáhlo.
        * **Co uvidíte:** Číslo zápasu, kdy byla meta poprvé pokořena. Pokud se tak nestalo, uvidíte text 'Nedosáhnuto'. **Pokud zaškrtnete políčko pro skrytí, tyto neúspěšné sezóny se v tabulce vůbec nezobrazí.**
        
        ---

        ### 🔍 Vysvětlení pojmů (Body v aplikaci)
        * **Reálné body:** Skutečný stav, jaký tehdy platil v oficiální ligové tabulce (např. do roku 2000 byly za výhru jen 2 body).
        * **Přepočtené body (3b):** Hlavní motor kalkulačky. Ohodnotí každý historický zápas moderním tříbodovým systémem pro spravedlivé srovnání napříč dekádami.
        
        ---
        
        ### 🔄 Vývoj bodového systému v historii
        * **Do sezóny 1999/00:** Platil klasický 2bodový systém (2 body za výhru, 1 bod za remízu po 60 minutách).
        * **Od sezóny 2000/01:** Došlo k zavedení současného 3bodového systému (3 body za výhru v základní hrací době, 2 body za výhru v prodloužení či nájezdech, 1 bod za prohru v prodloužení či nájezdech).
        """)

except Exception as e:
    st.error(f"Došlo k chybě při načítání nebo zpracování dat: {e}")
