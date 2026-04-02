import sys
from pathlib import Path

# 添加项目根目录到Python路径
sys.path.insert(0, str(Path(__file__).parent.parent))

"""RAG引擎模块"""
import os
import re
from typing import List, Dict
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
from langchain.embeddings.base import Embeddings
from zhipuai import ZhipuAI
import requests

from config.settings import settings
from src.utils import logger, timer


class ZhipuEmbeddings(Embeddings):
    """智谱AI嵌入类"""
    
    def __init__(self):
        self.client = ZhipuAI(api_key=settings.zhipu_api_key)
        self.model = settings.zhipu_embedding_model
    
    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        """批量嵌入文档"""
        embeddings = []
        for text in texts:
            response = self.client.embeddings.create(
                model=self.model,
                input=text
            )
            embeddings.append(response.data[0].embedding)
        return embeddings
    
    def embed_query(self, text: str) -> List[float]:
        """嵌入单个查询"""
        response = self.client.embeddings.create(
            model=self.model,
            input=text
        )
        return response.data[0].embedding


class RAGEngine:
    """RAG引擎"""
    
    def __init__(self):
        self.embeddings = ZhipuEmbeddings()
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=settings.chunk_size,
            chunk_overlap=settings.chunk_overlap,
        )
    
    @timer
    def load_pdf(self, pdf_path: str) -> List:
        """加载PDF文件"""
        if not os.path.exists(pdf_path):
            raise FileNotFoundError(f"文件不存在: {pdf_path}")
        
        loader = PyPDFLoader(pdf_path)
        documents = loader.load()
        logger.info(f"加载PDF成功，共{len(documents)}页")
        return documents
    
    @timer
    def split_documents(self, documents: List) -> List:
        """切分文档"""
        chunks = self.text_splitter.split_documents(documents)
        logger.info(f"切分成{len(chunks)}个文本块")
        return chunks
    
    @timer
    def create_vector_store(self, texts: List[str], metadatas: List[Dict] = None):
        """创建向量存储"""
        vectordb = Chroma.from_texts(
            texts=texts,
            embedding=self.embeddings,
            metadatas=metadatas,
            persist_directory=str(settings.vector_db_path)
        )
        logger.info(f"向量库创建成功，共{len(texts)}个向量")
        return vectordb
    
    @timer
    def analyze_resume(self, pdf_path: str, job_desc: str) -> Dict:
        """分析简历匹配度"""
        try:
            # 1. 加载PDF
            docs = self.load_pdf(pdf_path)
            
            # 2. 切分文本
            chunks = self.split_documents(docs)
            
            if not chunks:
                return {"success": False, "error": "无法从PDF中提取内容"}
            
            # 3. 提取文本和元数据
            texts = [c.page_content for c in chunks]
            metadatas = [c.metadata for c in chunks]
            
            # 4. 创建向量库并检索
            vectordb = self.create_vector_store(texts, metadatas)
            results = vectordb.similarity_search(job_desc, k=settings.retrieval_k)
            
            # 5. 提取相关片段
            relevant_text = "\n\n".join([r.page_content for r in results[:settings.rerank_k]])
            
            # 6. 调用DeepSeek分析
            analysis = self._call_deepseek(job_desc, relevant_text)
            
            # 7. 提取分数（优化版 - 优先匹配"匹配度评分"）
            score_patterns = [
                r'匹配度评分[：:]\s*(\d+)',
                r'总体匹配度评分[：:]\s*(\d+)',
                r'评分[：:]\s*(\d+)分',
                r'(\d+)分'
            ]
            
            score = 50
            for pattern in score_patterns:
                score_match = re.search(pattern, analysis)
                if score_match:
                    score = int(score_match.group(1))
                    break
            
            return {
                "success": True,
                "score": score,
                "analysis": analysis,
                "chunks_count": len(chunks)
            }
            
        except Exception as e:
            logger.error(f"分析失败: {e}")
            return {"success": False, "error": str(e)}
    
    def _call_deepseek(self, job_desc: str, resume_text: str) -> str:
        """调用DeepSeek API"""
        prompt = f"""请分析以下简历与职位描述的匹配度：

【职位描述】
{job_desc}

【简历内容】
{resume_text}

请从以下几个方面分析：
1. 总体匹配度评分（0-100分）
2. 匹配的优势（列出3点）
3. 不足之处（列出2-3点）
4. 改进建议

请用中文回答，格式清晰。"""

        response = requests.post(
            "https://api.deepseek.com/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {settings.deepseek_api_key}",
                "Content-Type": "application/json"
            },
            json={
                "model": settings.deepseek_chat_model,
                "messages": [{"role": "user", "content": prompt}],
                "temperature": 0.3
            },
            timeout=60
        )
        
        if response.status_code == 200:
            result = response.json()
            return result["choices"][0]["message"]["content"]
        else:
            raise Exception(f"API调用失败: {response.status_code}")