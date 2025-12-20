

## Project Overview

Paper2Code is a multi-agent LLM system that transforms scientific papers into code repositories. It uses a three-stage pipeline: planning, analysis, and code generation.

## Environment Setup

### Python Version

No Python version pin detected.

### Dependencies

Install the core dependencies using pip:

```bash
pip install -r requirements.txt
```
(Source: `README.md`, `requirements.txt`)

Alternatively, for specific use cases:
- For OpenAI API:
```bash
pip install openai
```
(Source: `README.md`)
- For open-source models with vLLM:
```bash
pip install vllm
```
(Source: `README.md`)

## Running Paper2Code

### Using OpenAI API

1. Set your OpenAI API key:
```bash
export OPENAI_API_KEY="<OPENAI_API_KEY>"
```
(Source: `README.md`)

2. Run Paper2Code with a PDF-based JSON input:
```bash
cd scripts
bash run.sh
```
(Source: `README.md`)

3. Run Paper2Code with a LaTeX source input:
```bash
cd scripts
bash run_latex.sh
```
(Source: `README.md`)

### Using Open Source Models with vLLM

1. Run Paper2Code with a PDF-based JSON input (default model: `deepseek-ai/DeepSeek-Coder-V2-Lite-Instruct`):
```bash
cd scripts
bash run_llm.sh
```
(Source: `README.md`)

2. Run Paper2Code with a LaTeX source input:
```bash
cd scripts
bash run_latex_llm.sh
```
(Source: `README.md`)

## Evaluation

The project includes scripts for model-based evaluation of generated repositories.

### Environment Setup for Evaluation

```bash
pip install tiktoken
export OPENAI_API_KEY="<OPENAI_API_KEY>"
```
(Source: `README.md`)

### Reference-free Evaluation

```bash
cd codes/
python eval.py \
    --paper_name Transformer \
    --pdf_json_path ../examples/Transformer_cleaned.json \
    --data_dir ../data \
    --output_dir ../outputs/Transformer \
    --target_repo_dir ../outputs/Transformer_repo \
    --eval_result_dir ../results \
    --eval_type ref_free \
    --generated_n 8 \
    --papercoder
```
(Source: `README.md`)

### Reference-based Evaluation

```bash
cd codes/
python eval.py \
    --paper_name Transformer \
    --pdf_json_path ../examples/Transformer_cleaned.json \
    --data_dir ../data \
    --output_dir ../outputs/Transformer \
    --target_repo_dir ../outputs/Transformer_repo \
    --gold_repo_dir ../examples/Transformer_gold_repo \
    --eval_result_dir ../results \
    --eval_type ref_based \
    --generated_n 8 \
    --papercoder
```
(Source: `README.md`)

## Development Tools

### Pre-commit Hooks

The project uses `nbstripout` via `pre-commit` hooks.
```yaml
# .pre-commit-config.yaml snippet
repos:
  - repo: https://github.com/kynan/nbstripout
    rev: master
    hooks:
      - id: nbstripout
```
(Source: `.pre-commit-config.yaml`)


Token usage: unknown (242,201)