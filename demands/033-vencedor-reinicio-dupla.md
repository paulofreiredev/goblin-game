# 033 — Vencedor em destaque e reinício da dupla

- Estado: Pronta
- Responsável atual: Codificador (executor único, papéis em sequência)
- Pedido original: No jogo de dois precisa aparecer grande na tela quem venceu e depois de 2 segundos começar novamente.

## Objetivo e comportamento esperado

Ao coletar todas as bandeiras da própria cor, mostrar VERDE VENCEU! ou AZUL VENCEU! grande no centro da tela. Manter o resultado por dois segundos de jogo ativo e iniciar automaticamente nova rodada.

## Escopo

- Incluído: anúncio central, espera e reinício com placares zerados, jogadores nas bases e novas bandeiras no mesmo nível.
- Fora do escopo: alterações nas regras, controles ou modo solo.

## Contexto, dúvidas e decisões

- Código existente relacionado: game/app.py, game/capture.py e tests/test_app.py.
- Manter Panda3D e fontes existentes; nenhuma dependência ou asset adicional.
- Sem dúvidas bloqueantes. Pausa no menu suspende a espera; continuar restaura o anúncio.
- Usar tempo decorrido real do quadro para a espera, separado do passo limitado de movimento. Começar a contar após detectar a vitória.

## Critérios de aceitação e testes

| ID | Critério observável | Tipo de teste | Entrada/passos | Resultado esperado | Resultado real/evidência |
| --- | --- | --- | --- | --- | --- |
| CA-01 | Ambas as equipes têm anúncio grande | Integração e manual | Coletar todas as bandeiras da cor | Anúncio central com equipe correta | Pendente |
| CA-02 | Reinício após dois segundos | Integração | Avançar 1,99 s e depois 0,01 s | Antes mantém resultado; aos 2 s nova rodada zerada no mesmo nível | Pendente |
| CA-03 | Pausa e saída preservam ciclo de vida | Integração | Pausar/continuar e sair para solo | Anúncio restaurado; interface removida ao sair | Pendente |
| CA-04 | Legibilidade e fluxo gráfico | Manual | Jogar, vencer, observar espera e nova rodada | Texto grande legível nas duas vistas; reinício sem erros | Pendente |

## Plano de implementação

1. Adicionar anúncio à interface local e contador reinicializado por rodada.
2. Integrar espera ao update com tempo real; usar new_capture para reconstruir a rodada.
3. Testar ambas as equipes, limites temporais, pausa e recursos; atualizar README.

## Riscos e mitigação

Contar o quadro anterior à vitória reduziria a exibição: iniciar contador na detecção. Reconstrução de câmeras: usar ciclo de limpeza existente e conferir quantidade de câmeras.

## Entrega do codificador

Pendente.

## Revisão

Pendente.

## Encerramento

Pendente.

## Evidências finais e revisão

- Arquivos alterados: game/app.py, tests/test_app.py e README.md.
- `.venv/bin/python -m pytest -q`: 116 passaram, 14 ignorados, 0,34 s.
- `RUN_GRAPHICS_TESTS=1 .venv/bin/python -m pytest -q`: 130 passaram, 14,26 s. Integração offscreen verifica ambas as cores, anúncio maior que placar, tempo real independente do passo de movimento, limite 1,99/2 s, pausa/retomada, placares, bandeiras, bases, nível e ausência de acúmulo de câmeras.
- Captura offscreen por script Python inline com armazenamento temporário: `/tmp/goblin-vencedor.png`; imagem inspecionada, anúncio AZUL VENCEU! grande e central, legível sobre as duas vistas.
- `git diff --check`: passou sem saída.
- CA-01 a CA-03: integração aprovada; CA-04 ainda requer jogar interativamente. Ambiente não abre display :0; renderização offscreen funciona, sem substituir interação.
- Roteiro: `.venv/bin/python main.py`, Dois jogadores → Jogar; vencer com cada cor, observar 2 segundos e reinício; pausar durante o anúncio, continuar e conferir espera restante.
- Revisão pelo executor no papel de reviewer: fluxo de vitória, interface, cronômetro e limpeza conferidos; nenhum achado de código. Parecer: Validação pendente para interação gráfica.
- Estado final: Validação pendente.
