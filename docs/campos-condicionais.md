# Campos condicionais no Admin

## Formato real das RULES
O arquivo `apiary/js/conditional-fields.js` define um array global `RULES`. Cada entrada usa a estrutura:
```json
{
  "when": {
    "nameEndsWith": "controller_suffix",
    "equals": "valor",
    "valueIn": ["opcional"],
    "notEmpty": true,
    "isChecked": true,
    "not": true,
    "idEquals": "opcional"
  },
  "then": [
    { "nameEndsWith": "target_suffix", "required": true },
    { "idEquals": "target_id" }
  ]
}
```
- `when` identifica os campos controladores por sufixo de `name` ou `id`. Apenas uma propriedade de identificação é necessária.  
- `then` lista os campos-alvo, também identificados por sufixo de `name` ou `id`. A flag `required` determina se o campo se torna obrigatório quando a regra está ativa.【F:apiary/static/apiary/js/conditional-fields.js†L1-L207】

## Operadores suportados
- **`equals`**: exige correspondência exata do valor do controlador.【F:apiary/static/apiary/js/conditional-fields.js†L270-L274】
- **`valueIn`**: aceita qualquer valor contido na lista informada.【F:apiary/static/apiary/js/conditional-fields.js†L275-L279】
- **`notEmpty`**: considera ativo quando o valor não é vazio (após `trim`).【F:apiary/static/apiary/js/conditional-fields.js†L281-L286】
- **`isChecked`**: disponível para radios/checkboxes, comparando o estado marcado.【F:apiary/static/apiary/js/conditional-fields.js†L265-L268】
- **`not`**: inverte o resultado final, útil para “diferente de”.【F:apiary/static/apiary/js/conditional-fields.js†L288-L292】

Outros efeitos padrões:
- Campos-alvo ficam ocultos via `display: none` quando nenhuma regra ativa está apontando para eles. O script memoriza o display original e aplica `aria-hidden` para acessibilidade.【F:apiary/static/apiary/js/conditional-fields.js†L319-L357】
- Requisitos são aplicados removendo/adicionando o atributo `required`, mantendo consistência com validação HTML e Django.【F:apiary/static/apiary/js/conditional-fields.js†L358-L365】

Não há suporte nativo para `clear_on_hide`, `disable` ou outros efeitos além de exibir/ocultar e marcar como obrigatório.

## Onde declarar e momento da avaliação
As `RULES` ficam no topo do próprio arquivo e são carregadas junto com o mixin de mídia do Admin. O script roda no `DOMContentLoaded`, vincula eventos `change`/`input` em cada controlador encontrado e reavalia todas as regras imediatamente. Ele também reexecuta o binding quando o Django dispara `formset:added` ou `formset:removed`, garantindo compatibilidade com inlines dinâmicos.【F:apiary/static/apiary/js/conditional-fields.js†L400-L455】

Para adicionar novas regras, edite o array `RULES` no início do arquivo ou extraia a constante para outro módulo importado antes do script. Certifique-se de que o arquivo esteja disponível via `collectstatic` e listado na mídia do Admin.

## Exemplos reais do projeto
1. **Gestão realizada → descrição obrigatória**  
   ```json
   {
     "when": { "nameEndsWith": "management_performed", "notEmpty": true },
     "then": [{ "nameEndsWith": "management_description", "required": true }]
   }
   ```
   Garante que, ao selecionar qualquer ação de manejo, o campo de descrição apareça e seja obrigatório.【F:apiary/static/apiary/js/conditional-fields.js†L3-L6】

2. **Tipo de revisão = colheita**  
   Ativa campos de quantidades de mel, própolis, cera, pólen e notas específicas ao escolher “colheita”.【F:apiary/static/apiary/js/conditional-fields.js†L7-L15】

3. **Método de aquisição = compra**  
   Expõe a data de aquisição e marca a origem como obrigatória quando o método for “compra”. Outras regras similares lidam com “divisão”, “captura” e “ninho_isca”.【F:apiary/static/apiary/js/conditional-fields.js†L27-L56】

## Notas finais
- **Validação do servidor:** mantenha validações em formulários Django para garantir consistência mesmo se o JavaScript falhar.  
- **Degradação elegante:** caso o script não carregue, todos os campos permanecem visíveis e editáveis, reduzindo o risco de bloqueios.  
- **Integração com Select2 e prévia de imagem:** como as regras atuam sobre containers padrão do Admin (`.form-row`, `.fieldBox`, etc.), os campos continuam compatíveis com outros scripts carregados pelo mixin.【F:apiary/static/apiary/js/conditional-fields.js†L66-L318】
