try:
    from devops_engine.config import load_env
    load_env()
except ImportError:
    try:
        from config import load_env
        load_env()
    except ImportError:
        pass

"""Interactive Streamlit Dashboard for Autonomous DevOps Decision Engine & RAG Q&A (Phase 1).
Provides real-time codebase scanning, ML model probabilities, AWS vs GCP comparative costing,
and interactive Context-Aware Question Answering.
"""

import warnings
warnings.filterwarnings("ignore")
try:
    import torch
    torch.classes.__path__ = []
except Exception:
    pass

import os
import sys

_current_dir = os.path.dirname(os.path.abspath(__file__))
if os.path.basename(_current_dir) == "devops_engine":
    BASE_DIR = _current_dir
    ROOT_DIR = os.path.dirname(_current_dir)
else:
    BASE_DIR = os.path.join(_current_dir, "devops_engine")
    ROOT_DIR = _current_dir

if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

import streamlit as st

st.set_page_config(
    page_title="AI Autonomous DevOps Platform (Phase 1)",
    layout="wide",
    initial_sidebar_state="expanded",
)

import pandas as pd
import numpy as np

try:
    from devops_engine.analyzer.codebase_scanner import scan_directory
    from devops_engine.analyzer.feature_extractor import extract_ml_features
    from devops_engine.ml.predictor import DevOpsPredictor
    from devops_engine.decision_rules.policy_engine import apply_decision_rules
    from devops_engine.rag.qa_engine import DevOpsQAEngine
except ImportError:
    from analyzer.codebase_scanner import scan_directory
    from analyzer.feature_extractor import extract_ml_features
    from ml.predictor import DevOpsPredictor
    from decision_rules.policy_engine import apply_decision_rules
    from rag.qa_engine import DevOpsQAEngine

st.title("AI-Driven Autonomous DevOps Platform")
st.caption("Phase 1: Codebase Decision Making (ML AWS/GCP) & Context-Aware Question Answering (RAG)")


# -----------------------------------------------------------------------------
# Sidebar: Configuration & Target Project Selection
# -----------------------------------------------------------------------------
st.sidebar.header("Project & Strategy Controls")

# BASE_DIR configured dynamically above
SAMPLE_DIR = os.path.join(BASE_DIR, "sample_projects")

sample_options = {
    "FastAPI Order Microservice (Python + Postgres + Redis)": os.path.join(SAMPLE_DIR, "fastapi_microservice"),
    "User Management REST API (Node.js + Express + MongoDB)": os.path.join(SAMPLE_DIR, "node_express_api"),
    "Enterprise Billing Service (Java Spring Boot + Postgres)": os.path.join(SAMPLE_DIR, "java_spring_service"),
    "Serverless Webhook Handler (Python Raw / Uncontainerized)": os.path.join(SAMPLE_DIR, "python_serverless"),
    "Custom Path...": "custom"
}

selected_choice = st.sidebar.selectbox("Select Target Codebase", list(sample_options.keys()))

if selected_choice == "Custom Path...":
    project_path = st.sidebar.text_input("Enter absolute codebase folder path", value=os.path.join(SAMPLE_DIR, "fastapi_microservice"))
else:
    project_path = sample_options[selected_choice]

st.sidebar.markdown("---")
st.sidebar.subheader("Cloud Preferences & Rules")

cloud_constraint = st.sidebar.selectbox(
    "Cloud Provider Constraint",
    ["Auto (ML Decides)", "AWS Only", "GCP Only"]
)
forced_cloud = None
if cloud_constraint == "AWS Only":
    forced_cloud = "AWS"
elif cloud_constraint == "GCP Only":
    forced_cloud = "GCP"

opt_strategy = st.sidebar.selectbox(
    "Optimization Objective",
    ["Balanced (ML + Cost)", "Cheapest (Enforce Lowest Monthly Bill)", "Performance (Favor Container PaaS)"]
)
strategy_key = "balanced"
if "Cheapest" in opt_strategy:
    strategy_key = "cheapest"
elif "Performance" in opt_strategy:
    strategy_key = "performance"

traffic_slider = st.sidebar.select_slider(
    "Expected Traffic Tier",
    options=["Light (300k req/mo)", "Medium (2.5M req/mo)", "Heavy (15M req/mo)"],
    value="Medium (2.5M req/mo)"
)
traffic_key = "medium"
if "Light" in traffic_slider:
    traffic_key = "light"
elif "Heavy" in traffic_slider:
    traffic_key = "heavy"




# -----------------------------------------------------------------------------
# Main Execution Engine
# -----------------------------------------------------------------------------
if not os.path.exists(project_path):
    st.error(f"Selected project path does not exist: {project_path}")
    st.stop()

@st.cache_resource(show_spinner=False)
def get_predictor():
    return DevOpsPredictor()

@st.cache_resource(show_spinner=False)
def get_qa_engine():
    return DevOpsQAEngine()

predictor = get_predictor()
qa_engine = get_qa_engine()

# Run Scanner & Prediction
scan = scan_directory(project_path)
features = extract_ml_features(scan)
ml_result = predictor.predict_full_pipeline(features, forced_cloud=forced_cloud)
decision = apply_decision_rules(scan, ml_result, forced_cloud=forced_cloud, optimization_strategy=strategy_key)

# Index in RAG engine
qa_engine.set_context(project_path, scan, decision)


# -----------------------------------------------------------------------------
# Tab Layout
# -----------------------------------------------------------------------------
tab1, tab2, tab3, tab4 = st.tabs([
    "1. Codebase Analysis",
    "2. ML Recommendation & Sizing",
    "3. Context-Aware Q&A (RAG)",
    "4. Model Training & Validation"
])


# -----------------------------------------------------------------------------
# TAB 1: Codebase Analysis
# -----------------------------------------------------------------------------
with tab1:
    st.header("Static Codebase Characterization")
    st.write(f"Analyzed Directory: `{project_path}`")

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Primary Language", scan["primary_language"])
    col2.metric("Primary Framework", scan["primary_framework"])
    col3.metric("Primary Database", scan["primary_database"])
    col4.metric("Containerized", "Yes (Dockerfile)" if scan["is_containerized"] else "No (Bare Runtime)")

    col_a, col_b = st.columns([1, 1])

    with col_a:
        st.subheader("Architectural Signatures")
        st.markdown(f"- **Lines of Code (LOC):** `{scan['total_loc']}` lines across `{scan['total_files']}` files")
        st.markdown(f"- **Discovered Routes:** `{scan['route_count']}` HTTP endpoints")
        st.markdown(f"- **In-Memory Caching:** `{'Redis' if scan['has_cache'] else 'None'}`")
        st.markdown(f"- **Target Port:** `{scan['detected_port']}`")
        if scan.get("env_vars"):
            st.markdown(f"- **Referenced Environment Variables:** `{', '.join(scan['env_vars'])}`")

    with col_b:
        st.subheader("Discovered HTTP Routes")
        if scan.get("routes"):
            routes_df = pd.DataFrame(scan["routes"])
            st.dataframe(routes_df, use_container_width=True, height=180)
        else:
            st.info("No standard web endpoints discovered (Event-driven or non-HTTP runtime).")

    with st.expander("View Full Extracted Feature Vector for ML"):
        st.json(features)


# -----------------------------------------------------------------------------
# TAB 2: ML Recommendation & Sizing
# -----------------------------------------------------------------------------
with tab2:
    st.header("ML-Driven Multi-Cloud Recommendation")

    final_cloud = decision["final_cloud"]
    final_compute = decision["final_compute"]
    infra = decision["final_infrastructure"]

    m1, m2, m3 = st.columns(3)
    m1.success(f"**Target Cloud:** {final_cloud}")
    m2.info(f"**Compute Archetype:** {ml_result['archetype']}")
    m3.warning(f"**Compute Service:** {final_compute}")

    if decision.get("override_reason"):
        st.caption(f"**Rule Layer Notice:** {decision['override_reason']}")

    col_prob1, col_prob2 = st.columns(2)

    with col_prob1:
        st.subheader("Cloud Provider Confidence (AWS vs GCP)")
        cloud_df = pd.DataFrame({
            "Provider": list(ml_result["cloud_probabilities"].keys()),
            "Probability": [v * 100 for v in ml_result["cloud_probabilities"].values()]
        })
        st.bar_chart(cloud_df.set_index("Provider"), height=220)

    with col_prob2:
        st.subheader("Compute Service Probabilities")
        comp_df = pd.DataFrame({
            "Service": list(ml_result["compute_probabilities"].keys()),
            "Probability": [v * 100 for v in ml_result["compute_probabilities"].values()]
        })
        st.bar_chart(comp_df.set_index("Service"), height=220)

    st.markdown("---")
    st.subheader("Monthly Cost Sizing Breakdown (AWS vs GCP)")

    costs = decision["cost_comparison"]
    aws_c = costs["AWS"]
    gcp_c = costs["GCP"]

    c1, c2, c3 = st.columns(3)
    c1.metric("AWS Projected Bill", f"${aws_c['total_estimated_monthly_usd']:.2f} / mo")
    c2.metric("GCP Projected Bill", f"${gcp_c['total_estimated_monthly_usd']:.2f} / mo")
    c3.metric(
        "Cost Winner",
        f"{costs['cheaper_provider']}",
        f"Save ${costs['monthly_difference_usd']:.2f} ({costs['percentage_savings']}%)"
    )

    cost_table = pd.DataFrame({
        "Component": ["Compute", "Database", "Cache", "Storage", "Egress", "Total Monthly"],
        "AWS ($/mo)": [
            aws_c["breakdown"]["compute"],
            aws_c["breakdown"]["database"],
            aws_c["breakdown"]["cache"],
            aws_c["breakdown"]["storage"],
            aws_c["breakdown"]["network_egress"],
            aws_c["total_estimated_monthly_usd"],
        ],
        "GCP ($/mo)": [
            gcp_c["breakdown"]["compute"],
            gcp_c["breakdown"]["database"],
            gcp_c["breakdown"]["cache"],
            gcp_c["breakdown"]["storage"],
            gcp_c["breakdown"]["network_egress"],
            gcp_c["total_estimated_monthly_usd"],
        ]
    })
    st.dataframe(cost_table, use_container_width=True)

    st.markdown("---")
    st.subheader(f"Complete Generated Cloud Architecture ({final_cloud})")
    arch_cols = st.columns(3)
    arch_cols[0].markdown(f"**Compute:** `{final_compute}`\n\n*{infra['compute_details']['type']}*")
    arch_cols[1].markdown(f"**Database:** `{infra['database_service']}`\n\n*Multi-AZ / High Availability*")
    arch_cols[2].markdown(f"**Cache & Storage:** `{infra['cache_service']}` | `{infra['storage_service']}`")

    st.subheader("DevSecOps Validation Gates")
    for check in decision["policy_checks"]:
        if check["status"] == "PASS":
            st.success(f"**{check['gate']}**: {check['message']}")
        elif check["status"] == "PASS_WITH_POLICY":
            st.info(f"**{check['gate']}**: {check['message']}")
        else:
            st.warning(f"**{check['gate']}**: {check['message']}")


# -----------------------------------------------------------------------------
# TAB 3: Context-Aware Q&A (RAG)
# -----------------------------------------------------------------------------
with tab3:
    st.header("Context-Aware Application Question Answering (RAG)")
    st.write(
        "Ask questions about the application's source code, dependencies, architecture, "
        "and cloud deployment requirements. Answers are grounded in the vector index with exact citations."
    )

    st.subheader("Suggested Context-Specific Diagnostic Questions:")
    suggested_questions = qa_engine.generate_contextual_questions()

    selected_q = None
    for q_idx, q_text in enumerate(suggested_questions):
        if st.button(f"{q_text}", key=f"sq_{q_idx}"):
            selected_q = q_text

    st.markdown("---")
    user_query = st.text_input(
        "Or enter a custom question:",
        value=selected_q if selected_q else "",
        placeholder="e.g. Why was GCP chosen over AWS? How should secrets be handled?"
    )

    if st.button("Generate Answer", type="primary") or user_query:
        if user_query:
            with st.spinner("Retrieving relevant code chunks and generating citation-grounded answer..."):
                ans_data = qa_engine.answer_question(user_query)

            st.markdown(ans_data["answer"])

            with st.expander("View Retrieved Semantic Chunks (Evidence)"):
                for c in ans_data["retrieved_chunks"]:
                    st.markdown(f"**{c['title']}** (Relevance: `{c.get('relevance_score', 1.0)}`)")
                    st.code(c["content"], language="text")


# -----------------------------------------------------------------------------
# TAB 4: Model Training & Validation
# -----------------------------------------------------------------------------
with tab4:
    st.header("ML Model Architecture, Training & Empirical Validation")

    metrics_file = os.path.join(BASE_DIR, "ml", "models", "evaluation_metrics.json")
    if os.path.exists(metrics_file):
        import json
        with open(metrics_file, "r") as f:
            metrics = json.load(f)

        m_col1, m_col2, m_col3 = st.columns(3)
        m_col1.metric("Archetype Model Accuracy", f"{metrics['archetype_classifier']['test_accuracy']*100:.1f}%")
        m_col2.metric("Cloud Model Accuracy", f"{metrics['cloud_recommender']['test_accuracy']*100:.1f}%")
        m_col3.metric("Compute Model Accuracy", f"{metrics['compute_recommender']['test_accuracy']*100:.1f}%")

        st.subheader("Top Predictive Features for Cloud Recommendation")
        top_feats = metrics.get("top_cloud_features", [])
        if top_feats:
            feats_df = pd.DataFrame(top_feats)
            st.bar_chart(feats_df.set_index("feature"), height=250)

        with st.expander("View Complete Classification Report"):
            st.json(metrics)
    else:
        st.info("Evaluation metrics file not found. Run model training from CLI.")
