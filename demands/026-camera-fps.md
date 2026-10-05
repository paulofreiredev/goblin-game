# 026 — Alternar primeira e terceira pessoa com F

- Estado: Validação pendente
- Responsável atual: Code reviewer (executor único)
- Pedido original: “de a possibilidade de jogarm em fps ou 3 pessoa usando F pra alternar entre os dois modos”

## Objetivo e comportamento esperado

F alterna durante a partida entre terceira pessoa acompanhando por trás e primeira pessoa na altura dos olhos. Em FPS, mouse controla olhar e WASD/setas movem em relação à visão; salto/corrida/ataque mantidos. Esc abre menu e libera mouse.

## Escopo

- Incluído: troca instantânea, mouse em FPS, mira discreta central, ocultar sprite/sombra próprios em FPS, movimento e ataque relativos ao olhar.
- Fora do escopo: armas, tiro, novos assets e alteração de regras de combate.

## Contexto, dúvidas e decisões

- Código: game/camera.py, game/app.py, game/controls.py.
- Hipóteses reversíveis: F reservado (saves antigos com F em salto/ataque usam padrão válido). Visão apenas por sessão, mantida ao pausar e avançar fase. Câmera a 2 unidades acima dos pés; pitch limitado a ±75 graus. Cursor confinado só em janela durante FPS; offscreen testa orientação por chamada determinística.
- Dependências: nenhuma nova.
- Limitação: mouse físico exige validação interativa.

## Critérios de aceitação e testes

| ID | Critério observável | Tipo de teste | Entrada/passos | Resultado esperado | Resultado real/evidência |
| --- | --- | --- | --- | --- | --- |
| CA-01 | F alterna somente durante jogo/vitória | Integração | Enviar evento F no campo/menu | Câmera correta, sprite oculto em FPS e visível em terceira | Pendente |
| CA-02 | Movimento/ataque em FPS seguem olhar | Automatizado/integração | Olhar para leste e avançar/atacar | Avanço para leste e golpe nessa direção | Pendente |
| CA-03 | FPS acompanha salto/queda e menu libera cursor | Integração/manual | Saltar, Esc e Continuar | Altura correta; cursor livre no menu | Pendente |

## Plano de implementação

1. Reservar F, adicionar orientação e movimento relativos ao olhar.
2. Integrar troca, cursor e mira com ciclo de UI.
3. Executar suíte, conferir capturas/GIF, README e commit.

## Riscos e mitigação

- F em mapeamento antigo conflitar: validar/reservar e testar migração.
- Mouse preso no menu/foco perdido: liberar em Esc, opções, derrota e perda de foco.

## Entrega do codificador

- Arquivos: game/app.py, game/camera.py, game/controls.py, testes de câmera/controles/integração, tools/capture_camera_preview.py, README e capturas/GIF.
- Execução: `.venv/bin/python main.py`.
- `RUN_GRAPHICS_TESTS=1 .venv/bin/python -m pytest -q`: 102 aprovados em 11.01s.
- `.venv/bin/python tools/capture_camera_preview.py`: captura FPS e GIF de troca entre modos, com movimento, usando save temporário.
- Roteiro manual: F em partida e menu; olhar com mouse, mover, atacar, saltar e cair; Esc/liberação do cursor; Continuar; perda/retorno de foco. Não executado por indisponibilidade do display.

## Revisão

- Parecer: Validação pendente. Integração verifica evento F, FPS na altura dos olhos, movimento para leste ao olhar para leste, ataque frontal, altura no salto, limite de pitch e retorno à terceira pessoa/menu.
- Sem defeitos que exijam correção; mouse físico e captura de foco dependem do roteiro interativo.

## Encerramento

- Código, testes e documentação entregues; validação gráfica interativa pendente.
