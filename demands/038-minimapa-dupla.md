# 038 — Minimapa dos dois jogadores

- Estado: Pronta
- Responsável atual: Executor único, papéis em sequência
- Pedido original: Põe um mapinha para os jogadores saberem onde está o outro.

## Objetivo e comportamento esperado

Exibir um pequeno mapa no canto superior direito de cada metade da tela, mostrando as posições Verde e Azul e as áreas elevadas/deprimidas como referência. Norte permanece para cima.

## Escopo

- Incluído: dois minimapas iguais com marcadores de ambas as cores atualizados durante partida, pausa/retomada e reinício.
- Fora do escopo: revelar bandeiras, alterar mapa solo ou regras.

## Contexto, dúvidas e decisões

- Código: game/app.py já tem mapa solo; modo captura tem interface separada. Preservar alterações anteriores.
- Nova instrução substitui decisão anterior de não ter mapa na dupla. Usar Panda3D/Pillow existentes, textura estática compartilhada e marcadores GUI móveis para evitar gerar imagem a cada quadro.
- Sem dúvidas bloqueantes, assets ou dependências adicionais. Um mapa por metade permite consulta sem olhar para tela do oponente.

## Critérios de aceitação e testes

| ID | Critério observável | Tipo de teste | Entrada/passos | Resultado esperado | Resultado real/evidência |
| --- | --- | --- | --- | --- | --- |
| CA-01 | Mapa por metade com ambas as posições | Integração/visual | Iniciar dupla | Dois mapas e dois marcadores por mapa | Pendente |
| CA-02 | Movimento e limites corretos | Integração | Mover jogadores e colocá-los nos extremos do campo | Marcadores acompanham X/Y com norte acima, dentro do mapa | Pendente |
| CA-03 | Ciclo de vida preservado | Integração | Pausar/continuar, reiniciar e sair para solo | Mapas atualizados, nós anteriores removidos, solo preservado | Pendente |
| CA-04 | Legibilidade em partida | Manual | Jogar com dois jogadores e consultar mapas | Localização clara sem cobrir placares | Pendente |

## Plano de implementação

1. Criar textura de campo/terreno e painéis em cada metade.
2. Atualizar marcadores com posições atuais após movimento.
3. Testar ciclo de vida e limites, inspecionar captura, atualizar README.

## Riscos e mitigação

Sobreposição de marcadores: verde maior que azul, permitindo perceber ambos no mesmo ponto. Sobrecarga por imagens dinâmicas: criar textura somente ao montar interface, mover nós a cada quadro.

## Entrega do codificador

Pendente.

## Revisão

Pendente.

## Encerramento

Pendente.

## Entrega e evidências

- Arquivos: game/app.py, tests/test_app.py, README.md; sem novos assets/dependências. Alterações anteriores preservadas.
- Mapas quadrados de campo inteiro no canto superior direito de cada metade. Uma textura estática para terreno; marcadores GUI Verde/Azul atualizados com posições reais após movimento/colisão. Norte fixo acima. Nenhuma imagem é gerada no update por quadro.
- Script Python inline usando Game(offscreen=True), posições (-20,10)/(30,-40), renderFrame e saveScreenshot: captura `/tmp/goblin-minimapa-dupla.png`. Imagem inspecionada: mapas legíveis nas duas metades, cores corretas e terreno de referência, sem sobreposição com placares.
- Primeira execução `RUN_GRAPHICS_TESTS=1 .venv/bin/python -m pytest -q`: 134 passaram e 1 falhou em 27,19 s. Teste novo esperava centro do jogador exatamente no limite do campo, mas colisão limita posição pelo raio do corpo; corrigido para conferir posição real e permanência dentro do mapa.
- Reexecução inicial após editar teste falhou na coleta por erro de indentação; corrigido antes da verificação final.
- `git diff --check`: passou sem saída.
- Executar: `.venv/bin/python main.py` → Dois jogadores → Jogar. Roteiro manual: movimentar ambos, consultar marcadores, aproximar jogadores até sobreporem posições, pausar/continuar e vencer para reiniciar.
- Ambiente offscreen funcional; display :0 indisponível. Roteiro interativo CA-04 ainda não executado.

## Revisão técnica

- Executor assumiu reviewer: conferidos escala pixel/campo/GUI, sinal de Y (norte acima), posições das duas metades, ausência de dependência de orientação da câmera e destruição dos painéis/filhos por clear_ui.
- CA-01 a CA-03 cobertos por integração: criação, posições intermediárias, extremos e sobreposição, cores, pausa/retomada, reinício e mapa solo preservado.
- Sem achados de código pendentes. Parecer: Validação pendente para CA-04 interativo.

## Encerramento atualizado

- Estado final: Validação pendente.
- Documentação atualizada; implementação pronta para validação jogando em janela.

- Verificação final: `RUN_GRAPHICS_TESTS=1 .venv/bin/python -m pytest -q` — 135 testes passaram em 27,19 s. CA-01 a CA-03 aprovados na integração offscreen; CA-04 permanece pendente.
