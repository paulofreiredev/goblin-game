# 037 — Isolar dois joysticks USB simultâneos

- Estado: Pronta
- Responsável atual: Executor único, papéis em sequência
- Pedido original: Está mapeando o controle como se os dois fossem um só; devem configurar dois joysticks USB simultaneamente.

## Objetivo e comportamento esperado

Dois dispositivos conectados, inclusive com nome e modelo iguais, mantêm associação e entradas independentes para Verde e Azul. A configuração de uma cor só recebe comandos de seu joystick.

## Escopo

- Incluído: identidade física por dispositivo, seleção/scan e navegação da configuração isolada, regressão com dispositivos iguais.
- Fora do escopo: drivers externos ou identidade persistente entre execuções.

## Contexto, dúvidas e decisões

A seleção/scan usa igualdade dos objetos; testes anteriores usam nomes diferentes e não exercitam controles idênticos. Além disso, o update une entradas de ambos para navegar em todos os menus, inclusive configuração por cor. Usar ponteiro nativo Panda3D para identificar dispositivo, identidade de objeto como fallback nos testes; durante configuração usar só joystick da cor selecionada. Nenhuma dependência nova. A causa no hardware do usuário não pode ser comprovada sem os dispositivos físicos.

## Critérios de aceitação e testes

| ID | Critério observável | Tipo de teste | Entrada/passos | Resultado esperado | Resultado real/evidência |
| --- | --- | --- | --- | --- | --- |
| CA-01 | Dois controles iguais permanecem distintos | Automatizado/integração | Objetos iguais em valor, com mesmo nome | Verde e Azul associados a instâncias distintas | Pendente |
| CA-02 | Remapear e jogar simultaneamente | Integração | Ambos USB ativos com entradas distintas | Cada mapeamento e movimento recebem somente seu dispositivo | Pendente |
| CA-03 | Configuração não recebe navegação da outra cor | Integração | Oponente move direcional durante configuração | Seleção do menu permanece | Pendente |
| CA-04 | Dois USB físicos | Manual | Conectar ambos, identificar e remapear, jogar | Independência visível | Pendente |

## Plano de implementação

1. Centralizar comparação por identidade do dispositivo.
2. Isolar navegação na configuração; testar mesmo nome/modelo, seleção e entradas simultâneas.
3. Registrar comandos, resultados e limites.

## Riscos e mitigação

Wrappers Python diferentes do mesmo dispositivo: comparar ponteiro nativo, não apenas identidade Python. Sem hardware disponível: registrar validação pendente sem afirmar causa comprovada no computador do usuário.

## Entrega do codificador

Pendente.

## Revisão

Pendente.

## Encerramento

Pendente.

## Entrega e revisão final

- Arquivos alterados: game/gamepad.py, game/app.py, tests/test_gamepad.py, tests/test_app.py, README.md.
- Identidade centralizada em same_device: ponteiro nativo Panda3D quando disponível; identidade de objeto para dispositivos simulados. Scan, seleção e troca usam a mesma regra.
- Navegação de controller_options recebe apenas ações do dispositivo da equipe selecionada. Partida já possuía arrays separados; preservados e verificados com entradas simultâneas.
- `.venv/bin/python` usado para inspecionar API local InputDevice: atributo `this` disponível; sem depender de nome, fabricante ou modelo para identidade.
- `RUN_GRAPHICS_TESTS=1 .venv/bin/python -m pytest -q`: 134 passaram em 18,56 s.
- Regressões novas: dois objetos de mesmo nome e valores inicialmente iguais permanecem distintos no scan/seleção; remapeamento Azul ignora botão Verde; direcional Verde não navega na configuração Azul; ambos movem personagens em direções distintas no mesmo quadro; após retornarem ao estado de repouso continuam associados separadamente. Teste unitário verifica wrappers com mesmo ponteiro e ponteiros diferentes.
- `git diff --check`: passou sem saída.
- Reviewer (executor único): conferidos fluxo de associação, troca, comparação nativa, polling, mapeamentos por cor e seleção do pad para menus. Sem achados pendentes no código.
- CA-01 a CA-03: testes aprovados. CA-04: pendente por ausência de dois joysticks físicos e display interativo acessível. Não se afirma diagnóstico comprovado do driver/dispositivos do usuário.
- Executar: `.venv/bin/python main.py`; conectar os dois controles antes de abrir Dois jogadores; escolher USB Verde e identificar o primeiro, USB Azul e identificar o segundo, mapear botões diferentes; jogar com ambos pressionados simultaneamente e conferir independência.
- Parecer e estado final: Validação pendente para hardware real. Implementação e documentação atualizadas; validação automatizada aprovada.
