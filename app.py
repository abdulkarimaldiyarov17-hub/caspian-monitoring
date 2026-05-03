import streamlit as st
import google.generativeai as genai
import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression
import plotly.graph_objects as go
from openai import OpenAI
import base64

def get_base64(file_path):
    with open(file_path, "rb") as f:
        return base64.b64encode(f.read()).decode()

img = get_base64("bg.jpg")

# --- 1. БЕТ ЖӘНЕ ЖИ БАПТАУ ---
st.set_page_config(page_title="Caspian Navigation", layout="wide", page_icon="🌊")


# API кілтін Streamlit-тің жасырын баптауларынан (Secrets) алу
if "GOOGLE_API_KEY" in st.secrets:
    GOOGLE_API_KEY = st.secrets["GOOGLE_API_KEY"]
    genai.configure(api_key=GOOGLE_API_KEY)
else:
    st.error("API кілті табылмады. Streamlit Cloud Settings бөлімін тексеріңіз.")

# --- 2. ДИЗАЙН (CSS) ---

st.markdown(f"""
    <style>
    [data-testid="stAppViewContainer"] {{
        background-image: linear-gradient(rgba(0,0,0,0.4), rgba(0,0,0,0.4)),
                          url("data:image/jpg;base64,{img}");
        background-size: cover;
        background-position: center;
        background-attachment: fixed;
        background-repeat: no-repeat;
    }}

    [data-testid="stSidebar"] {{
        background-color: rgba(0,0,0,0.7);
    }}

    h1, h2, h3, p, span, label, div {{
        color: white !important;
    }}
    </style>
""", unsafe_allow_html=True)

# --- 3. НАВИГАЦИЯ (SOL JYK MENU) ---
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/826/826070.png", width=100)
    st.title("CASPIAN NAV")
    st.markdown("---")

    # Мәзір таңдау
    menu = st.radio(
        "Бөлімді таңдаңыз:",
        ["🏠 Басты бет", "📊 Аналитика", "🗺️ Карта", "🔮 Прогноз", "⚠️ Қауіпті аймақтар", "⚙️ Баптаулар"],
        index=0
    )
    st.markdown("---")
    st.info("Ақтау қаласы бойынша Каспий теңізінің мониторингі")

# --- 4. ДЕРЕКТЕРДІ ДАЙЫНДАУ ---
years = np.array([2010, 2015, 2020, 2024]).reshape(-1, 1)
levels = np.array([-28.4, -29.1, -29.9, -30.8])
lin_model = LinearRegression().fit(years, levels)

# --- 5. БӨЛІМДЕР ФУНКЦИЯСЫ ---

# 1. БАСТЫ БЕТ
if menu == "🏠 Басты бет":
    st.markdown("""
        <div style="text-align: center; padding: 20px 0px;">
            <h1 style="color: white; font-size: 42px; font-weight: 800; text-transform: uppercase; letter-spacing: 2px; text-shadow: 2px 2px 10px rgba(0, 86, 179, 0.8);">
                Ақтау: Каспий мониторинг
            </h1>
            <p style="color: #00b4db; font-size: 18px; font-weight: 500;">
                Нақты уақыт режиміндегі теңіз деңгейінің аналитикалық жүйесі
            </p>
        </div>
    """, unsafe_allow_html=True)

    # 1. KPI КАРТОЧКАЛАРЫ
    kpi1, kpi2, kpi3, kpi4 = st.columns(4)
    kpi1.metric("Су деңгейі", "-30.82 м")
    kpi2.metric("Температура", "24°C")
    kpi3.metric("Қауіп", "Жоғары", delta_color="inverse")
    kpi4.metric("Жыл", "2026")

    st.markdown("---")
    col_graph, col_info = st.columns([2, 1])

    with col_graph:
        # Графикке арналған деректер
        x = np.linspace(0, 200, 50)
        y = np.linspace(0, 100, 50)
        X, Y = np.meshgrid(x, y)
        Z_land = -0.1 * X - 26
        Z_water = np.full_like(X, -30.8)

        # --- ТЕРЕҢДІК ПЕН ТРЕНДТІ КӨРСЕТЕТІН ЖАҢАРТЫЛҒАН ГРАФИК ---
        fig_hero = go.Figure()

        # 1. Жағалау (Құмды рельеф)
        fig_hero.add_trace(go.Surface(
            z=Z_land, x=X, y=Y, 
            colorscale=[[0, '#C2B280'], [1, '#EDC9AF']], 
            showscale=False, name="Рельеф"
        ))

        # 2. Тегіс су беті
        fig_hero.add_trace(go.Surface(
            z=Z_water, x=X, y=Y, 
            colorscale='Blues', 
            showscale=False, opacity=0.6, name="Ағымдағы деңгей"
        ))

        # 3. ТӨМЕНДЕУ ТРЕНДІ (Динамикалық көрсеткіш - Сарғыш бағыттауыш)
        fig_hero.add_trace(go.Scatter3d(
            x=np.linspace(10, 100, 10), 
            y=[50]*10, 
            z=np.linspace(-27, -33, 10),
            mode='lines+markers',
            line=dict(color='orange', width=7),
            marker=dict(size=4, color='white'),
            name="Төмендеу тренді"
        ))

        # 4. ТЕРЕҢДІК ДЕҢГЕЙЛЕРІ (Инженерлік белгілер)
        # 2010 жылғы жағалау сызығы
        fig_hero.add_trace(go.Scatter3d(
            x=[10]*100, y=y, z=[-27]*100,
            mode='lines', line=dict(color='cyan', width=5), name="2010 деңгейі (-27м)"
        ))
        
        # Қазіргі деңгей белгісі
        fig_hero.add_trace(go.Scatter3d(
            x=[48]*100, y=y, z=[-30.8]*100,
            mode='lines', line=dict(color='red', width=5), name="Қазіргі деңгей (-30.8м)"
        ))

        # 2030 болжамды деңгейі (Пунктир сызық)
        fig_hero.add_trace(go.Scatter3d(
            x=[80]*100, y=y, z=[-32.5]*100,
            mode='lines', line=dict(color='gray', width=3, dash='dash'), name="2030 болжам"
        ))

        # Пальмалар (Жағалауда)
        for px, py in [(5, 20), (5, 50), (5, 80)]:
            fig_hero.add_trace(go.Scatter3d(
                x=[px, px], y=[py, py], z=[-26, -21],
                mode='lines', line=dict(color='#5d4037', width=8), showlegend=False
            ))

        fig_hero.update_layout(
            height=600,
            margin=dict(l=0, r=0, b=0, t=0),
            paper_bgcolor='rgba(0,0,0,0)',
            scene=dict(
                aspectratio=dict(x=1.8, y=1, z=0.6),
                xaxis=dict(title="Шегіну қашықтығы", showgrid=True, gridcolor='rgba(255,255,255,0.1)'),
                yaxis=dict(visible=False),
                zaxis=dict(title="Тереңдік (м)", range=[-35, -20], gridcolor='rgba(255,255,255,0.1)'),
                camera=dict(eye=dict(x=1.5, y=1.2, z=0.8))
            )
        )
        st.plotly_chart(fig_hero, use_container_width=True, key="trend_depth_3d")
        
# 2. АНАЛИТИКА

elif menu == "📊 Аналитика":
    st.header("📊 Каспий теңізінің тереңдетілген аналитикасы")
    
    # --- 1. ЖЫЛДАМ ЕСЕПТЕУЛЕР (Real-time Indicators) ---
    st.subheader("⚡ 1. Жылдам көрсеткіштер")
    m1, m2, m3 = st.columns(3)
    with m1:
        st.metric("Күндік өзгеріс", "-0.2 см", "🔻 Төмендеу")
    with m2:
        st.metric("Апталық динамика", "-1.5 см", "🔻 Төмендеу", delta_color="inverse")
    with m3:
        st.metric("Айлық болжамды булану", "120 мм", "🔺 Жоғары")

    st.markdown("---")

    # --- 2. ТРЕНД АНАЛИЗ (Time Series Analysis) ---
    st.subheader("📈 2. Тренд және циклдік талдау")
    col_chart, col_desc = st.columns([2, 1])
    
    # Жасанды деректер (Тренд үшін)
    trend_data = pd.DataFrame({
        'Айлар': ['Қаңтар', 'Ақпан', 'Наурыз', 'Сәуір', 'Мамыр', 'Маусым'],
        'Деңгей (м)': [-30.5, -30.55, -30.62, -30.70, -30.85, -31.00],
        'Булану деңгейі': [20, 25, 45, 70, 110, 150]
    })
    
    with col_chart:
        st.line_chart(trend_data.set_index('Айлар')['Деңгей (м)'])
    
    with col_desc:
        st.info("""
        **Талдау:**
        Соңғы 6 айда су деңгейінің маусымдық төмендеуі байқалады. 
        Маусым айында температураның көтерілуіне байланысты булану қарқыны 30%-ға артқан.
        """)

    st.markdown("---")

    # --- 3. САЛЫСТЫРУ (Comparative Analysis) ---
    st.subheader("⚖️ 3. Тарихи салыстыру")
    compare_data = pd.DataFrame({
        'Көрсеткіш': ['1995 жыл (Пик)', '2010 жыл', '2024 жыл', '2030 (Прогноз)'],
        'Деңгей (м)': [-26.5, -28.4, -30.8, -31.5]
    })
    st.bar_chart(compare_data.set_index('Көрсеткіш'))
    st.caption("1995 жылғы ең жоғары деңгеймен салыстырғанда теңіз 4 метрден астамға төмендеген.")

    st.markdown("---")

    # --- 4. СЕБЕПТЕР МЕН ФАКТОРЛАР (Environmental Factors) ---
    st.subheader("🌪️ 4. Төмендеу себептерін талдау")
    
    f1, f2, f3 = st.columns(3)
    
    with f1:
        st.write("🌡️ **Температура әсері**")
        st.progress(85)
        st.write("Ауа температурасының нормадан 2°C жоғары болуы булануды тездетуде.")
        
    with f2:
        st.write("🌬️ **Жел және Ағыс**")
        st.progress(60)
        st.write("Солтүстік-шығыс желі суды оңтүстікке айдап, Ақтау жағалауын таяз қылуда.")
        
    with f3:
        st.write("💧 **Өзен ағысы (Еділ/Жайық)**")
        st.progress(40)
        st.write("Солтүстіктен келетін тұщы су көлемінің азаюы басты факторлардың бірі.")

    # Аналитикалық қорытынды
    st.success("""
    **Кешенді қорытынды:** Аналитика көрсеткендей, қазіргі төмендеу тек табиғи цикл емес, антропогендік және климаттық факторлардың жиынтығы. 
    Келесі 3 айда су деңгейі тағы 5-8 см-ге төмендеуі мүмкін.
    """)

# 3. КАРТА
elif menu == "🗺️ Карта":
    st.header("🗺️ Каспий жағалауы: Интерактивті Мониторинг Картасы")
    
    map_points = pd.DataFrame({
        'Аймақ атауы': [
            'МАЭК су тарту каналы', 'Приморский жағалауы', 
            '4-шағын аудан жағажайы', 'Жылы жағажай (Теплый пляж)', 
            'Сенсор станциясы №1', 'Сенсор станциясы №2'
        ],
        'lat': [43.6150, 43.6300, 43.6400, 43.5500, 43.6200, 43.5800],
        'lon': [51.1850, 51.1600, 51.1450, 51.2500, 51.1700, 51.2100],
        'Түрі': ['Қауіпті', 'Қауіпті', 'Орташа', 'Тұрақты', 'Сенсор', 'Сенсор'],
        'Түсі': ['#FF0000', '#FF0000', '#FFA500', '#00FF00', '#0071e3', '#0071e3']
    })

    fig_map = go.Figure()

    for index, row in map_points.iterrows():
        fig_map.add_trace(go.Scattermapbox(
            lat=[row['lat']],
            lon=[row['lon']],
            mode='markers+text',
            marker=go.scattermapbox.Marker(size=14, color=row['Түсі']),
            text=[row['Аймақ атауы']],
            name=row['Түрі']
        ))

    fig_map.update_layout(
        mapbox=dict(
            style="carto-darkmatter",
            center=dict(lat=43.60, lon=51.18),
            zoom=10
        ),
        margin=dict(l=0, r=0, b=0, t=0),
        height=600,
        showlegend=True,
        paper_bgcolor='rgba(0,0,0,0)',
    )

    col_map, col_info = st.columns([3, 1])
    
    with col_map:
        st.plotly_chart(fig_map, use_container_width=True, key="monitoring_map")

    with col_info:
        st.markdown("### 🔍 Карта аңызы")
        st.write("🔴 **Қауіпті:** Су тез шегініп жатқан және инфрақұрылымға зақым келуі мүмкін аймақтар.")
        st.write("🟢 **Тұрақты:** Рельефі терең, өзгерістер аз аймақтар.")
        st.write("🔵 **Сенсор:** Нақты уақыт режимінде деңгейді өлшейтін құрылғылар.")
        
        st.markdown("---")
        st.subheader("📏 Шегіну көрсеткіші")
        st.info("МАЭК аймағында судың шегінуі жылына 1.2 метрді құрайды.")

    st.markdown("### 📉 Жағалаудың нүктелер бойынша шегіну динамикасы")
    shiginu_data = pd.DataFrame({
        'Аймақ': ['МАЭК', 'Приморский', '4-мкр', 'Теплый пляж'],
        'Шегіну (метр)': [85, 120, 45, 30]
    })
    st.bar_chart(shiginu_data.set_index('Аймақ'))

# 4. ПРОГНОЗ
elif menu == "🔮 Прогноз":
    st.header("🔮 Каспий теңізін сақтау: 2025-2055 Жол картасы")
    
    target_year = st.slider("Болжам жылын таңдаңыз:", 2025, 2055, 2030, key="prognoz_slider")
    pred_level = lin_model.predict([[target_year]])[0]
    
    col_metric1, col_metric2 = st.columns(2)
    with col_metric1:
        st.metric(f"{target_year} жылғы деңгей", f"{pred_level:.2f} м")
    with col_metric2:
        recession = (pred_level - (-27)) / (-0.08)
        st.metric("Болжамды шегіну", f"{recession:.0f} метр")

    st.markdown("---")
    st.subheader("📅 Онжылдық іс-қимыл жоспары (Күнтізбелік кесте)")

    tab1, tab2, tab3 = st.tabs(["2025-2035 жылдар", "2035-2045 жылдар", "2045-2055 жылдар"])

    with tab1:
        st.markdown("""
        ### 🏗️ Шұғыл инженерлік кезең
        * **2026-2028:** Ақтау қаласындағы барлық су тарту каналдарын 3.5 метрге тереңдету.
        * **2030:** МАЭК-тің жаңа деңгейге бейімделген автономды су алу қондырғыларын іске қосу.
        * **2032:** Жағалау бойындағы "Пальма" және демалыс аймақтарын жаңа жағалау сызығына көшіру.
        """)
        st.info("💡 **Шешім:** Суды үнемдеу технологияларын енгізу және жағалауды нығайту.")

    with tab2:
        st.markdown("""
        ### 🌊 Экологиялық бейімделу кезеңі
        * **2036:** Теңіз түбін тереңдететін ірі халықаралық флотилияны тұрақты жұмысқа қосу.
        * **2040:** Ақтау айналасында су ресурстарын сақтайтын жасанды бөгеттер мен дамбалар жүйесін құру.
        * **2042:** Каспий маңы елдерімен бірлескен "Транскаспий су тасымалы" жобасын бастау.
        """)
        st.warning("⚠️ **Қауіп:** Су деңгейі -32 метрден төмен түсуі мүмкін.")

    with tab3:
        st.markdown("""
        ### 🌍 Глобалды қалпына келтіру кезеңі
        * **2046:** Еділ мен Жайық өзендерінің ағысын реттейтін цифрлық су бекеттерін толық іске қосу.
        * **2050:** Каспийді толтыру мақсатында солтүстік өзендерді бұру немесе Каналдар арқылы су әкелудің финалдық кезеңі.
        * **2055:** "Жасыл Ақтау" белдеуін жаңа жағалауда толық қалыптастыру.
        """)
        st.error("🚨 **Мақсат:** Теңіздің экожүйесін толық жойылудан сақтап қалу.")

    st.markdown("### 📈 Стратегиялық тиімділік графигі")
    timeline_data = pd.DataFrame({
        'Жыл': [2025, 2035, 2045, 2055],
        'Қажетті инвестиция (млрд $)': [1.2, 3.5, 7.8, 12.0],
        'Тиімділік (%)': [15, 45, 75, 95]
    })
    st.area_chart(timeline_data.set_index('Жыл'))

# 5. ҚАУІПТІ АЙМАҚТАР
elif menu == "⚠️ Қауіпті аймақтар":
    st.header("⚠️ Ақтау қаласы: Қауіпті аймақтар тізілімі")
    
    st.error("### 🔴 Жоғары қауіп (Судың шегінуі: 80-120м+)")
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("""
        **📍 Мекенжайы:** Приморский елді мекені, жағалау сызығы.
        * **Қауіп:** Жағалаудың батпақтануы, экожүйенің бұзылуы.
        * **Шешім:** Жағалауды жасанды түрде құммен толтыру, гидротехникалық бөгеттер салу.
        """)
    with col2:
        st.markdown("""
        **📍 Мекенжайы:** МАЭК су тарту каналдары (Индустриалды аймақ).
        * **Қауіп:** Қаланы сумен және токпен қамтамасыз етудің тоқтау қаупі.
        * **Шешім:** Канал түбін шұғыл тереңдету (кемінде 4 метр), насостарды жаңарту.
        """)

    st.warning("### 🟡 Орташа қауіп (Судың шегінуі: 40-70м)")
    col3, col4 = st.columns(2)
    with col3:
        st.markdown("""
        **📍 Мекенжайы:** 1-ші және 4-ші шағын аудандардың жағажайы.
        * **Қауіп:** Туристік нысандардың теңізден алшақтап қалуы.
        * **Шешім:** Пирстерді ұзарту, жағалау инфрақұрылымын қайта жоспарлау.
        """)
    with col4:
        st.markdown("""
        **📍 Мекенжайы:** "Сары құм" (Жылы жағажай аймағы).
        * **Қауіп:** Су астындағы тастардың бетке шығуы, шомылу қауіпсіздігі.
        * **Шешім:** Рельефті тегістеу, қауіпті аймақтарды белгілеу.
        """)

    st.markdown("---")
    
    st.subheader("🏃‍♂️ Тұрғындар мен кәсіпкерлерге арналған нұсқаулық")
    
    with st.expander("✅ Кәсіпкерлер үшін (Жағалаудағы бизнес)"):
        st.markdown("""
        1. **Инфрақұрылымды жылжыту:** Жағалаудағы жылжымалы нысандарды су деңгейіне қарай бейімдеу.
        2. **Қауіпсіздік:** Су қайтқан жерлердегі лай мен батпақты тазарту.
        3. **Инвестиция:** Ұзақ мерзімді пирстер мен понтонды айлақтарды қолдану.
        """)

    with st.expander("👨‍👩‍👧‍👦 Қала тұрғындары үшін"):
        st.markdown("""
        1. **Суды үнемдеу:** Қаладағы су тапшылығын болдырмау үшін күнделікті тұрмыста суды үнемді пайдалану.
        2. **Хабардар болу:** "Caspian Nav" сияқты мониторинг жүйелерін бақылап отыру.
        3. **Экологиялық еріктілік:** Жағалау тазалығына үлес қосу (су қайтқан жердегі қоқыстарды жинау).
        """)

    st.info("### 🛠️ Қауіптен шығудың мемлекеттік шешімі")
    st.success("""
    * **Тереңдету:** Ақтау теңіз порты мен МАЭК аумағында үздіксіз драглайн жұмыстарын жүргізу.
    * **Тұщыту:** Жағалауға тәуелділікті азайту үшін қосымша су тұщыту зауыттарын (Кәспий, Альцион) салу.
    * **Мониторинг:** Жағалаудың әр 500 метріне автоматты лазерлік деңгей өлшегіштер орнату.
    """)

# 6. БАПТАУЛАР
elif menu == "⚙️ Баптаулар":
    st.header("⚙️ Жүйе баптаулары")
    st.checkbox("Қараңғы режимді қосу", value=True)
    st.checkbox("Хабарламаларды жіберу")
    st.button("Деректерді жаңарту")
    st.write("Бағдарлама нұсқасы: 2.0.1 (Aktau Edition)")

# --- 6. ЧАТ-БОТ (БАРЛЫҚ БЕТТЕ КӨРІНЕДІ) ---
st.markdown("---")
with st.expander("🤖 ЖИ Көмекшімен сөйлесу"):
    if "msg" not in st.session_state: 
        st.session_state.msg = []
    
    # 1. Тарихты көрсету
    for m in st.session_state.msg: 
        with st.chat_message(m["role"]):
            st.write(m["content"])
    
    # 2. Пайдаланушы енгізуі
    if p := st.chat_input("Сұрақ қойыңыз..."):
        st.session_state.msg.append({"role": "user", "content": p})
        with st.chat_message("user"):
            st.write(p)
        
        # 3. ЖИ жауабын қауіпсіз алу
        with st.chat_message("assistant"):
            with st.spinner("Жауап дайындалуда..."):
                try:
                    response = client.chat.completions.create(
                        model="gpt-4o",
                        messages=[
                            {"role": "system", "content": "Сен Каспий теңізі және Ақтау қаласы бойынша сарапшысың. Барлық жауаптарыңды тек қазақ тілінде бер. Ешқашан орыс немесе ағылшын тілінде жауап берме."},
                            {"role": "user", "content": p}
                        ]
                    )
                    answer = response.choices[0].message.content
                    if answer:
                        st.write(answer)
                        st.session_state.msg.append({"role": "assistant", "content": answer})
                    else:
                        st.warning("ЖИ жауап беруден бас тартты немесе жауап бос.")
                except Exception as e:
                    st.error(f"Қате орын алды: {e}")
