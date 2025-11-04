'''基于chunks LLM反馈进一提炼，形成一个文档；解决了429错误、实现了自动重传机制；
同时解决了LLM反馈中文字片段不完整的问题'''

import os
import time
import requests
from dotenv import load_dotenv
from pathlib import Path
import urllib3

# 禁用 InsecureRequestWarning 警告
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# 加载 .env 环境变量
ENV_PATH = "C:\\Users\\e005476\\CompareTdocTest\\.env"
load_dotenv(dotenv_path=ENV_PATH)

# 从 .env 文件中获取 LLM 配置信息
LLM_KEY = os.getenv("LITE_LLM_KEY")
LLM_URL = os.getenv("LITE_LLM_URL1")
LLM_MODEL = os.getenv("LITE_LLM_MODEL")

# 输入路径设置
BASE_DIR = Path("C:\\Users\\e005476\\CompareTdocTest")
TARGETS_FILE = BASE_DIR / "Targets.txt"
DETAILS_DIR = BASE_DIR / "CompanyDetails"
OUTPUT_FILE = BASE_DIR / "Output.txt"

# 调用 LLM 模型进行分析（POST 请求）
def analyze_with_llm_post(content, task_description, max_retries=5, initial_delay=5):
    """
    使用 POST 请求调用 LLM 服务，支持 429 错误的重试机制
    """
    headers = {
        "Authorization": f"Bearer {LLM_KEY}",
        "Content-Type": "application/json"
    }
    # 构造请求体
    payload = {
        "model": LLM_MODEL,
        "prompt": f"{task_description}\n\n{content}",
        "max_tokens": 600,  # 调整生成内容的最大长度
        "temperature": 0.5  # 调整生成随机性的高低
    }

    retries = 0
    delay = initial_delay

    while retries < max_retries:
        try:
            print(f"Sending POST request to {LLM_URL} (Attempt {retries + 1}/{max_retries})...")
            response = requests.post(LLM_URL, json=payload, headers=headers, verify=False)
            
            # 检查 HTTP 状态码
            response.raise_for_status()  # 若返回非 2xx 状态码会抛出异常
            
            # 打印响应内容（调试用）
            print(f"DEBUG: Server response: {response.text}")

            # 成功返回 JSON 中的结果
            result = response.json().get("choices", [{}])[0].get("text", "LLM 未返回结果")
        
            # 检查语义完整性
            if not result.endswith(('.', '。')):
                print("生成结果可能不完整，尝试重新生成...")
                retries += 1
                time.sleep(delay)  # 等待后重试
                continue  # 重新发送请求
            
            return result  # 返回完整生成结果
        
        except requests.exceptions.HTTPError as e:
            if response.status_code == 429:  # 捕获 429 错误
                print(f"429 错误：请求过多，等待 {delay} 秒重试...")
                time.sleep(delay)  # 等待后重试
                retries += 1
                delay *= 2  # 指数退避，延长等待时间
            else:
                print(f"POST 请求失败（非 429 错误）: {e}")
                return "LLM 服务请求失败"
        except Exception as e:
            print(f"POST 请求失败: {e}")
            return "LLM 服务请求失败"
        
     # 如果重试后仍然失败，则丢弃结果中最后部分
    if retries >= max_retries:
        print("多次重试后仍然失败，丢弃不完整的最后结果片段...")
        if result:
            # 改为仅丢弃最后的截断部分，保留剩余内容前所有完整文本
            if '.' in result:
                truncated_result = result.rsplit('.', 1)[0] + '.'
            elif '。' in result:
                truncated_result = result.rsplit('。', 1)[0] + '。'
            else:
                truncated_result = result.strip()  # 如果没有标点符号，返回原内容

            print(f"丢弃的内容：{result[len(truncated_result):]}")  # 打印丢弃的部分以便调试
            return truncated_result.strip()  # 返回处理后的有效内容
        return "LLM 服务请求失败"
    

# 分块输入数据（避免单请求长度过大）

def chunk_input(content, chunk_size=1000, overlap=100):  # 每chunk 1000 字符，重叠 100 字符
    """
    将长文本内容分块，为每块添加 overlap 字符以提升上下文连贯性
    """
    step = chunk_size - overlap  # 每块实际前进的步长
    for i in range(0, len(content), step):
        yield content[i:i + chunk_size]


def analyze_with_llm_in_chunks(content, task_description):
    """分块调用 LLM 服务"""
    results = []
    for chunk in chunk_input(content, chunk_size=4000):  # 每块 4000 字符
        print("Processing chunk...")
        result = analyze_with_llm_post(chunk, task_description)  # 使用 POST 请求
        results.append(result)  # 将当前块的结果添加到列表中
        time.sleep(2)  # 在每次请求之间添加 2 秒的延迟
    return "\n".join(results)

# 处理每个公司的文件信息
def process_company(company_name):
    company_file = DETAILS_DIR / f"{company_name}.txt"
    if not company_file.exists():
        print(f"未找到公司文件: {company_name}")
        return None
    # 读取公司详细内容
    with open(company_file, "r", encoding="utf-8") as file:
        content = file.read()
    # 定义任务描述
    task_description = (
        "从以下文本中提取关键信息，生成如下格式：\n"
        "公司名称\n"
        "公司主要业务：100字介绍业务分布\n"
        "公司市场占有情况：100字介绍市场情况\n"
        "公司财务数据：100字介绍营收情况\n"
    )
    # 调用 LLM 分析，分块处理
    result = analyze_with_llm_in_chunks(content, task_description)
    return result

def process_output_summary():
    """
    基于 Output.txt 的内容进一步生成公司摘要，每项内容限制在 400 字以内，
    按指定格式写入 OutputSummary.txt。
    """
    summary_task_description = (
        "从以下内容中生成每家公司的总结，每个公司的总结独立分开，每个公司总结的字数不得超过400字，严格按以下格式生成：\n"
        "公司1名称\n"
        "公司1主要业务：100字介绍业务分布\n"
        "公司1市场占有情况：100字介绍市场情况\n"
        "公司1财务数据：100字介绍营收情况\n"
        "此外，请勿引入任何与输入内容无关的信息。"
    )

    output_path = BASE_DIR / "Output.txt"
    summary_output_path = BASE_DIR / "OutputSummary.txt"

    # 检查 Output.txt 文件是否存在
    if not output_path.exists():
        print("未找到 Output.txt 文件。无法生成摘要。")
        return
    
      # 读取 Output.txt 文件内容
    with open(output_path, "r", encoding="utf-8") as file:
        output_content = file.read()

    # 使用 LLM 对内容进行总结
    print("生成摘要中...")
    summary_result = analyze_with_llm_in_chunks(output_content, summary_task_description)

    # 将摘要结果写入 OutputSummary.txt
    with open(summary_output_path, "w", encoding="utf-8") as summary_file:
        summary_file.write(summary_result)

    print(f"摘要生成完成，结果保存在: {summary_output_path}")

# 主函数
def main():
    # 检查 Targets.txt 是否存在
    if not TARGETS_FILE.exists():
        print("未找到 Targets.txt 文件。")
        return

    # 读取目标公司列表
    with open(TARGETS_FILE, "r", encoding="utf-8") as file:
        target_companies = file.read().strip().split(",")

    # 遍历目标公司并处理
    final_output = []
    for company in target_companies:
        company = company.strip()
        print(f"处理公司: {company}")
        result = process_company(company)
        if result:
            final_output.append(result)

    # 将处理结果写入 Output.txt
    if final_output:
        with open(OUTPUT_FILE, "w", encoding="utf-8") as output_file:
            output_file.write("\n\n".join(final_output))
        print(f"处理完成，结果保存在: {OUTPUT_FILE}")
    else:
        print("未生成任何输出。")

#  运行主函数
if __name__ == "__main__":
    main()
    # 基于生成的 Output.txt 生成摘要
    process_output_summary()