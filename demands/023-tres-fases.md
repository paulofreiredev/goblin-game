# 023 — Três fases: manhã, tarde e noite

- Estado: Validação pendente
- Responsável atual: Code reviewer (executor único, perfis em sequência)
- Pedido original: “faça 3 fazes, uma de manhã uma numa tarde alarajnada uma a noite com uma lua grande”

## Objetivo e comportamento esperado

Três fases em sequência no campo existente: manhã clara, tarde alaranjada e noite azul escura com lua grande visível acima do horizonte. Derrotar os oito monstros avança da manhã à tarde e da tarde à noite; vitória final após vencer a noite.

## Escopo

- Incluído: progressão, visual de céu/nuvens/neblina/cenário, lua procedural, persistência da fase, reposição de inimigos e itens a cada fase.
- Fora do escopo: novo mapa, dependências, piscinas, textos inferiores e mudanças nos controles.

## Contexto, dúvidas e decisões

- Código relacionado: game/app.py (céu, iluminação e término), game/state.py (save), game/world.py (encontros).
- Dúvidas bloqueantes: nenhuma.
- Hipóteses reversíveis: início de cada fase no centro, 120s e novos três relógios/dois corações/oito monstros; conservar vidas e moedas já coletadas entre fases. Novo jogo ou perda de todas as vidas reinicia na manhã conforme regra existente. Tempo esgotado mantém derrota. Moedas ainda no chão são substituídas pelo encontro da próxima fase.
- Biblioteca: Panda3D existente, lua com geometria procedural; sem assets externos.
- Saves antigos: fase padrão manhã; índice validado entre 0 e 2.
- Limitação: ambiente offscreen disponível, display interativo indisponível nas demandas anteriores.

## Critérios de aceitação e testes

| ID | Critério observável | Tipo de teste | Entrada/passos | Resultado esperado | Resultado real/evidência |
| --- | --- | --- | --- | --- | --- |
| CA-01 | Três ambientes distintos; lua grande apenas à noite | Integração/captura/manual | Conferir cada fase | Manhã clara, tarde laranja, noite escura legível e lua visível | Integração aprovada; manual pendente quando visual |
| CA-02 | Progressão em ordem e vitória somente após noite | Integração | Derrotar os oito em cada fase | Índices 0,1,2; repor encontros/tempo; vitória final | Integração aprovada; manual pendente quando visual |
| CA-03 | Continuar preserva fase; legado compatível | Automatizado/integração | Salvar tarde/noite, continuar; save sem fase/inválido | Retomar fase correta; legado/inválido usa manhã | Integração aprovada; manual pendente quando visual |
| CA-04 | HUD, relógios e regras preservados | Integração | Suíte completa; derrota/reinício | Sem regressões; parte inferior sem texto | Integração aprovada; manual pendente quando visual |

## Plano de implementação

1. Persistir índice de fase e definir três temas visuais.
2. Aplicar tema ao céu/campo/iluminação e construir lua acima do horizonte.
3. Integrar progressão, testar transições/continuação, conferir capturas e documentar.

## Riscos e mitigação

- Noite ilegível: tons azulados moderados no chão/personagem e lua sem neblina.
- Lua fora da câmera: posição relativa ao céu que acompanha o jogador, à frente da câmera.
- Estado incorreto ao avançar: novo Player conserva apenas vidas/moedas e fase seguinte; novo Encounter repõe itens.

## Entrega do codificador

- Arquivos: game/app.py, game/state.py, game/world.py, tests/test_state.py, tests/test_app.py, tests/test_phases.py, README.md, tools/capture_preview.py, docs/images e demandas 023/024.
- Execução: `.venv/bin/python main.py`.
- Comandos executados: inspeção com rg/sed; `RUN_GRAPHICS_TESTS=1 .venv/bin/python -m pytest -q`: 94 aprovados em 8.91s com as duas funcionalidades integradas.
- `.venv/bin/python tools/capture_preview.py`: três capturas de fases, captura de dificuldade e GIF de 4.5 segundos com 90 quadros do jogo rodando offscreen, jogador em movimento e cronômetro ativo. Capturas em docs/images; GIF com resolução 640×360 e quadros de 50ms. Uso de save temporário para preservar partida do usuário.
- Inspeção visual: primeira lua estava cortada; ajustada de Z=28/raio12 para Z=13/raio9. Noite clareada para facilitar leitura do campo. Capturas finais de noite e opções inspecionadas: lua grande visível, campo legível e seletor de dificuldade presente.
- Testes de progressão nos três modos verificam quantidade exata de nós, fases 0/1/2, preservação de moedas e vida, reposição de tempo/itens e continuação; vitória somente após noite. Validação de fases e dificuldades inválidas e saves legados incluída.
- Roteiro manual: escolher cada dificuldade em Opções, iniciar e derrotar todos; conferir passagem manhã→tarde→noite e vitória final; Esc/Continuar em cada fase, expirar tempo e perder todas as vidas; conferir iluminação e lua com movimento.
- Limitações: interação gráfica não executada, display :0 indisponível; capturas e GIF offscreen não substituem roteiro interativo.
- Commits: repositório original estava vazio e somente leitura; `git status` falhou. `git init` comum falhou por proteção de .git; inicialização escalada autorizada concluída. Base e funcionalidades sendo registradas em commits separados, sem envio remoto.

## Revisão

- Parecer: Validação pendente.
- Critérios conferidos: progressão, save/restauração, quantidade de inimigos por modo, reconstrução de nós ao mudar quantidade, cores de céu/neblina/cenário, lua apenas na noite e HUD preservado. Testes automatizados aprovados.
- Achados: lua inicialmente cortada na captura, corrigida pelo codificador e captura repetida. Sem defeitos remanescentes que exijam correção.
- Verificações posteriores: suíte final será registrada após organização dos commits.

## Encerramento

- Critérios verificados: automatizados e capturas; manual pendente.
- Testes obrigatórios: integração aprovada; interação gráfica pendente.
- Revisão aprovada: depende do roteiro gráfico.
- Documentação: README com capturas e GIF.
- Resultado: implementação entregue com evidências visuais reais offscreen e limitação interativa explícita.
