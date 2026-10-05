# 021 — HUD em linha com displays de sete segmentos

- Estado: Validação pendente
- Responsável atual: Code reviewer (executor único, perfis em sequência)
- Pedido original: “O tempo faça na forma 7 segmentos branco com uma grande fonte e desfaça a caixa preta aonde tem vidas moedas e corrações todos devem aparecer em linha, corações exatamente como está moedas e tempo usando display 7 segmentos, mas moeda com o simbolo de moeda ao lado”

## Objetivo e comportamento esperado

HUD em uma linha: cinco corações existentes, símbolo dourado da moeda e contagem, cronômetro MM:SS. Números brancos de sete segmentos, grandes, sem caixa preta.

## Escopo

- Incluído: apresentação do HUD durante jogo e vitória; dígitos procedurais transparentes; atualização de moedas e tempo.
- Incluído após refinamento do usuário: fonte digital semelhante a segmentos também em menus, botões e mensagens, com letras e acentos legíveis.
- Fora do escopo: regras de tempo, vidas e coleta.

## Contexto, dúvidas e decisões

- Código relacionado: `make_hud` e `update_hud` em `game/app.py`; testes de integração existentes.
- Dúvidas bloqueantes: nenhuma.
- Hipóteses reversíveis: manter textura, tamanho e cores dos corações e símbolo da moeda; numerais de 0.14 unidade de altura, alinhados pelo centro com os ícones. Sem prefixo “Tempo”, conforme confirmação explícita do usuário.
- Renderizador: Panda3D existente; gerar textura com Pillow já instalado. Fonte vetorial original gerada localmente com fontTools disponível no Python do sistema; nenhuma dependência nova para executar o jogo.
- Limitação: display interativo indisponível nas demandas anteriores.

## Critérios de aceitação e testes

| ID | Critério observável | Tipo de teste | Entrada/passos | Resultado esperado | Resultado real/evidência |
| --- | --- | --- | --- | --- | --- |
| CA-01 | Uma linha sem caixa preta, corações preservados e símbolo ao lado das moedas | Integração/manual | Iniciar jogo, conferir posições, transparência e captura | Ícones originais, HUD transparente e alinhado | Integração e captura aprovadas; manual pendente |
| CA-02 | Tempo e moedas brancos em sete segmentos, grandes | Integração/visual | Conferir 02:00, 02:30 e coleta de moeda | Dígitos reconhecíveis e brancos; tempo maior que o antigo | Captura inspecionada; integração aprovada |
| CA-03 | Atualização correta e sem regressão de regras | Integração | Coletar moedas/relógios, perder vida, reiniciar | Contagens e cores corretas | Integração aprovada |

## Plano de implementação

1. Gerar dígitos sete segmentos em textura transparente, com cache do último valor.
2. Reorganizar HUD em linha, ajustar testes e README.
3. Executar integração offscreen, inspecionar captura e revisar.

## Riscos e mitigação

- Contagem longa colidir com cronômetro: posicionar tempo após a largura da contagem.
- Regerar texturas a cada quadro: atualizar apenas quando o valor mudar.

## Entrega do codificador

- Arquivos alterados: `game/app.py`, `game/hud.py`, `tools/build_digital_font.py`, `assets/fonts/goblin-digital.ttf`, `tests/test_app.py`, `README.md` e esta demanda.
- Fonte original de traços segmentados com letras maiúsculas, equivalentes para minúsculas e acentos latinos. Carregada em todos os DirectLabels/DirectButtons; norte do minimapa usa a mesma fonte via Pillow.
- Cronômetro sem rótulo; moedas e tempo brancos, 0.14 unidade de altura; corações e moeda mantêm imagens e tamanho. HUD com fundo transparente e centros alinhados. Cronômetro deslocado conforme largura das moedas. Texturas só atualizadas quando os números mudam.
- Comando para executar: `.venv/bin/python main.py`.
- Comandos e resultados reais:
  - Inspeção com `rg` e `sed`; verificação de fontTools no Python do sistema e da venv: disponível apenas no sistema.
  - `/usr/bin/python3 tools/build_digital_font.py`: TTF gerado (23 KB), sem dependência de execução nova.
  - `RUN_GRAPHICS_TESTS=1 .venv/bin/python -m pytest -q`: primeira implementação do HUD, 76 aprovados em 5.86s.
  - Primeira execução após fonte: 74 aprovados, 2 falhas por passar Filename a loadFont; corrigido para str. Execução seguinte: 76 aprovados em 5.41s.
  - Após ampliar verificações de estilo: 75 aprovados e 1 falha do teste ao acessar NodePath como widget; corrigido buscando o DirectFrame correspondente.
  - Execução final `RUN_GRAPHICS_TESTS=1 .venv/bin/python -m pytest -q`: 76 aprovados em 5.40s.
  - Script offscreen: capturas `/tmp/goblin-digital-hud.png` e `/tmp/goblin-digital-menu.png` inspecionadas. HUD em linha transparente com 0 e 02:00 brancos; menu e mensagens com fonte digital. Capturas anteriores ao ajuste do N do minimapa, validado na integração final.
- Roteiro manual: conferir HUD durante movimento, perda de vida, coleta de moeda e relógio; Esc/Continuar; menus e opções com acentos; redimensionar janela. Registrado no README.
- Limitação: display :0 inacessível, integração offscreen disponível; validação interativa não executada.

## Revisão

- Parecer: Validação pendente.
- Critérios conferidos: HUD transparente com ícones originais e numerais grandes; cronômetro sem palavra Tempo; fonte digital em todos os pontos de texto existentes, incluindo minimapa; atualização numérica correta em coleta, continuação e reinício nos testes.
- Achados: nenhum defeito que exija correção. Validação visual interativa e redimensionamento ainda pendentes.
- Correções e verificações posteriores: assinatura de loadFont e acesso do teste ao widget corrigidos pelo codificador; suíte completa final aprovada.

## Encerramento

- Critérios verificados: automatizados e capturas de CA-01 a CA-03; roteiro interativo pendente.
- Testes obrigatórios aprovados: 76 automatizados/integração.
- Revisão aprovada: depende da validação interativa.
- Documentação atualizada: README, com comportamento, origem da fonte e roteiro.
- Resultado comunicado: alteração implementada, sem rótulo de tempo, com limitação gráfica explícita.
