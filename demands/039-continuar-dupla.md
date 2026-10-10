# 039 — Continuar retoma a partida de dois

- Estado: Pronta
- Responsável atual: Executor único, papéis em sequência
- Pedido original: Se estiver de dois ao apertar continuar deve continuar o jogo de dois, não o de um.

## Objetivo e comportamento esperado

Continuar no menu principal retoma a partida de dois pausada, preservando jogadores, bandeiras, placares, câmeras e espera de vitória. Funciona mesmo sem save solo. Sem partida de dois na sessão, mantém carregamento solo existente.

## Escopo

- Incluído: botão Continuar e retorno por Esc que usam continue_game; disponibilidade sem save solo.
- Fora do escopo: persistir partida dupla ao fechar aplicativo; Novo jogo continua iniciando solo.

## Contexto, dúvidas e decisões

continue_game fecha capture_match antes de carregar save solo; botão só habilita com save solo. Usar capture_match existente como prioridade de retomada, antes de limpar/carregar. Sem dependências, assets ou dúvidas bloqueantes. Preservar alterações anteriores.

## Critérios de aceitação e testes

| ID | Critério observável | Tipo de teste | Entrada/passos | Resultado esperado | Resultado real/evidência |
| --- | --- | --- | --- | --- | --- |
| CA-01 | Continuar prioriza dupla | Integração | Solo salvo, iniciar dupla, pausar e clicar Continuar | Mesma partida dupla, sem carregar solo | Pendente |
| CA-02 | Funciona sem save solo | Integração | Iniciar dupla, pausar e continuar por botão/Esc | Botão habilitado e partida retomada | Pendente |
| CA-03 | Preservar estados e modo solo | Integração | Retomar com coleta e vitória; iniciar Novo jogo e continuar | Estado local preservado, solo continua quando sem dupla | Pendente |
| CA-04 | Fluxo interativo | Manual | Pausar dupla, visitar opções e Continuar | Duas vistas retornam | Pendente |

## Plano de implementação

1. Habilitar Continuar se existe capture_match.
2. Retomar captura antes do caminho de carregamento solo.
3. Ajustar regressão anterior que esperava carregar solo; verificar estado e atualizar README.

## Riscos e mitigação

Destruir partida antes de decidir: retorno antecipado sem close_capture. Solo salvo sobrescrito: conferir arquivo de save inalterado na retomada dupla.

## Entrega do codificador

Pendente.

## Revisão

Pendente.

## Encerramento

Pendente.

## Entrega e revisão final

- Arquivos: game/app.py, tests/test_app.py e README.md. Alterações anteriores preservadas; sem novas dependências.
- Botão habilita com captura em memória ou save solo. continue_game retorna resume_capture antes de limpar a partida local. Esc e botão compartilham a regra.
- `RUN_GRAPHICS_TESTS=1 .venv/bin/python -m pytest -q`: 136 passaram em 18,68 s.
- Regressão anterior ajustada ao novo requisito: dupla pausada com save solo retoma a mesma sessão, mantém posições e não altera save.
- Novo teste: sem save solo, botão Continuar habilitado e comando real retoma; mesma câmera, coleta, placar e posições preservados; passagem por opções e Esc retoma dupla; anúncio e espera de vitória preservados; Novo jogo muda para solo e Continuar segue carregando solo quando não há captura.
- `git diff --check`: passou sem saída.
- Execução/roteiro: `.venv/bin/python main.py` → Dois jogadores → Jogar; coletar bandeira, Esc, Continuar; repetir passando por Opções. Conferir split, posições e placares. Criar Novo jogo solo, pausar e continuar para conferir retorno solo.
- Reviewer (executor único): conferidos habilitação, retorno antecipado, caminhos de Esc/opções, preservação do save e ciclo de interface/câmeras. Sem achados de código pendentes.
- CA-01 a CA-03: integração offscreen aprovada. CA-04: interação em janela pendente; display :0 indisponível no ambiente, testes offscreen não substituem verificação interativa.
- Parecer e estado final: Validação pendente para CA-04. Documentação atualizada e correção implementada.
