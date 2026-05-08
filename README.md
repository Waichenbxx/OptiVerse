# OptiVerse: A Comprehensive Benchmark towards Optimization Problem Solving

[![arXiv](https://img.shields.io/badge/📄_arXiv_Paper-2604.21510-b31b1b.svg)](https://arxiv.org/abs/2604.21510)
[![Dataset](https://img.shields.io/badge/🤗_Hugging_Face_Dataset-Waicheng/OptiVerse-blue.svg)](https://huggingface.co/datasets/Waicheng/OptiVerse)
[![GitHub](https://img.shields.io/badge/💻_GitHub_Repository-Waichenbxx/OptiVerse-black.svg)](https://github.com/Waichenbxx/OptiVerse)


---

**OptiVerse has been accepted to ACL 2026 Findings**

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

We conducted an extensive empirical study evaluating 22 Large Language Models across varying scales. The comprehensive evaluation results on the benchmark are presented below:

<table align="center">
  <thead>
    <tr>
      <th rowspan="2">Large Language Model</th>
      <th colspan="6">Domain</th>
      <th colspan="3">Difficulty</th>
      <th rowspan="2">Avg.</th>
    </tr>
    <tr>
      <th>MP</th>
      <th>CO</th>
      <th>SO</th>
      <th>DO</th>
      <th>OC</th>
      <th>GO</th>
      <th>Easy</th>
      <th>Med.</th>
      <th>Hard</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td colspan="11" align="center" bgcolor="#f2f2f2"><b>Open-Source Non-Thinking Models</b></td>
    </tr>
    <tr>
      <td>Internlm3-8B-instruct</td>
      <td>11.44</td><td>7.56</td><td>5.00</td><td>8.22</td><td>0.00</td><td>3.92</td><td>18.67</td><td>3.75</td><td>3.00</td><td>8.00</td>
    </tr>
    <tr>
      <td>Ministral3-8B-Instruct</td>
      <td>26.01</td><td>18.44</td><td>19.35</td><td>12.08</td><td>2.56</td><td>5.88</td><td>39.33</td><td>14.75</td><td>5.67</td><td>18.20</td>
    </tr>
    <tr>
      <td>Qwen3-8B-Instruct</td>
      <td>23.98</td><td>22.69</td><td>20.83</td><td>14.38</td><td>6.41</td><td>13.73</td><td>42.67</td><td>12.25</td><td>7.67</td><td>20.00</td>
    </tr>
    <tr>
      <td>Qwen2.5-72B</td>
      <td>31.61</td><td>27.31</td><td>20.00</td><td>15.75</td><td>7.69</td><td>13.73</td><td>48.00</td><td>16.50</td><td>10.33</td><td>24.10</td>
    </tr>
    <tr>
      <td>Qwen3-Coder-30B</td>
      <td>30.79</td><td>31.09</td><td>23.33</td><td>23.29</td><td>8.97</td><td>9.80</td><td>49.67</td><td>19.25</td><td>11.67</td><td>26.10</td>
    </tr>
    <tr>
      <td>Qwen3-30B-Instruct</td>
      <td>38.96</td><td>36.13</td><td>31.67</td><td>34.25</td><td>19.23</td><td>15.69</td><td>70.33</td><td>21.75</td><td>14.00</td><td>34.00</td>
    </tr>
    <tr>
      <td>Kimi-K2</td>
      <td>40.05</td><td>44.54</td><td>38.33</td><td>39.73</td><td>24.36</td><td>25.49</td><td>71.33</td><td>31.50</td><td>16.33</td><td>38.90</td>
    </tr>
    <tr>
      <td>Qwen3-235B-Instruct</td>
      <td>44.41</td><td>47.06</td><td>45.83</td><td>41.10</td><td>42.31</td><td>41.18</td><td>78.33</td><td>39.75</td><td>16.67</td><td>44.40</td>
    </tr>
    <tr>
      <td>DeepSeek-V3.2-Chat</td>
      <td>51.23</td><td>47.48</td><td>45.00</td><td>43.15</td><td>21.79</td><td>35.29</td><td>79.67</td><td>39.25</td><td>19.00</td><td>45.30</td>
    </tr>
    <tr>
      <td colspan="11" align="center" bgcolor="#f2f2f2"><b>Open-Source Thinking Models</b></td>
    </tr>
    <tr>
      <td>Qwen3-8B-Thinking</td>
      <td>40.33</td><td>43.70</td><td>41.67</td><td>39.73</td><td>25.64</td><td>37.25</td><td>73.00</td><td>33.00</td><td>16.00</td><td>39.90</td>
    </tr>
    <tr>
      <td>GPT-OSS-120B</td>
      <td>49.54</td><td>55.33</td><td>34.19</td><td>38.93</td><td>32.05</td><td>35.29</td><td>78.67</td><td>39.25</td><td>18.67</td><td>44.90</td>
    </tr>
    <tr>
      <td>Qwen3-30B-Thinking</td>
      <td>49.59</td><td>46.64</td><td>46.67</td><td>46.58</td><td>30.77</td><td>43.14</td><td>80.67</td><td>40.00</td><td>20.33</td><td>46.30</td>
    </tr>
    <tr>
      <td>DeepSeek-V3.2-Reasoner</td>
      <td>53.68</td><td>52.52</td><td>45.00</td><td>49.32</td><td>28.21</td><td>49.02</td><td>84.33</td><td>44.50</td><td>21.33</td><td>49.50</td>
    </tr>
    <tr>
      <td>Qwen3-235B-Thinking</td>
      <td>53.68</td><td>51.26</td><td>49.17</td><td>52.74</td><td>43.59</td><td>49.02</td><td>87.33</td><td>47.00</td><td>21.33</td><td>51.40</td>
    </tr>
    <tr>
      <td colspan="11" align="center" bgcolor="#f2f2f2"><b>Closed-Source Thinking Models</b></td>
    </tr>
    <tr>
      <td>Gemini-2.5-Flash</td>
      <td>46.05</td><td>46.22</td><td>48.33</td><td>48.63</td><td>48.72</td><td>54.90</td><td>82.33</td><td>42.75</td><td>18.67</td><td>47.40</td>
    </tr>
    <tr>
      <td>Gemini-2.5-Pro</td>
      <td>53.68</td><td>49.16</td><td>50.00</td><td>47.95</td><td>38.46</td><td>43.14</td><td>87.00</td><td>43.75</td><td>20.00</td><td>49.60</td>
    </tr>
    <tr>
      <td>Claude-4.5-Sonnet</td>
      <td>53.41</td><td>52.52</td><td>46.67</td><td>47.95</td><td>34.62</td><td>45.10</td><td>83.67</td><td>45.25</td><td>21.67</td><td>49.70</td>
    </tr>
    <tr>
      <td>o3</td>
      <td>52.04</td><td>53.78</td><td>45.83</td><td>56.85</td><td>39.74</td><td>45.10</td><td>86.67</td><td>47.25</td><td>20.67</td><td>51.10</td>
    </tr>
    <tr>
      <td>o4-mini</td>
      <td>50.95</td><td>54.20</td><td>48.33</td><td>55.48</td><td>42.31</td><td>47.06</td><td>87.67</td><td>46.75</td><td>20.67</td><td>51.20</td>
    </tr>
    <tr>
      <td>GPT-5.2</td>
      <td>55.86</td><td>57.14</td><td>50.00</td><td>57.53</td><td>50.00</td><td>54.90</td><td>91.00</td><td>50.75</td><td>25.33</td><td>55.20</td>
    </tr>
    <tr>
      <td>Gemini-3-Flash</td>
      <td>54.77</td><td>59.24</td><td>54.17</td><td>55.48</td><td>48.72</td><td>56.86</td><td>88.67</td><td>53.25</td><td>25.33</td><td>55.50</td>
    </tr>
    <tr>
      <td>Gemini-3-Pro</td>
      <td>58.04</td><td>57.14</td><td>56.67</td><td>56.85</td><td>42.31</td><td>50.98</td><td>89.00</td><td>52.75</td><td>27.00</td><td>55.90</td>
    </tr>
  </tbody>
</table>

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

## 🔗 Quick Links

- [📄 Paper](https://arxiv.org/abs/2604.21510) 
- [🤗 Dataset](https://huggingface.co/datasets/Waicheng/OptiVerse)
- [🌐 Project Page](https://waichenbxx.github.io/OptiVerse/)
- [💻 GitHub Repository](https://github.com/Waichenbxx/OptiVerse)
