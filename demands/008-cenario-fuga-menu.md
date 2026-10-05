# 008 — Menu, terreno, fuga e poças menores

- Estado: Validação pendente
- Responsável atual: Code reviewer (executor único, papéis assumidos em sequência)
- Pedido original: No menu as moedas também devem ser grandes; o terreno deve ter elevações e depressões; inimigos devem fugir e não perseguir; poças menores.

## Objetivo e comportamento esperado

Símbolo e número maiores no menu; terreno com níveis; inimigos fogem dentro de 19 unidades, velocidade 2.4 em terra e 1.2 na água, respeitando limites e sólidos. Poças com metade dos raios anteriores (área de um quarto). Relevo suave inicial substituído por blocos em 010.

## Escopo

- Incluído: comportamento descrito acima e integração com a partida existente.
- Fora do escopo: novas dependências, publicação ou deploy.

## Contexto, dúvidas e decisões

- Código relacionado: game/app.py, game/state.py, game/world.py, game/controls.py e game/collisions.py, conforme o recurso.
- Biblioteca: Panda3D/Pillow existentes; sem dependências novas. Código anterior lido antes da implementação.
- Dúvidas bloqueantes: nenhuma; escolhas reversíveis descritas no objetivo.
- Fluxo: refinamento → pronta → implementação → revisão; complementos posteriores registrados em demandas próprias.
- Limitação: DISPLAY=:0 não abriu no sandbox; renderização offscreen funciona. Capturas não substituem interação em janela.

## Critérios de aceitação e testes

| ID | Critério observável | Tipo de teste | Entrada/passos | Resultado esperado | Resultado real/evidência |
| --- | --- | --- | --- | --- | --- |
| CA-01 | Regras/integração conforme objetivo | Automatizado/integração | test_fleeing_and_environment; test_fleeing_respects_bounds_obstacles_and_frame_time; test_terrain_has_blocks_depressions_and_flat_pond_beds; test_menu_game_options_and_resume | Comportamento descrito no objetivo | Suíte final: 69 aprovados, incluindo integração offscreen |
| CA-02 | Aparência e interação reais | Manual | Conferir menu, aproximar-se de monstros, observar fuga e tamanho das poças. | Funcionamento sem sobreposição ou erros visuais | Capturas conferidas quando disponíveis; roteiro interativo pendente |

## Plano de implementação

1. Refinar usando os módulos e assets existentes, preservando comportamento não alterado pelo pedido.
2. Implementar regras puras e integrar renderização/interface conforme o recurso.
3. Executar testes relevantes, revisar capturas, atualizar README e registros.

## Riscos e mitigação

- Testes sem janela não comprovam controles reais e apresentação durante a interação: manter roteiro manual pendente.
- Complementos alteram requisitos anteriores: conservar decisões finais no README e nos documentos vinculados por número.

## Entrega do codificador

- Arquivos alterados: módulos e testes relacionados acima; README.md.
- Executar: `.venv/bin/python main.py`.
- Testes: `RUN_GRAPHICS_TESTS=1 .venv/bin/python -m pytest -q` — 69 aprovados; `.venv/bin/python -m pytest -q` — 68 aprovados e 1 integração gráfica omitida.
- Evidências compartilhadas e comandos intermediários: [registro](VALIDACAO-003-018.md).
- Roteiro manual: CA-02, ainda não executado interativamente.

## Revisão

- Parecer: Validação pendente.
- Critérios conferidos: regras, integração, persistência quando aplicável e regressões; testes aprovados.
- Achados: sem defeito pendente reproduzido nos testes; falta verificação obrigatória em janela.
- Correções posteriores: migração dos testes às regras refinadas; guard de captura de teclado quando offscreen não tem ButtonThrower; volume do personagem e colisão extraída dos troncos.

## Encerramento

- Critérios automatizados verificados: sim.
- Testes obrigatórios aprovados: automatizados; manual pendente.
- Revisão aprovada: ainda não; depende da validação interativa conforme WORKFLOW.md.
- Documentação atualizada: README.md.
- Resultado comunicado: implementação e limitações informadas ao usuário.
