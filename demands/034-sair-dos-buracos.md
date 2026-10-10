# 034 — Salto para sair de todos os buracos

- Estado: Revisão
- Responsável atual: Executor único, papéis em sequência
- Pedido original: Ao cair num buraco fiquei preso; não deve ser possível ficar preso em buraco nenhum; o boneco deve pular alto o suficiente para sair.

## Objetivo e comportamento esperado

Permitir que ambos os modos saiam de todas as depressões saltando em direção à borda, inclusive pelas paredes sem escadas.

## Escopo

Incluído: impulso suficiente no interior das depressões e colisão permitindo alcançar terreno de altura zero. Fora do escopo: alterar salto em terreno plano, regras de subida das elevações e dano de queda.

## Contexto, dúvidas e decisões

- Inspeção: game/state.py usa impulso 8 e gravidade 20 (altura máxima 1,6); game/world.py limita toda subida a 0,8. Há buracos de 1,6 e 2,4, um sem escadas.
- Refinamento: aumentar impulso conforme profundidade do apoio, com margem de altura 0,6. Permitir transições ascendentes dentro da depressão e até altura zero quando os pés ultrapassarem a borda; preservar limite nas elevações.
- Biblioteca: Panda3D existente, sem novos assets ou dependências. Sem dúvidas bloqueantes.

## Critérios de aceitação e testes

| ID | Critério observável | Tipo de teste | Entrada/passos | Resultado esperado | Resultado real/evidência |
| --- | --- | --- | --- | --- | --- |
| CA-01 | Sair dos dois buracos pelos quatro lados | Automatizado | Saltar junto a cada borda e avançar | Atingir exterior e aterrissar sem dano | Oito casos passaram |
| CA-02 | Preservar colisão e salto único | Automatizado | Andar contra borda e tentar salto duplo | Parede bloqueia caminhada; salto duplo bloqueado | Oito casos passaram |
| CA-03 | Preservar elevações e quedas | Automatizado | Testes existentes de combate | Regras anteriores preservadas | Suíte sem janela: 116 passaram, 14 ignorados |
| CA-04 | Saída jogável e visível | Manual | Em solo e dupla, cair nos dois buracos e saltar avançando por cada lado | Sair sem ficar preso | Pendente |

## Plano de implementação

1. Ajustar impulso em jump_player e autorização de subida em move_on_terrain.
2. Testar bordas das depressões, aterrissagem e regressões; atualizar README.

## Riscos e mitigação

Permitir escalar elevações por acidente: exceção limitada a apoio negativo e destino até zero; testes de subida de elevações mantidos.

## Entrega do codificador

- Arquivos: game/world.py, tests/test_combat.py e README.md.
- Executar: .venv/bin/python main.py.
- Testes: .venv/bin/python -m pytest -q — 116 passaram, 14 ignorados em 0,34 s.
- Roteiro interativo: CA-04 ainda não executado.

## Revisão

- Inspecionado impulso, altura dos pés, colisão, dano e regressões. Nenhum achado de código.
- Parecer: Validação pendente para CA-04; testes sem janela não substituem interação.

## Encerramento

- Estado final: Validação pendente.
- Documentação atualizada; validação manual permanece necessária.

## Verificação final complementar

- `RUN_GRAPHICS_TESTS=1 .venv/bin/python -m pytest -q`: 130 passaram em 14,26 s, incluindo integrações dos modos solo e dupla.
- `git diff --check`: passou sem saída.
- Contexto gráfico interativo indisponível: display :0 não abre. CA-04 permanece pendente; testes offscreen aprovados não validam a experiência interativa.
