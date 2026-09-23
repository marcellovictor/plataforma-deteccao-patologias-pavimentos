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