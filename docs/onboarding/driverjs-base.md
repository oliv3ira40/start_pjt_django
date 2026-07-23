# Driver.js — instalação base (etapa preparatória)

## Objetivo desta etapa

- Instalar o Driver.js localmente no projeto.
- Preparar os assets JS/CSS para uso futuro em páginas autenticadas.
- Deixar um ponto de entrada técnico mínimo para integração posterior.

Esta etapa **não** ativa tour real e **não** integra com o fluxo de releases/onboarding ainda.

## Como foi integrado

- Dependência instalada via npm:
  - `driver.js` em `package.json`
- Assets sincronizados para o Django static:
  - origem: `node_modules/driver.js/dist/`
  - destino compartilhado: `core/static/vendor/driverjs/`
  - arquivos:
    - `driver.js` (a partir de `driver.js.iife.js`)
    - `driver.css`

## Scripts npm adicionados

- `npm run sync:driverjs-assets`
  - copia os assets do Driver.js para `core/static/vendor/driverjs/`
- `npm run verify:driverjs`
  - valida versão instalada e presença dos assets copiados
- `postinstall`
  - executa automaticamente o `sync:driverjs-assets` após `npm install`

## Ponto de entrada preparado

- Arquivo base compartilhado: `core/static/js/onboarding_driver_base.js`
- Exposto em `window.onboardingDriverBase` com:
  - `hasDriverLoaded()`
  - `ensureDriverReady()`
  - `createDriverInstance(options)`
- O arquivo pode ser carregado pelas páginas que precisarem dele, mas **não inicia tour automaticamente**.

## Comandos úteis

```bash
npm install
npm run sync:driverjs-assets
npm run verify:driverjs
```

## Próxima etapa (não implementada aqui)

- Conectar o Driver.js ao fluxo real de releases/onboarding.
- Definir e executar etapas reais de tour nas páginas aprovadas.
