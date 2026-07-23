# Campos condicionais no Admin

## Objetivo

Campos condicionais tornam formulários mais objetivos ao exibir e exigir informações apenas quando forem aplicáveis. Devem ser implementados como melhoria progressiva: o servidor continua sendo a fonte de verdade para validação e limpeza de dados.

## Contrato de uma regra

Uma regra deve identificar um campo controlador, uma condição e os campos-alvo. Prefira identificadores estáveis, como `data-*`, nomes de campo ou IDs específicos; não dependa de texto visível ou posição no DOM.

Condições comuns:

- valor igual a um valor esperado;
- valor pertencente a uma lista;
- valor preenchido;
- checkbox ou radio marcado;
- negação de uma condição.

Efeitos recomendados:

- exibir ou ocultar o container do campo;
- ajustar o atributo HTML `required`;
- preservar acessibilidade com `aria-hidden` e foco coerente.

## Implementação segura

- Declare regras em módulo JavaScript reutilizável ou em configuração específica da página, sem misturar regras de domínios diferentes.
- Avalie as regras no carregamento e nos eventos `change` e `input` pertinentes.
- Reaplique a inicialização em `formset:added` e `formset:removed` para inlines dinâmicos.
- Ao ocultar um campo, defina no backend se o valor deve ser ignorado, validado ou limpo. A decisão não pode depender apenas do cliente.
- Se o JavaScript falhar, o formulário deve continuar utilizável e a validação Django deve retornar erros claros.

## Checklist

- A regra funciona no formulário principal e em inlines.
- Campos obrigatórios ficam obrigatórios também no backend quando aplicáveis.
- Valores que não se aplicam não são persistidos indevidamente.
- A interação por teclado e leitores de tela continua compreensível.
