# 027 — Controle USB e tela de configuração

- Estado: Validação pendente
- Responsável atual: Codificador Python 3D (executor único)
- Pedido original: “uso controle usb de super nitendo, faça a possibilidade de usar um controle pra controlar o jogo e faça uma tela aonde se configura as direções, botão de salto, de corrida e de ataque”

## Objetivo e comportamento esperado

Opções → Controle USB abre tela dedicada para mapear quatro direções, salto, corrida e ataque. Aceitar direcional como botões ou eixos; persistir escolhas. Teclado continua disponível. Controle USB permite jogar em terceira pessoa e FPS.

## Escopo

- Incluído: detectar dispositivos gamepad/genéricos, mapear, salvar, misturar teclado/controle, tratar desconexão e reconexão.
- Fora do escopo: drivers, novas dependências e navegação do menu pelo controle.

## Contexto, dúvidas e decisões

- Panda3D InputDeviceManager/InputDevice já disponíveis. Estado bruto lido por poll; eixos com zona morta de 0.35.
- Dúvidas bloqueantes: nenhuma. Identificadores dos controles USB variam; captura interativa evita presumir layout definitivo.
- Hipóteses reversíveis: primeiro gamepad/dispositivo genérico conectado. Direções por eixo ou botão; capturar após soltar controles já mantidos. Mapeamentos repetidos rejeitados. Padrão convencional inicial; mapeamento personalizado sobrescreve. Conforme reforço do usuário, todas as quatro direções seguem a visão, inclusive no controle. Acrescentados Virar esq./dir. para os botões laterais: giram a câmera sem mudar a semântica do direcional.
- Preferências preservadas junto com som, dificuldade e teclas; desconexão zera ações do controle sem afetar teclado.
- Limitação: ambiente não tem /dev/input e não detecta dispositivos físicos. Testes simulam estados; validação com o controle USB real permanece necessária.

## Critérios de aceitação e testes

| ID | Critério observável | Tipo de teste | Entrada/passos | Resultado esperado | Resultado real/evidência |
| --- | --- | --- | --- | --- | --- |
| CA-01 | Opção visível e tela para sete ações | Integração/captura | Opções → Controle USB | Sete campos e status de conexão; Esc cancela captura | Pendente |
| CA-02 | Botões/eixos configuráveis, persistentes e sem duplicação | Automatizado/integração | Capturar botão/eixo, salvar/reabrir, tentar repetir | Mapeamento salvo; repetido rejeitado; zona morta | Pendente |
| CA-03 | Direções, salto, corrida e ataque funcionam | Integração/hardware | Simular estados e usar controle físico | Movimento/corrida, ações por borda de pressão, FPS com giro | Pendente |
| CA-04 | Desconexão/menus não deixam ações presas | Automatizado/integração | Soltar/desconectar/abrir menu | Sem movimento/ações residuais | Pendente |

## Plano de implementação

1. Ler e validar estado/mapeamentos em game/gamepad.py.
2. Expor botão e tela de configuração, integrar polling e ações.
3. Testar estados simulados, capturar tela, README e commit separado.

## Riscos e mitigação

- Direcional USB aparecer como eixo em vez de botão: capturar ambos.
- Salto/ataque repetir segurando botão: executar somente na transição para pressionado.
- Controle desconectado continuar movendo: retornar estado vazio e limpar histórico.

## Entrega do codificador

- Pendente.

## Revisão

- Parecer: Não revisado.

## Encerramento

- Pendente.

## Complementos de refinamento

- Direções relativas à visão nos dois modos, conforme insistência explícita do usuário. Giro da terceira pessoa por botão direito do mouse; giro por botões laterais do controle em ambos os modos.
- Aviso relatado `/dev/input/event13 is not readable`: documentação oficial Panda3D consultada; causa de permissão do Linux registrada no README. Ambiente sem /dev/input impede corrigir/testar hardware físico local.
- Testes com dispositivo simulado verificam remapeamento, rejeição de duplicação, persistência, corrida, salto, ataque sem repetição ao manter botão e desconexão.

## Evidências e revisão atualizadas

`RUN_GRAPHICS_TESTS=1 .venv/bin/python -m pytest -q`: **109 passaram em 17,58 s**. Revisão do fluxo de captura, persistência e carregamento; testes cobrem troca de todas as combinações de entradas, Start/B e eixos. A rejeição de entradas ocupadas foi substituída por troca conforme demanda 029. Start abre menu, direcional navega e B confirma em teste simulado. Capturas offscreen mostram menus em tela cheia. Parecer: **Validação pendente**, pois não há janela interativa nem controle físico neste ambiente. O usuário confirmou que o USB funciona em seu computador.
