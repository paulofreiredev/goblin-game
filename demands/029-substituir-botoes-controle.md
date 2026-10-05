# 029 — Substituir botões configurados do controle

- Estado: Validação pendente
- Responsável atual: Executor único, papéis refinador/codificador/reviewer em sequência
- Pedido original: Ao apertar outro botão na configuração do controle, ele deve substituir mesmo.

## Objetivo e comportamento esperado

Reabrir qualquer ação e pressionar outra entrada substitui imediatamente a associação e salva. Uma entrada já ocupada troca de lugar com a anterior; associações compartilhadas entre B de confirmação e uma ação de jogo acompanham a troca quando há conflito.

## Escopo

- Incluído: botões, eixos, Start, B, persistência e configuração repetida.
- Fora do escopo: drivers USB.

## Contexto, dúvidas e decisões

O bloqueio vinha da rejeição de entradas usadas por outra ação em `Game.poll_gamepad`. A captura já permite soltar a entrada mantida e pressionar outra. A troca preserva todas as ações configuradas e evita que o carregamento rejeite duplicações. Nenhuma dependência nova. Ambiente sem controle físico e sem janela interativa disponível.

## Critérios de aceitação e testes

| ID | Critério observável | Tipo de teste | Entrada/passos | Resultado esperado | Resultado real/evidência |
| --- | --- | --- | --- | --- | --- |
| CA-01 | Nova entrada substitui a anterior | Automatizado/integração | Remapear ataque duas vezes | Última escolha salva | Pendente |
| CA-02 | Entrada ocupada também aceita | Automatizado | Todas as combinações, incluindo Start/B/eixos | Troca válida, sem ação perdida | Pendente |
| CA-03 | Configuração persiste | Integração | Captura simulada e leitura de settings | Mapeamentos iguais aos aplicados | Pendente |
| CA-04 | Controle físico e menu legível | Manual | Opções → Controle USB, selecionar ação e apertar outro botão | Substituição imediata e rótulos atualizados | Pendente no hardware do usuário |

## Plano de implementação

1. Extrair substituição/troca para game/gamepad.py.
2. Aplicar na captura e atualizar mensagem/documentação.
3. Executar testes determinísticos e integração offscreen, capturar tela e revisar.

## Riscos e mitigação

Start pode conflitar com B/ações: trocar grupos de entradas mantém separação válida. Entrada que abriu a captura: exigir soltura antes de recapturar.

## Entrega do codificador

- Arquivos: game/gamepad.py, game/app.py, tests/test_gamepad.py, tests/test_app.py, README.md.
- Execução: `.venv/bin/python main.py`.
- Testes/resultados: aguardando execução atual.
- Roteiro manual: seguir CA-04, fechar e reabrir para conferir persistência.
- Limitação: testes offscreen não substituem interação física.

## Revisão

- Parecer: Pendente.

## Encerramento

- Testes e revisão pendentes; documentação em atualização.

## Evidências e revisão atualizadas

`RUN_GRAPHICS_TESTS=1 .venv/bin/python -m pytest -q`: **109 passaram em 17,58 s**. Revisão do fluxo de captura, persistência e carregamento; testes cobrem troca de todas as combinações de entradas, Start/B e eixos. A rejeição de entradas ocupadas foi substituída por troca conforme demanda 029. Start abre menu, direcional navega e B confirma em teste simulado. Capturas offscreen mostram menus em tela cheia. Parecer: **Validação pendente**, pois não há janela interativa nem controle físico neste ambiente. O usuário confirmou que o USB funciona em seu computador.
