"""配置管理模块"""
import os
from pathlib import Path
from dotenv import load_dotenv

# 加载.env文件
load_dotenv()

class Settings:
    """统一配置管理"""
    
    def __init__(self):
        # 项目路径
        self.project_root = Path(__file__).parent.parent
        self.data_dir = self.project_root / "data"
        self.logs_dir = self.project_root / "logs"
        
        # 创建必要目录
        self.data_dir.mkdir(exist_ok=True)
        self.logs_dir.mkdir(exist_ok=True)
        
        # API密钥
        self.zhipu_api_key = os.getenv("ZHIPU_API_KEY", "")
        self.deepseek_api_key = os.getenv("DEEPSEEK_API_KEY", "")
        
        # 模型配置
        self.zhipu_embedding_model = "embedding-2"
        self.deepseek_chat_model = "deepseek-chat"
        
        # RAG配置
        self.chunk_size = 200
        self.chunk_overlap = 50
        self.retrieval_k = 5
        self.rerank_k = 3
        
        # 验证API密钥
        self._validate_keys()
    
    def _validate_keys(self):
        """验证API密钥是否存在"""
        if not self.zhipu_api_key:
            print("⚠️ 警告: ZHIPU_API_KEY 未设置")
        if not self.deepseek_api_key:
            print("⚠️ 警告: DEEPSEEK_API_KEY 未设置")
    
    @property
    def vector_db_path(self):
        return self.data_dir / "vector_db"

# 关键：创建settings实例供导入
settings = Settings()