
from src.clients import get_qwen_client
from src.config import CONFIG

#生成
def generate_answer(question:str, contexts:list[dict]) -> str:
    content_parts = []

    for index, item in enumerate(contexts, start=1):

        metadata = item["metadata"]

        source = metadata.get("source", "未知文件")
        page = metadata.get("page", "未知页码")

        #将每一条信息进行整理
        content_parts.append(
            f"""
            [资料：{index}]
            来源: {source}
            页码: {page}  
            内容: {item["page_content"]}  """ )

    context_text = "\n\n".join(content_parts)

    #加载千问模型
    client = get_qwen_client()

    #生成答案
    response = client.chat.completions.create(
        model= CONFIG.chat_model,
        messages=[
            {
                "role": "system",
                "content":
                    "你是一个学校资料RAG助手。"
                    "必须只根据检索资料回答；"
                    "资料不足时明确说明知识库中没有足够信息；"
                    "不要编造。"
            },
            {
                "role" : "user",
                "content":f"""用户问题: {question}
                检索资料:{context_text}
                请给出清楚、简洁的回答。
                引用资料时使用 [资料1]、[资料2] 这样的编号。
                """
            }
        ],
        n=1     #大模型返回1个答案，默认情况也是n=1
    )
    return response.choices[0].message.content or ""


