# Prompts das Pipelines de Geração de Questões

Este diretório contém os prompts usados nas três pipelines de geração automática de questões de múltipla escolha, conforme descrito no TCC.

Os trechos entre chaves (ex.: `{N}`, `{texto limpo da página}`) são preenchidos em tempo de execução pelo código. O nome da organização foi substituído por "empresa".

## Estrutura

```
prompts/
├── p1/                    # Pipeline 1: Regras e modelo T5
│   ├── avaliacao.txt      # Avaliação das questões geradas
│   ├── correcao.txt       # Correção das questões
│   ├── distratores.txt    # Geração de novos distratores
│   └── enunciado.txt      # Reescrita do enunciado
├── p2/                    # Pipeline 2: Cadeia de LLMs (Claude)
│   ├── visao.txt          # Descrição visual da página
│   ├── resumo.txt         # Resumo da página
│   ├── geracao.txt        # Geração das questões
│   ├── nota-imagem.txt    # Nota para páginas com imagens
│   ├── revisor.txt        # Revisão semântica e formal
│   ├── corretor.txt       # Correção de pistas formais
│   ├── julgador.txt       # Julgamento final
│   └── sem-fonte.txt      # Teste "sem a fonte" (guessable)
└── p3/                    # Pipeline 3: Modelos abertos locais
    ├── visao.txt          # Descrição visual da página
    ├── resumo.txt         # Resumo da página
    ├── geracao.txt        # Geração das questões
    └── reparo.txt         # Reparo de questões reprovadas
```

## Descrição das Pipelines

### P1 - Regras e modelo T5

A P1 gera a pergunta com o T5 e regras determinísticas, sem prompt de geração. Os prompts desta pasta são usados pelos modelos Claude para **avaliar e corrigir** as questões geradas na fase 2.

### P2 - Cadeia de LLMs

A P2 usa uma cadeia de modelos Claude com papéis especializados:
- **Gerador**: cria as questões a partir do texto da página
- **Revisor**: confronta a questão com a fonte e corrige problemas
- **Corretor**: elimina pistas formais nas alternativas
- **Julgador**: decisão final independente (aprovada/revisão/rejeitada)

### P3 - Modelos abertos locais

A P3 executa modelos abertos localmente (Qwen, Mistral, InternVL) seguindo o procedimento "evidência primeiro": o modelo copia o trecho que sustenta a resposta antes de redigir a questão.

## Modelos Utilizados

| Etapa | Papel | Modelo | Identificador |
|-------|-------|--------|---------------|
| Aplicação (v1) | Geração em tempo real | Claude Sonnet 4.5 | `databricks-claude-sonnet-4-5` |
| P1, fase 1 | Geração da pergunta | T5 pequeno PT-BR | `vabatista/question-generation-t5-small-pt-br` |
| P1, fase 1 | Validação ida e volta | BERT QA PT | `pierreguillou/bert-base-cased-squad-v1.1-portuguese` |
| P1, fase 1 | Representação semântica | MiniLM multilíngue | `paraphrase-multilingual-MiniLM-L12-v2` |
| P1, fase 2 | Avaliação | Claude Opus 5.5 | `databricks-claude-opus-5-5` |
| P1, fase 2 | Correção única | Claude Sonnet 5.5 | `databricks-claude-sonnet-5-5` |
| P2 | Gerador | Claude Sonnet 4.6 | `databricks-claude-sonnet-4-6` |
| P2 | Revisor semântico e formal | Claude Sonnet 5.5 | `databricks-claude-sonnet-5-5` |
| P2 | Julgador | Claude Sonnet 5 | `databricks-claude-sonnet-5` |
| P2 | Visão, resumo, teste sem fonte | Claude Haiku 4.5 | `databricks-claude-haiku-4-5` |
| P2 | Representação semântica | Qwen3-Embedding 0.6B | `databricks-qwen3-embedding-0-6b` |
| P3 | Gerador (1.224 questões) | Qwen3.6 35B | `qwen3.6:35b` |
| P3 | Gerador (120 questões) | Mistral Small 3.2 24B | `mistral-small3.2:24b` |
| P3 | Resumo de página | Mistral Small 3.2 24B | `mistral-small3.2:24b` |
| P3 | Representação semântica | BGE-M3 | `bge-m3:latest` |
| P3 | Visão (fluxogramas) | InternVL3.5 8B | `blaifa/InternVL3_5:8b` |

## Referência

Para detalhes sobre a engenharia de prompts, pilares de design e aprendizados, consulte o Apêndice F do TCC.
