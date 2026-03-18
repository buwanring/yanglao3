# 平台3_合规风控审核系统.py
import streamlit as st
import pandas as pd
import json
import os
import datetime
import hashlib
import numpy as np
from datetime import datetime
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# ========== 自定义JSON编码器 ==========
class NumpyEncoder(json.JSONEncoder):
    """处理numpy数据类型的JSON编码器"""
    def default(self, obj):
        if isinstance(obj, (np.integer, np.int64, np.int32)):
            return int(obj)
        elif isinstance(obj, (np.floating, np.float64, np.float32)):
            return float(obj)
        elif isinstance(obj, np.ndarray):
            return obj.tolist()
        elif isinstance(obj, (pd.Timestamp, datetime.date, datetime.datetime)):
            return str(obj)
        return super().default(obj)

# ========== 设置页面配置 ==========
st.set_page_config(
    page_title="平台3：合规风控审核系统 | 风控岗",
    page_icon="🛡️",
    layout="wide"
)

# ========== 高级样式 ==========
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700;900&display=swap');
.platform-header {
    background: linear-gradient(135deg, #2c3e50, #4a6fa5);
    padding: 2rem;
    border-radius: 20px;
    margin-bottom: 2rem;
    color: white;
    text-align: center;
    box-shadow: 0 20px 40px rgba(0,0,0,0.3);
    border: 1px solid #00ff88;
    animation: glow 2s ease-in-out infinite alternate;
}
@keyframes glow {
    from { box-shadow: 0 20px 40px rgba(74,111,165,0.2); }
    to { box-shadow: 0 20px 60px rgba(74,111,165,0.4); }
}
.platform-title {
    font-family: 'Orbitron', sans-serif;
    font-size: 2.5rem;
    font-weight: 900;
    background: linear-gradient(45deg, #00ff88, #00b8ff);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}
.role-badge {
    background: #4a6fa5;
    color: white;
    padding: 8px 20px;
    border-radius: 30px;
    display: inline-block;
    font-weight: 600;
    margin-top: 10px;
    border: 1px solid #00ff88;
}
.compliance-card {
    background: rgba(255,255,255,0.1);
    backdrop-filter: blur(10px);
    border-radius: 15px;
    padding: 20px;
    border: 1px solid rgba(74,111,165,0.3);
    margin: 10px 0;
    transition: all 0.3s;
}
.compliance-card:hover {
    transform: translateY(-5px);
    box-shadow: 0 10px 30px rgba(74,111,165,0.2);
}
.rule-item {
    padding: 15px;
    margin: 10px 0;
    border-radius: 10px;
    border-left: 4px solid #00ff88;
}
.rule-pass {
    background: rgba(0, 255, 136, 0.1);
    border-left-color: #00ff88;
}
.rule-fail {
    background: rgba(255, 68, 68, 0.1);
    border-left-color: #ff4444;
}
.rule-warning {
    background: rgba(255, 170, 0, 0.1);
    border-left-color: #ffaa00;
}
.compliance-badge {
    padding: 5px 15px;
    border-radius: 20px;
    font-weight: bold;
    margin-right: 5px;
}
.compliance-badge-pass {
    background: #00ff88;
    color: black;
}
.compliance-badge-fail {
    background: #ff4444;
    color: white;
}
.compliance-badge-warning {
    background: #ffaa00;
    color: black;
}
.insight-box {
    background: linear-gradient(135deg, #e6f7ff, #d1e7ff);
    border-left: 5px solid #4a6fa5;
    padding: 20px;
    border-radius: 10px;
    margin: 15px 0;
}
.compliance-summary {
    background: rgba(74, 111, 165, 0.1);
    border-radius: 15px;
    padding: 20px;
    border: 1px solid rgba(74, 111, 165, 0.3);
    margin: 15px 0;
}
</style>
""", unsafe_allow_html=True)

# ========== 合规规则库 ==========
class ComplianceRuleLibrary:
    """合规规则库，包含所有合规规则和检查逻辑"""
    def __init__(self):
        # 银行业养老金融合规规则
        self.rules = [
            {
                "rule_id": "R001",
                "name": "年龄限制",
                "description": "客户年龄不得超过产品规定的最大年龄",
                "check_function": self.check_age_limit
            },
            {
                "rule_id": "R002",
                "name": "风险等级匹配",
                "description": "客户风险等级必须与产品风险等级兼容",
                "check_function": self.check_risk_compatibility
            },
            {
                "rule_id": "R003",
                "name": "产品类型限制",
                "description": "产品类型必须符合客户风险偏好",
                "check_function": self.check_product_type
            },
            {
                "rule_id": "R004",
                "name": "起购金额要求",
                "description": "客户可投资资产必须达到产品最低起购金额",
                "check_function": self.check_min_purchase
            },
            {
                "rule_id": "R005",
                "name": "流动性需求匹配",
                "description": "高流动性需求客户应匹配短期产品",
                "check_function": self.check_liquidity_match
            },
            {
                "rule_id": "R006",
                "name": "双录要求",
                "description": "所有推荐产品必须进行双录",
                "check_function": self.check_dual_recording
            }
        ]
    
    def check_age_limit(self, profile, product):
        """检查年龄是否符合产品要求"""
        age = profile['customer_data']['年龄']
        max_age = product['合规限制'].get('年龄_max', 100)
        if age <= max_age:
            return True, f"客户年龄 {age} 岁，符合产品年龄限制 ({max_age}岁)"
        else:
            return False, f"客户年龄 {age} 岁，超过产品年龄限制 ({max_age}岁)"
    
    def check_risk_compatibility(self, profile, product):
        """检查风险等级是否匹配"""
        customer_risk = profile['ml_result']['risk_level']
        product_risk = product['风险等级']
        
        # 客户风险等级到产品风险等级的兼容关系
        risk_compatibility = {
            "低风险": ["R1"],
            "中风险": ["R1", "R2"],
            "高风险": ["R1", "R2", "R3", "R4"]
        }
        
        if product_risk in risk_compatibility.get(customer_risk, []):
            return True, f"客户风险等级 {customer_risk} 与产品风险等级 {product_risk} 匹配"
        else:
            return False, f"客户风险等级 {customer_risk} 与产品风险等级 {product_risk} 不匹配"
    
    def check_product_type(self, profile, product):
        """检查产品类型是否符合客户风险偏好"""
        customer_risk = profile['ml_result']['risk_level']
        product_type = product['产品类型']
        
        # 根据风险等级限制产品类型
        risk_type_restrictions = {
            "低风险": ["存款类", "理财类"],
            "中风险": ["理财类", "基金类"],
            "高风险": ["基金类"]
        }
        
        if product_type in risk_type_restrictions.get(customer_risk, []):
            return True, f"客户风险等级 {customer_risk} 与产品类型 {product_type} 匹配"
        else:
            return False, f"客户风险等级 {customer_risk} 与产品类型 {product_type} 不匹配"
    
    def check_min_purchase(self, profile, product):
        """检查起购金额是否符合要求"""
        asset = profile['customer_data']['可投资资产(万)']
        min_purchase = product['起购金额(万)']
        
        if asset >= min_purchase:
            return True, f"客户可投资资产 {asset} 万，符合产品起购金额 {min_purchase} 万"
        else:
            return False, f"客户可投资资产 {asset} 万，低于产品起购金额 {min_purchase} 万"
    
    def check_liquidity_match(self, profile, product):
        """检查流动性需求是否匹配"""
        big_expense = profile['customer_data']['一年内大额支出']
        product_term = product['期限(天)']
        
        # 高流动性需求客户应匹配短期产品（≤90天）
        if big_expense == '是' and product_term <= 90:
            return True, "客户有高流动性需求，产品期限符合要求"
        elif big_expense == '否' and product_term >= 180:
            return True, "客户无高流动性需求，产品期限符合长期投资要求"
        else:
            return False, "客户流动性需求与产品期限不匹配"
    
    def check_dual_recording(self, profile, product):
        """检查是否需要双录"""
        # 所有养老金融产品都需要双录
        return True, "所有养老金融产品均需进行双录"

# ========== 数据传输类 ==========
class DataTransfer:
    """数据传输类（读取平台2的方案）"""
    @staticmethod
    def get_latest_proposal():
        """获取最新的产品方案文件"""
        proposal_files = [f for f in os.listdir() if f.startswith("proposal_") and f.endswith(".json")]
        if not proposal_files:
            return None
        latest_file = max(proposal_files, key=os.path.getctime)
        try:
            with open(latest_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            st.error(f"读取方案文件失败: {e}")
            return None

# ========== 合规审核引擎 ==========
class ComplianceReviewEngine:
    """合规审核引擎"""
    def __init__(self):
        self.rule_library = ComplianceRuleLibrary()
    
    def review_proposal(self, proposal):
        """审核整个产品方案"""
        results = []
        overall_pass = True
        
        for product in proposal['selected_products']:
            product_result = {
                '产品名称': product['产品名称'],
                '产品代码': product['产品代码'],
                '合规检查': []
            }
            
            # 检查每个合规规则
            for rule in self.rule_library.rules:
                is_pass, message = rule['check_function'](proposal['profile'], product)
                product_result['合规检查'].append({
                    'rule_id': rule['rule_id'],
                    'rule_name': rule['name'],
                    'description': rule['description'],
                    'is_pass': is_pass,
                    'message': message
                })
                
                if not is_pass:
                    overall_pass = False
            
            results.append(product_result)
        
        # 检查整体方案
        overall_result = {
            'is_pass': overall_pass,
            'message': "方案通过合规审核" if overall_pass else "方案存在合规问题，需修改"
        }
        
        return {
            'proposal': proposal,
            'results': results,
            'overall_result': overall_result
        }

# ========== 主界面 ==========
def main():
    """主程序"""
    st.markdown("""
    <div class="platform-header">
        <h1 class="platform-title">🛡️ 平台3：合规风控审核系统</h1>
        <p style="font-size:1.2rem;">风控岗 · 前置合规审核 · 三层风控机制</p>
        <div class="role-badge">👤 3号：风控岗</div>
    </div>
    """, unsafe_allow_html=True)
    
    # ===== 左侧：接收到的方案 =====
    st.markdown("## 📥 接收到的方案")
    
    # 获取最新方案
    proposal = DataTransfer.get_latest_proposal()
    
    if proposal is None:
        st.warning("⚠️ 暂无产品方案数据，请等待平台2（营销岗）发送")
        
        # 添加模拟方案按钮
        if st.button("🔄 使用模拟数据进行演示"):
            # 创建模拟方案（基于王阿姨）
            mock_profile = {
                "customer_id": "CUST1001",
                "customer_data": {
                    "年龄": 72,
                    "性别": "女",
                    "婚姻状态": "丧偶",
                    "子女支持": "无",
                    "月养老金收入": 3500,
                    "可投资资产(万)": 10,
                    "医疗支出占比(%)": 35,
                    "是否有负债": "否",
                    "风险问卷得分": 45,
                    "投资经验年限": 2,
                    "一年内大额支出": "否",
                    "资金锁定期限(年)": 2
                },
                "ml_result": {
                    "risk_level": "中风险",
                    "confidence": 85.5,
                    "probabilities": {
                        "低风险": 15.2,
                        "中风险": 85.5,
                        "高风险": 12.3
                    }
                },
                "cluster": "稳健型中产",
                "tags": ['👴 银发族', '💊 中等医疗负担', '🌱 投资新手'],
                "timestamp": datetime.now().isoformat()
            }
            
            mock_products = [
                {
                    "产品代码": "P003",
                    "产品名称": "稳健养老理财",
                    "风险等级": "R2",
                    "预期收益": "3.5%-4.2%",
                    "期限(天)": 180,
                    "起购金额(万)": 5,
                    "产品类型": "理财类",
                    "特点": "中低风险，主投债券",
                    "适合人群": ["稳健型", "中等收入"],
                    "合规限制": {"年龄_max": 85, "风险等级": ["低风险", "中风险"]}
                },
                {
                    "产品代码": "P005",
                    "产品名称": "养老目标基金2030",
                    "风险等级": "R3",
                    "预期收益": "5.0%-7.0%",
                    "期限(天)": 1095,
                    "起购金额(万)": 1,
                    "产品类型": "基金类",
                    "特点": "目标日期策略，自动调整",
                    "适合人群": ["稳健型", "中长期投资"],
                    "合规限制": {"年龄_max": 75, "风险等级": ["中风险", "高风险"]}
                }
            ]
            
            mock_proposal = {
                'profile': mock_profile,
                'selected_products': mock_products,
                'config_details': [
                    {
                        '产品名称': '稳健养老理财',
                        '产品类型': '理财类',
                        '建议配置(万)': 5.0,
                        '预期收益': '3.5%-4.2%',
                        '期限(天)': 180
                    },
                    {
                        '产品名称': '养老目标基金2030',
                        '产品类型': '基金类',
                        '建议配置(万)': 5.0,
                        '预期收益': '5.0%-7.0%',
                        '期限(天)': 1095
                    }
                ],
                'total_asset': 10,
                'timestamp': datetime.now().isoformat(),
                'status': '待审核'
            }
            
            # 保存模拟方案
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"proposal_sim_{timestamp}.json"
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(mock_proposal, f, ensure_ascii=False, indent=2, cls=NumpyEncoder)
            
            st.session_state['proposal'] = mock_proposal
            st.success("✅ 已加载模拟方案（王阿姨）")
            st.rerun()
    else:
        st.session_state['proposal'] = proposal
        st.success(f"✅ 已加载产品方案 - 接收时间：{proposal.get('timestamp', '未知')}")
    
    # ===== 显示方案内容 =====
    if 'proposal' in st.session_state:
        proposal = st.session_state['proposal']
        
        # 显示客户画像摘要
        st.markdown("### 📌 客户画像摘要")
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.markdown("**👤 客户信息**")
            st.info(f"ID: {proposal['profile']['customer_id']}\n\n年龄: {proposal['profile']['customer_data']['年龄']}岁")
        with col2:
            st.markdown("**📊 风险等级**")
            risk = proposal['profile']['ml_result']['risk_level']
            if risk == '低风险':
                st.success(f"🟢 {risk}")
            elif risk == '中风险':
                st.warning(f"🟡 {risk}")
            else:
                st.error(f"🔴 {risk}")
            st.caption(f"置信度: {proposal['profile']['ml_result']['confidence']:.1f}%")
        with col3:
            st.markdown("**🏷️ 客户标签**")
            tags = proposal['profile'].get('tags', [])
            for tag in tags:
                st.markdown(f"- {tag}")
        with col4:
            st.markdown("**💰 资产信息**")
            st.info(f"可投资产: {proposal['profile']['customer_data']['可投资资产(万)']}万\n\n养老金: {proposal['profile']['customer_data']['月养老金收入']}元")
        
        # 显示产品方案摘要
        st.markdown("### 📦 产品方案摘要")
        st.markdown(f"#### 📋 方案名称: {proposal['profile']['customer_id']}_养老方案")
        st.markdown(f"#### 💰 总可投资资产: {proposal['total_asset']}万元")
        st.markdown(f"#### 📅 方案状态: {proposal['status']}")
        
        # 显示方案产品列表
        st.markdown("#### 📋 产品配置详情")
        config_df = pd.DataFrame(proposal['config_details'])
        config_df = config_df.rename(columns={
            '产品名称': '产品名称',
            '产品类型': '产品类型',
            '建议配置(万)': '建议配置(万)',
            '预期收益': '预期收益',
            '期限(天)': '期限(天)'
        })
        st.dataframe(config_df, use_container_width=True, hide_index=True)
        
        # ===== 合规审核按钮 =====
        st.markdown("---")
        st.markdown("## 🔍 合规审核")
        
        if st.button("🔍 开始合规审核", use_container_width=True):
            with st.spinner("合规审核中..."):
                # 执行合规审核
                engine = ComplianceReviewEngine()
                review_result = engine.review_proposal(proposal)
                
                # 保存审核结果到session
                st.session_state['compliance_result'] = review_result
                st.balloons()
        
        # ===== 显示审核结果 =====
        if 'compliance_result' in st.session_state:
            review_result = st.session_state['compliance_result']
            
            # 显示总体审核结果
            st.markdown("### 📊 审核结果概览")
            col_s1, col_s2, col_s3 = st.columns(3)
            with col_s1:
                total_products = len(review_result['results'])
                st.metric("产品数量", total_products)
            with col_s2:
                passed_products = sum(1 for r in review_result['results'] if all(rule['is_pass'] for rule in r['合规检查']))
                st.metric("通过产品数", passed_products)
            with col_s3:
                overall_score = (passed_products / total_products) * 100 if total_products > 0 else 0
                st.metric("合规通过率", f"{overall_score:.1f}%")
            
            # 显示总体审核结论
            if review_result['overall_result']['is_pass']:
                st.success(f"✅ 方案合规通过！所有产品均符合合规要求")
            else:
                st.error(f"❌ 方案存在合规问题，需修改！{review_result['overall_result']['message']}")
            
            # 显示每个产品的合规检查结果
            st.markdown("### 📌 产品合规检查详情")
            
            for product_result in review_result['results']:
                st.markdown(f"#### 📦 产品: {product_result['产品名称']} ({product_result['产品代码']})")
                
                # 创建合规检查卡片
                for rule in product_result['合规检查']:
                    if rule['is_pass']:
                        card_class = "rule-pass"
                        badge_class = "compliance-badge-pass"
                        badge_text = "通过"
                    else:
                        card_class = "rule-fail"
                        badge_class = "compliance-badge-fail"
                        badge_text = "不通过"
                    
                    st.markdown(f"""
                    <div class="compliance-card {card_class}">
                        <div class="compliance-badge {badge_class}">{badge_text}</div>
                        <h4>{rule['rule_name']}</h4>
                        <p>{rule['description']}</p>
                        <p><strong>检查结果</strong>: {rule['message']}</p>
                    </div>
                    """, unsafe_allow_html=True)
            
            # ===== 人工复核界面 =====
            st.markdown("### 👨‍💼 人工复核")
            st.markdown("请对审核结果进行复核，如有疑问请添加备注")
            
            # 人工复核状态
            if 'review_comments' not in st.session_state:
                st.session_state['review_comments'] = {}
            
            # 为每个产品提供复核输入
            for product_result in review_result['results']:
                product_key = f"{product_result['产品代码']}_{product_result['产品名称']}"
                
                # 初始化评论
                if product_key not in st.session_state['review_comments']:
                    st.session_state['review_comments'][product_key] = ""
                
                st.markdown(f"#### 产品: {product_result['产品名称']} ({product_result['产品代码']})")
                comment = st.text_area(
                    "复核备注",
                    value=st.session_state['review_comments'][product_key],
                    key=f"comment_{product_key}",
                    height=100
                )
                st.session_state['review_comments'][product_key] = comment
            
            # 人工复核结果
            if review_result['overall_result']['is_pass']:
                review_status = "通过"
                review_color = "success"
            else:
                review_status = "不通过"
                review_color = "error"
            
            # 人工复核操作按钮
            col_r1, col_r2 = st.columns(2)
            with col_r1:
                if st.button("✅ 确认通过", use_container_width=True):
                    # 保存审核结果
                    review_result['manual_review'] = {
                        'status': '通过',
                        'comments': st.session_state['review_comments'],
                        'timestamp': datetime.now().isoformat()
                    }
                    st.session_state['compliance_result'] = review_result
                    st.success("✅ 人工复核通过，方案已提交至经理岗")
                    st.balloons()
            with col_r2:
                if st.button("❌ 确认不通过", use_container_width=True):
                    # 保存审核结果
                    review_result['manual_review'] = {
                        'status': '不通过',
                        'comments': st.session_state['review_comments'],
                        'timestamp': datetime.now().isoformat()
                    }
                    st.session_state['compliance_result'] = review_result
                    st.error("❌ 人工复核不通过，方案已退回营销岗")
                    st.balloons()
            
            # ===== 生成合规报告 =====
            st.markdown("---")
            st.markdown("## 📄 合规报告")
            
            if 'manual_review' in review_result:
                # 生成合规报告
                report = {
                    "report_id": f"CR_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                    "proposal_id": proposal['profile']['customer_id'],
                    "customer_id": proposal['profile']['customer_id'],
                    "review_date": datetime.now().isoformat(),
                    "overall_status": review_result['manual_review']['status'],
                    "total_products": len(review_result['results']),
                    "passed_products": sum(1 for r in review_result['results'] if all(rule['is_pass'] for rule in r['合规检查'])),
                    "review_comments": review_result['manual_review']['comments'],
                    "rules_checked": len(ComplianceRuleLibrary().rules),
                    "compliance_score": (sum(1 for r in review_result['results'] if all(rule['is_pass'] for rule in r['合规检查'])) / len(review_result['results'])) * 100 if len(review_result['results']) > 0 else 0
                }
                
                # 显示报告摘要
                st.markdown("### 📊 报告摘要")
                col_r1, col_r2, col_r3 = st.columns(3)
                with col_r1:
                    st.metric("报告ID", report['report_id'])
                with col_r2:
                    st.metric("客户ID", report['customer_id'])
                with col_r3:
                    st.metric("审核状态", report['overall_status'])
                
                # 显示详细合规报告
                st.markdown("### 📝 详细合规报告")
                
                # 合规得分
                st.markdown(f"#### 📊 合规得分: {report['compliance_score']:.1f}%")
                
                # 合规规则检查情况
                st.markdown("#### ✅ 合规规则检查")
                rule_counts = {
                    "通过": 0,
                    "不通过": 0,
                    "需复核": 0
                }
                
                for product in review_result['results']:
                    for rule in product['合规检查']:
                        if rule['is_pass']:
                            rule_counts["通过"] += 1
                        else:
                            rule_counts["不通过"] += 1
                
                # 创建合规规则统计图
                rule_df = pd.DataFrame({
                    '规则状态': list(rule_counts.keys()),
                    '数量': list(rule_counts.values())
                })
                
                fig_rule = px.pie(
                    rule_df, 
                    values='数量', 
                    names='规则状态',
                    title='合规规则检查结果',
                    color_discrete_map={
                        "通过": "#00ff88",
                        "不通过": "#ff4444",
                        "需复核": "#ffaa00"
                    }
                )
                st.plotly_chart(fig_rule, use_container_width=True)
                
                # 显示规则检查详情
                st.markdown("#### 🔍 规则检查详情")
                for product in review_result['results']:
                    st.markdown(f"**产品: {product['产品名称']} ({product['产品代码']})**")
                    for rule in product['合规检查']:
                        status = "✅ 通过" if rule['is_pass'] else "❌ 不通过"
                        st.markdown(f"- {rule['rule_name']}: {status} - {rule['message']}")
                
                # 保存合规报告
                report_filename = f"compliance_report_{report['report_id']}.json"
                with open(report_filename, 'w', encoding='utf-8') as f:
                    json.dump(report, f, ensure_ascii=False, indent=2, cls=NumpyEncoder)
                
                # 下载按钮
                with open(report_filename, 'r', encoding='utf-8') as f:
                    report_content = f.read()
                
                st.download_button(
                    label="📥 下载合规报告",
                    data=report_content,
                    file_name=report_filename,
                    mime="application/json",
                    use_container_width=True
                )
                
                # 发送至经理岗按钮
                if st.button("📤 发送至经理岗", use_container_width=True):
                    # 保存完整合规报告
                    report['proposal'] = proposal
                    report['review_result'] = review_result
                    report_filename = f"compliance_report_{report['report_id']}_final.json"
                    
                    with open(report_filename, 'w', encoding='utf-8') as f:
                        json.dump(report, f, ensure_ascii=False, indent=2, cls=NumpyEncoder)
                    
                    st.success(f"✅ 已发送至经理岗！文件：{report_filename}")
                    st.balloons()

if __name__ == "__main__":
    main()