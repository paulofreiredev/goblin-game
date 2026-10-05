# 022 — Remover texto inferior da partida

- Estado: Validação pendente
- Responsável atual: Code reviewer (executor único, perfis em sequência)
- Pedido original: “remova o texto na parte inferior da tela”

## Objetivo e comportamento esperado

Deixar a parte inferior do campo livre de instruções e mensagens de status durante a partida e após a vitória.

## Escopo

- Incluído: remover instruções de controles, status de ação/monstros e aviso inferior após vencer.
- Fora do escopo: HUD superior, título de vitória e textos dos menus/opções/derrota.

## Contexto, dúvidas e decisões

- Código relacionado: `start_game`, `finish_match`, `update` em `game/app.py`.
- Dúvidas bloqueantes: nenhuma.
- Hipótese reversível: pedido refere-se aos textos sobrepostos ao campo, incluindo a linha de status.
- Biblioteca e dependências: Panda3D existente; nenhuma adição.
- Plataformas e limitações: validação gráfica interativa pendente; display indisponível nas demandas anteriores.

## Critérios de aceitação e testes

| ID | Critério observável | Tipo de teste | Entrada/passos | Resultado esperado | Resultado real/evidência |
| --- | --- | --- | --- | --- | --- |
| CA-01 | Campo sem textos inferiores em partida e vitória | Integração/manual | Iniciar, mover, vencer | Sem instruções/status abaixo do campo | Pendente |
| CA-02 | HUD e regras continuam funcionando | Integração | Coletar, salvar, continuar, reiniciar | Suíte existente aprovada | Pendente |

## Plano de implementação

1. Remover criação e atualização dos textos inferiores.
2. Ajustar verificação de fonte que referenciava o status e documentar o comportamento.
3. Executar integração e revisar os fluxos.

## Riscos e mitigação

- Atualização tentar acessar label removido: remover também o trecho de status do ciclo de atualização.

## Entrega do codificador

- Arquivos alterados: game/app.py, tests/test_app.py, README.md e esta demanda.
- Comando: `.venv/bin/python main.py`.
- Testes: `RUN_GRAPHICS_TESTS=1 .venv/bin/python -m pytest -q`: 76 aprovados em 5.69s.
- Inspeção com rg confirmou remoção de status_label, instruções e aviso inferior de vitória.
- Roteiro manual: iniciar, mover e vencer; conferir parte inferior livre. Não executado (display indisponível).

## Revisão

- Parecer: Validação pendente. Fluxos de partida, atualização e vitória revisados sem referências ao label removido. Sem achados; falta interação gráfica.

## Encerramento

- Implementação e integração entregues; documentação atualizada; validação gráfica interativa pendente.
