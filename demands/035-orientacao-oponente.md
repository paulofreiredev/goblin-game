# 035 — Orientação do personagem na câmera do oponente

- Estado: Pronta
- Responsável atual: Executor único, papéis em sequência
- Pedido original: Na tela do oponente o personagem fica andando de costas ou de lado.

## Objetivo e comportamento esperado

Cada câmera mostra frente, costas ou lateral do personagem conforme a direção dele e a posição de quem observa, com animação e salto sincronizados.

## Escopo

- Incluído: sprites independentes por câmera no modo de dois jogadores; preservação de FPS e limpeza ao sair/reiniciar.
- Fora do escopo: alterar controles, movimento, assets e modo solo.

## Contexto, dúvidas e decisões

- game/app.py escolhe uma textura por personagem usando somente a câmera do próprio jogador. A mesma textura é exibida ao oponente.
- Manter Panda3D, billboard e folha existente. Criar duas representações por personagem, cada uma visível apenas para uma câmera. Calcular orientação pela posição real de cada câmera após atualizá-las.
- Sem dúvidas bloqueantes ou dependências adicionais. Preservar alterações anteriores do usuário.

## Critérios de aceitação e testes

| ID | Critério observável | Tipo de teste | Entrada/passos | Resultado esperado | Resultado real/evidência |
| --- | --- | --- | --- | --- | --- |
| CA-01 | Orientação correta nas duas vistas | Integração | Observar ambos os personagens de lados opostos e laterais | Texturas seguem observador; mesmo quadro de animação e altura | Pendente |
| CA-02 | FPS e ciclo de vida preservados | Integração | Alternar F, reiniciar e sair para solo | Próprio personagem oculto no FPS; oponente visível; sem sprites residuais | Pendente |
| CA-03 | Aparência durante movimento | Manual | Andar frente/trás/lados e girar câmeras em terceira pessoa e FPS | Corpo acompanha direção real nas duas telas | Pendente |

## Plano de implementação

1. Criar sprites por observador com máscaras de câmera e limpeza explícita.
2. Atualizar texturas após posicionar ambas as câmeras.
3. Testar orientação, animação, salto, FPS e saída; registrar evidências.

## Riscos e mitigação

Sprites duplicados ou máscara residual no solo: isolar visibilidade e restaurar sprite original na saída. Escolha de textura antes da câmera: atualizar após ambas as posições finais.

## Entrega do codificador

Pendente.

## Revisão

Pendente.

## Encerramento

Pendente.

## Entrega e evidências finais

- Arquivos: game/app.py, tests/test_app.py, README.md. Nenhuma dependência nova; mudanças anteriores preservadas.
- Execução: `.venv/bin/python main.py`.
- Primeiro comando `RUN_GRAPHICS_TESTS=1 .venv/bin/python -m pytest -q`: 130 passaram e 1 falhou em 15,10 s. O teste encontrou máscara do actor herdada do FPS ao recriar rodada. Corrigido restaurando todas as máscaras na saída.
- Reexecução do mesmo comando: 131 passaram em 15,65 s. Teste novo cobre oito posições de câmera, ambas as equipes, texturas independentes, animação/altura sincronizadas, isolamento por câmera, FPS, reinício e saída para solo.
- `git diff --check`: passou sem saída.
- Script Python inline com Game(offscreen=True), posições (0,-25)/(6,-25), direção oeste e câmeras opostas: captura `/tmp/goblin-orientacao.png`. Imagem inspecionada: mesmas direções físicas vistas por frente e costas nas respectivas telas, sem sobreposição de sprites.
- Ambiente não abre display :0; renderização offscreen funciona. Roteiro interativo não executado: abrir dupla, mover ambos para frente/trás/lados, girar câmeras, saltar, alternar F, pausar/continuar e reiniciar; conferir direção do oponente nas duas vistas.

## Revisão final

- Executor assumiu reviewer após implementação: conferidos posição final de ambas as câmeras, orientação pelo observador, quadros/altura, máscaras, ocultação do próprio actor no FPS e remoção dos nós adicionais.
- Achado corrigido: máscara herdada na recriação após FPS; reexecução aprovada.
- CA-01 e CA-02: integração aprovada; CA-03 permanece pendente.
- Parecer: Validação pendente para interação em janela; captura e testes offscreen não substituem essa verificação.

## Encerramento atualizado

- Estado final: Validação pendente.
- Documentação atualizada e correção implementada; interação gráfica permanece pendente.
