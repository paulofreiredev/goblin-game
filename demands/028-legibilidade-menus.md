# 028 — Menus em tela cheia e contraste do HUD

- Estado: Validação pendente
- Responsável atual: Code reviewer (executor único, perfis em sequência)
- Pedido original: textos ilegíveis, contraste ruim no céu da manhã, referência `docs/image.png`, popup cobrindo toda a tela.

## Objetivo e comportamento esperado

Menus em tela cheia com letras grandes e espaços entre botões. Configuração USB em duas colunas largas. HUD branco com contorno escuro, fundo transparente e corações preservados.

## Escopo

- Incluído: tipografia, fundo de menus, espaçamento, alinhamento e contorno de dígitos.
- Fora do escopo: alterar regras, substituir fonte digital dos números ou recolocar caixa preta no HUD.

## Contexto, dúvidas e decisões

- Referência do usuário inspecionada: docs/image.png; labels e botões em painel estreito, muito pequenos e com traços finos.
- Decisão: fonte monoespaçada DejaVu Sans Mono Bold legível em labels/botões, mantendo título digital e sete segmentos numéricos. Fonte incluída com licença em assets/fonts/menu-mono-LICENSE.txt; nenhuma dependência nova.
- Fundo relativo a render2d cobre a janela inteira independentemente da proporção; duas colunas nas opções e USB, com largura maior e intervalos verticais.
- HUD: contorno escuro de três pixels no asset numérico, mantendo áreas transparentes.
- Dúvidas bloqueantes: nenhuma.

## Critérios de aceitação e testes

| ID | Critério observável | Tipo de teste | Entrada/passos | Resultado esperado | Resultado real/evidência |
| --- | --- | --- | --- | --- | --- |
| CA-01 | Menus legíveis em tela cheia | Captura/manual | Abrir opções e USB | Texto grande, sem botões comprimidos | Capturas inspecionadas; manual pendente |
| CA-02 | Números brancos legíveis no céu claro | Captura/manual | Iniciar manhã | Contorno escuro e HUD sem caixa | docs/images/hud-contraste.png inspecionada |
| CA-03 | Sem regressão de ações/controles | Integração | Suíte completa | Aprovada | 105 aprovados em 13.88s antes do teste adicional de direções |

## Plano de implementação

1. Inspecionar imagem enviada; adotar fonte legível e painel de tela inteira.
2. Reorganizar botões e reforçar contraste de dígitos.
3. Gerar capturas, testar e atualizar README.

## Riscos e mitigação

- Fonte de sistema indisponível em outra máquina: incluir TTF e licença no projeto.
- Fundo não cobrir janelas largas: usar render2d e dimensões normalizadas de tela.

## Entrega do codificador

- Arquivos: game/app.py, game/hud.py, assets/fonts/menu-mono.ttf e licença, capturas docs/images/controle-usb.png, opcoes-controle.png, hud-contraste.png, README.
- Comando: `.venv/bin/python main.py`.
- Suíte e capturas offscreen executadas, com save temporário para preservar partida do usuário.
- Roteiro manual: menu/opções/USB em resoluções diferentes, capturar botões e conferir HUD em manhã/tarde/noite. Interação pendente.

## Revisão

- Parecer: Validação pendente. Capturas mostram telas inteiras com texto legível e dígitos brancos contornados; HUD continua transparente.
- Achados: nenhum que exija correção. Tipografia de textos comuns alterada deliberadamente em resposta ao requisito de legibilidade mais recente.

## Encerramento

- Implementação e capturas entregues; roteiro interativo pendente.

## Evidências e revisão atualizadas

`RUN_GRAPHICS_TESTS=1 .venv/bin/python -m pytest -q`: **109 passaram em 17,58 s**. Revisão do fluxo de captura, persistência e carregamento; testes cobrem troca de todas as combinações de entradas, Start/B e eixos. A rejeição de entradas ocupadas foi substituída por troca conforme demanda 029. Start abre menu, direcional navega e B confirma em teste simulado. Capturas offscreen mostram menus em tela cheia. Parecer: **Validação pendente**, pois não há janela interativa nem controle físico neste ambiente. O usuário confirmou que o USB funciona em seu computador.
