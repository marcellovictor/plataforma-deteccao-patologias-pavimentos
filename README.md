# Plataforma de detecção e classificação de patologias em pavimentos asfálticos

Plataforma que recebe uma imagem de pavimento asfáltico e devolve as patologias encontradas, cada uma com bounding box, classe e nível de confiança. Desenvolvida como Trabalho de Conclusão de Curso em Ciência da Computação na Universidade Federal Fluminense (UFF).

## Requisitos

- Python 3.12
- Linux (desenvolvida e testada no Ubuntu 24.04 sob WSL2)

## Como rodar localmente

A partir da raiz do repositório:

```bash
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
.venv/bin/python src/app.py
```

O terminal mostra o endereço em que a plataforma está rodando. Por padrão, é o `http://127.0.0.1:7860`. Se essa porta estiver ocupada, o Gradio usa a próxima livre.

Para encerrar, `Ctrl+C` no terminal.

### Opções

- `--database ARQUIVO`: database SQLite usado. Padrão: `plataforma.db` na raiz do repositório, criado vazio se não existir.
- `--arquivos-de-modelos DIRETORIO`: diretorio onde ficam as cópias dos arquivos de modelo. Padrão: `arquivos_de_modelos/` na raiz.
- `--gerenciar-modelos`: liga o cadastro e a remoção de modelos na tela de Configurações. Desligada por padrão.

## Modelos e detectores

Um **modelo** é um arquivo `.pt` com a correspondência das suas classes às patologias da norma DNIT 005/2003-TER. Um **detector** é um modelo com uma configuração de inferência (resolução de entrada, limiar de confiança e máximo de detecções); é o que se escolhe na tela de Análise.

Para permitir o cadastro um modelo pela plataforma, ela deve ser iniciada com `--gerenciar-modelos`, para que os modelos possam ser adicionados na tela de Configurações. Detectores são criados e removidos na mesma tela, sem precisar da opção.

Modelos e detectores **fixos** não podem ser removidos pela tela. A marcação é feita direto no database, pelo id que aparece na tela de Configurações:

```bash
.venv/bin/python -c "import sqlite3; c = sqlite3.connect('plataforma.db'); c.execute('UPDATE modelo SET fixo = 1 WHERE id = 1'); c.commit()"
.venv/bin/python -c "import sqlite3; c = sqlite3.connect('plataforma.db'); c.execute('UPDATE detector SET fixo = 1 WHERE id = 1'); c.commit()"
```

Para desfazer, troque `fixo = 1` por `fixo = 0`.

## Testes

```bash
.venv/bin/pip install -r requirements-dev.txt
.venv/bin/pytest
```

## Créditos

Ícones do [Lucide](https://lucide.dev), sob licença ISC.