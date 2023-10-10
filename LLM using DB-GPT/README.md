# DB-GPT: ChatGPT Integration Guide
Welcome to DB-GPT! This README will help you set up and integrate our project seamlessly with your environment and data.

## Table of Contents
- [Hardware Requirements](#hardware-requirements)
- [Installation](#installation)
- [Run](#run)
- [Advanced Configurations](#advanced-configurations)
- [Tips & Troubleshooting](#tips--troubleshooting)

## Hardware Requirements
To achieve optimal ChatGPT performance, ensure your system meets the following GPU requirements:

| GPU       | VRAM Size | Performance Description                                        |
|-----------|-----------|---------------------------------------------------------------|
| RTX 4090  | 24 GB     | Smooth conversation inference                                 |
| RTX 3090  | 24 GB     | Smooth conversation inference, superior to V100                |
| V100      | 16 GB     | Possible conversation inference, with noticeable stutter      |
| T4        | 16 GB     | Possible conversation inference, with noticeable stutter      |

For limited VRAM sizes, DB-GPT supports 8-bit and 4-bit quantization. Below are the VRAM sizes for various models and quantizations:

_Model & Quantization VRAM Usage Table Here_

## Installation

1. **Clone the Repository**

   ```
   git clone https://github.com/eosphoros-ai/DB-GPT.git
   ```

2. **Setup Environment**: Use Miniconda3 virtual environment for installation. [How to install Miniconda](#)
   ```bash
   python>=3.10
   conda create -n dbgpt_env python=3.10
   conda activate dbgpt_env
   pip install -e ".[default]"
   python -m spacy download zh_core_web_sm
   ```

3. **Download Models**: Create a `models` directory inside the project to store models from HuggingFace.
   ```bash
   cd DB-GPT
   mkdir models && cd models

   # llm model
   git clone https://huggingface.co/lmsys/vicuna-13b-v1.5

   # embedding model
   git clone https://huggingface.co/GanymedeNil/text2vec-large-chinese
   ```

   ⚠️ Ensure `git-lfs` is installed:
   ```
   centos: yum install git-lfs
   ubuntu: app-get install git-lfs
   macos:  brew install git-lfs
   ```

4. **Configure Environment File**: Copy and configure the `.env` template.
   ```bash
   cp .env.template .env
   ```

## Run

1. **(Optional)** Load examples into SQLite:

   For Linux/Mac:
   ```bash
   bash ./scripts/examples/load_examples.sh
   ```
   For Windows:
   ```
   .\scripts\examples\load_examples.bat
   ```

2. **Start the Server**:
   ```bash
   python pilot/server/dbgpt_server.py
   ```
   Visit [http://localhost:5000](http://localhost:5000) in your browser to see the product live!

## Advanced Configurations

- **External LLM Service Configuration**: Instructions [here](#).

- **GPU Management**: By default, DB-GPT utilizes all available GPUs. Modify the `.env` file's `CUDA_VISIBLE_DEVICES` setting to specify GPU IDs. Example usage:
  ```bash
  # 1 GPU
  CUDA_VISIBLE_DEVICES=0 python3 pilot/server/dbgpt_server.py

  # 4 GPUs
  CUDA_VISIBLE_DEVICES=3,4,5,6 python3 pilot/server/dbgpt_server.py
  ```

## Tips & Troubleshooting

- **Memory Constraints**: DB-GPT supports 8-bit and 4-bit quantization to aid devices with memory constraints. Adjust the `.env` file's `QUANTIZE_8bit` and `QUANTIZE_4bit` settings as needed.

- **Web UI**: Learn more about `dbgpt-webui` [here](https://github.com/csunny/DB-GPT/tree/new-page-framework/datacenter).
