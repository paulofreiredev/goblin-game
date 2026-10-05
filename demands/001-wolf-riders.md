# 001 — Wolf Riders: campo 3D, personagem, menu e música

- Estado: Validação pendente
- Responsável atual: validação manual gráfica/auditiva
- Pedido original: controlar o personagem de wolf_riders em campo verde, com animações, tema musical e menu Novo jogo, Continuar e Opções de som.

## Refinamento

Objetivo: explorar um campo com o cavaleiro montado, controlado pelo jogador. Hipótese: “controlado pelo boneco” significa controle por teclado do personagem fornecido. WASD/setas movimentam; Shift corre. Continuar retoma posição persistente. Novo jogo reinicia e substitui o save. Som é uma preferência persistente.

Escopo: menu, campo 3D, câmera fixa em orientação com acompanhamento, sprites nas oito direções, repouso/deslocamento/corrida, música e save. Fora do escopo: combate, missões, modelo 3D do personagem, inventário e gamepad.

Decisão: Panda3D 1.10.16 fornece cena, câmera, interface e áudio sem integrar renderizadores separados. O asset é PNG RGBA 5376×1024, com 42×8 células de 128 px. O personagem será um billboard animado dentro da cena 3D; não há modelo com esqueleto disponível. Repouso usa coluna 0; deslocamento usa 4–11; corrida acelera o mesmo ciclo. Mapeamento identificado por inspeção visual, sem metadados de animação fornecidos.

## Critérios e testes

| ID | Critério | Verificação | Evidência |
| --- | --- | --- | --- |
| CA-01 | Menu inicial antes de jogar, com Novo jogo/Continuar/Opções | Integração e captura do menu; Continuar desabilitado sem save | Captura inspecionada; teste gráfico registrado abaixo |
| CA-02 | Novo jogo inicia no campo verde 3D usando wolf_riders | Integração, captura e inspeção visual | Campo, sprite, sombra e UI vistos em captura |
| CA-03 | Andar/correr em oito direções, repousar, sem diagonal mais rápida | Testes de lógica, integração e roteiro interativo | 16 testes de lógica aprovados; roteiro humano pendente |
| CA-04 | Continuar recupera posição e Novo jogo reinicia | Persistência e integração | Teste de persistência aprovado; integração registrada abaixo |
| CA-05 | Tema em loop; opção de som persistente | Carregamento, integração de opções e audição humana | Tema carregado na execução gráfica sem erro; audição humana pendente |
| CA-06 | Esc pausa/salva; encerrar libera recursos | Integração e roteiro de fechamento | Execução offscreen encerrada com destroy; fechamento interativo pendente |

## Plano executado

1. Criar lógica de movimento e Storage independente da engine.
2. Montar campo, billboard direcional e câmera; carregar sprites sem alterar o original.
3. Implementar menu, opções, música, autosave e recuperação de dados inválidos.
4. Adicionar testes, executar integração gráfica e inspecionar capturas.
5. Revisar e documentar limitações.

## Entrega

Arquivos: main.py, game/state.py, game/app.py, testes, requirements e README. Execução: `.venv/bin/python main.py`. Dados em `.local/`. Dependências instaladas em venv local. Não foi definida meta de FPS: cena de protótipo sem hardware de referência exigido.

Verificações realizadas:
- `.venv/bin/python -m pytest -q`: 16 aprovados, 1 integração gráfica ignorada por padrão.
- Execução offscreen com acesso à tela/áudio: menu, novo jogo, um passo de movimento, capturas, opções, alternância de som e encerramento sem exceção.
- `/tmp/wolf-game.png` e `/tmp/wolf-menu.png` inspecionados visualmente. Corrigido separador de texto ausente na fonte; reduzida altura da câmera para abrir a perspectiva.

## Revisão

Papéis de refinador, codificador e reviewer assumidos sequencialmente pelo mesmo executor. Lógica, orientação das oito direções, normalização, persistência e rotas do menu revisadas. Sem achado bloqueante identificado até aqui; aprovação final depende das validações interativas e audíveis.

Riscos concretos: sprite fornecido tem resolução limitada quando ampliado; nomes das animações foram inferidos visualmente. Verificação offscreen não mede qualidade sonora nem testa teclado físico. Erros de escrita são exibidos ao usuário; saves inválidos desabilitam Continuar.

## Roteiro pendente

Executar conforme README: menu inicial, oito direções, Shift, repouso, Esc, Continuar, reinício do aplicativo, som desligado/ligado e fechamento da janela. Confirmar alinhamento visual e audição real. Não marcar demanda concluída sem essas evidências.

## Verificação posterior

A suíte da demanda 002 inclui a regressão de menu, opções, Novo jogo e Continuar: 25 testes aprovados com integração gráfica habilitada. A perda de foco foi alterada na demanda 002 para manter o jogo em execução ao tirar Print Screen.
