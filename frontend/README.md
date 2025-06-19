# Frontend

## Estrutura do Projeto

```
frontend/
│
├── public/                  # Arquivos estáticos
├── src/
│   ├── assets/              # Imagens e estilos
│   ├── components/          # Componentes reutilizáveis
│   ├── pages/               # Páginas principais
│   ├── services/            # Comunicação com a API
│   ├── App.tsx              # Componente principal
│   └── main.tsx             # Entrada do app
├── package.json             # Dependências e scripts
├── tsconfig.json            # Configuração TypeScript (se aplicável)
└── README.md                # Este arquivo
```

## Requisitos

- Node.js 18+
- npm 9+

## Instalação

1. Clone o repositório e acesse o diretório do frontend:

```bash
cd frontend
```

2. Instale as dependências:

```bash
npm install
```

## Dependências principais

- **React** 19
- **Material UI** (`@mui/material`, `@mui/icons-material`, `@mui/system`)
- **Emotion** (`@emotion/react`, `@emotion/styled`) – usada com MUI
- **React Router DOM** – para navegação
- **Chart.js** – gráficos
- **Lottie** (`lottie-react`, `@lottiefiles/dotlottie-react`) – animações
- **React Icons** – ícones adicionais

## Scripts disponíveis

```bash
npm start        # Inicia o servidor de desenvolvimento (http://localhost:3000)
npm run build    # Gera a versão de produção
```

> **Nota:** Certifique-se de que o backend esteja rodando na porta 5000, conforme definido no `proxy` do `package.json`.

