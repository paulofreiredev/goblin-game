# 020 — Remover piscinas

- Estado: Validação pendente
- Responsável atual: Code reviewer (perfis em sequência pelo executor)
- Pedido original: “pode remover as piscinas”

## Objetivo e comportamento esperado

Remover as quatro piscinas do cenário, recompondo os leitos com o terreno local. Jogador e inimigos passam pelos antigos pontos de água em velocidade normal.

## Escopo

- Incluído: remover superfícies e animação da água, rebaixamentos dos leitos e lentidão; atualizar testes e documentação.
- Fora do escopo: alterar blocos, árvores, combate, relógios ou excluir assets fornecidos.

## Contexto, dúvidas e decisões

- Código existente relacionado: `PONDS`, `terrain_height`, `in_water` em `game/world.py`; criação e atualização da água em `game/app.py`.
- Plataformas e limitações: Panda3D existente; display inacessível na demanda anterior.
- Dúvidas bloqueantes: nenhuma; piscinas interpretadas como as quatro poças existentes.
- Hipóteses reversíveis: manter `PONDS` vazio e `in_water` compatíveis com consumidores existentes; remover processamento gráfico e efeitos de água.
- Biblioteca/renderizador: manter Panda3D.
- Assets e dependências: nenhum novo; imagem de água preservada.

## Critérios de aceitação e testes

| ID | Critério observável | Tipo de teste | Entrada/passos | Resultado esperado | Resultado real/evidência |
| --- | --- | --- | --- | --- | --- |
| CA-01 | Antigos pontos sem água nem leitos rebaixados | Automatizado e manual | Verificar quatro centros e caminhar por eles | Altura igual ao terreno base; sem piscinas | Automatizado aprovado; manual pendente |
| CA-02 | Movimento normal nos antigos pontos | Integração | Andar em (9, 7) por um quadro | Deslocamento 6/60; sem aviso de água | Integração aprovada; aviso removido do fluxo |
| CA-03 | Demais mecânicas preservadas | Automatizado/integração | Executar suíte completa | Testes aprovados, incluindo relógios | 76 aprovados |

## Plano de implementação

1. Remover posições de piscinas, efeitos no terreno e processamento gráfico da água.
2. Ajustar expectativas dos testes e README.
3. Executar suíte completa e revisar alterações; registrar limitação gráfica.

## Riscos e mitigação

- Restar lentidão invisível: remover condição de água do movimento e conferir integração no antigo centro.

## Entrega do codificador

- Arquivos alterados: `game/world.py`, `game/app.py`, `tests/test_combat.py`, `tests/test_app.py`, `README.md` e esta demanda.
- Removidos carregamento da textura, criação das malhas, subdivisões dos leitos, animação e lentidão da água. Áreas antigas agora usam o terreno base, inclusive blocos existentes.
- Comando para executar: `.venv/bin/python main.py`.
- Comandos executados: inspeção com `rg` e `sed`; `RUN_GRAPHICS_TESTS=1 .venv/bin/python -m pytest -q`.
- Resultado: 76 testes aprovados em 5.61s, incluindo integração offscreen, ausência de nós de piscina, velocidade no antigo ponto (9, 7) e relógios.
- Roteiro manual: iniciar, caminhar nos quatro antigos centros (9, 7), (-12, 35), (34, 20), (-38, -28), conferir ausência de água e leitos, movimento normal e demais blocos preservados; salvar/continuar.
- Limitações: roteiro gráfico interativo não executado; display indisponível conforme evidência da demanda 019. Integração offscreen não substitui validação interativa.

## Revisão

- Parecer: Validação pendente.
- Critérios conferidos: regras de terreno, movimento, renderização e atualização sem referências gráficas residuais à água; testes e documentação coerentes com remoção. Relógios preservados e testados.
- Achados: nenhum defeito que exija correção; falta evidência interativa de CA-01.
- Correções e verificações posteriores: não necessárias.

## Encerramento

- Critérios verificados: CA-02 e CA-03; parte automatizada de CA-01.
- Testes obrigatórios aprovados: 76 automatizados/integração; manual pendente.
- Revisão aprovada: depende de validação gráfica interativa.
- Documentação atualizada: README.
- Resultado comunicado: piscinas removidas e testes aprovados; limitação gráfica informada.
