"""Streamlit主程序"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))
import streamlit as st
import tempfile
import os
from datetime import datetime

from config.settings import settings
from src.rag_engine import RAGEngine
from src.utils import logger

# 页面配置
st.set_page_config(
    page_title="AI简历筛选系统",
    page_icon="🤖",
    layout="wide"
)

# 标题
st.title("🤖 AI简历筛选系统")
st.markdown("上传简历PDF，输入职位描述，系统自动分析匹配度")

# 初始化引擎
@st.cache_resource
def init_engine():
    return RAGEngine()

engine = init_engine()

# 侧边栏
with st.sidebar:
    st.header("⚙️ 配置信息")
    st.markdown("**使用模型：**")
    st.markdown("- 嵌入模型：智谱AI embedding-2")
    st.markdown("- 对话模型：DeepSeek deepseek-chat")
    st.markdown("---")
    st.markdown("**使用方法：**")
    st.markdown("1. 上传PDF简历")
    st.markdown("2. 输入职位描述")
    st.markdown("3. 点击开始分析")
    st.markdown("---")
    st.markdown(f"**当前时间：** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

# 主界面
col1, col2 = st.columns(2)

with col1:
    st.subheader("📄 上传简历")
    uploaded_file = st.file_uploader("选择PDF文件", type=["pdf"])
    
    if uploaded_file:
        st.success(f"已上传: {uploaded_file.name}")

with col2:
    st.subheader("📋 职位描述")
    job_description = st.text_area(
        "粘贴职位描述",
        height=300,
        placeholder="例如：\n职位：Python开发工程师\n要求：\n- 熟悉Python、FastAPI\n- 有AI项目经验"
    )

# 分析按钮
if st.button("🚀 开始分析", type="primary"):
    if not uploaded_file:
        st.error("请先上传简历")
    elif not job_description:
        st.error("请输入职位描述")
    else:
        # 保存临时文件
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
            tmp.write(uploaded_file.getvalue())
            tmp_path = tmp.name
        
        with st.spinner("AI正在分析中，请稍候..."):
            result = engine.analyze_resume(tmp_path, job_description)
        
        # 清理临时文件
        os.unlink(tmp_path)
        
        if result["success"]:
            score = result["score"]
            
            if score >= 80:
                st.balloons()
                st.success(f"🎉 匹配度评分: {score}/100 - 高度匹配！")
            elif score >= 60:
                st.info(f"📊 匹配度评分: {score}/100 - 中等匹配")
            else:
                st.warning(f"⚠️ 匹配度评分: {score}/100 - 匹配度较低")
            
            st.subheader("📝 详细分析报告")
            st.markdown(result["analysis"])
            
            # 下载报告
            report = f"""# AI简历分析报告

## 匹配度评分: {score}/100

## 详细分析
{result["analysis"]}

---
生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""
            st.download_button(
                label="📥 下载报告",
                data=report,
                file_name="简历分析报告.md",
                mime="text/markdown"
            )
        else:
            st.error(result.get("error", "分析失败"))

# 页脚
st.markdown("---")
st.markdown("💡 提示：支持PDF格式，首次分析需加载模型")