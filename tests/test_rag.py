"""RAG引擎测试"""
import sys
from pathlib import Path

# 添加项目根目录到路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.rag_engine import RAGEngine

def test_rag_engine():
    """测试RAG引擎初始化"""
    try:
        engine = RAGEngine()
        print("✅ RAG引擎初始化成功")
    except Exception as e:
        print(f"❌ 初始化失败: {e}")

if __name__ == "__main__":
    test_rag_engine()