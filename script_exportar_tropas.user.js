// ==UserScript==
// @name         TW Calculadora - Exportar Tropas
// @namespace    http://tampermonkey.net/
// @version      1.4
// @description  Adiciona um botão para exportar tropas da aldeia atual para a calculadora
// @author       Leandro Beraldo
// @match        https://*.tribalwars.com.br/*screen=overview*
// @updateURL    https://raw.githubusercontent.com/Leandruz/tw-calculadora/main/script_exportar_tropas.user.js
// @downloadURL  https://raw.githubusercontent.com/Leandruz/tw-calculadora/main/script_exportar_tropas.user.js
// @grant        none
// ==/UserScript==

(function() {
    'use strict';
    
    var VERSAO_ATUAL = 1.4;
    var URL_SCRIPT = 'https://raw.githubusercontent.com/Leandruz/tw-calculadora/main/script_exportar_tropas.user.js';

    var btn = document.createElement('div');
    btn.className = 'quest';
    btn.id = 'export_troops_btn';
    btn.style.cssText = "font-size: 14pt; font-family: Verdana, Arial; border-spacing: 0; width: 25px; height: 25px; border: 1px solid #603000; background-color: #E9D0A9; margin: 10px; cursor: pointer; position: relative; text-align: center; box-shadow: rgba(60, 30, 0, 0.7) 2px 2px 2px; border-radius: 3px; display: flex; align-items: center; justify-content: center;";
    btn.innerText = "🛡️";
    btn.title = "Exportar Tropas para Calculadora";

    // Verifica se há alguma atualização no GitHub
    fetch(URL_SCRIPT, { cache: "no-store" })
        .then(res => res.text())
        .then(text => {
            var match = text.match(/@version\s+([\d\.]+)/);
            if (match && parseFloat(match[1]) > VERSAO_ATUAL) {
                // Altera o visual do botão para indicar atualização
                btn.innerText = "🔄";
                btn.style.backgroundColor = "#ffcccc"; // Fundo avermelhado
                btn.style.border = "1px solid #cc0000";
                btn.title = "Atualização Disponível! Clique para atualizar o script.";
                
                // Sobrescreve a função de clique para redirecionar para a atualização
                btn.onclick = function() {
                    window.location.href = URL_SCRIPT;
                };
                btn.dataset.outdated = "true";
            }
        }).catch(err => console.log("Erro ao checar versão do script:", err));

    btn.onclick = function() {
        if (btn.dataset.outdated === "true") return; // Previne execução caso esteja desatualizado
        
        var mapa = { 'spear': 'lanceiro', 'sword': 'espadachim', 'axe': 'barbaro', 'archer': 'arqueiro', 'light': 'cavalaria_leve', 'marcher': 'arqueiro_cavalo', 'heavy': 'cavalaria_pesada', 'ram': 'ariete', 'catapult': 'catapulta', 'militia': 'milicia' };
        var tropasExportar = {};
        
        var tabelaDetalhada = document.getElementById('unit_overview_table') || document.getElementById('show_units');
        if (tabelaDetalhada) {
            var linhasAll = tabelaDetalhada.getElementsByClassName('all_unit');
            if (linhasAll.length > 0) {
                for (var i = 0; i < linhasAll.length; i++) {
                    var strongs = linhasAll[i].querySelectorAll('strong[data-count]');
                    for (var j = 0; j < strongs.length; j++) {
                        var unitKey = strongs[j].getAttribute('data-count');
                        if (mapa[unitKey]) {
                            var qtd = parseInt(strongs[j].innerText.replace(/\D/g, ''));
                            if (qtd > 0) tropasExportar[mapa[unitKey]] = qtd;
                        }
                    }
                }
            } else {
                var todosStrongs = tabelaDetalhada.querySelectorAll('strong[data-count]');
                for (var s = 0; s < todosStrongs.length; s++) {
                    var uKey = todosStrongs[s].getAttribute('data-count');
                    if (mapa[uKey]) {
                        var q = parseInt(todosStrongs[s].innerText.replace(/\D/g, ''));
                        if (q > 0) tropasExportar[mapa[uKey]] = q;
                    }
                }
            }
        }

        if (Object.keys(tropasExportar).length === 0 && window.game_data && window.game_data.village && window.game_data.village.unit_info) {
            var tropas = window.game_data.village.unit_info.own;
            for (var un in tropas) {
                if (mapa[un] && tropas[un] > 0) tropasExportar[mapa[un]] = tropas[un];
            }
        }

        var params = [];
        for (var k in tropasExportar) {
            params.push('def_' + k + '=' + tropasExportar[k]);
        }

        var urlCalculadora = 'https://defesatribalwars.streamlit.app/'; 
        if (params.length > 0) {
            window.open(urlCalculadora + '?' + params.join('&'), '_blank');
        } else {
            alert("Não foi possível encontrar tropas nesta tela. Certifique-se de estar na página inicial da aldeia.");
        }
    };

    var refQuest = document.getElementById('new_quest') || document.querySelector('.quest');
    if (refQuest && refQuest.parentNode) {
        refQuest.parentNode.appendChild(btn);
    } else {
        btn.style.position = 'fixed';
        btn.style.left = '10px';
        btn.style.top = '150px';
        btn.style.zIndex = '9999';
        document.body.appendChild(btn);
    }
})();
