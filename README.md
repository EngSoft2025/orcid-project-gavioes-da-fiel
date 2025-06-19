<h1 align="center">Gaviões da Fiel 🦅</h1>
<p align="center">Projeto da disciplina SSC0130 - Engenharia de Software (ICMC/USP)</p>

<p align="center">
  <a href="#estrutura-do-projeto">Estrutura do Projeto</a> • 
  <a href="#instalacao">Instalação e Uso</a> • 
  <a href="#objetivo">Objetivo</a> • 
  <a href="#tecnologias">Tecnologias</a> • 
  <a href="#estrutura_branches">Estrutura de Branches</a> • 
  <a href="#testes">Testes</a> • 
  <a href="#ciclo">Ciclo de Desenvolvimento</a> • 
  <a href="#cronograma">Cronograma</a> • 
  <a href="#riscos">Gerenciamento de Riscos</a> •
  <a href="#agradecimentos">Agradecimentos</a> •
  <a href="#licenca">Licença</a>
</p>

---

## <div id="objetivo"></div> Objetivo

A proposta do projeto **Gaviões da Fiel** é desenvolver uma aplicação web que complemente e melhore a experiência de uso da plataforma **ORCID**, com foco nas necessidades específicas dos pesquisadores brasileiros. Entre os objetivos estão:

* Melhorar a usabilidade e acessibilidade da interface
* Tornar a produção científica mais compreensível ao público geral
* Facilitar vínculos com coautores
* Integrar com bases como openAlex
* Ampliar a visibilidade da produção científica

---

## <div id="estrutura-do-projeto"></div> Estrutura do Projeto

```bash
orcid-project-gavioes-da-fiel/
│
├── backend/                     # Lógica de servidor e integração com APIs
│   ├── api_clients/            # Clientes para integração com APIs externas
│   │   ├── __init__.py
│   │   ├── openalex_client.py
│   │   └── orcid_client.py
│   ├── endpoints.py            # Endpoints principais da API
│   ├── requirements.txt        # Dependências Python
│   └── README.md               # Documentação específica do backend
│
├── frontend/                   # Aplicação React (interface do usuário)
│   ├── public/                 # Arquivos públicos (ícones, HTML, imagens)
│   │   ├── index.html
│   │   ├── data/
│   │   └── img/
│   ├── src/                    # Código-fonte React
│   │   ├── components/         # Componentes reutilizáveis
│   │   ├── pages/              # Páginas da aplicação
│   │   ├── App.js
│   │   ├── App.css
│   │   ├── index.js
│   │   ├── Dashboard.css
│   │   └── LoadingDrop.css
│   ├── package.json            # Dependências e scripts do projeto
│   ├── package-lock.json       # Trava exata das versões instaladas
│   └── README.md               # Instruções específicas do frontend
│
├── README.md                   # Documentação principal do projeto
---

Claro! Aqui está a seção **atualizada** de **Instalação e Uso**, agora com instruções separadas para frontend e backend:

---

## <div id="instalacao"></div> Instalação e Uso

### Requisitos

* **Node.js 18+** (para o frontend)
* **Python 3.10+** (para o backend)

---

### Frontend

```bash
# Clonar o repositório
git clone https://github.com/EngSoft2025/orcid-project-gavioes-da-fiel.git
cd orcid-project-gavioes-da-fiel/frontend

# Instalar dependências do React
npm install

# Rodar servidor de desenvolvimento
npm run dev
```

---

### Backend

```bash
# Entrar na pasta do backend
cd ../backend

# Criar ambiente virtual (opcional, mas recomendado)
python -m venv venv
source venv/bin/activate  # No Windows: venv\\Scripts\\activate

# Instalar dependências do FastAPI
pip install -r requirements.txt

# Rodar servidor FastAPI
uvicorn endpoints:app --reload
```

---

## <div id="tecnologias"></div> Tecnologias

- **React.js** (front-end moderno e responsivo)
- **FastAPI (Python)** (backend leve, rápido e com suporte a OpenAPI)
- **Node.js** (ambiente de execução para ferramentas e build do front-end)
- **Git + GitHub** (controle de versão e colaboração)
- **OpenAlex / ORCID APIs** (integração de dados acadêmicos)
- **Scrum** (metodologia ágil de desenvolvimento)

---

## <div id="estrutura_branches"></div> Estrutura de Branches

* `main`: versão estável
* `dev`: versão de integração contínua
* `feature/<nome>`: funcionalidades específicas

Exemplo: `feature/implementar-métricas-na-dashboard`

---

## <div id="testes"></div> Testes

O projeto adota testes em múltiplos níveis:

* **Funcionais:** Verificam se as funcionalidades cumprem seu papel
* **Usabilidade:** Testes com professores e colegas
* **Integração:** Comunicação entre módulos e APIs externas
* **Regressão:** Garantir funcionamento após mudanças
* **Critérios de aceitação:** Definidos por funcionalidade no backlog

---

## <div id="ciclo"></div> Ciclo de Desenvolvimento

1. Sprint Planning semanal
2. Desenvolvimento assíncrono
3. Sprint Review (com avaliações durante o horários das aulas)
4. Retrospectiva
5. Entregas incrementais com validação contínua

---

## <div id="cronograma"></div> Cronograma

| Semana | Etapa                       | Entregável                    |
| ------ | --------------------------- | ----------------------------- |
| 1      | Planejamento                | Documento de planejamento     |
| 2      | Requisitos e Casos de Uso   | Documento de requisitos       |
| 3      | Design + Desenvolvimento    | Protótipo de média fidelidade |
| 4      | MVP                         | MVP navegável                 |
| 5      | Testes com usuários         | Feedback e melhorias          |
| 6      | Iterações finais            | Versão beta                   |
| 7      | Documentação e Apresentação | Vídeo, documentos e entrega final |

---

## <div id="riscos"></div> Gerenciamento de Riscos

| Risco                           | Impacto | Mitigação                       |
| ------------------------------- | ------- | ------------------------------- |
| APIs instáveis (ORCID/OpenAlex) | Alto    | Camadas de serviço e fallback   |
| Scope Creep                     | Alto    | Backlog priorizado e PO atuante |
| Time reduzido                   | Médio   | Pair programming e foco         |
| Pouca validação                 | Alto    | Prototipação contínua           |
| Falta de stakeholders           | Médio   | Antecipação e uso de colegas    |

---

## <div id="licenca"></div>📝 Licença

Este projeto está licenciado sob a Licença MIT. Veja `LICENSE` para mais informações.

---

## <div id="agradecimentos"></div> Agradecimentos

Um agradecimento especial ao grandioso professor **Seiji Isotani** e a todos os monitores da disciplina pela orientação e apoio ao longo do projeto.

---

## 👥 Equipe

* **Julia Cavallio Orlando** – 14758721 *(Product Owner)*
* **Gabriel de Andrade Abreu** – 14571362 *(Scrum Master)*
* **Isabela B. S. N. Farias** – 13823833 *(Dev)*
* **Antônio C. de A. M. Neto** – 14559013 *(Dev)*
* **Nicolas Carreiro Rodrigues** – 14600801 *(Dev)*

Estudantes de Ciências de Computação – USP
