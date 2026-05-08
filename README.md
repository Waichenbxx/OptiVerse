# OptiVerse: A Comprehensive Benchmark towards Optimization Problem Solving

[![arXiv](https://img.shields.io/badge/📄_arXiv_Paper-2604.21510-b31b1b.svg)](https://arxiv.org/abs/2604.21510)
[![Dataset](https://img.shields.io/badge/🤗_Hugging_Face_Dataset-Waicheng/OptiVerse-blue.svg)](https://huggingface.co/datasets/Waicheng/OptiVerse)
[![GitHub](https://img.shields.io/badge/💻_GitHub_Repository-Waichenbxx/OptiVerse-black.svg)](https://github.com/Waichenbxx/OptiVerse)


---

OptiVerse has been accepted to **ACL 2026 Findings**

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

## 🤖 Dual-View Auditor Agent (DVA-Agent)

Error analysis reveals that **Modeling & Logic errors** remain the primary bottleneck across all LLMs. To address this, we propose the **Dual-View Auditor Agent (DVA-Agent)**. 

Unlike simple syntax checkers, DVA-Agent acts as an adversarial evaluator using **Semantic Triangulation**:
1. **Requirement Extraction**: Extracts missing constraints directly from the problem text.
2. **Blind Code Abstraction**: Reverse-engineers the mathematical logic purely from the generated code.
3. **Cross-Reference Analysis**: Compares the above to produce a discrepancy set. Modification is triggered only if discrepancies exist.

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

We conducted an extensive empirical study evaluating 22 Large Language Models across varying scales (from 8B parameter models to flagship frontiers like GPT-5.2 and Gemini-3-Pro). 

**Key Findings:**
1. **Significant Difficulty Sensitivity**: All LLMs exhibit sharp performance degradation as task difficulty scales. While top-tier models maintain high accuracy on Easy problems, they struggle profoundly with Hard problems—even advanced models like GPT-5.2 and Gemini-3-Pro fail to exceed **27%** accuracy.
2. **Superiority of Reasoning Chains**: Models equipped with explicit reasoning capabilities (e.g., Qwen3-Thinking, DeepSeek-Reasoner, OpenAI o3) consistently outperform their standard instruction-tuned counterparts by a significant margin.
3. **Domain-Specific Fragility**: Models lack cross-domain robustness. Success rates in understudied categories (e.g., Optimal Control, Dynamic Optimization) severely trail behind common Mathematical Programming and Combinatorial Optimization tasks.
4. **Modeling is the Primary Bottleneck**: Fine-grained error analysis reveals that *Modeling & Logic errors* constitute the predominant bottleneck, often manifesting as silent semantic discrepancies despite successful code execution.


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
      --model "deepseek-chat" \
      --base_url "https://api.deepseek.com"

### 3. Evaluation (LLM-as-a-Judge)

Evaluate the executed results against the ground truth using our 0.1% relative tolerance framework:

    python evaluate.py \
      --input_file "./results/solved.json" \
      --output_dir "./results/evaluation" 

## 📝 Citation

If you find OptiVerse useful in your research, please cite our paper:

    @article{zhang2026optiverse,
      title={OptiVerse: A Comprehensive Benchmark towards Optimization Problem Solving},
      author={Zhang, Boxuan and others},
      journal={arXiv preprint arXiv:2604.21510},
      year={2026}
    }

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.
