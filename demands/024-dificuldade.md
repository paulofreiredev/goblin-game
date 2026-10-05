# 024 — Dificuldade com 3, 8 ou 12 monstros

- Estado: Validação pendente
- Responsável atual: Code reviewer (executor único)
- Pedido original: “faça um modo facil com apenas 3 monstros, um médio com 8 e um dificil com 12”

## Objetivo e comportamento esperado

Selecionar em Opções Fácil (3), Médio (8) ou Difícil (12). Quantidade aplicada em cada uma das três fases da demanda 023, mantida ao continuar e avançar.

## Escopo

- Incluído: seleção persistente para novo jogo, quantidade de inimigos e nós gráficos correspondentes, salvamento da dificuldade da partida.
- Fora do escopo: alterar dano, velocidade, vida dos inimigos, tempo ou quantidade de relógios.

## Contexto, dúvidas e decisões

- Código relacionado: game/state.py, game/world.py, game/app.py e testes.
- Dúvidas bloqueantes: nenhuma.
- Hipóteses reversíveis: Médio padrão; seletor cíclico em Opções. Alterar seleção não modifica save existente. Reinício por perda de vidas conserva dificuldade da partida e volta à manhã.
- Assets e dependências: existentes; quatro posições adicionais de inimigos no Difícil.
- Limitação: validação gráfica interativa indisponível; integração offscreen disponível.

## Critérios de aceitação e testes

| ID | Critério observável | Tipo de teste | Entrada/passos | Resultado esperado | Resultado real/evidência |
| --- | --- | --- | --- | --- | --- |
| CA-01 | Fácil 3, Médio 8, Difícil 12 em todas as fases | Automatizado/integração | Selecionar e iniciar/avançar | Número exato de monstros, barras e moedas associados | Integração aprovada; manual pendente quando visual |
| CA-02 | Escolha em Opções e persistência correta | Integração/automatizado | Alternar, iniciar, salvar, alterar escolha e continuar | Save conserva dificuldade; preferência aplica ao novo jogo | Integração aprovada; manual pendente quando visual |
| CA-03 | Vitória depende de todos os inimigos e nenhuma regressão | Integração | Executar suíte e concluir fases | Progressão correta nos três modos | Integração aprovada; manual pendente quando visual |

## Plano de implementação

1. Persistir dificuldade e configurar spawns 3/8/12.
2. Adicionar seletor e ajustar criação de nós gráficos à quantidade.
3. Testar junto com as três fases; atualizar documentação e revisar.

## Riscos e mitigação

- Nós antigos ficarem visíveis ao mudar modo: remover e reconstruir itens/inimigos quando o número mudar.
- Continuar usar preferência nova: restaurar dificuldade do Player salvo.

## Entrega do codificador

- Arquivos: game/app.py, game/state.py, game/world.py, tests/test_state.py, tests/test_app.py, tests/test_phases.py, README.md, tools/capture_preview.py, docs/images e demandas 023/024.
- Execução: `.venv/bin/python main.py`.
- Comandos executados: inspeção com rg/sed; `RUN_GRAPHICS_TESTS=1 .venv/bin/python -m pytest -q`: 94 aprovados em 8.91s com as duas funcionalidades integradas.
- `.venv/bin/python tools/capture_preview.py`: três capturas de fases, captura de dificuldade e GIF de 4.5 segundos com 90 quadros do jogo rodando offscreen, jogador em movimento e cronômetro ativo. Capturas em docs/images; GIF com resolução 640×360 e quadros de 50ms. Uso de save temporário para preservar partida do usuário.
- Inspeção visual: primeira lua estava cortada; ajustada de Z=28/raio12 para Z=13/raio9. Noite clareada para facilitar leitura do campo. Capturas finais de noite e opções inspecionadas: lua grande visível, campo legível e seletor de dificuldade presente.
- Testes de progressão nos três modos verificam quantidade exata de nós, fases 0/1/2, preservação de moedas e vida, reposição de tempo/itens e continuação; vitória somente após noite. Validação de fases e dificuldades inválidas e saves legados incluída.
- Roteiro manual: escolher cada dificuldade em Opções, iniciar e derrotar todos; conferir passagem manhã→tarde→noite e vitória final; Esc/Continuar em cada fase, expirar tempo e perder todas as vidas; conferir iluminação e lua com movimento.
- Limitações: interação gráfica não executada, display :0 indisponível; capturas e GIF offscreen não substituem roteiro interativo.
- Commits: repositório original estava vazio e somente leitura; `git status` falhou. `git init` comum falhou por proteção de .git; inicialização escalada autorizada concluída. Base registrada em `8fd6da7`; fases e capturas/GIF em `bc6fa4c`; dificuldade em commit próprio na sequência, sem envio remoto.

## Revisão

- Parecer: Validação pendente.
- Critérios conferidos: progressão, save/restauração, quantidade de inimigos por modo, reconstrução de nós ao mudar quantidade, cores de céu/neblina/cenário, lua apenas na noite e HUD preservado. Testes automatizados aprovados.
- Achados: lua inicialmente cortada na captura, corrigida pelo codificador e captura repetida. Sem defeitos remanescentes que exijam correção.
- Verificações posteriores: suíte com fases sem dificuldade, 83 aprovados em 6.26s; suíte final integrada `RUN_GRAPHICS_TESTS=1 .venv/bin/python -m pytest -q`, 94 aprovados em 8.99s. `git diff --check` sem problemas.

## Encerramento

- Critérios verificados: automatizados e capturas; manual pendente.
- Testes obrigatórios: integração aprovada; interação gráfica pendente.
- Revisão aprovada: depende do roteiro gráfico.
- Documentação: README com capturas e GIF.
- Resultado: implementação entregue com evidências visuais reais offscreen e limitação interativa explícita.
