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
    .block-container { padding-top: 2rem; padding-bottom: 2rem; max-width: 1400px; }
    
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
    
    /* Ocultar botões +/- do Streamlit e botão de limpar */
    div[data-testid="stNumberInputStepUp"], div[data-testid="stNumberInputStepDown"], 
    button[aria-label="Step down"], button[aria-label="Step up"], 
    button[aria-label="Clear value"] { display: none !important; }
    
    /* Comprimir os inputs e reduzir a fonte */
    input[type=number] { 
        font-size: 0.8rem !important; 
        padding: 4px 2px !important; 
        text-align: center !important; 
        -moz-appearance: textfield; 
    }
    input[type=number]::-webkit-inner-spin-button, 
    input[type=number]::-webkit-outer-spin-button { -webkit-appearance: none; margin: 0; }
    
    /* Diminuir o gap das colunas na linha de tropas */
    div[data-testid="column"] { padding: 0 3px !important; }
    
    hr { border-color: #334155; margin: 30px 0; }
</style>
""", unsafe_allow_html=True)

I18N = {
    'pt': {
        'title': '🛡️ Calculadora de Defesa',
        'subtitle': 'Configure os templates de ataque e defesa para simular cenários de resistência em massa.',
        'script_title': '🛠️ Instalar Script de Importação Automática (Tampermonkey)',
        'script_desc': '**Como usar:**\n1. Copie o código abaixo.\n2. Crie um novo script no **Tampermonkey** no seu navegador e cole o código.\n3. No jogo, acesse a **Visualização da Aldeia**. Clique no ícone de escudo 🛡️ que aparecerá ao lado das suas missões. A calculadora abrirá já preenchida!',
        'script_not_found': 'Script não encontrado no servidor.',
        'clear_all': '🗑️ Limpar Tudo',
        'clear_all_help': 'Zerar todas as tropas',
        'atk': 'Ataque',
        'def': 'Defesa',
        'effects_title': '✨ Efeitos e Bônus',
        'effects_subtitle': 'Adicione bônus de itens do paladino, tribo ou bandeiras.',
        'atk_bonus': '### ⚔️ Bônus do Atacante',
        'def_bonus': '### 🛡️ Bônus do Defensor',
        'effect_lbl': 'Efeito:',
        'mag_lbl': 'Magnitude:',
        'unit_lbl': 'Unidades Afetadas:',
        'add_atk_btn': 'Adicionar ao atacante',
        'add_def_btn': 'Adicionar ao defensor',
        'warn_unit': 'Selecione ao menos uma unidade.',
        'clear_atk': 'Limpar bônus de ataque',
        'clear_def': 'Limpar bônus de defesa',
        'mult_def': 'Multiplicar a defesa em',
        'wall': 'Nível da Muralha Inicial',
        'luck': 'Sorte (%)',
        'faith_atk': 'Fé do Ataque (100%)',
        'faith_def': 'Fé da Defesa (100%)',
        'nb': 'Bônus Noturno',
        'nb_pct': 'Bônus Noturno (%)',
        'sim_btn': 'Simular Cenário',
        'err_troops': 'Configure tropas para o ataque e para a defesa.',
        'pop_total': 'População Total',
        'atk_survived': 'Ataques Suportados',
        'wall_after': 'Muralha Após 1º Ataque',
        'level': 'Nível',
        'chart_title': 'Curva de Resistência da Aldeia',
        'pop_rem': 'População Restante',
        'wall_level': 'Nível Muralha',
        'details': 'Ver Detalhes por Ataques',
        'sweet_title': '### 📈 Análise de Escalabilidade (Sweet Spot)',
        'sweet_sub': 'Quantos ataques você suportaria se hospedasse diferentes volumes de fulls?',
        'def_fulls': 'Fulls Defensivos',
        'waves_surv': 'Ondas Suportadas',
        'population': 'População',
        'lang': 'Idioma / Language',
        'poder de ataque': 'poder de ataque',
        'poder de defesa': 'poder de defesa',
        'Dano do edifício': 'Dano do edifício',
        'Nível máximo de defesa da muralha': 'Nível máximo de defesa da muralha',
        'escondido': 'escondido',
        'para': 'para'
    },
    'en': {
        'title': '🛡️ Defense Calculator',
        'subtitle': 'Configure attack and defense templates to simulate mass resistance scenarios.',
        'script_title': '🛠️ Install Auto-Import Script (Tampermonkey)',
        'script_desc': '**How to use:**\n1. Copy the code below.\n2. Create a new script in **Tampermonkey** in your browser and paste the code.\n3. In-game, go to **Village Overview**. Click the shield icon 🛡️ that appears next to your quests. The calculator will open pre-filled!',
        'script_not_found': 'Script not found on server.',
        'clear_all': '🗑️ Clear All',
        'clear_all_help': 'Reset all troops',
        'atk': 'Attack',
        'def': 'Defense',
        'effects_title': '✨ Effects and Bonuses',
        'effects_subtitle': 'Add bonuses from paladin items, tribe, or flags.',
        'atk_bonus': '### ⚔️ Attacker Bonuses',
        'def_bonus': '### 🛡️ Defender Bonuses',
        'effect_lbl': 'Effect:',
        'mag_lbl': 'Magnitude:',
        'unit_lbl': 'Affected Units:',
        'add_atk_btn': 'Add to attacker',
        'add_def_btn': 'Add to defender',
        'warn_unit': 'Select at least one unit.',
        'clear_atk': 'Clear attack bonuses',
        'clear_def': 'Clear defense bonuses',
        'mult_def': 'Multiply defense by',
        'wall': 'Initial Wall Level',
        'luck': 'Luck (%)',
        'faith_atk': 'Attacker Faith (100%)',
        'faith_def': 'Defender Faith (100%)',
        'nb': 'Night Bonus',
        'nb_pct': 'Night Bonus (%)',
        'sim_btn': 'Simulate Scenario',
        'err_troops': 'Configure troops for attack and defense.',
        'pop_total': 'Total Population',
        'atk_survived': 'Attacks Survived',
        'wall_after': 'Wall After 1st Attack',
        'level': 'Level',
        'chart_title': 'Village Resistance Curve',
        'pop_rem': 'Remaining Population',
        'wall_level': 'Wall Level',
        'details': 'View Details by Attack',
        'sweet_title': '### 📈 Scalability Analysis (Sweet Spot)',
        'sweet_sub': 'How many attacks would you survive hosting different volumes of fulls?',
        'def_fulls': 'Defensive Fulls',
        'waves_surv': 'Waves Survived',
        'population': 'Population',
        'lang': 'Language / Idioma',
        'poder de ataque': 'Attack power',
        'poder de defesa': 'Defense power',
        'Dano do edifício': 'Building damage',
        'Nível máximo de defesa da muralha': 'Max wall defense level',
        'escondido': 'hidden',
        'para': 'for'
    }
}

UNIDADES = [
    ('lanceiro', {'pt': 'Lanceiro', 'en': 'Spearman'}, 'https://dsbr.innogamescdn.com/asset/1d2499b/graphic/unit/unit_spear.png', {'atk': 10, 'def_inf': 15, 'def_cav': 45, 'def_arq': 20, 'tipo_atk': 'inf', 'pop': 1}),
    ('espadachim', {'pt': 'Espadachim', 'en': 'Swordsman'}, 'https://dsbr.innogamescdn.com/asset/1d2499b/graphic/unit/unit_sword.png', {'atk': 25, 'def_inf': 50, 'def_cav': 15, 'def_arq': 40, 'tipo_atk': 'inf', 'pop': 1}),
    ('barbaro', {'pt': 'Bárbaro', 'en': 'Axeman'}, 'https://dsbr.innogamescdn.com/asset/1d2499b/graphic/unit/unit_axe.png', {'atk': 40, 'def_inf': 10, 'def_cav': 5, 'def_arq': 10, 'tipo_atk': 'inf', 'pop': 1}),
    ('arqueiro', {'pt': 'Arqueiro', 'en': 'Archer'}, 'https://dsbr.innogamescdn.com/asset/1d2499b/graphic/unit/unit_archer.png', {'atk': 15, 'def_inf': 50, 'def_cav': 40, 'def_arq': 5, 'tipo_atk': 'arq', 'pop': 1}),
    ('cavalaria_leve', {'pt': 'Cavalaria Leve', 'en': 'Light Cavalry'}, 'https://dsbr.innogamescdn.com/asset/1d2499b/graphic/unit/unit_light.png', {'atk': 130, 'def_inf': 30, 'def_cav': 40, 'def_arq': 30, 'tipo_atk': 'cav', 'pop': 4}),
    ('arqueiro_cavalo', {'pt': 'Arq. a Cavalo', 'en': 'Mounted Archer'}, 'https://dsbr.innogamescdn.com/asset/1d2499b/graphic/unit/unit_marcher.png', {'atk': 120, 'def_inf': 40, 'def_cav': 30, 'def_arq': 50, 'tipo_atk': 'arq', 'pop': 5}),
    ('cavalaria_pesada', {'pt': 'Cav. Pesada', 'en': 'Heavy Cavalry'}, 'https://dsbr.innogamescdn.com/asset/1d2499b/graphic/unit/unit_heavy.png', {'atk': 150, 'def_inf': 200, 'def_cav': 80, 'def_arq': 180, 'tipo_atk': 'cav', 'pop': 6}),
    ('ariete', {'pt': 'Aríete', 'en': 'Ram'}, 'https://dsbr.innogamescdn.com/asset/1d2499b/graphic/unit/unit_ram.png', {'atk': 2, 'def_inf': 20, 'def_cav': 50, 'def_arq': 20, 'tipo_atk': 'inf', 'pop': 5}),
    ('catapulta', {'pt': 'Catapulta', 'en': 'Catapult'}, 'https://dsbr.innogamescdn.com/asset/1d2499b/graphic/unit/unit_catapult.png', {'atk': 100, 'def_inf': 100, 'def_cav': 50, 'def_arq': 100, 'tipo_atk': 'inf', 'pop': 8}),
    ('paladino', {'pt': 'Paladino', 'en': 'Paladin'}, 'https://dsbr.innogamescdn.com/asset/1d2499b/graphic/unit/unit_knight.png', {'atk': 150, 'def_inf': 250, 'def_cav': 400, 'def_arq': 150, 'tipo_atk': 'cav', 'pop': 10}),
    ('nobre', {'pt': 'Nobre', 'en': 'Nobleman'}, 'https://dsbr.innogamescdn.com/asset/1d2499b/graphic/unit/unit_snob.png', {'atk': 30, 'def_inf': 100, 'def_cav': 50, 'def_arq': 100, 'tipo_atk': 'inf', 'pop': 100}),
    ('explorador', {'pt': 'Explorador', 'en': 'Scout'}, 'https://dsbr.innogamescdn.com/asset/1d2499b/graphic/unit/unit_spy.png', {'atk': 0, 'def_inf': 2, 'def_cav': 1, 'def_arq': 2, 'tipo_atk': 'cav', 'pop': 2}),
    ('milicia', {'pt': 'Milícia', 'en': 'Militia'}, 'https://dsbr.innogamescdn.com/asset/1d2499b/graphic/unit/unit_militia.png', {'atk': 5, 'def_inf': 15, 'def_cav': 45, 'def_arq': 25, 'tipo_atk': 'inf', 'pop': 0})
]
UNIDADES_DICT = {u[0]: u[3] for u in UNIDADES}

def get_populacao(tropa_dict):
    return sum((qtd or 0) * UNIDADES_DICT[u]['pop'] for u, qtd in tropa_dict.items() if u in UNIDADES_DICT)

def calcular_reducao_muralha(arietes, muralha_atual):
    if muralha_atual <= 0 or not arietes or arietes <= 0: return 0
    return arietes / 21.5

def simular_combate(atacante, defensor, muralha=20, sorte=0.0, fe_ataque=True, fe_defesa=True, bonus_noturno=0.0, bonus_atacante=None, bonus_defensor=None):
    if bonus_atacante is None: bonus_atacante = []
    if bonus_defensor is None: bonus_defensor = []
    atk_inf = atk_cav = atk_arq = 0
    dano_edificio_mod = 1.0
    
    for unidade, qtd in atacante.items():
        if unidade in UNIDADES_DICT and qtd:
            atk_mod = 1.0
            for b in bonus_atacante:
                if unidade in b['unidades'] or 'global' in b['unidades']:
                    if b['efeito'] == 'poder de ataque':
                        atk_mod += b['magnitude'] / 100.0
                    elif b['efeito'] == 'Dano do edifício' and unidade in ['ariete', 'catapulta']:
                        dano_edificio_mod += b['magnitude'] / 100.0
                        
            poder = qtd * (UNIDADES_DICT[unidade]['atk'] * atk_mod)
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
    defesa_muralha_mod = 1.0
    
    for unidade, qtd in defensor.items():
        if unidade in UNIDADES_DICT and qtd:
            def_mod = 1.0
            for b in bonus_defensor:
                if unidade in b['unidades'] or 'global' in b['unidades']:
                    if b['efeito'] == 'poder de defesa':
                        def_mod += b['magnitude'] / 100.0
                    elif b['efeito'] == 'Nível máximo de defesa da muralha' and unidade == 'ariete':
                        defesa_muralha_mod += b['magnitude'] / 100.0
                        
            def_inf_total += qtd * (UNIDADES_DICT[unidade]['def_inf'] * def_mod)
            def_cav_total += qtd * (UNIDADES_DICT[unidade]['def_cav'] * def_mod)
            def_arq_total += qtd * (UNIDADES_DICT[unidade]['def_arq'] * def_mod)

    def_efetiva = (def_inf_total * prop_inf) + (def_cav_total * prop_cav) + (def_arq_total * prop_arq)
    
    if bonus_noturno > 0:
        def_efetiva *= (1 + (bonus_noturno / 100.0))
        
    arietes = atacante.get('ariete', 0)
    base_drop = calcular_reducao_muralha(arietes, muralha) * dano_edificio_mod
    queda_combate = min(muralha / 2.0, base_drop)
    
    muralha_combate = max(0, int(round(muralha - queda_combate)))
    defesa_base_aldeia = 50 + (50 * muralha_combate)
    bonus_muralha = 1.037 ** muralha_combate
    
    def_total = (def_efetiva * bonus_muralha) + (defesa_base_aldeia * defesa_muralha_mod)
    
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


def simular_cenario(ataque_base, defesa_base, qtd_fulls, muralha_inicial, sorte_ondas, limit=200, fe_ataque=True, fe_defesa=True, bn=0.0, bonus_atacante=None, bonus_defensor=None):
    defesa_atual = {k: round((v or 0) * qtd_fulls) for k, v in defesa_base.items()}
    populacao_inicial = get_populacao(defesa_atual)
    
    muralha_atual = muralha_inicial
    onda_atual = 0
    dados = []
    
    dados.append({
        "Onda": 0, "População Restante": populacao_inicial, 
        "Nível Muralha": muralha_atual, "Capacidade Restante": 100.0
    })
    
    while True:
        onda_atual += 1
        res = simular_combate(ataque_base, defesa_atual, muralha_atual, sorte_ondas, fe_ataque, fe_defesa, bn, bonus_atacante, bonus_defensor)
        
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


query_params = st.query_params

if 'lang' not in st.session_state:
    if 'lang' in query_params and query_params['lang'] in ['pt', 'en']:
        st.session_state['lang'] = query_params['lang']
    else:
        st.session_state['lang'] = 'pt'

col_title, col_lang = st.columns([5, 1])
with col_lang:
    st.markdown("<br>", unsafe_allow_html=True)
    lang_opts = {'pt': '🇧🇷 Português', 'en': '🇺🇸 English'}
    selected_lang_name = st.selectbox(I18N[st.session_state['lang']]['lang'], options=list(lang_opts.values()), index=0 if st.session_state['lang'] == 'pt' else 1, label_visibility="collapsed")
    new_lang = 'pt' if 'Português' in selected_lang_name else 'en'
    if new_lang != st.session_state['lang']:
        st.session_state['lang'] = new_lang
        st.rerun()

lang = st.session_state['lang']
t = I18N[lang]

with col_title:
    st.markdown(f"<div class='main-title'>{t['title']}</div>", unsafe_allow_html=True)
st.markdown(f"<div class='subtitle'>{t['subtitle']}</div>", unsafe_allow_html=True)


with st.expander(t['script_title']):
    st.markdown(t['script_desc'])
    try:
        with open("script_exportar_tropas.user.js", "r", encoding="utf-8") as f:
            script_code = f.read()
        st.code(script_code, language="javascript")
    except FileNotFoundError:
        st.error(t['script_not_found'])

if 'init_done' not in st.session_state:
    st.session_state['init_done'] = True
    st.session_state['bonus_atacante'] = []
    st.session_state['bonus_defensor'] = []
    st.session_state['is_night_bonus_init'] = False
    st.session_state['bn_pct_init'] = 300
    default_atk = {'barbaro': 6000, 'cavalaria_leve': 3000, 'ariete': 300}
    default_def = {'lanceiro': 10000, 'espadachim': 10000}
    
    is_import = any(key.startswith('def_') for key in query_params.keys())
    
    for k in [u[0] for u in UNIDADES]:
        st.session_state[f'atk_{k}'] = default_atk.get(k, None)
        
        if f'def_{k}' in query_params:
            try:
                st.session_state[f'def_{k}'] = int(query_params[f'def_{k}'])
            except ValueError:
                st.session_state[f'def_{k}'] = None if is_import else default_def.get(k, None)
        else:
            st.session_state[f'def_{k}'] = None if is_import else default_def.get(k, None)
            
    if 'bonus' in query_params:
        bonuses = query_params.get_all('bonus')
        for b in bonuses:
            parts = b.split('|')
            if len(parts) >= 3:
                unidade = parts[0]
                try:
                    magnitude = int(parts[1])
                except ValueError:
                    continue
                efeito_str = parts[2].lower()
                
                efeitos = []
                if "ataque e defesa" in efeito_str or "attack and defense" in efeito_str:
                    efeitos.extend(["poder de ataque", "poder de defesa"])
                elif "dano" in efeito_str or "damage" in efeito_str:
                    efeitos.append("Dano do edifício")
                elif "muralha" in efeito_str or "wall" in efeito_str or (unidade == "global" and ("cerco" in efeito_str or "força de defesa" in efeito_str or "siege" in efeito_str)):
                    efeitos.append("Nível máximo de defesa da muralha")
                    unidade = "ariete"
                elif "ataque" in efeito_str or "attack" in efeito_str:
                    efeitos.append("poder de ataque")
                elif "defesa" in efeito_str or "defense" in efeito_str:
                    efeitos.append("poder de defesa")
                else:
                    pass
                    
                if unidade == "global" and not efeitos: continue
                
                if unidade == "global" and "poder de defesa" in efeitos:
                    st.session_state['is_night_bonus_init'] = True
                    st.session_state['bn_pct_init'] = magnitude
                    efeitos.remove("poder de defesa")
                    
                for ef in efeitos:
                    st.session_state['bonus_defensor'].append({
                        'efeito': ef,
                        'magnitude': magnitude,
                        'unidades': [unidade]
                    })

def limpar_tropas():
    for k in [u[0] for u in UNIDADES]:
        st.session_state[f'atk_{k}'] = None
        st.session_state[f'def_{k}'] = None

with st.container():
    st.button(t['clear_all'], on_click=limpar_tropas, help=t['clear_all_help'], type="secondary")
    
    padrao_atk, padrao_def = {}, {}
    
    cols = st.columns([1.5] + [1]*len(UNIDADES) + [0.5])
    for i, (key, nome_dict, img, _) in enumerate(UNIDADES):
        nome_exib = nome_dict[lang]
        with cols[i+1]: st.markdown(f'<img src="{img}" title="{nome_exib}" class="unit-img">', unsafe_allow_html=True)
    
    cols_atk = st.columns([1.5] + [1]*len(UNIDADES) + [0.5])
    with cols_atk[0]: st.markdown(f"<div class='row-label'>{t['atk']}</div>", unsafe_allow_html=True)
    for i, (key, nome_dict, _, _) in enumerate(UNIDADES):
        with cols_atk[i+1]:
            padrao_atk[key] = st.number_input(f"atk_{key}", value=None, min_value=0, step=50, placeholder="0", label_visibility="collapsed", disabled=(key=='milicia'), key=f"atk_{key}")
            
    st.markdown("<div style='height: 10px'></div>", unsafe_allow_html=True)
            
    cols_def = st.columns([1.5] + [1]*len(UNIDADES) + [0.5])
    with cols_def[0]: st.markdown(f"<div class='row-label'>{t['def']}</div>", unsafe_allow_html=True)
    for i, (key, nome_dict, _, _) in enumerate(UNIDADES):
        with cols_def[i+1]:
            padrao_def[key] = st.number_input(f"def_{key}", value=None, min_value=0, step=50, placeholder="0", label_visibility="collapsed", key=f"def_{key}")

st.markdown("<hr>", unsafe_allow_html=True)

with st.expander(t['effects_title']):
    st.markdown(f"<div class='subtitle'>{t['effects_subtitle']}</div>", unsafe_allow_html=True)
    c_atk, c_def = st.columns(2)
    
    chaves_efeitos = ["poder de ataque", "poder de defesa", "Dano do edifício", "Nível máximo de defesa da muralha", "escondido"]
    # Mostramos a tradução dos efeitos
    opcoes_efeitos_exib = [t[ef] for ef in chaves_efeitos]
    opcoes_magnitude = [f"+{i}%" for i in range(1, 101)]
    nomes_unidades = [u[1][lang] for u in UNIDADES]
    unidades_dict_nome_para_key = {u[1][lang]: u[0] for u in UNIDADES}
    efeito_dict_nome_para_key = {t[ef]: ef for ef in chaves_efeitos}
    
    with c_atk:
        st.markdown(t['atk_bonus'])
        ef_atk_exib = st.selectbox(t['effect_lbl'], opcoes_efeitos_exib, key="ef_atk")
        ef_atk = efeito_dict_nome_para_key[ef_atk_exib]
        mag_atk = st.selectbox(t['mag_lbl'], opcoes_magnitude, key="mag_atk")
        uni_atk = st.multiselect(t['unit_lbl'], nomes_unidades, key="uni_atk")
        if st.button(t['add_atk_btn'], use_container_width=True):
            if uni_atk:
                val = int(mag_atk.replace("+", "").replace("%", ""))
                st.session_state['bonus_atacante'].append({'efeito': ef_atk, 'magnitude': val, 'unidades': [unidades_dict_nome_para_key[u] for u in uni_atk]})
                st.rerun()
            else:
                st.warning(t['warn_unit'])
                
        if st.session_state['bonus_atacante']:
            for i, b in enumerate(st.session_state['bonus_atacante']):
                st.info(f"{t[b['efeito']]} (+{b['magnitude']}%) {t['para']} {', '.join([next((u[1][lang] for u in UNIDADES if u[0] == un), 'Todas as unidades' if lang == 'pt' else 'All units') for un in b['unidades']])}")
            if st.button(t['clear_atk'], key="clear_atk_btn"):
                st.session_state['bonus_atacante'] = []
                st.rerun()
                
    with c_def:
        st.markdown(t['def_bonus'])
        ef_def_exib = st.selectbox(t['effect_lbl'], opcoes_efeitos_exib, key="ef_def")
        ef_def = efeito_dict_nome_para_key[ef_def_exib]
        mag_def = st.selectbox(t['mag_lbl'], opcoes_magnitude, key="mag_def")
        uni_def = st.multiselect(t['unit_lbl'], nomes_unidades, key="uni_def")
        if st.button(t['add_def_btn'], use_container_width=True):
            if uni_def:
                val = int(mag_def.replace("+", "").replace("%", ""))
                st.session_state['bonus_defensor'].append({'efeito': ef_def, 'magnitude': val, 'unidades': [unidades_dict_nome_para_key[u] for u in uni_def]})
                st.rerun()
            else:
                st.warning(t['warn_unit'])
                
        if st.session_state['bonus_defensor']:
            for i, b in enumerate(st.session_state['bonus_defensor']):
                st.success(f"{t[b['efeito']]} (+{b['magnitude']}%) {t['para']} {', '.join([next((u[1][lang] for u in UNIDADES if u[0] == un), 'Todas as unidades' if lang == 'pt' else 'All units') for un in b['unidades']])}")
            if st.button(t['clear_def'], key="clear_def_btn"):
                st.session_state['bonus_defensor'] = []
                st.rerun()

st.markdown("<hr>", unsafe_allow_html=True)

c1, c2, c3, c4 = st.columns(4)
with c1: 
    qtd_fulls_def = st.number_input(t['mult_def'], min_value=0.1, max_value=100.0, value=1.0, step=0.5)
with c2: 
    muralha_inicial = st.number_input(t['wall'], min_value=0, max_value=20, value=20, step=1)
with c3: 
    sorte_ondas = st.slider(t['luck'], -25.0, 25.0, 0.0, 0.1)
with c4:
    fe_ataque = st.checkbox(t['faith_atk'], value=True)
    fe_defesa = st.checkbox(t['faith_def'], value=True)

c5, c6, c7, c8 = st.columns(4)
with c5:
    is_night_bonus = st.toggle(t['nb'], value=st.session_state.get('is_night_bonus_init', False))
with c6:
    bn_pct = st.number_input(t['nb_pct'], min_value=0, value=st.session_state.get('bn_pct_init', 300), step=10, disabled=not is_night_bonus)
with c8:
    st.markdown("<br>", unsafe_allow_html=True)
    simular_btn = st.button(t['sim_btn'], use_container_width=True, type="primary")

if simular_btn:
    ataque_base = {k: (v or 0) for k, v in padrao_atk.items()}
    defesa_base = {k: (v or 0) for k, v in padrao_def.items()}
    
    if sum(ataque_base.values()) == 0 or sum(defesa_base.values()) == 0:
        st.error(t['err_troops'])
    else:
        st.markdown("<hr>", unsafe_allow_html=True)
        bn_val = bn_pct if is_night_bonus else 0.0
        ondas, mur_final, pop_inicial, dados = simular_cenario(ataque_base, defesa_base, qtd_fulls_def, muralha_inicial, sorte_ondas, 200, fe_ataque, fe_defesa, bn_val, st.session_state.get('bonus_atacante', []), st.session_state.get('bonus_defensor', []))
        
        mur_pos_primeiro = dados[1]["Nível Muralha"] if len(dados) > 1 else muralha_inicial
        
        m1, m2, m3 = st.columns(3)
        with m1: st.metric(t['pop_total'], f"{pop_inicial:,.0f}".replace(',','.'))
        with m2: st.metric(t['atk_survived'], f"{ondas}")
        with m3: st.metric(t['wall_after'], f"{t['level']} {mur_pos_primeiro}")
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        df_grafico = pd.DataFrame(dados)
        df_grafico["Capacidade Restante"] = df_grafico["Capacidade Restante"].apply(lambda x: f"{x:.1f}%")
        
        df_grafico_exib = df_grafico.rename(columns={
            "População Restante": t['pop_rem'],
            "Nível Muralha": t['wall_level']
        })
        
        from plotly.subplots import make_subplots
        
        fig = make_subplots(specs=[[{"secondary_y": True}]])
        fig.add_trace(
            go.Scatter(x=df_grafico_exib["Onda"], y=df_grafico_exib[t['pop_rem']], name=t['population'],
                       line=dict(color="#f43f5e", width=3), mode='lines+markers', marker=dict(size=8, color="#f43f5e")),
            secondary_y=False,
        )
        fig.add_trace(
            go.Scatter(x=df_grafico_exib["Onda"], y=df_grafico_exib[t['wall_level']], name=t['wall_level'],
                       line=dict(color="#eab308", width=3, dash='dot'), mode='lines+markers', marker=dict(size=8, color="#eab308")),
            secondary_y=True,
        )
        fig.update_layout(
            title=t['chart_title'],
            plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)', font=dict(color='#f8fafc'),
            xaxis=dict(showgrid=False, color='#94a3b8'),
            margin=dict(l=0, r=0, t=40, b=0),
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
        )
        fig.update_yaxes(title_text=t['pop_rem'], showgrid=True, gridcolor='#334155', color='#f43f5e', secondary_y=False)
        fig.update_yaxes(title_text=t['wall_level'], showgrid=False, color='#eab308', range=[0, 20], secondary_y=True)
        st.plotly_chart(fig, use_container_width=True)
        
        with st.expander(t['details']):
            st.dataframe(df_grafico_exib, use_container_width=True, hide_index=True)
            
        st.markdown("<hr>", unsafe_allow_html=True)
        
        st.markdown(t['sweet_title'])
        st.markdown(f"<div class='subtitle'>{t['sweet_sub']}</div>", unsafe_allow_html=True)
        
        fulls_to_test = [1, 2, 3, 4, 5, 6, 8, 10, 15]
        sweet_data = []
        for f in fulls_to_test:
            ondas_f, _, pop_f, _ = simular_cenario(ataque_base, defesa_base, f, muralha_inicial, sorte_ondas, 1000, fe_ataque, fe_defesa, bn_val, st.session_state.get('bonus_atacante', []), st.session_state.get('bonus_defensor', []))
            sweet_data.append({t['def_fulls']: f, t['waves_surv']: ondas_f, t['population']: pop_f})
            
        df_sweet = pd.DataFrame(sweet_data)
        fig2 = px.bar(df_sweet, x=t['def_fulls'], y=t['waves_surv'], text=t['waves_surv'], color=t['waves_surv'], color_continuous_scale="Reds")
        fig2.update_layout(
            plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)', font=dict(color='#f8fafc'),
            xaxis=dict(showgrid=False, color='#94a3b8', type='category'), yaxis=dict(showgrid=True, gridcolor='#334155', color='#94a3b8'),
            coloraxis_showscale=False, margin=dict(l=0, r=0, t=20, b=0)
        )
        fig2.update_traces(textposition='outside')
        st.plotly_chart(fig2, use_container_width=True)
