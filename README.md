This project leverages LLMs (Large Language Models) to batch analyze documents and summarize key information for each company, producing structured output summaries for business analysis and data archiving.

## Features

- Supports chunk-wise processing for long texts, avoiding request length limitations.
- Auto-retries with exponential backoff to handle HTTP 429 errors from LLM service.
- Checks the semantic completeness of the generated LLM content and avoids incomplete fragments.
- Outputs structured key data per company, covering business, market share, and financials.
- Automated workflow for summarizing results into a concise format.

## Usage

1. **Environment Setup:**
   - The script requires a `.env` file to store sensitive LLM configuration (KEY, URL, MODEL).  
   - The `.env` file is ignored by git (`.gitignore`). Please create your own `.env` file locally.

   Required variable example:
   ```
   LITE_LLM_KEY=your_key_here
   LITE_LLM_URL1=https://your-llm-api-url
   LITE_LLM_MODEL=your-llm-model-name
   ```

2. **Prepare Input Files:**
   - List target companies in the `Targets.txt` file (comma-separated).
   - Place each company's details in the `CompanyDetails` folder as `{company_name}.txt`.

3. **Run the Script:**
   - Running the script will:
     - Read the list of target companies.
     - Call the LLM on each company’s text in chunks, summarizing key data to `Output.txt`.
     - Further summarize `Output.txt` into concise, structured company summaries (≤400 characters each) in `OutputSummary.txt`.

   Example command (Windows):
   ```
   python <your_script_filename>.py
   ```

## File Structure

- `.env` *(user-provided, ignored in repo)*: API key and model configuration.
- `Targets.txt`: List of target companies (comma-separated).
- `CompanyDetails/`: Folder holding each company’s detail file.
- `Output.txt`: Raw LLM output.
- `OutputSummary.txt`: Final structured summary.

## Dependencies

- Python 3.x
- [requests](https://pypi.org/project/requests/)
- [python-dotenv](https://pypi.org/project/python-dotenv/)
- [urllib3](https://pypi.org/project/urllib3/)
- Standard library: os, time, pathlib

Make sure all dependencies are installed via pip.

## Notes

- You must create the `CompanyDetails` folder, `Targets.txt`, and `.env` with suitable contents/paths

------------------------------------Chinese-----------------------------------------
## 功能亮点

- 支持长文本分块处理，有效避免单次请求长度受限。
- 自动处理 LLM 请求的 429 错误并实现指数退避重试机制。
- 检查 LLM 反馈内容语义完整性，避免片段断裂问题。
- 支持按指定格式输出公司业务、市场占有与财务数据摘要。
- 提供自动化摘要生成流程，将分析结果进一步浓缩。

## 使用说明

1. **环境变量配置：**
   - 本脚本依赖 `.env` 文件存放 LLM KEY、URL、MODEL 等敏感配置信息。该文件默认已被 `.gitignore` 忽略，请根据实际情况在本地创建 `.env` 文件。

   需要配置的变量包括（示例）：
   ```
   LITE_LLM_KEY=your_key_here
   LITE_LLM_URL1=https://your-llm-api-url
   LITE_LLM_MODEL=your-llm-model-name
   ```

2. **输入文件准备：**
   - 在 `Targets.txt` 文件中列出目标公司名称（以逗号分隔）。
   - 在 `CompanyDetails` 文件夹下，将每家公司的详细信息分别存为 `{公司名称}.txt` 文件。

3. **运行脚本：**
   - 运行主程序会自动：
     - 读取目标公司名单。
     - 调用 LLM 对每家公司文本进行分块处理并归纳输出关键数据到 `Output.txt` 文件。
     - 基于 `Output.txt` 的内容进一步生成限制400字以内的公司独立摘要，输出至 `OutputSummary.txt`。

   示例命令（Windows环境下）：
   ```
   python <your_script_filename>.py
   ```

## 文件结构

- `.env`*（需用户自建，已忽略）*：存放API密钥和模型配置。
- `Targets.txt`：目标公司清单（逗号分隔）。
- `CompanyDetails/`：每家公司详细资料txt文件。
- `Output.txt`：LLM生成的原始输出。
- `OutputSummary.txt`：最终公司摘要（结构化输出）。

## 主要依赖

- Python 3.x
- [requests](https://pypi.org/project/requests/)
- [python-dotenv](https://pypi.org/project/python-dotenv/)
- [urllib3](https://pypi.org/project/urllib3/)
- 标准库: os, time, pathlib

请确保上述依赖均已通过 pip 安装。

## 注意事项

- `CompanyDetails` 文件夹、`Targets.txt`、`.env` 文件需根据实际路径和内容自建。
- 本项目仅做结构化业务信息整理，输出不包含与输入内容无关的信息。
- 如遇频繁429请求，请适当调整重试次数与等待时间。

## 贡献与反馈

如有建议或 BUG，欢迎提交 Issues。

````
