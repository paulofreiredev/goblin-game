# 031 — Elevações e depressões com poucos acessos largos

- Estado: Validação pendente
- Responsável atual: Executor único
- Pedido original: reduzir escadas estreitas por todos os lados; algumas elevações e depressões, com uma escadinha larga em lados específicos.

## Objetivo e comportamento esperado

Quatro áreas grandes: duas elevações e duas depressões. Apenas a elevação oeste e a depressão noroeste têm escadas, em um lado cada. Degraus com 4 unidades de profundidade e largura de todo o lado. Outros lados têm transição direta e as superfícies internas são planas.

## Escopo

Incluído: geometria, suporte físico, testes de salto/queda e evidências. Sem piscinas ou dependências novas.

## Contexto, dúvidas e decisões

Panda3D existente. Substituir seis blocos em anéis por quatro blocos e faixas retangulares, reutilizadas por altura, apoio e malha. Manter altura do degrau de 0,8 para preservar regra de salto. Escadas com 26 e 30 unidades de largura.

## Critérios de aceitação e testes

| ID | Critério observável | Tipo de teste | Entrada/passos | Resultado esperado | Resultado real/evidência |
| --- | --- | --- | --- | --- | --- |
| CA-01 | Poucos blocos, apenas dois acessos largos | Automatizado/visual | Inspecionar faixas e captura | Quatro blocos; escadas em apenas um lado de dois blocos | Pendente |
| CA-02 | Colisão acompanha geometria | Automatizado/integração | Subir, cair e tocar cantos | Apoio correto; salto por nível; dano de queda | Pendente |
| CA-03 | Cenário jogável | Manual | Caminhar entre áreas nos dois modos de jogo | Caminhos largos e enquadramento correto | Pendente no computador do usuário |

## Plano de implementação

Centralizar faixas em world.py; malha e suporte usam as mesmas faixas. Atualizar posições de testes conforme profundidade de degraus. Regenerar captura, revisar e commit.

## Riscos e mitigação

Colisão divergente da malha: uma única definição de superfícies. Escadas encostarem em árvores: conferir captura e caminhos.

## Entrega do codificador

Pendente.

## Revisão

Pendente.

## Encerramento

Pendente.

## Evidências e revisão

115 testes passaram em 20,53 s na primeira verificação; nova suíte após correção de cancelamento local registrada no histórico de ferramentas. Captura tools/capture_local_preview.py executada e imagem inspecionada: dois blocos elevados, escada apenas no lado leste do primeiro; faces diretas no segundo. Testes determinísticos cobrem 4 blocos, 8 faixas, larguras, degraus, quinas, subida de um nível por salto e dano somente na aterrissagem. Fonte geométrica e física compartilhada revisada. Parecer: validação pendente para caminhada interativa; roteiro manual CA-03 não executado.
