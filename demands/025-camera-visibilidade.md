# 025 — Câmera em terceira pessoa com personagem visível

- Estado: Validação pendente
- Responsável atual: Code reviewer (executor único, perfis em sequência)
- Pedido original: “ajuste a camera para que o personagem nunca fique oculto”

## Objetivo e comportamento esperado

Manter o personagem enquadrado e visível enquanto caminha, salta e cai, inclusive perto de árvores e degraus. Aproximar a câmera quando houver obstáculos entre ela e o personagem.

## Escopo

- Incluído: detecção de obstruções por volumes das árvores e altura do terreno; distância adaptativa; proteção de visibilidade do sprite.
- Fora do escopo: mapas, fases e regras de combate.

## Contexto, dúvidas e decisões

- Código relacionado: game/app.py, game/world.py e malhas das árvores.
- Dúvidas bloqueantes: nenhuma.
- Hipóteses reversíveis: preservar posição padrão atrás ao sul, distância 20 e altura 7. Usar volumes de cada árvore/pedra, margem de segurança e testar o terreno a cada 0.25 unidade. Se espaço próximo for insuficiente, usar posição elevada próxima; sprite renderizado acima do cenário garante visibilidade residual.
- Renderizador: Panda3D existente; cálculos independentes de janela em game/camera.py.
- Assets/dependências: nenhum novo.
- Limitação: display interativo indisponível nas verificações anteriores.

## Critérios de aceitação e testes

| ID | Critério observável | Tipo de teste | Entrada/passos | Resultado esperado | Resultado real/evidência |
| --- | --- | --- | --- | --- | --- |
| CA-01 | Câmera aproxima diante de árvore/parede e fica acima do solo | Automatizado/integração | Volume entre câmera e alvo, terreno elevado | Câmera no lado livre, altura segura | Pendente |
| CA-02 | Sprite enquadrado e visível em árvores, salto e queda | Integração/captura/manual | Explorar bosque e degraus | Sprite visível; alvo acompanha pés | Pendente |
| CA-03 | Sem regressão de regras e fases | Integração | Suíte completa | Aprovada | Pendente |

## Plano de implementação

1. Isolar cálculos de obstrução e posição em game/camera.py.
2. Extrair volumes das malhas existentes e integrar atualização da câmera e visibilidade do sprite.
3. Testar, conferir captura, atualizar README e criar commit desta funcionalidade.

## Riscos e mitigação

- Suavização atravessar obstáculo: aplicar restrição depois de suavizar a posição.
- Volume conservador de copa bloquear espaço vazio: fallback próximo elevado e sprite sem teste de profundidade.

## Entrega do codificador

- Arquivos: game/camera.py, game/app.py, tests/test_camera.py, README.md, docs/images/camera-terceira.png e camera-bosque.png, esta demanda.
- Comando: `.venv/bin/python main.py`.
- Testes: `RUN_GRAPHICS_TESTS=1 .venv/bin/python -m pytest -q`: 98 aprovados em 8.41s.
- Script offscreen com save temporário: capturas em docs/images; personagem em (-11,9), atualização do alvo e da câmera diante de bosque. Captura inspecionada.
- Cálculo usa caixas de cada malha de árvore/pedra, terreno a cada 0.25 unidade, margem 0.3/0.4 e proteção de profundidade do sprite. Restrição aplicada após suavização.
- Roteiro manual: caminhar entre árvores e diante de paredes; correr, saltar, subir e cair de degraus; conferir enquadramento contínuo. Não executado: display indisponível.

## Revisão

- Parecer: Validação pendente.
- Evidências: testes de segmento paralelo, contato, alvo interno, campo livre, árvore, parede, espaço curto e altura durante queda; integração completa aprovada; captura de bosque inspecionada.
- Achados: nenhum defeito que exija correção. Sprite sobreposto ao cenário é decisão explícita para cumprir visibilidade residual, inclusive nos volumes conservadores de copa.

## Encerramento

- Implementação, testes e captura entregues; README atualizado; validação gráfica interativa pendente.

## Ajuste solicitado pelo usuário

- Pedido: “ficou péssimo, não é pra ficar em cima do personagem só mudar a possição da camera pra acompahar”.
- Refeito o acompanhamento para posição traseira relativa à direção do movimento. Rotação suavizada pelo ângulo, mantendo raio; não interpolar posições em linha reta através do personagem.
- Removidos fallback sobre o personagem e renderização do sprite por cima de obstáculos. Preferir posições traseiras/laterais livres; obstruções remanescentes das árvores são atenuadas com transparência temporária.
- Tests reavaliam distância, altura, posição lateral livre, rotação angular e altura na queda.
