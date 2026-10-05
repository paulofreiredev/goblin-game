# 030 — Dois jogadores e captura de bandeiras

- Estado: Validação pendente
- Responsável atual: Executor único
- Pedido original: opção de um ou dois jogadores; dois personagens com botões distintos configuráveis; capture a bandeira verde e azul.

## Objetivo e comportamento esperado

Menu principal oferece Dois jogadores. Partida local com duas bandeiras, equipes verde/azul e controles independentes configuráveis. Primeiro a três capturas vence. Capturar exige trazer bandeira adversária à base com a própria bandeira em casa. Ataque devolve adversário à base e deixa bandeira no chão. Caça de um jogador e save preservados.

## Escopo

Incluído: duas personagens, configurações de teclado por jogador, controle USB configurado para jogador verde, pausa por Start/Esc, retomada da sessão local. Câmera compartilhada enquadra ambos. Fora: rede e persistência de partida local.

## Contexto, dúvidas e decisões

Base Panda3D existente. Câmera compartilhada escolhida para a partida local; FPS existente continua no modo de um jogador. Sem dependências novas. Uma entrada ocupada troca associações, inclusive entre jogadores. Ambiente sem controle físico e janela interativa disponível.

## Critérios de aceitação e testes

| ID | Critério observável | Tipo de teste | Entrada/passos | Resultado esperado | Resultado real/evidência |
| --- | --- | --- | --- | --- | --- |
| CA-01 | Opção visível e duas personagens | Integração | Menu → Dois jogadores → Jogar | Partida local ativa | Pendente |
| CA-02 | Bandeiras verde/azul, regras de captura | Automatizado | Pegar, devolver, capturar três vezes | Placar e vitória corretos | Pendente |
| CA-03 | Controles independentes relativos à visão | Integração | Movimentar com teclas de cada equipe | Só jogador correspondente move | Pendente |
| CA-04 | Start pausa e menu permite retomar | Integração/manual | Start durante captura | Mundo para, sessão preservada | Pendente |
| CA-05 | Save solo preservado | Integração | Jogar captura e voltar à caça | Save solo intacto | Pendente |

## Plano de implementação

Regras em game/capture.py; interface e renderização no aplicativo. Testes de regra e integração, capturas e README.

## Riscos e mitigação

Save solo sobrescrito: modo capture não salva Player local. Distância entre jogadores: câmera enquadra ambos. Configuração conflitante: troca de teclas sem duplicação.

## Entrega do codificador

Pendente.

## Revisão

Pendente; interação física necessária.

## Encerramento

Pendente.

## Evidências, entrega e revisão

Implementados game/capture.py, integração/menu/configuração em game/app.py, tests/test_capture.py, teste de integração em tests/test_app.py e tools/capture_local_preview.py. Comando: `RUN_GRAPHICS_TESTS=1 .venv/bin/python -m pytest -q`: **114 passaram em 19,46 s**. Verificados pickup/captura/vitória, exigência da própria bandeira em casa, ataque/frente/distância/recarga, troca de controles entre equipes, movimento independente, pausa Start/retomada e preservação do save solo. Captura offscreen e inspeção de docs/images/dois-jogadores.png confirmam bandeiras verde/azul e duas personagens; GIF de 2,5 s gerado com ambas andando. README atualizado.

Revisão: fluxo de entrada/saída, save solo e configurações conferidos. Sem achado bloqueante nos testes. **Parecer: Validação pendente** pela ausência de janela interativa e hardware USB neste ambiente. Roteiro manual: selecionar dois jogadores, remapear ambas equipes, jogar uma captura, atacar, pausar por Start, retomar com direcional/B e concluir três capturas; abrir caça salva depois. Não declarar esse roteiro executado.
