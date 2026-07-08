# 全局页面配置
import streamlit as st
st.set_page_config(page_title="乳腺癌数据可视化实践", layout="wide", page_icon="📋")

# 统一全部依赖
import os
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.datasets import load_breast_cancer
from PIL import Image
import pyecharts.options as opts
from pyecharts.charts import Pie, Radar
from streamlit_echarts import st_pyecharts

# 自定义医疗配色（恶性红色，良性蓝色）
COLOR_BENIGN = "#3498db"
COLOR_MALIGN = "#e74c3c"
# 全局seaborn绘图主题统一
sns.set_theme(style="whitegrid", palette=[COLOR_MALIGN, COLOR_BENIGN], font_scale=1.05)
# 全局matplotlib设置
plt.rcParams["font.family"] = ["SimHei", "WenQuanYi Micro Hei"]
plt.rcParams["axes.unicode_minus"] = False
plt.rcParams["savefig.dpi"] = 300
# 底图柔和浅蓝
plt.rcParams["axes.facecolor"] = "#e6f0f8"
BASE_DIR = os.getcwd()

# 缓存数据集
@st.cache_data
def load_data():
    cancer = load_breast_cancer()
    df = pd.DataFrame(cancer.data, columns=cancer.feature_names)
    df["类别标签"] = cancer.target
    # 修正映射：0=恶性，1=良性
    df["肿瘤类型"] = df["类别标签"].map({0:"恶性",1:"良性"})
    return df
df = load_data()

# 页面顶部公共头部
def page_header():
    st.title("📈 乳腺癌数据可视化实践")
    st.divider()

# ========== 页面1：项目概览 ==========
def page_overview():
    page_header()
    st.markdown("# 🏠 项目概览")
    st.divider()
    # 项目简介、样本统计、数据集预览、作业日志全部放这
    st.markdown("### 项目简介")
    st.info("本项目依次经过Excel基础统计和绘图、美林BI可视化，Python深度静态绘图，PyECharts交互式图表，Web仪表盘开发，工具对比五大环节，从描述统计、特征相关性、分布差异性多维度挖掘乳腺肿瘤良恶性的特征规律，为辅助肿瘤分类提供数据依据。")
    st.divider()

    # 彩色指标卡片创新排版
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("📋 总样本量", value=df.shape[0])
    with col2:
        st.metric("🧩 特征总数", value=30)
    with col3:
        st.metric("🔴 恶性样本", value=len(df[df["肿瘤类型"] == "恶性"]), delta_color="inverse")
    with col4:
        st.metric("🟢 良性样本", value=len(df[df["肿瘤类型"] == "良性"]), delta_color="normal")
    st.divider()

    # 从excel_output文件夹读取
    excel_stat_path = os.path.join(BASE_DIR, "excel_output", "描述统计.xlsx")
    stat_df = pd.read_excel(excel_stat_path, sheet_name="描述统计")

    with st.expander("📊 数据集Excel描述性统计表", expanded=False):
        st.dataframe(stat_df, use_container_width=True)

    # 数据预览
    st.subheader("🔍 数据集预览（前10行）")
    st.dataframe(df.head(10), use_container_width=True)

    # 数据集说明
    with st.expander("📖 数据集详细说明"):
        st.markdown("""
    1. 数据源：sklearn.datasets.load_breast_cancer()
    2. 样本数量：569条乳腺肿块医学检测样本
    3. 特征构成：30个连续数值特征，分为均值、误差、最差值三类指标
    4. 分类标签：恶性肿瘤(212例)、良性肿瘤(357例)
    """)

    # 作业日志
    try:
        try:
            with open(os.path.join(BASE_DIR, "作业日志.txt"), "r", encoding="utf-8") as f:
                log = f.read()
        except UnicodeDecodeError:
            # 中文Windows系统用gbk编码打开
            with open(os.path.join(BASE_DIR, "作业日志.txt"), "r", encoding="gbk") as f:
                log = f.read()

        with st.expander("📝 项目日志与学习感悟"):
            st.markdown(log)

    except FileNotFoundError:
        st.warning("请在项目根目录创建【作业日志.txt】文件，填写不少于200字的开发过程与心得体会。")
# ========== 页面2：Excel基础分析 ==========
def page_excel():
    page_header()
    BASE_DIR = os.getcwd()

    st.title("🟢 第一阶段：Excel描述统计 & 美林BI可视化")

    # 读取根目录下的描述统计表
    excel_stat_path = os.path.join(BASE_DIR, "excel_output", "描述统计.xlsx")
    stat_df = pd.read_excel(excel_stat_path, sheet_name="描述统计")
    st.subheader("数据集描述性统计表（Excel制作）")
    st.dataframe(stat_df, use_container_width=True)
    st.divider()

    # 图之典参考截图
    ref_img = Image.open(os.path.join(BASE_DIR, "excel_output", "图之典参考截图.png"))
    st.subheader("图表选型参考截图")
    st.image(ref_img)
    st.divider()

    # 展示所有图表（两列排版，顺序规整）
    img_path = os.path.join(BASE_DIR, "excel_output")
    img_order = [
        "饼图.png",
        "mean_area分布.png",
        "mean_radius分布.png",
        "mean_texture分布.png",
        "mean_radius箱线图.png",
        "mean_texture箱线图.png",
    ]

    desc_list = [
        """整个数据集一共 569 份乳腺肿瘤样本，良性样本占比63%，恶性样本占比37%，样本分布不均衡，良性样本数量明显更多。后续建模时需要留意样本不平衡可能带来的预测偏向问题。""",
        """该直方图展示肿块面积样本分布，多数样本集中在400-800区间，面积超过800后样本数量逐步递减，整体呈现右偏分布特征，能直观看到肿块面积的集中取值范围，为后续特征分组分析提供基础依据。""",
        """肿块平均半径样本大多集中在12至16区间，整体是右偏分布，样本主要集中在中小半径范围，极大极小半径样本数量偏少，结合临床常识猜测，肿块越大恶性概率越高，后面分组箱线图可以验证这个规律是否成立。""",
        """肿块纹理特征样本主要集中在16到20区间，整体呈近似正态分布，大部分患者肿块纹理数值处于中等水平，高低极值样本较少，说明单看整体分布看不出良恶性区别，需要结合分组箱线图对比两类肿瘤的纹理数值差异。""",
        """从箱线图能直观看出，恶性肿块的平均半径整体远高于良性，不管是中位数还是四分位数，恶性区间完全在良性上方，两者数值几乎没有重叠。这个特征区分效果很强，肿块平均半径是辨别乳腺肿瘤良恶性的核心指标。""",
        """对比两类肿瘤纹理分布箱线图，可以看出恶性肿块纹理整体数值更高，两类样本存在少量重叠区间。仅依靠纹理无法完全区分肿瘤类型，但具备一定区分趋势，可作为辅助判断良恶性的次要特征。"""
    ]

    # 两列布局
    cols = st.columns(2)
    for idx, img_name in enumerate(img_order):
        with cols[idx % 2]:
            img = Image.open(os.path.join(img_path, img_name))
            st.subheader(f"可视化图表：{img_name}")
            st.image(img)
            st.markdown(desc_list[idx])
            st.divider()

# ========== 页面3：Python静态可视化 ==========
def page_python():
    page_header()
    BASE_DIR = os.getcwd()

    st.title("🟠 第二阶段：Python静态深度可视化分析")

    chart_dir = os.path.join(BASE_DIR, "static_charts")
    png_list = sorted([f for f in os.listdir(chart_dir) if f.endswith(".png")])

    select_img = st.selectbox("请选择需要查看的可视化图表", png_list)
    img = Image.open(os.path.join(chart_dir, select_img))
    st.image(img)
    st.subheader("图表分析解读")
    if "heatmap" in select_img or "热力" in select_img:
        st.write("基于30维特征绘制相关性热力图，肿块半径、周长、面积等几何特征存在强相关性，存在多重共线性，后续建模需要特征降维筛选。")
    elif "violin" in select_img or "小提琴" in select_img:
        st.write("六大均值特征小提琴分布图，恶性肿瘤在半径、面积、紧致度等指标整体数值更高，纹理、平滑度两类特征样本重叠度高，分类效果较弱。")
    elif "cdf" in select_img.lower():
        st.write("肿块面积累积分布CDF函数图，蓝色良性曲线整体靠左、橙色恶性曲线整体靠右，两条曲线分离度高。恶性肿瘤肿块面积整体显著大于良性，该特征对肿瘤良恶性具备优秀的区分能力。")
    elif "pair" in select_img or "配对" in select_img:
        st.write("多特征配对散点矩阵图，既验证特征间相关性，也直观观察到两类样本存在明显聚类分离效果，可辅助筛选高区分度特征。")
    elif "radar" in select_img or "雷达" in select_img:
        st.write("归一化多维雷达图，从六大维度直观对比良恶性肿瘤整体指标差异，恶性肿瘤在尺寸类特征上整体取值更高。")
    elif "混淆矩阵" in select_img:
        st.write("混淆矩阵纵轴为真实肿瘤类别，横轴为模型预测类别，0代表恶性、1代表良性；仅7例恶性漏诊、2例良性误诊，错分样本极少，模型分类精准度高。")
    elif "ROC" in select_img or "roc" in select_img:
        st.write("ROC曲线紧贴左上角，AUC数值0.989接近1，代表该逻辑回归模型区分乳腺良恶性肿瘤的能力极强，漏诊与误诊概率都很低。")

# ========== 页面4：PyEcharts交互图表 ==========
def page_pyecharts():
    page_header()
    BASE_DIR = os.getcwd()

    st.title("🔴 第三阶段：PyEcharts交互式可视化图表")

    html_dir = os.path.join(BASE_DIR, "pyecharts_output")
    html_files = [f for f in os.listdir(html_dir) if f.endswith(".html")]

    select_html = st.radio("选择交互式可视化图表", html_files)
    with open(os.path.join(html_dir, select_html), "r", encoding="utf-8") as f:
        html_content = f.read()
    st.components.v1.html(html_content, height=720)

    st.subheader("图表分析说明")
    if "饼图" in select_html:
        st.markdown("""
        该环形交互饼图统计乳腺肿瘤数据集良恶性样本分布，恶性样本212例、良性样本357例，数据集样本分布不均衡。
        鼠标悬浮可查看样本数量与占比，支持图例筛选、图表下载、视图重置等交互操作，快速判断数据集类别均衡性。
        """)
    else:
        st.markdown("""
        多维交互式雷达图选取六大核心均值特征对比两类肿瘤指标差异，恶性肿瘤在半径、周长、面积维度均值显著更高。
        鼠标悬浮可查看每个维度精确特征数值，支持图例切换、图表导出、区域缩放，实现多维度特征差异交互式探索。
        """)

# ========== 页面5：综合探索仪表盘 ==========
def page_dashboard():
    page_header()
    plt.rcParams["font.family"] = ["SimHei", "Microsoft YaHei"]
    plt.rcParams["axes.unicode_minus"] = False

    @st.cache_data
    def load_data():
        cancer = load_breast_cancer()
        df = pd.DataFrame(cancer.data, columns=cancer.feature_names)
        # 修正映射
        df["肿瘤类型"] = cancer.target
        df["肿瘤类型"] = df["肿瘤类型"].map({0: "恶性", 1: "良性"})
        return df

    df = load_data()
    st.title("🎯 乳腺肿瘤特征动态探索综合仪表盘")

    # 交互控件
    feature_list = [col for col in df.columns if "mean" in col]
    selected_feat = st.selectbox("选择分析特征", feature_list)
    chart_type = st.radio("选择图表类型", ["箱线图", "直方图(KDE)"])

    # 绘图，调色板修正：恶性在前红色，良性在后蓝色
    fig, ax = plt.subplots(figsize=(12, 5))
    if chart_type == "箱线图":
        sns.boxplot(x="肿瘤类型", y=selected_feat, data=df, palette=[COLOR_MALIGN, COLOR_BENIGN], ax=ax)
        ax.set_title(f"{selected_feat} 良恶性肿瘤箱线分布")
    else:
        sns.histplot(data=df, x=selected_feat, hue="肿瘤类型", kde=True, palette=[COLOR_MALIGN, COLOR_BENIGN], ax=ax)
        ax.set_title(f"{selected_feat} 良恶性分布直方图")

    st.pyplot(fig)

    # 分组统计
    col_left, col_right = st.columns(2)
    with col_left:
        st.subheader("恶性样本特征描述统计")
        st.dataframe(df[df["肿瘤类型"]=="恶性"][selected_feat].describe(), use_container_width=True)
    with col_right:
        st.subheader("良性样本特征描述统计")
        st.dataframe(df[df["肿瘤类型"]=="良性"][selected_feat].describe(), use_container_width=True)

    # 创新点：数据质量检测
    st.divider()
    st.subheader("数据集质量检测")
    c1, c2 = st.columns(2)
    with c1:
        st.metric("缺失值总数量", df.isnull().sum().sum())
    with c2:
        st.metric("重复样本数量", df.duplicated().sum())
    st.success("数据集无缺失、无重复数据，数据质量良好，可用于特征分析与建模。")

# ==================== 页面6：工具对比  ====================
def page_compare():
    page_header()
    st.title("🛠️ 多可视化工具综合对比拓展模块")
    st.divider()

    st.subheader("1. 项目所用工具优缺点对比")
    table_data = [
        ["Excel", "零代码易上手 快速生成基础统计表格与简单图表", "无交互功能 大数据运行卡顿 无法实现专业统计绘图", "饼图 基础直方图 描述统计表"],
        ["Matplotlib & Seaborn", "高度自定义 支持热力图 ROC 混淆矩阵等建模配套专业图表", "需要Python编程基础 原生无交互效果", "热力图 分组箱线图 ROC曲线 配对散点图"],
        ["PyEcharts", "自带悬浮提示 缩放筛选等交互 可独立导出HTML网页", "缺少复杂统计分析功能 建模绘图支持不足", "雷达图 交互式饼图 动态分布直方图"],
        ["Streamlit", "一键整合全部代码与图表 快速生成可交付Web网页平台", "页面自定义样式存在少量限制", "整合全流程分析成果 生成完整数据分析仪表盘"]
    ]
    df = pd.DataFrame(table_data, columns=["工具名称","核心优势","局限性","适配图表与功能"])
    st.dataframe(df, use_container_width=True, height=320)
    st.divider()

    st.subheader("2. 本项目各工具分工实践总结")
    st.text("1 基础数据探查阶段 使用Excel完成原始数据描述统计 快速观察样本均值最值等基础信息")
    st.text("2 深度统计建模阶段 采用Matplotlib与Seaborn绘制专业统计图表 挖掘良恶性肿瘤特征分界规律")
    st.text("3 交互式展示阶段 使用PyEcharts制作可悬浮筛选的交互图表 提升数据可读性")
    st.text("4 成果整合交付阶段 通过Streamlit将全部内容整合为统一网页 实现完整可浏览数据分析项目")
    st.divider()

    st.subheader("3. 工具选择拓展思考")
    st.text("各类可视化工具各有侧重 不存在绝对最优工具 分层搭配使用可弥补单一工具短板")
    st.text("多工具组合完整覆盖从数据探查深度分析到网页交付的全流程 完成乳腺癌数据集多维可视化探索任务")

# ========== 美化后侧边栏导航 ==========
with st.sidebar:
    st.markdown("<h1 style='text-align: center;'> 📊 乳腺癌数据可视化平台</h1>", unsafe_allow_html=True)
    st.divider()
    st.subheader("📑 页面导航")
    st.divider()

    nav_dict = {
        "🏠 项目概览": page_overview,
        "📊 Excel基础分析": page_excel,
        "🐍 Python静态可视化": page_python,
        "📈 PyEcharts交互图表": page_pyecharts,
        "📋 综合探索仪表盘": page_dashboard,
        "⚖️ 可视化工具对比": page_compare
    }
    select_page = st.radio(
        label="",
        options=list(nav_dict.keys()),
        label_visibility="collapsed"
    )
    st.divider()
    st.info("💡 点击上方选项切换不同分析模块")

# 执行页面跳转
nav_dict[select_page]()