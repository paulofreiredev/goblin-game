# 032 — Split screen, dois controles USB e todas as bandeiras

- Estado: Validação pendente
- Responsável atual: Executor único
- Pedido original: dois controles configuráveis, bandeiras menores que personagens, split de duas telas, sem tempo, terminar ao capturar todas as bandeiras.

## Objetivo e comportamento esperado

Duas vistas em split horizontal, Verde acima e Azul abaixo, câmera acompanhando cada personagem. USB 1 controla Verde e USB 2 controla Azul, com configurações independentes persistentes. Conforme correção posterior do usuário: 3/8/12 bandeiras por cor, dependendo do nível, espalhadas aleatoriamente. Verde coleta verdes; Azul coleta azuis. Vence quem coleta todas da própria cor. Nenhum cronômetro.

## Escopo

Incluído: segundo dispositivo, captura/configuração por equipe, split, regras e imagens. Preservar teclado configurável, caça solo e save. Fora: rede.

## Contexto, dúvidas e decisões

Refinamento da demanda 030: substitui câmera compartilhada e regra de bases por duas vistas horizontais e busca de bandeiras por cor. Fácil=3, médio=8 e difícil=12 por cor, conforme requisito explícito. Nenhum retorno a base ou transporte. Bandeiras com metade da altura do sprite do personagem. Sem mapa ou cronômetro nesse modo. Panda3D existente; zero dependências. Hardware USB real indisponível no ambiente.

## Critérios de aceitação e testes

| ID | Critério observável | Tipo de teste | Entrada/passos | Resultado esperado | Resultado real/evidência |
| --- | --- | --- | --- | --- | --- |
| CA-01 | Configuração independente de dois USB | Integração simulada/manual | Mapear e mover dois dispositivos | Cada USB controla sua equipe | Pendente |
| CA-02 | Duas vistas com câmeras próprias | Integração/captura/manual | Jogar e voltar à caça | Split local; solo restaura vista única | Pendente |
| CA-03 | Bandeiras menores e captura de todas | Automatizado/visual | Coletar 3/8/12 da própria cor | Cada uma desaparece ao tocar; última encerra; sem tempo ou mapa | Pendente |
| CA-04 | Start de ambos pausa | Integração/manual | Start no USB azul e verde | Menu pausa ambos | Pendente |

## Plano de implementação

Refinar capture.py para 3/8/12 bandeiras por cor; adicionar segundo polling/configuração e câmeras; testar independência, vitória e retorno ao solo; atualizar GIF/README.

## Riscos e mitigação

DisplayRegion residual no solo: remover segunda câmera e restaurar dimensões/lente. USB remapear equipe errada: seleção visível e bindings separados. Controles físicos: validar posteriormente no computador do usuário.

## Entrega do codificador

Pendente.

## Revisão

Pendente.

## Encerramento

Pendente.

## Correção explícita de requisitos

Pedido posterior: bandeiras aleatórias por nível, cada jogador coleta sua própria cor, split horizontal, metade do personagem, sem mapa. Esta definição substitui as regras de captura em base registradas na demanda 030 e no refinamento inicial da 032.

## Entrega e revisão do comportamento final

- Implementação: game/capture.py distribui bandeiras aleatoriamente em terreno acessível, separa cores, coleta por contato, mantém contagem por nível e encerra ao completar a própria cor. game/app.py cria regiões superior/inferior, duas câmeras, dois dispositivos/mapeamentos USB, seleção Verde/Azul e placares individuais; não cria cronômetro ou minimapa local. F funciona nas duas vistas e oculta o personagem próprio somente em sua câmera. Start de qualquer USB pausa.
- Recursos: saída para solo remove display region/câmera secundária, restaura lente e máscara originais; camList não acumula câmeras removidas. Desconexão do USB Verde não transfere USB Azul para a equipe errada.
- Bandeiras: poste de 4 unidades reduzido a 1,705, metade da altura de 3,41 do sprite. Billboard em torno do eixo vertical evita bandeiras invisíveis quando vistas de lado.
- Evidências: testes determinísticos verificam 3/8/12 por cor, distribuição acessível, coleta apenas da própria cor, ambas as equipes podendo vencer, salto não coletando à distância vertical; integração simula dois USB, remapeamento independente/persistência, movimento independente, Start azul, vitória, dimensões horizontais, escala exata e retorno ao solo. Teste de desconexão/reconexão preserva equipes. Capturas e GIF regenerados por tools/capture_local_preview.py; imagem inspecionada com Verde acima, Azul abaixo, placares separados e sem mapa/tempo.
- Roteiro manual pendente: conectar dois USB reais; configurar cada um pela seleção no topo; escolher nível; verificar cada personagem, girar, saltar e correr; Start em ambos, direcional/B; retomar; coletar apenas a própria cor e terminar. Reiniciar aplicativo e conferir mapeamentos. Sem janela interativa ou /dev/input no ambiente; não declarar esse roteiro executado.
- Parecer: **Validação pendente** para hardware/interação; regras, integração offscreen e documentação revisadas. Sem achado bloqueante após restauração correta da máscara de câmera.

## Verificação final

`RUN_GRAPHICS_TESTS=1 .venv/bin/python -m pytest -q`: **120 passaram em 23,50 s**. `git diff --check`: sem erros. `.venv/bin/python tools/capture_local_preview.py`: executado, prints e GIF atualizados. README explica os requisitos finais, dois controles e retomada. Validação gráfica interativa continua pendente conforme WORKFLOW.md.
