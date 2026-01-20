import streamlit as st
import pandas as pd

st.set_page_config(
    page_title="Climate Adaptation Risk Matrix (H×E×V)",
    page_icon="🌍",
    layout="wide"
)

st.title("🌍 Climate Adaptation Risk Matrix (H × E × V) – wersja projektowa")
st.caption(
    "Wybierz temat projektu i wypełnij macierz ryzyka. Aplikacja porządkuje priorytety adaptacyjne "
    "na podstawie modelu: Ryzyko = Poziom zagrożenia/ryzyka (H-Hazard) × Ekspozycja (E) × Wrażliwość (V) (skala 1–5)."
)

st.divider()

def risk_level(score: int) -> str:
    if score <= 20:
        return "Niskie"
    if score <= 50:
        return "Umiarkowane"
    if score <= 80:
        return "Wysokie"
    return "Bardzo wysokie"

def action_suggestions(key: str):
    base = {
        "UHI": [
            "Zwiększenie zieleni wysokiej (drzewa) i zacienienia",
            "Rozszczelnianie powierzchni + ogrody deszczowe / nawierzchnie przepuszczalne",
            "Błękitno-zielona infrastruktura (mikroretencja, woda w mieście)",
            "Materiały o wyższym albedo / ograniczenie nagrzewania nawierzchni",
            "Ochrona korytarzy przewietrzania"
        ],
        "FLOOD": [
            "Mała/średnia retencja (zbiorniki/poldery) + spowalnianie odpływu",
            "Ochrona terenów zalewowych i renaturyzacja cieków",
            "Rozszczelnianie + infiltracja (SUDS)",
            "Udrożnienie przepustów i likwidacja wąskich gardeł hydraulicznych",
            "Ograniczenie zabudowy w strefach ryzyka (planowanie przestrzenne)"
        ],
        "DROUGHT": [
            "Zwiększenie retencji i magazynowania wody (także opadowej)",
            "Ograniczanie szybkiego odpływu + poprawa infiltracji",
            "Zwiększenie odporności zieleni (dobór gatunków, podlewanie celowane)",
            "Ponowne wykorzystanie wód opadowych (zbieranie/wykorzystanie)",
            "Ochrona gleb i ograniczenie degradacji"
        ],
        "AIR": [
            "Redukcja emisji lokalnych (transport/ogrzewanie) – działania organizacyjne",
            "Zielone korytarze i przewietrzanie (urbanistyka, ograniczanie kanionów ulicznych)",
            "Strefy niskiej emisji / uspokojenie ruchu",
            "Monitoring i alerty zdrowotne + komunikacja ryzyka",
            "Zwiększenie zieleni o funkcji filtracyjnej (tam, gdzie to ma sens urbanistyczny)"
        ]
    }
    return base.get(key, ["Działanie adaptacyjne (ogólne)"])

# -----------------------------
# Sidebar: temat projektu
# -----------------------------
st.sidebar.header("Ustawienia projektu")

project_topic = st.sidebar.selectbox(
    "Wybierz temat projektu",
    [
        "Systemy miejskiej retencji wody (inteligentne)",
        "Rozbudowa infrastruktury przeciwpowodziowej i systemów retencji wodnej",
        "Poprawa jakości powietrza w Krakowie"
    ]
)

project_name = st.sidebar.text_input("Nazwa projektu/obszaru (opcjonalnie)", value="Mój projekt")
area_type = st.sidebar.radio(
    "Typ obszaru",
    ["Miasto / centrum", "Obszar podmiejski", "Zlewnia / dolina rzeczna", "Inny"],
    index=0
)

st.sidebar.subheader("Zagrożenia do oceny")
haz_uhi = st.sidebar.checkbox("Upał / UHI", value=True)
haz_flood = st.sidebar.checkbox("Powódź / podtopienia", value=True)
haz_drought = st.sidebar.checkbox("Susza / deficyt wody", value=True)

# Dodatkowe zagrożenie tylko dla tematu jakości powietrza
haz_air = False
if project_topic == "Poprawa jakości powietrza w Krakowie":
    haz_air = st.sidebar.checkbox("Epizody jakości powietrza (smog)", value=True)

if not any([haz_uhi, haz_flood, haz_drought, haz_air]):
    st.warning("Zaznacz przynajmniej jedno zagrożenie w panelu po lewej.")
    st.stop()

st.sidebar.divider()

# -----------------------------
# Tematyczne podpowiedzi H/E/V
# -----------------------------
topic_hints = {
    "Systemy miejskiej retencji wody (inteligentne)": {
        "UHI": "UHI nie jest głównym celem, ale może wpływać na zużycie wody i komfort. Zwróć uwagę na uszczelnienie i brak zieleni.",
        "FLOOD": "Hazard: nawalne opady / przeciążenia kanalizacji. Ekspozycja: infrastruktura, budynki. Wrażliwość: brak retencji i sterowania.",
        "DROUGHT": "Hazard: dłuższe okresy bezopadowe. Ekspozycja: zieleń, gospodarka wodna. Wrażliwość: brak magazynowania i efektywnego zarządzania.",
        "AIR": ""
    },
    "Rozbudowa infrastruktury przeciwpowodziowej i systemów retencji wodnej": {
        "UHI": "UHI może być wątkiem pobocznym (zależny od zieleni i wody), ale priorytetem zwykle są zagrożenia hydrologiczne.",
        "FLOOD": "Hazard: wezbrania, opady ekstremalne. Ekspozycja: zabudowa w dolinach. Wrażliwość: wąskie gardła, brak przestrzeni dla wody.",
        "DROUGHT": "Hazard: deficyt opadów. Ekspozycja: użytkownicy wody. Wrażliwość: brak retencji, szybki odpływ, degradacja gleb.",
        "AIR": ""
    },
    "Poprawa jakości powietrza w Krakowie": {
        "UHI": "UHI wzmacnia stres cieplny i bywa powiązane ze stagnacją powietrza w zwartej zabudowie.",
        "FLOOD": "Powodzie są ważne, ale jeśli projekt jest stricte o powietrzu – oceń je tylko jeśli w obszarze mają znaczenie.",
        "DROUGHT": "Susza może wpływać na zieleń miejską i pylenie wtórne; oceń, jeśli widzisz związek z tematem.",
        "AIR": "Hazard: epizody smogowe/inwersje. Ekspozycja: gęsto zaludnione obszary i wrażliwe grupy. Wrażliwość: kaniony uliczne, emisje lokalne."
    }
}

# -----------------------------
# Main layout
# -----------------------------
left, right = st.columns([1.1, 1.0], gap="large")

with left:
    st.subheader("1) Wypełnij macierz ryzyka (H–E–V)")
    st.write(f"**Temat:** {project_topic}")
    st.write(f"**Projekt/obszar:** {project_name}  |  **Typ:** {area_type}")

    with st.expander("Skala 1–5 – krótkie przypomnienie"):
        st.markdown(
            """
- **1** – bardzo niskie  
- **2** – niskie  
- **3** – umiarkowane  
- **4** – wysokie  
- **5** – bardzo wysokie
            """
        )

    results = []

    def add_block(title, key):
        st.markdown(f"### {title}")
        hint = topic_hints[project_topic].get(key, "")
        if hint:
            st.caption(hint)

        H = st.slider(f"Hazard (H) – {title}", 1, 5, 3, key=f"H_{key}")
        E = st.slider(f"Ekspozycja (E) – {title}", 1, 5, 3, key=f"E_{key}")
        V = st.slider(f"Wrażliwość (V) – {title}", 1, 5, 3, key=f"V_{key}")
        score = int(H * E * V)
        results.append((title, H, E, V, score, risk_level(score), key))
        st.divider()

    if haz_uhi:
        add_block("🌡️ Upał / UHI (miejska wyspa ciepła)", "UHI")
    if haz_flood:
        add_block("🌧️ Powódź / podtopienia", "FLOOD")
    if haz_drought:
        add_block("🌿 Susza / deficyt wody", "DROUGHT")
    if haz_air:
        add_block("🌫️ Epizody jakości powietrza (smog)", "AIR")

with right:
    st.subheader("2) Wyniki, ranking i rekomendacje")
    df = pd.DataFrame(results, columns=["Zagrożenie", "H", "E", "V", "Ryzyko (H×E×V)", "Poziom", "Key"])
    df_sorted = df.sort_values(by="Ryzyko (H×E×V)", ascending=False).reset_index(drop=True)

    st.dataframe(df_sorted.drop(columns=["Key"]), use_container_width=True, hide_index=True)

    st.markdown("#### Ranking priorytetów adaptacji")
    top = df_sorted.iloc[0]
    st.success(f"Najwyższy priorytet: **{top['Zagrożenie']}** | Ryzyko: {int(top['Ryzyko (H×E×V)'])} | Poziom: {top['Poziom']}")

    if len(df_sorted) > 1:
        st.info(f"Drugi priorytet: **{df_sorted.iloc[1]['Zagrożenie']}** (Ryzyko: {int(df_sorted.iloc[1]['Ryzyko (H×E×V)'])})")
    if len(df_sorted) > 2:
        st.info(f"Trzeci priorytet: **{df_sorted.iloc[2]['Zagrożenie']}** (Ryzyko: {int(df_sorted.iloc[2]['Ryzyko (H×E×V)'])})")

    st.markdown("#### Porównanie ryzyk")
    chart_df = df_sorted[["Zagrożenie", "Ryzyko (H×E×V)"]].set_index("Zagrożenie")
    st.bar_chart(chart_df)

    st.divider()

    st.subheader("3) Działanie adaptacyjne dla najwyższego priorytetu")
    key_top = top["Key"]
    suggestions = action_suggestions(key_top)
    action = st.selectbox("Wybierz przykładowe działanie", suggestions)

    # Dodatkowe pole specyficzne dla inteligentnej retencji
    if project_topic == "Systemy miejskiej retencji wody (inteligentne)":
        st.markdown("**Opcjonalnie: sposób sterowania**")
        control = st.radio(
            "Które podejście wybierasz jako bardziej realistyczne dla Twojego projektu?",
            ["Proste reguły (IF-THEN)", "Model predykcyjny / ML", "Hybrydowe (reguły + predykcja)"],
            index=2
        )
        st.caption("W refleksji w UPeL możesz krótko uzasadnić wybór pod kątem niezawodności i wdrożenia.")

    justification = st.text_area("Uzasadnij w 1 zdaniu", height=90)

    st.caption(
        "Aplikacja nie zapisuje danych. Przepisz wartości H/E/V i wynikowy ranking do formularza w UPeL."

    )

