# 019 — Relógios coletáveis de tempo

- Estado: Validação pendente
- Responsável atual: Code reviewer (executor único; perfis em sequência)
- Pedido original: “Faça uns relógios 3D semelhantes em formato a moeda que me dão mais 30s. pelo menos 3 espalhados”

## Objetivo e comportamento esperado

Três relógios circulares com volume, semelhantes às moedas, distribuídos pelo campo. Aproximar-se de cada relógio perto do chão acrescenta exatamente 30 segundos ao cronômetro e remove o item.

## Escopo

- Incluído: malha circular existente com mostrador e ponteiros nas duas faces; giro; coleta única; salvamento; reinício dos itens em nova partida.
- Fora do escopo: novos assets externos, dependências e mudanças no combate.

## Contexto, dúvidas e decisões

- Código existente relacionado: `game/app.py` (malha e animação das moedas), `game/world.py` (itens e coleta), `game/state.py` (tempo e persistência).
- Plataformas e limitações: Panda3D existente; teste offscreen não comprova interação gráfica.
- Dúvidas bloqueantes: nenhuma.
- Hipóteses reversíveis: três posições fixas livres de árvores/água: (6, -4), (-18, -20), (38, 12); mesmo raio de coleta das moedas (1.2) e salto inferior a 1 unidade. Bônus apenas em partida ativa.
- Biblioteca/renderizador: preservar Panda3D e geometria procedural existente.
- Assets e dependências: nenhum novo; limite válido de tempo salvo passa de 120 a 210 segundos (120 + 3 × 30).

## Critérios de aceitação e testes

| ID | Critério observável | Tipo de teste | Entrada/passos | Resultado esperado | Resultado real/evidência |
| --- | --- | --- | --- | --- | --- |
| CA-01 | Três relógios espalhados, fora de obstáculos e água | Automatizado | Conferir posições e distâncias | Três posições livres e distintas | Aprovado: `test_three_clocks_spread_over_clear_ground` |
| CA-02 | Cada coleta concede 30s uma vez | Automatizado | Aproximar, repetir, saltar, ficar longe | +30s por item; até +90s; sem coleta longe/alto | Aprovado: testes em `tests/test_clocks.py` |
| CA-03 | Salvamento preserva bônus e itens; novo jogo repõe os três | Automatizado/integração | Salvar/continuar/reiniciar; save legado | Tempo acima de 120 aceito; coletados não reaparecem; legado compatível | Aprovado: testes de estado, relógios e integração |
| CA-04 | Relógios 3D circulares com mostrador, espessura e giro; HUD atualizado | Integração e manual | Iniciar, observar perto, coletar e continuar | Item reconhecível, giro, desaparecimento e cronômetro +30s | Integração aprovada; captura offscreen inspecionada; interação manual pendente |

## Plano de implementação

1. Adicionar estado, posições, coleta e persistência dos relógios; ajustar limite de tempo salvo.
2. Construir relógios com a extrusão circular das moedas e mostrador procedural nas duas faces; integrar animação e restauração.
3. Testar regras e fluxo offscreen; atualizar README e revisar.

## Riscos e mitigação

- Save antigo rejeitar tempo bonificado: validar até o máximo de 210s e testar retorno.
- Bônus duplicado ao continuar: persistir flags de coleta junto ao tempo.
- Ponteiros invisíveis ao girar: aplicar mostrador em ambas as faces.

## Entrega do codificador

- Arquivos alterados: `game/state.py`, `game/world.py`, `game/app.py`, `tests/test_state.py`, `tests/test_clocks.py`, `tests/test_app.py`, `README.md` e esta demanda.
- Comando para executar: `.venv/bin/python main.py`.
- Comandos de testes e resultados reais:
  - `.venv/bin/python -m pytest -q`: 74 aprovados, 2 ignorados (gráficos).
  - Primeira execução `RUN_GRAPHICS_TESTS=1 .venv/bin/python -m pytest -q`: 75 aprovados, 1 falha na tolerância de dimensão da malha (0.9000015 contra 0.9). Corrigida tolerância do teste para 0.00001; sem alteração no tamanho do item.
  - Execução final `RUN_GRAPHICS_TESTS=1 .venv/bin/python -m pytest -q`: 76 aprovados em 5.72s.
  - Script offscreen com câmera próxima ao primeiro relógio: captura em `/tmp/goblin-clock.png`, inspecionada visualmente; mostrador, aro circular e ponteiros visíveis. Primeira tentativa do script falhou por passar string como diretório de Storage; repetida com Path e concluída.
  - Inspeção de posições com `blocked` e `in_water`: as três livres.
  - `git status --short`: indisponível, diretório `.git` não contém repositório utilizável.
- Roteiro manual: iniciar, conferir mostrador/espessura em movimento, coletar os três e verificar +30s por item, Esc/Continuar, Novo jogo. Detalhado no README.
- Limitações: display `:0` inacessível; integração utilizou renderização offscreen. Não houve validação gráfica interativa. Avisos de cache Panda3D sem acesso de escrita não impediram captura ou testes.

## Revisão

- Parecer: Validação pendente.
- Critérios conferidos: CA-01 a CA-03 atendidos por testes determinísticos e integração; CA-04 possui evidência offscreen e captura, mas falta roteiro interativo.
- Inspecionado o fluxo de criação, coleta, atualização do HUD, salvamento, continuação e reinício. Relógios não estendem partida encerrada nem ressuscitam tempo zerado; moedas e vidas mantêm seus fluxos.
- Achados: nenhum defeito de implementação que exija correção. Tolerância de teste corrigida no papel de codificador antes desta revisão.
- Correções e verificações posteriores: suíte completa com integração aprovada (76 testes).

## Encerramento

- Critérios verificados: CA-01, CA-02, CA-03; parte automatizada e captura de CA-04.
- Testes obrigatórios aprovados: automatizados e integração; manual pendente.
- Revisão aprovada: ainda não; depende da validação interativa.
- Documentação atualizada: README com comportamento e roteiro.
- Resultado comunicado: implementação entregue com limitação gráfica explícita.
