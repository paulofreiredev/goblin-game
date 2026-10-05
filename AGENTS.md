# Agentes do projeto

Este projeto desenvolve jogos 3D em Python. Ao receber uma demanda de implementação, siga [WORKFLOW.md](WORKFLOW.md).

## Papéis

- **Refinador**: siga [agents/refinador.md](agents/refinador.md) para transformar a demanda em requisitos verificáveis.
- **Codificador Python 3D**: siga [agents/codificador.md](agents/codificador.md) para implementar e testar a solução.
- **Code reviewer**: siga [agents/code-reviewer.md](agents/code-reviewer.md) para revisar comportamento, código e evidências.

Os perfis são instruções de trabalho; sua existência não inicia processos nem configura automaticamente uma plataforma de agentes. Um executor pode assumir os papéis em sequência ou delegá-los a agentes disponíveis. Se delegar, forneça o perfil, a demanda e os artefatos necessários. Alterações em arquivos compartilhados devem ter apenas um responsável por vez.

## Regras comuns

- Trabalhe em português na documentação e na comunicação. Use nomes consistentes no código.
- Leia o código existente antes de definir a solução. Preserve alterações do usuário.
- Registre cada demanda em `demands/`, usando [o modelo](demands/TEMPLATE.md).
- Registre decisões, comandos executados, resultados e limitações. Nunca declare um teste executado sem executá-lo.
- Prefira mudanças pequenas e relacionadas à demanda. Não acrescente funcionalidades ou dependências sem justificativa.
- Não envie, publique ou faça deploy automaticamente. A revisão técnica não concede autorização para essas ações.
- Não substitua validação gráfica interativa por sucesso de testes sem janela.
