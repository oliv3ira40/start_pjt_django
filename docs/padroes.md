# Padrões de desenvolvimento

## Versionamento

- Use branches em inglês, com prefixos que expressem a intenção: `feature/`, `fix/`, `refactor/` e `chore/`.
- Mantenha commits em inglês e no formato [Conventional Commits](https://www.conventionalcommits.org/pt-br/v1.0.0/).
- Escreva título e descrição de merge request em português, com resumo claro do impacto.
- Adote [Semantic Versioning 2.0.0](https://semver.org/lang/pt-BR/) quando o projeto publicar versões.

Exemplos:

```bash
git switch -c feature/nome-da-mudanca
git commit -m "feat: add validated profile update"
git commit -m "fix: prevent cross-tenant object access"
```

## Revisão

Uma mudança deve ser pequena, coerente, testada e documentada quando alterar um contrato estável. Evite misturar refatorações não relacionadas, alterações de formatação extensas e mudanças de comportamento na mesma entrega sem necessidade.
