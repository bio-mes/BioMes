# BioMes

BioMes is a Biological Multi-Expert System that simulates cross-disciplinary expert deliberation to generate mechanistically grounded and experimentally testable hypotheses. You can try BioMes online at [http://biomes.top/chat](http://biomes.top/chat).

## Requirements

- Python: 3.11
- See `requirements.txt` for Python package dependencies.

Install dependencies:

```bash
pip install -r requirements.txt
```

## Project layout

```bash
benchmark/  # Benchmark construction
BioMes/  # BioMes source code
LLMwTools/  # Baseline: LLM with Tools
ReAct/  # Baseline: ReAct Agent
Workflow/  # Baseline: Orchestrated Workflow
```

## Usage

In `BioMes/config/config_H_gpt-5-mini.yaml` and `BioMes/script/eval.sh`, set relevant parameters, and run `bash script/eval.sh` in the `BioMes` folder to conduct the evaluation.

Evaluation for other baselines is similar.


