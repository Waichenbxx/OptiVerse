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
