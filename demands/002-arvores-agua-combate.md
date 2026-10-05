# 002 — Árvores, água, inimigos, salto e ataque

- Estado: Validação pendente
- Pedido: usar low.obj para árvores, Water Top para água e stilagmate.blend para inimigos; adicionar salto e ataque.

## Refinamento e decisões

Preservar menu, música, movimento e saves anteriores. Distribuir dez conjuntos de árvores e quatro lagoas no campo. Água rasa reduz velocidade no chão; salto evita a redução. Espaço salta; X ataca na direção atual. Inimigos próximos perseguem, têm dois pontos de vida e causam dano por contato; cavaleiro tem cinco pontos. Derrota devolve o jogador ao centro com vida restaurada. Sem sistema de missões nesta demanda.

low.obj contém um pequeno bosque, com plano de chão e materiais externos ausentes: excluir plano e usar cores de tronco/copa. Converter stilagmate.blend 2.49 em dados triangulados via Blender portátil 3.6.23, preservando a geometria e retirando apenas o plano de chão da cena exportada. Aplicar textura procedural de pedra nos inimigos. Arquivo derivado incluído no projeto; Blender não é dependência de execução.

Salto anima a elevação física do billboard, mantendo o ciclo existente. Ataque usa colunas 12–17 identificadas visualmente. Golpe instantâneo frontal, alcance 3.8, intervalo de 0.6 s, sem dano repetido por frame. Persistir vida e estado dos inimigos; ações transitórias não persistem. Saves antigos recebem padrões compatíveis.

## Critérios de aceitação

| ID | Comportamento | Verificação |
| --- | --- | --- |
| CA-01 | Árvores usam geometria low.obj e bloqueiam passagem na área do bosque | Inspeção de modelo, teste de região, captura e teste interativo |
| CA-02 | Água em quatro locais usa Water Top.png e reduz velocidade no chão | Captura, geometria, lógica e integração |
| CA-03 | Oito inimigos usam malha derivada do blend e perseguem nas proximidades | Exportação, teste de perseguição, captura |
| CA-04 | Espaço salta/aterra; não permite salto duplo | Teste de física e integração |
| CA-05 | X ataca; só acerta alvos próximos à frente; dois golpes derrotam | Testes de dano, direção, alcance e intervalo; integração |
| CA-06 | Contato causa dano com intervalo, salto alto evita contato e derrota reinicia posição | Testes de combate e integração |
| CA-07 | Continuar recupera vida/inimigos e carrega saves antigos | Testes de persistência e integração |

## Plano

1. Exportar e inspecionar modelos; criar carregadores de geometria.
2. Separar layout, colisão e combate da interface gráfica.
3. Integrar árvores, lagoas, inimigos, ações e HUD.
4. Executar regressão de menu, testes novos e capturas gráficas.
5. Revisar e atualizar README com controles e limitações.

## Evidências e revisão

- Exportação por Blender 3.6.23: Plane (4 vértices), Sphere (89 vértices/166 triângulos), Sphere.001 (10 vértices/8 triângulos). O plano é excluído no carregamento.
- Execução offscreen real e inspeção de `/tmp/wolf-scenery-final.png` e `/tmp/wolf-attack-jump.png`: árvores, água, modelos dos inimigos, barras de vida, sprite elevado e feedback de golpe visíveis.
- Teste de integração usa eventos reais Panda (`space`, `x`), confirma salto/aterrissagem, intervalo entre golpes, morte/ocultação do inimigo, pause, persistência, novo jogo, redução de velocidade na água e bloqueio de bosque.
- Revisão sequencial: preservação de menu/som, compatibilidade de save, conversão de eixos, triangulação, aplicação de cores, aterrissagem, direção/alcance do ataque e dano por contato. Corrigida classificação das copas: cada grupo cylinder contém tanto tronco quanto folhagem. Adicionada relocação de save antigo dentro de bosque para evitar personagem preso.
- Parecer: sem defeito bloqueante encontrado nas verificações automatizadas e capturas; validação humana de teclado, jogabilidade e áudio permanece pendente conforme workflow.

## Comandos e resultados

`env RUN_GRAPHICS_TESTS=1 .venv/bin/python -m pytest -q`: **25 testes aprovados** (2.75 s), incluindo integração gráfica offscreen, salto/ataque em X, persistência, água, colisão e perda de foco sem pausa. Compilação Python verificada. Nenhum novo pacote é necessário no runtime. Blender portátil foi usado apenas na exportação; a tentativa de instalar bpy não encontrou distribuição compatível.

## Roteiro interativo pendente

Executar `.venv/bin/python main.py`. Iniciar/continuar, explorar bosques e lagoas, usar Espaço e X, verificar animação nas oito direções, receber dano e retornar ao centro ao perder vida. Conferir que sair/reabrir preserva inimigos derrotados, que Novo jogo reinicia e que som/menu mantêm comportamento anterior.


## Ajustes solicitados durante a implementação

- Copas explicitamente verdes, incluindo os níveis inferiores do pinheiro; troncos mantêm cor de madeira.
- Inimigos reduzidos de 2.6 para 1.45 unidade de altura (aproximadamente 44% menores), com textura procedural de pedra e UVs projetadas por face. Barras de vida ajustadas.
- Ataque simplificado para X, com atualização de HUD, documentação e teste de eventos.
- Print Screen não deve pausar: perda de foco deixa o jogo em execução, apenas limpa teclas para evitar movimento preso. Somente Esc/menu pausa. Teste simula a perda de foco disparada por ferramentas de captura.

Capturas finais `/tmp/wolf-stone-final.png` e `/tmp/wolf-stone-action.png` inspecionadas: copas verdes, inimigos menores com textura de pedra, lagoas, HUD indicando X e salto com sombra no chão.
