import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import math
import copy

# Page configuration
st.set_page_config(
    page_title="TW Defense Calculator",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Custom CSS for Modern Dark Dashboard
st.markdown("""
<style>
    .block-container { padding-top: 4rem; padding-bottom: 2rem; max-width: 1400px; }
    
    /* Clean headers */
    h1, h2, h3 { font-family: 'Inter', sans-serif; font-weight: 600; color: #f8fafc; margin-bottom: 0.5rem; }
    .main-title { font-size: 2rem; border-bottom: 1px solid #334155; padding-bottom: 10px; margin-bottom: 30px; margin-top: 10px; }
    .subtitle { color: #94a3b8; font-size: 0.95rem; font-weight: 400; margin-bottom: 30px; }
    
    div[data-testid="stMetricValue"] { font-size: 1.8rem; font-weight: 700; color: #f43f5e; }
    div[data-testid="stMetricLabel"] { font-size: 0.85rem; color: #94a3b8; font-weight: 500; text-transform: uppercase; letter-spacing: 0.05em; }
    
    .stDataFrame { border-radius: 8px; overflow: hidden; border: 1px solid #334155 !important; }
    
    .unit-img { display: block; margin-left: auto; margin-right: auto; margin-bottom: 5px; opacity: 0.9; }
    .unit-img:hover { opacity: 1; transform: scale(1.1); transition: 0.2s ease-in-out; }
    .row-label { font-size: 0.9rem; font-weight: 600; color: #cbd5e1; text-transform: uppercase; letter-spacing: 0.05em; margin-top: 8px; }
    
    input[type=number]::-webkit-inner-spin-button, 
    input[type=number]::-webkit-outer-spin-button { -webkit-appearance: none; margin: 0; }
    input[type=number] { -moz-appearance: textfield; }
    
    hr { border-color: #334155; margin: 30px 0; }
</style>
""", unsafe_allow_html=True)

UNIDADES = [
    ('lanceiro', 'Lanceiro', 'https://dsbr.innogamescdn.com/asset/1d2499b/graphic/unit/unit_spear.png', {'atk': 10, 'def_inf': 15, 'def_cav': 45, 'def_arq': 20, 'tipo_atk': 'inf', 'pop': 1}),
    ('espadachim', 'Espadachim', 'https://dsbr.innogamescdn.com/asset/1d2499b/graphic/unit/unit_sword.png', {'atk': 25, 'def_inf': 50, 'def_cav': 15, 'def_arq': 40, 'tipo_atk': 'inf', 'pop': 1}),
    ('barbaro', 'Bárbaro', 'https://dsbr.innogamescdn.com/asset/1d2499b/graphic/unit/unit_axe.png', {'atk': 40, 'def_inf': 10, 'def_cav': 5, 'def_arq': 10, 'tipo_atk': 'inf', 'pop': 1}),
    ('arqueiro', 'Arqueiro', 'https://dsbr.innogamescdn.com/asset/1d2499b/graphic/unit/unit_archer.png', {'atk': 15, 'def_inf': 50, 'def_cav': 40, 'def_arq': 5, 'tipo_atk': 'arq', 'pop': 1}),
    ('cavalaria_leve', 'Cavalaria Leve', 'https://dsbr.innogamescdn.com/asset/1d2499b/graphic/unit/unit_light.png', {'atk': 130, 'def_inf': 30, 'def_cav': 40, 'def_arq': 30, 'tipo_atk': 'cav', 'pop': 4}),
    ('arqueiro_cavalo', 'Arq. a Cavalo', 'https://dsbr.innogamescdn.com/asset/1d2499b/graphic/unit/unit_marcher.png', {'atk': 120, 'def_inf': 40, 'def_cav': 30, 'def_arq': 50, 'tipo_atk': 'arq', 'pop': 5}),
    ('cavalaria_pesada', 'Cav. Pesada', 'https://dsbr.innogamescdn.com/asset/1d2499b/graphic/unit/unit_heavy.png', {'atk': 150, 'def_inf': 200, 'def_cav': 80, 'def_arq': 180, 'tipo_atk': 'cav', 'pop': 6}),
    ('ariete', 'Aríete', 'https://dsbr.innogamescdn.com/asset/1d2499b/graphic/unit/unit_ram.png', {'atk': 2, 'def_inf': 20, 'def_cav': 50, 'def_arq': 20, 'tipo_atk': 'inf', 'pop': 5}),
    ('catapulta', 'Catapulta', 'https://dsbr.innogamescdn.com/asset/1d2499b/graphic/unit/unit_catapult.png', {'atk': 100, 'def_inf': 100, 'def_cav': 50, 'def_arq': 100, 'tipo_atk': 'inf', 'pop': 8}),
    ('milicia', 'Milícia', 'https://dsbr.innogamescdn.com/asset/1d2499b/graphic/unit/unit_militia.png', {'atk': 5, 'def_inf': 15, 'def_cav': 45, 'def_arq': 25, 'tipo_atk': 'inf', 'pop': 0})
]
UNIDADES_DICT = {u[0]: u[3] for u in UNIDADES}

def get_populacao(tropa_dict):
    return sum((qtd or 0) * UNIDADES_DICT[u]['pop'] for u, qtd in tropa_dict.items() if u in UNIDADES_DICT)

def calcular_reducao_muralha(arietes, muralha_atual):
    if muralha_atual <= 0 or not arietes or arietes <= 0: return 0
    return arietes / 21.5

def simular_combate(atacante, defensor, muralha=20, sorte=0.0, fe_ataque=True, fe_defesa=True, bonus_noturno=0.0):
    atk_inf = atk_cav = atk_arq = 0
    for unidade, qtd in atacante.items():
        if unidade in UNIDADES_DICT and qtd:
            poder = qtd * UNIDADES_DICT[unidade]['atk']
            tipo = UNIDADES_DICT[unidade]['tipo_atk']
            if tipo == 'inf': atk_inf += poder
            elif tipo == 'cav': atk_cav += poder
            elif tipo == 'arq': atk_arq += poder
            
    atk_total = atk_inf + atk_cav + atk_arq
    if atk_total == 0: return {"erro": "Nenhuma tropa atacante."}

    atk_total = atk_total * (1 + (sorte / 100.0))
    if not fe_ataque:
        atk_total *= 0.5

    atk_base = atk_total / (1 + (sorte / 100.0)) if not fe_ataque else atk_total
    prop_inf = atk_inf / atk_base if atk_base > 0 else 0
    prop_cav = atk_cav / atk_base if atk_base > 0 else 0
    prop_arq = atk_arq / atk_base if atk_base > 0 else 0

    def_inf_total = def_cav_total = def_arq_total = 0
    for unidade, qtd in defensor.items():
        if unidade in UNIDADES_DICT and qtd:
            def_inf_total += qtd * UNIDADES_DICT[unidade]['def_inf']
            def_cav_total += qtd * UNIDADES_DICT[unidade]['def_cav']
            def_arq_total += qtd * UNIDADES_DICT[unidade]['def_arq']

    def_efetiva = (def_inf_total * prop_inf) + (def_cav_total * prop_cav) + (def_arq_total * prop_arq)
    
    # Aplica bonus noturno na defesa efetiva (tropas)
    if bonus_noturno > 0:
        def_efetiva *= (1 + (bonus_noturno / 100.0))
        
    arietes = atacante.get('ariete', 0)
    base_drop = calcular_reducao_muralha(arietes, muralha)
    queda_combate = min(muralha / 2.0, base_drop)
    
    muralha_combate = max(0, int(round(muralha - queda_combate)))
    defesa_base_aldeia = 50 + (50 * muralha_combate)
    bonus_muralha = 1.037 ** muralha_combate
    
    def_total = (def_efetiva * bonus_muralha) + defesa_base_aldeia
    
    if not fe_defesa:
        def_total *= 0.5

    vencedor = "Defensor" if def_total > atk_total else "Atacante"
    
    if vencedor == "Defensor":
        perdas_atacante_pct = 1.0
        perdas_defensor_pct = (atk_total / def_total) ** 1.5 if def_total > 0 else 0
        queda_final = min(muralha, int(round(base_drop * perdas_defensor_pct)))
    else:
        perdas_defensor_pct = 1.0
        perdas_atacante_pct = (def_total / atk_total) ** 1.5 if atk_total > 0 else 0
        queda_final = min(muralha, int(round(base_drop)))

    perdas_atacante_pct = min(1.0, perdas_atacante_pct)
    perdas_defensor_pct = min(1.0, perdas_defensor_pct)

    relatorio = {'vencedor': vencedor, 'perdas_atacante': {}, 'perdas_defensor': {}}

    for unidade, qtd in atacante.items():
        if qtd:
            relatorio['perdas_atacante'][unidade] = {'enviados': qtd, 'restantes': qtd - round(qtd * perdas_atacante_pct)}
    for unidade, qtd in defensor.items():
        if qtd:
            relatorio['perdas_defensor'][unidade] = {'enviados': qtd, 'restantes': qtd - round(qtd * perdas_defensor_pct)}

    relatorio['muralha_restante'] = max(0, muralha - queda_final)
    return relatorio


def simular_cenario(ataque_base, defesa_base, qtd_fulls, muralha_inicial, sorte_ondas, limit=200, fe_ataque=True, fe_defesa=True, bn=0.0):
    defesa_atual = {k: round((v or 0) * qtd_fulls) for k, v in defesa_base.items()}
    populacao_inicial = get_populacao(defesa_atual)
    
    muralha_atual = muralha_inicial
    onda_atual = 0
    dados = [{
        "Onda": 0, "População Restante": populacao_inicial, 
        "Nível Muralha": muralha_atual, "Capacidade Restante": 100.0
    }]
    
    while True:
        onda_atual += 1
        res = simular_combate(ataque_base, defesa_atual, muralha_atual, sorte_ondas, fe_ataque, fe_defesa, bn)
        
        for u, stats in res['perdas_defensor'].items():
            defesa_atual[u] = stats['restantes']
            
        muralha_atual = res['muralha_restante']
        pop_restante = get_populacao(defesa_atual)
        cap_restante = (pop_restante / populacao_inicial) * 100 if populacao_inicial > 0 else 0
        
        dados.append({
            "Onda": onda_atual, "População Restante": pop_restante,
            "Nível Muralha": muralha_atual, "Capacidade Restante": cap_restante
        })
        
        if res['vencedor'] == 'Atacante' or pop_restante <= 0 or onda_atual >= limit:
            break
            
    return onda_atual, muralha_atual, populacao_inicial, dados


st.markdown("<div class='main-title'>🛡️ Calculadora de Defesa</div>", unsafe_allow_html=True)
st.markdown("<div class='subtitle'>Configure os templates de ataque e defesa para simular cenários de resistência em massa.</div>", unsafe_allow_html=True)

if 'init_done' not in st.session_state:
    st.session_state['init_done'] = True
    default_atk = {'barbaro': 6000, 'cavalaria_leve': 3000, 'ariete': 300}
    default_def = {'lanceiro': 10000, 'espadachim': 10000}
    query_params = st.query_params
    
    # Verifica se estamos recebendo uma exportação da URL
    is_import = any(key.startswith('def_') for key in query_params.keys())
    
    for k in [u[0] for u in UNIDADES]:
        st.session_state[f'atk_{k}'] = default_atk.get(k, None)
        
        # Lê os parâmetros da URL para a defesa, caso existam
        if f'def_{k}' in query_params:
            try:
                st.session_state[f'def_{k}'] = int(query_params[f'def_{k}'])
            except ValueError:
                st.session_state[f'def_{k}'] = None if is_import else default_def.get(k, None)
        else:
            # Se for importação e não veio essa tropa, zera (None). Senão, usa padrão.
            st.session_state[f'def_{k}'] = None if is_import else default_def.get(k, None)

def limpar_tropas():
    for k in [u[0] for u in UNIDADES]:
        st.session_state[f'atk_{k}'] = None
        st.session_state[f'def_{k}'] = None

with st.container():
    cols = st.columns([1.5] + [1]*len(UNIDADES) + [0.5])
    cols[0].button("🗑️ Limpar", on_click=limpar_tropas, help="Zerar tropas")
    for i, (key, nome, img, _) in enumerate(UNIDADES):
        with cols[i+1]: st.markdown(f'<img src="{img}" title="{nome}" class="unit-img">', unsafe_allow_html=True)
    
    padrao_atk, padrao_def = {}, {}
    
    cols_atk = st.columns([1.5] + [1]*len(UNIDADES) + [0.5])
    with cols_atk[0]: st.markdown("<div class='row-label'>Padrão Ataque</div>", unsafe_allow_html=True)
    for i, (key, nome, _, _) in enumerate(UNIDADES):
        with cols_atk[i+1]:
            padrao_atk[key] = st.number_input(f"atk_{key}", value=None, min_value=0, step=50, placeholder="0", label_visibility="collapsed", disabled=(key=='milicia'), key=f"atk_{key}")
            
    st.markdown("<div style='height: 10px'></div>", unsafe_allow_html=True)
            
    cols_def = st.columns([1.5] + [1]*len(UNIDADES) + [0.5])
    with cols_def[0]: st.markdown("<div class='row-label'>Padrão Defesa</div>", unsafe_allow_html=True)
    for i, (key, nome, _, _) in enumerate(UNIDADES):
        with cols_def[i+1]:
            padrao_def[key] = st.number_input(f"def_{key}", value=None, min_value=0, step=50, placeholder="0", label_visibility="collapsed", key=f"def_{key}")

st.markdown("<hr>", unsafe_allow_html=True)

c1, c2, c3, c4 = st.columns(4)
with c1: 
    qtd_fulls_def = st.number_input("Multiplicar a defesa em", min_value=0.1, max_value=100.0, value=1.0, step=0.5)
with c2: 
    muralha_inicial = st.number_input("Nível da Muralha Inicial", min_value=0, max_value=20, value=20, step=1)
with c3: 
    sorte_ondas = st.slider("Sorte (%)", -25.0, 25.0, 0.0, 0.1)
with c4:
    fe_ataque = st.checkbox("Fé do Ataque (100%)", value=True)
    fe_defesa = st.checkbox("Fé da Defesa (100%)", value=True)

c5, c6, c7, c8 = st.columns(4)
with c5:
    is_night_bonus = st.toggle("Bônus Noturno", value=False)
with c6:
    bn_pct = st.number_input("Bônus Noturno (%)", min_value=0, value=300, step=10, disabled=not is_night_bonus)
with c8:
    st.markdown("<br>", unsafe_allow_html=True)
    simular_btn = st.button("Simular Cenário", use_container_width=True, type="primary")

if simular_btn:
    ataque_base = {k: (v or 0) for k, v in padrao_atk.items()}
    defesa_base = {k: (v or 0) for k, v in padrao_def.items()}
    
    if sum(ataque_base.values()) == 0 or sum(defesa_base.values()) == 0:
        st.error("Configure tropas para o ataque e para a defesa.")
    else:
        st.markdown("<hr>", unsafe_allow_html=True)
        bn_val = bn_pct if is_night_bonus else 0.0
        ondas, mur_final, pop_inicial, dados = simular_cenario(ataque_base, defesa_base, qtd_fulls_def, muralha_inicial, sorte_ondas, 200, fe_ataque, fe_defesa, bn_val)
        
        mur_pos_primeiro = dados[1]["Nível Muralha"] if len(dados) > 1 else muralha_inicial
        
        m1, m2, m3 = st.columns(3)
        with m1: st.metric("População Total", f"{pop_inicial:,.0f}".replace(',','.'))
        with m2: st.metric("Ataques Suportados", f"{ondas}")
        with m3: st.metric("Muralha Após 1º Ataque", f"Nível {mur_pos_primeiro}")
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        df_grafico = pd.DataFrame(dados)
        df_grafico["Capacidade Restante"] = df_grafico["Capacidade Restante"].apply(lambda x: f"{x:.1f}%")
        
        from plotly.subplots import make_subplots
        
        fig = make_subplots(specs=[[{"secondary_y": True}]])
        fig.add_trace(
            go.Scatter(x=df_grafico["Onda"], y=df_grafico["População Restante"], name="População",
                       line=dict(color="#f43f5e", width=3), mode='lines+markers', marker=dict(size=8, color="#f43f5e")),
            secondary_y=False,
        )
        fig.add_trace(
            go.Scatter(x=df_grafico["Onda"], y=df_grafico["Nível Muralha"], name="Muralha",
                       line=dict(color="#eab308", width=3, dash='dot'), mode='lines+markers', marker=dict(size=8, color="#eab308")),
            secondary_y=True,
        )
        fig.update_layout(
            title="Curva de Resistência da Aldeia",
            plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)', font=dict(color='#f8fafc'),
            xaxis=dict(showgrid=False, color='#94a3b8'),
            margin=dict(l=0, r=0, t=40, b=0),
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
        )
        fig.update_yaxes(title_text="População Restante", showgrid=True, gridcolor='#334155', color='#f43f5e', secondary_y=False)
        fig.update_yaxes(title_text="Nível Muralha", showgrid=False, color='#eab308', range=[0, 20], secondary_y=True)
        st.plotly_chart(fig, use_container_width=True)
        
        with st.expander("Ver Detalhes por Ataques"):
            st.dataframe(df_grafico, use_container_width=True, hide_index=True)
            
        st.markdown("<hr>", unsafe_allow_html=True)
        
        st.markdown("### 📈 Análise de Escalabilidade (Sweet Spot)")
        st.markdown("<div class='subtitle'>Quantos ataques você suportaria se hospedasse diferentes volumes de fulls?</div>", unsafe_allow_html=True)
        
        fulls_to_test = [1, 2, 3, 4, 5, 6, 8, 10, 15]
        sweet_data = []
        for f in fulls_to_test:
            ondas_f, _, pop_f, _ = simular_cenario(ataque_base, defesa_base, f, muralha_inicial, sorte_ondas, 1000, fe_ataque, fe_defesa, bn_val)
            sweet_data.append({"Fulls Defensivos": f, "Ondas Suportadas": ondas_f, "População": pop_f})
            
        df_sweet = pd.DataFrame(sweet_data)
        fig2 = px.bar(df_sweet, x="Fulls Defensivos", y="Ondas Suportadas", text="Ondas Suportadas", color="Ondas Suportadas", color_continuous_scale="Reds")
        fig2.update_layout(
            plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)', font=dict(color='#f8fafc'),
            xaxis=dict(showgrid=False, color='#94a3b8', type='category'), yaxis=dict(showgrid=True, gridcolor='#334155', color='#94a3b8'),
            coloraxis_showscale=False, margin=dict(l=0, r=0, t=20, b=0)
        )
        fig2.update_traces(textposition='outside')
        st.plotly_chart(fig2, use_container_width=True)
