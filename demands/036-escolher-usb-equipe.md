# 036 — Escolher joystick USB por equipe

- Estado: Pronta
- Responsável atual: Executor único, papéis em sequência
- Pedido original: Permita configurar individualmente um joystick USB para Azul e outro para Verde.

## Objetivo e comportamento esperado

Abrir configuração de cada cor diretamente e identificar o joystick físico pressionando um botão nele. Configurar ações separadamente por equipe.

## Escopo

- Incluído: acesso separado Verde/Azul, identificação física, atribuição exclusiva e troca entre equipes, cancelamento.
- Fora do escopo: identificação persistente de hardware entre execuções (controles iguais podem não expor identificador estável). Mapeamentos de ações continuam salvos separadamente.

## Contexto, dúvidas e decisões

game/app.py já separa mapeamentos mas atribui dispositivos automaticamente, sem escolha física. Manter Panda3D e identificação por botão; se controle estiver na outra equipe, trocar dispositivos preservando configurações por cor. Nenhuma nova dependência. Sem dúvida bloqueante.

## Critérios de aceitação e testes

| ID | Critério observável | Tipo de teste | Entrada/passos | Resultado esperado | Resultado real/evidência |
| --- | --- | --- | --- | --- | --- |
| CA-01 | Escolher dispositivo por cor | Integração | Identificar Azul pressionando controle inicialmente Verde | Dispositivos trocados, exclusivos | Pendente |
| CA-02 | Configurações independentes | Integração | Remapear Azul com joystick escolhido | Só Azul muda e é salvo | Pendente |
| CA-03 | Cancelamento e bordas de entrada | Integração | Botão já segurado, soltar/pressionar; Esc | Sem escolha acidental; cancelamento sem trocar | Pendente |
| CA-04 | Uso com dois USB reais | Manual | Configurar ambos e mover jogadores | Cada joystick controla sua cor | Pendente |

## Plano de implementação

1. Acessos diretos por cor e botão de identificação física.
2. Ler novas pressões de botão e atribuir/trocar sem sobrepor dispositivos.
3. Testar e documentar.

## Riscos e mitigação

Botão já pressionado atribuir por acidente: capturar apenas novas pressões. Hardware sem identidade estável: informar seleção por sessão e manter associação durante reconexões conforme fluxo existente.

## Entrega do codificador

Pendente.

## Revisão

Pendente.

## Encerramento

Pendente.

## Entrega e revisão final

- Arquivos: game/app.py, tests/test_app.py, README.md. Alterações anteriores preservadas.
- Interface: acessos USB Verde/USB Azul; botão Escolher joystick mostra dispositivo atribuído; novas pressões de botão identificam o dispositivo. Troca entre equipes mantém mapeamentos vinculados à cor; Esc cancela. Mapeamentos persistem em settings.json; escolha física vale por sessão.
- Execução: `.venv/bin/python main.py` → Dois jogadores → USB Verde/USB Azul → Escolher joystick; pressionar botão físico e configurar ações.
- `RUN_GRAPHICS_TESTS=1 .venv/bin/python -m pytest -q`: primeira execução 131 passaram/1 falhou em 13,83 s por teste antigo exigir nome em DirectLabel. Atualizado para DirectButton, pois nome agora é botão de seleção. Reexecução: 132 passaram em 16,28 s.
- Novo teste confirma atribuição Azul e Verde, exclusividade, botão inicialmente segurado não atribuir, nova pressão atribuir, Esc cancelar, leitura somente do USB escolhido para remapeamento, persistência do mapeamento e associação preservada no scan.
- Script Python inline offscreen com configuração Azul e identificação ativa: captura `/tmp/goblin-escolher-usb.png`, inspecionada; botão de seleção e instrução de pressionar joystick legíveis, sem sobreposição.
- `git diff --check`: passou sem saída.
- Reviewer (executor único): conferidos fluxo de seleção, troca, polling, bloqueio de navegação durante captura, limpeza no menu e cancelamento. Sem achados de código pendentes.
- CA-01 a CA-03: integração aprovada. CA-04: pendente, sem acesso a USB físicos ou display interativo :0 no ambiente.
- Roteiro manual: conectar dois USB, atribuir cada cor por botão, remapear ação distinta em cada, iniciar dupla e verificar independência; repetir com desconexão/reconexão e controles de mesmo nome.
- Parecer e estado final: Validação pendente para CA-04. Testes e imagem offscreen não substituem uso interativo com hardware real.
