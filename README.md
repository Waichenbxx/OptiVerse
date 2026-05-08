# OptiVerse: A Comprehensive Benchmark towards Optimization Problem Solving

[![arXiv](https://img.shields.io/badge/📄_arXiv_Paper-2604.21510-b31b1b.svg)](https://arxiv.org/abs/2604.21510)
[![Dataset](https://img.shields.io/badge/🤗_Hugging_Face_Dataset-Waicheng/OptiVerse-blue.svg)](https://huggingface.co/datasets/Waicheng/OptiVerse)
[![GitHub](https://img.shields.io/badge/💻_GitHub_Repository-Waichenbxx/OptiVerse-black.svg)](https://github.com/Waichenbxx/OptiVerse)


---

[cite_start]OptiVerse has been accepted to **ACL 2026 Findings** [cite: 2]

## 📋 Overview

While Large Language Models (LLMs) demonstrate remarkable reasoning capabilities, complex optimization tasks remain highly challenging. Existing benchmarks focus narrowly on Mathematical Programming and Combinatorial Optimization, hindering comprehensive evaluation. 

To address this, we introduce **OptiVerse**, a comprehensive benchmark of **1,000 carefully curated optimization problems** spanning six distinct and often neglected domains. Our extensive experiments with 22 LLMs reveal sharp performance degradation on hard problems, where even advanced models like GPT-5.2 and Gemini-3 struggle to exceed 30% accuracy.

## ✨ Key Features

* 📊 **Dataset Size**: 1,000 high-quality, curated optimization problems.
* 🎯 **Six Domains**: Mathematical Programming (MP), Combinatorial Optimization (CO), Stochastic Optimization (SO), Dynamic Optimization (DO), Optimal Control (OC), Game Optimization (GO).
* 📈 **Three Difficulty Levels**: Easy (300), Medium (400), Hard (300).
* 🔄 **Cross-Paradigm Versatility**: Requires models to autonomously identify the paradigm and write executable code using various solvers (gurobi, scipy, cvxpy, pulp, etc.).
* 🤖 **DVA-Agent**: Introduces a novel Dual-View Auditor Agent to detect and repair silent semantic discrepancies during modeling.

## 📊 Benchmark Comparison

| Benchmark | Size | Table | Graph | Answer Form | MP | CO | SO | DO | OC | GO |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| ComplexOR | 37 | ❌ | ❌ | Scalar | ✅ | ✅ | ❌ | ❌ | ❌ | ❌ |
| NLP4LP | 269 | ❌ | ❌ | Scalar | ✅ | ✅ | ❌ | ❌ | ❌ | ❌ |
| MAMO | 863 | ✅ | ✅ | Scalar | ✅ | ✅ | ❌ | ❌ | ❌ | ❌ |
| OptiBench | 605 | ✅ | ❌ | Scalar | ✅ | ✅ | ❌ | ❌ | ❌ | ❌ |
| **OptiVerse (Ours)** | **1000** | ✅ | ✅ | **Vector** | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |

## 🔧 Data Collection & Curation

To construct a benchmark that is both comprehensive and rigorously challenging, we curated a massive dataset derived from highly authoritative academic resources through a meticulous five-stage pipeline:

1. **Acquisition**: Sourced from a raw corpus of 82 distinct authoritative textbooks, graduate entrance exams, and applied modeling case studies (encompassing 26,702 pages).
2. **Standardization**: Processed using the MinerU2.5 framework to accurately extract and preserve complex tabular and graphical data alongside textual descriptions.
3. **Verification & Translation**: Rigorously reviewed and translated by domain-expert Ph.D. and Master's students in Operations Research to guarantee technical precision and correct mathematical notation.
4. **Quality Filtering**: Strictly excluded problems whose solutions were readily accessible through web searches to mitigate data contamination risks.
5. **Classification**: Organized into a 2D taxonomy spanning the 6 optimization domains and 3 difficulty levels.

## 🔍 Evaluation Framework

To handle the complexity of diverse solver outputs and varying formatting styles, we employ a robust two-stage **LLM-as-a-Judge** evaluation methodology:

* **Stage 1: Answer Extraction**: A Structure Synthesis Prompt acts as an extractor, parsing raw execution logs and unstructured intermediate outputs into a clean, valid JSON object containing specific numerical values and decisions.
* **Stage 2: Answer Verification**: A judge model (acting as a "Strict Mathematics Teaching Assistant") evaluates the extracted JSON against the Ground Truth based on three rigorous criteria:
  * **Completeness & Precision**: Enforces a strict relative numerical error tolerance of **$\le 0.1\%$**.
  * **Semantic Flexibility**: Intelligently handles unit variations (e.g., "0.5" vs. "50%") and assesses the semantic equivalence of non-numerical strategies (e.g., game theory decisions).
  * **Reasoning-First Verification**: Generates a step-by-step verification log prior to delivering the final `is_correct` boolean verdict.

## 📈 Experimental Results

We conducted an extensive empirical study evaluating 22 Large Language Models across varying scales. [cite_start]The comprehensive evaluation results on the benchmark are presented below[cite: 233, 236]:

| Large Language Model | MP | CO | DO | SO | OC | GO | Easy | Med. | Hard | Avg. |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **Open-Source Non-Thinking Models** | | | | | | | | | | |
| Internlm3-8B-instruct | 11.44 | 0.00 | 8.22 | 7.56 | 5.00 | 3.92 | 18.67 | 3.75 | 3.00 | 8.00 |
| Ministral3-8B-Instruct | 26.01 | 2.56 | 12.08 | 19.35 | 18.44 | 5.88 | 39.33 | 14.75 | 5.67 | 18.20 |
| Qwen3-8B-Instruct | 23.98 | 6.41 | 14.38 | 20.83 | 22.69 | 13.73 | 42.67 | 12.25 | 7.67 | 20.00 |
| Qwen2.5-72B | 31.61 | 27.31 | 15.75 | 7.69 | 20.00 | 13.73 | 48.00 | 16.50 | 10.33 | 24.10 |
| Qwen3-Coder-30B | 30.79 | 8.97 | 23.29 | 23.33 | 31.09 | 9.80 | 49.67 | 19.25 | 11.67 | 26.10 |
| Qwen3-30B-Instruct | 38.96 | 36.13 | 31.67 | 34.25 | 19.23 | 15.69 | 70.33 | 21.75 | 14.00 | 34.00 |
| Kimi-K2 | 40.05 | 24.36 | 39.73 | 38.33 | 44.54 | 25.49 | 71.33 | 31.50 | 16.33 | 38.90 |
| Qwen3-235B-Instruct | 44.41 | 42.31 | 41.10 | 45.83 | 47.06 | 41.18 | 78.33 | 39.75 | 16.67 | 44.40 |
| DeepSeek-V3.2-Chat | 51.23 | 45.00 | 47.48 | 21.79 | 43.15 | 35.29 | 79.67 | 39.25 | 19.00 | 45.30 |
| **Open-Source Thinking Models** | | | | | | | | | | |
| Qwen3-8B-Thinking | 40.33 | 39.73 | 25.64 | 41.67 | 43.70 | 37.25 | 73.00 | 33.00 | 16.00 | 39.90 |
| GPT-OSS-120B | 49.54 | 38.93 | 32.05 | 34.19 | 55.33 | 35.29 | 78.67 | 39.25 | 18.67 | 44.90 |
| Qwen3-30B-Thinking | 49.59 | 46.58 | 30.77 | 46.67 | 46.64 | 43.14 | 80.67 | 40.00 | 20.33 | 46.30 |
| DeepSeek-V3.2-Reasoner | 53.68 | 49.32 | 28.21 | 45.00 | 52.52 | 49.02 | 84.33 | 44.50 | 21.33 | 49.50 |
| Qwen3-235B-Thinking | 53.68 | 52.74 | 43.59 | 49.17 | 51.26 | 49.02 | 87.33 | 47.00 | 21.33 | 51.40 |
| **Closed-Source Models** | | | | | | | | | | |
| Gemini-2.5-Flash | 46.05 | 48.33 | 46.22 | 48.63 | 48.72 | 54.90 | 82.33 | 42.75 | 18.67 | 47.40 |
| Gemini-2.5-Pro | 53.68 | 49.16 | 50.00 | 47.95 | 38.46 | 43.14 | 87.00 | 43.75 | 20.00 | 49.60 |
| Claude-4.5-Sonnet | 53.41 | 47.95 | 34.62 | 46.67 | 52.52 | 45.10 | 83.67 | 45.25 | 21.67 | 49.70 |
| o3 | 52.04 | 53.78 | 45.83 | 56.85 | 39.74 | 45.10 | 86.67 | 47.25 | 20.67 | 51.10 |
| o4-mini | 50.95 | 42.31 | 54.20 | 48.33 | 55.48 | 47.06 | 87.67 | 46.75 | 20.67 | 51.20 |
| GPT-5.2 | 55.86 | 57.14 | 50.00 | 57.53 | 50.00 | 54.90 | 91.00 | 50.75 | 25.33 | 55.20 |
| Gemini-3-Flash | 54.77 | 59.24 | 54.17 | 55.48 | 48.72 | 56.86 | 88.67 | 53.25 | 25.33 | 55.50 |
| Gemini-3-Pro | 58.04 | 56.85 | 56.67 | 57.14 | 42.31 | 50.98 | 89.00 | 52.75 | 27.00 | 55.90 |

## 💡 Key Findings
1. **Significant Difficulty Sensitivity**: All LLMs exhibit sharp performance degradation as task difficulty scales. While top-tier models maintain high accuracy on Easy problems, they struggle profoundly with Hard problems—even advanced models like GPT-5.2 and Gemini-3-Pro fail to exceed **27%** accuracy.
2. **Superiority of Reasoning Chains**: Models equipped with explicit reasoning capabilities (e.g., Qwen3-Thinking, DeepSeek-Reasoner, OpenAI o3) consistently outperform their standard instruction-tuned counterparts by a significant margin.
3. **Domain-Specific Fragility**: Models lack cross-domain robustness. Success rates in understudied categories (e.g., Optimal Control, Dynamic Optimization) severely trail behind common Mathematical Programming and Combinatorial Optimization tasks.
4. **Modeling is the Primary Bottleneck**: Fine-grained error analysis reveals that *Modeling & Logic errors* constitute the predominant bottleneck, often manifesting as silent semantic discrepancies despite successful code execution.

## 🤖 Dual-View Auditor Agent (DVA-Agent)

Error analysis reveals that **Modeling & Logic errors** remain the primary bottleneck across all LLMs. To address this, we propose the **Dual-View Auditor Agent (DVA-Agent)**. 

Unlike simple syntax checkers, DVA-Agent acts as an adversarial evaluator using **Semantic Triangulation**:
1. **Requirement Extraction**: Extracts missing constraints directly from the problem text.
2. **Blind Code Abstraction**: Reverse-engineers the mathematical logic purely from the generated code.
3. **Cross-Reference Analysis**: Compares the above to produce a discrepancy set. Modification is triggered only if discrepancies exist.

## 🚀 Getting Started

### 1. Installation

Clone this repository and install the required environments and solvers.

    git clone https://github.com/Waichenbxx/OptiVerse.git
    cd OptiVerse
    pip install -r requirements.txt

*Note: Some problems require commercial solvers like Gurobi. Please ensure you have the appropriate licenses installed.*

### 2. Run Inference & Execution

Generate modeling code and execute it in the sandbox environment:

    export API_KEY="your_api_key_here"

    python run_inference.py \
      --input_file "./data/OptiVerse-full.json" \
      --output_dir "./results" \
      --model "<MODEL_NAME>" \
      --base_url "<API_BASE_URL>"

### 3. Evaluation (LLM-as-a-Judge)

Evaluate the executed results against the ground truth using our 0.1% relative tolerance framework:

    python evaluate.py \
      --input_file "./results/solved.json" \
      --output_dir "./results/evaluation" 

## 📝 Citation

If you find OptiVerse useful in your research, please cite our paper:

    @article{zhang2026optiverse,
      title={OptiVerse: A Comprehensive Benchmark towards Optimization Problem Solving},
      author={Zhang, Xinyu and Zhang, Boxuan and Wan, Yuchen and Zhang, Lingling and Yao, Yixing and Wei, Bifan and Wu, Yaqiang and Liu, Jun},
      journal={arXiv preprint arXiv:2604.21510},
      year={2026}
    }

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.
