# Workflow de demandas

## Fluxo

`Recebida → Refinamento → Pronta → Implementação → Revisão → Concluída`

Correções seguem `Revisão → Implementação → Revisão`. Mudanças de requisito voltam ao refinamento. Use `Bloqueada` quando falta uma informação ou condição indispensável, registrando motivo e próximo passo. Use `Validação pendente` quando a implementação precisa de uma verificação obrigatória ainda não realizada.

## 1. Registrar e refinar — refinador

Crie `demands/NNN-nome-curto.md` a partir de `demands/TEMPLATE.md`. Use o próximo identificador disponível. Leia o projeto e documente comportamento, critérios de aceitação, plano técnico e testes. Defina a biblioteca 3D somente quando a demanda exigir essa escolha; mantenha a base existente quando adequada.

Uma demanda fica pronta quando cada critério tem resultado esperado e verificação definida, e as dúvidas bloqueantes estão resolvidas. A escolha rotineira e reversível de implementação pode ser registrada como hipótese.

## 2. Implementar e verificar — codificador

Siga a ordem definida na demanda. Atualize o plano se a inspeção revelar uma necessidade técnica e registre a razão. Execute testes após a mudança e corrija falhas antes de encaminhar para revisão.

| Tipo de mudança | Verificação esperada |
| --- | --- |
| Regras, movimento e cálculos | Testes determinísticos de casos normais, limites e falhas relevantes |
| Integração de módulos ou assets | Teste do fluxo de carregamento/integração e erro esperado quando aplicável |
| Câmera, renderização e controles | Executar o jogo e seguir roteiro visual/interativo com resultado esperado |
| Janela e ciclo de vida | Iniciar, interagir e fechar, verificando erros e liberação de recursos |
| Desempenho | Medir na cena, resolução e hardware definidos; registrar método e resultado |
| Documentação ou configuração simples | Conferir links, sintaxe e comandos afetados; evitar testes artificiais |

Use `pytest` quando houver testes Python. Acrescente lint ou análise de tipos conforme a configuração do projeto. Não apresente comandos de ferramentas inexistentes como se já estivessem configuradas.

Execução sem janela pode verificar lógica e algumas integrações. Contexto gráfico, drivers e interação precisam de validação própria. Se não houver ambiente gráfico, registre o roteiro e mantenha a validação pendente.

## 3. Revisar — code reviewer

Revise requisitos, implementação e evidências. Registre achados reproduzíveis e um parecer. O codificador resolve os itens solicitados e executa novamente os testes afetados. O reviewer confere a correção e a cobertura de regressões antes de aprovar.

## 4. Concluir

A demanda só fica concluída quando os critérios foram verificados, os testes obrigatórios passaram, os problemas solicitados foram resolvidos e o reviewer aprovou. Atualize instruções de uso quando o comportamento ou a instalação mudou. Informe ao usuário o resultado, como executar e eventuais limitações. Publicação ou deploy dependem do pedido do usuário.

## Como usar os perfis

Para um executor único, leia e assuma cada perfil na ordem do fluxo, registrando as entregas no documento da demanda. Para execução com agentes distintos, forneça a cada agente seu perfil e o documento atualizado; o codificador é responsável pelas alterações de produção. O refinador e o reviewer entregam documentos e achados. Não permita edições concorrentes no mesmo arquivo.

Exemplo de despacho: “Assuma `agents/refinador.md` e refine a demanda de câmera em terceira pessoa usando `demands/TEMPLATE.md`”. Depois encaminhe a demanda pronta ao codificador e a implementação ao reviewer.
