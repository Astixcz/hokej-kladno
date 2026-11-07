import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Kladenská Hokejová Historie", layout="wide")

st.title("🏒 Historická hokejová kalkulačka Kladna — Verze 1.1")
st.write("Analýza výsledků od sezóny 1965/66 do 2025/26")

@st.cache_data
def nacti_data():
    df = pd.read_csv("Kladno_Cista_Data.csv", sep=";")
    df.columns = df.columns.str.strip().str.lower()
    převodník = {
        'sezóna': 'sezona', 'pořadí': 'poradi', 'skóre': 'skore', 
        'výsledek': 'vysledek', 'poznámka': 'poznamka',
        'kumul_rea': 'kumul_realne'
    }
    df = df.rename(columns=převodník)
    return df

try:
    df = nacti_data()

    verze = st.sidebar.radio("Vyberte si funkci:", [
        "1) Kolik bodů po X zápasech?", 
        "2) Kolik zápasů na X bodů?",
        "3) Bodový vývoj v sezóně",
        "4) Historické poznámky a pravidla"
    ])

    nizsi_soutez = [
        "1983/84", "1984/85", "1986/87", "2002/03", 
        "2014/15", "2015/16", "2016/17", "2017/18", "2018/19", "2020/21"
    ]
    
    titulove_sezony = [
        "1974/75", "1975/76", "1976/77", "1977/78", "1979/80"
    ]

    def urci_kategorii(sezona_str):
        sezona_clean = str(sezona_str).strip()
        if sezona_clean in titulove_sezony:
            return "Mistrovská sezóna (Titul)"
        elif sezona_clean in nizsi_soutez:
            return "1. liga (Nižší soutěž)"
        else:
            return "Extraliga (Nejvyšší soutěž)"

    barevna_mapa = {
        "Mistrovská sezóna (Titul)": "#D4AF37",
        "Extraliga (Nejvyšší soutěž)": "#1F77B4",
        "1. liga (Nižší soutěž)": "#FF4B4B"
    }

    if verze == "1) Kolik bodů po X zápasech?":
        st.header("📊 Bodový stav po odehraných zápasech")
        if 'poradi' in df.columns:
            max_zapasu = int(df['poradi'].max())
            pocet_zapasu = st.slider("Zadejte počet odehraných zápasů v sezóně:", 1, max_zapasu, 17)
            dostupne_sloupce = [col for col in ['sezona', 'kumul_realne', 'kumul_3b', 'poznamka'] if col in df.columns]
            vysledek = df[df['poradi'] == pocet_zapasu][dostupne_sloupce].copy()
            vysledek = vysledek.rename(columns={'sezona': 'Sezóna', 'kumul_realne': 'Reálné body', 'kumul_3b': 'Přepočtené body (3b)', 'poznamka': 'Poznámka'})
            
            if not vysledek.empty and 'Přepočtené body (3b)' in vysledek.columns:
                max_body = vysledek['Přepočtené body (3b)'].max()
                nej_sezony = vysledek[vysledek['Přepočtené body (3b)'] == max_body]['Sezóna'].tolist()
                st.info(f"🏆 Rekord po {pocet_zapasu} zápasech drží: {', '.join(nej_sezony)} ({max_body} bodů).")

            st.dataframe(vysledek.reset_index(drop=True), use_container_width=True)
            vysledek['Kategorie'] = vysledek['Sezóna'].apply(urci_kategorii)
            fig = px.bar(vysledek, x="Sezóna", y="Přepočtené body (3b)", color="Kategorie", color_discrete_map=barevna_mapa, template="plotly_white")
            fig.update_xaxes(categoryorder="array", categoryarray=vysledek['Sezóna'])
            st.plotly_chart(fig, use_container_width=True)

    elif verze == "2) Kolik zápasů na X bodů?":
        st.header("⏱️ Rychlost dosažení bodové mety")
        cilove_body = st.number_input("Zadejte cílový počet bodů:", min_value=1, max_value=120, value=20)
        skryt_nedosazeno = st.checkbox("Skrýt sezóny bez dosažení mety", value=False)

        if 'sezona' in df.columns and 'kumul_3b' in df.columns and 'poradi' in df.columns:
            zaznamy = []
            for sezona in df['sezona'].unique():
                sub_df = df[(df['sezona'] == sezona) & (df['kumul_3b'] >= cilove_body)]
                if not sub_df.empty:
                    prvni_zapas = sub_df['poradi'].min()
                    hodnoty_realne = sub_df[sub_df['poradi'] == prvni_zapas]['kumul_realne'].values
                    realne_body = int(hodnoty_realne[0]) if len(hodnoty_realne) > 0 and 'kumul_realne' in df.columns else "-"
                    zaznamy.append({"Sezóna": sezona, "Potřebný počet zápasů": int(prvni_zapas), "Reálné body v té chvíli": realne_body})
                elif not skryt_nedosazeno:
                    zaznamy.append({"Sezóna": sezona, "Potřebný počet zápasů": "Nedosáhnuto", "Reálné body v té chvíli": "-"})
                    
            vysledne_df = pd.DataFrame(zaznamy)
            st.dataframe(vysledne_df, use_container_width=True)
            graf_df = vysledne_df[vysledne_df["Potřebný počet zápasů"] != "Nedosáhnuto"].copy()
            
            if not graf_df.empty:
                graf_df["Potřebný počet zápasů"] = pd.to_numeric(graf_df["Potřebný počet zápasů"])
                graf_df['Kategorie'] = graf_df['Sezóna'].apply(urci_kategorii)
                graf_df = graf_df.sort_values(by="Potřebný počet zápasů")
                fig2 = px.bar(graf_df, x="Sezóna", y="Potřebný počet zápasů", color="Kategorie", color_discrete_map=barevna_mapa, template="plotly_white")
                fig2.update_xaxes(categoryorder="array", categoryarray=graf_df['Sezóna'])
                st.plotly_chart(fig2, use_container_width=True)

    elif verze == "3) Bodový vývoj v sezóně":
        st.header("📈 Křivka bodového růstu zápas po zápase")
        if 'sezona' in df.columns and 'poradi' in df.columns:
            seznam_sezon = sorted(df['sezona'].unique(), reverse=True)
            vybrana_sezona = st.selectbox("Vyberte sezónu:", seznam_sezon)
            sezona_df = df[df['sezona'] == vybrana_sezona].sort_values(by='poradi').copy()
            kat = urci_kategorii(vybrana_sezona)
            st.write(f"Status sezóny: **{kat}**")
            
            df_line = sezona_df.melt(id_vars=['poradi'], value_vars=['kumul_realne', 'kumul_3b'], var_name='Typ', value_name='Body')
            df_line['Typ'] = df_line['Typ'].map({'kumul_realne': 'Reálné body', 'kumul_3b': 'Přepočtené body (3b)'})
            
            fig3 = px.line(df_line, x='poradi', y='Body', color='Typ', color_discrete_map={'Reálné body': '#888888', 'Přepočtené body (3b)': barevna_mapa[kat]}, template='plotly_white', markers=True)
            st.plotly_chart(fig3, use_container_width=True)

    elif verze == "4) Historické poznámky a pravidla":
        st.header("📝 Jak kalkulačka funguje a Historický kontext")
        st.write("Kliknutím na záhlaví libovolného sloupce v tabulce data okamžitě seřadíte.")
        st.write("Záložka 1 porovnává body po X zápasech. Záložka 2 sleduje rychlost dosažení mety.")
        st.write("Záložka 3 ukazuje vývoj vybrané sezóny. Pokud byla meta Nedosáhnuto a zaškrtnete skrýt, sezóna se schová.")
        st.write("Zlatá barva značí 5 mistrovských titulů, modrá Extraligu a červená 1. ligu.")
        st.write("Reálné body jsou dle tehdejších pravidel (do r. 2000 byly za výhru 2 body). Přepočtené body používají moderní 3b systém.")

except Exception as e:
    st.error(f"Došlo k chybě: {e}")
