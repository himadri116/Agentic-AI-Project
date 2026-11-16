"""
DevTeam AI: Interactive Streamlit Observability Console.
Visualizes multi-agent message streams, state graphs, execution terminals,
syntax-highlighted code, and 15-problem empirical benchmark evaluations.
"""

import os
import streamlit as st
import time
import json
import pandas as pd
from typing import Dict, Any

from devteam_ai.graph import DevTeamOrchestrator
from devteam_ai.llm.provider import LLMProvider
from devteam_ai.llm.knowledge_base import BENCHMARK_CHALLENGES
from devteam_ai.benchmarks.suite import BenchmarkSuite
from devteam_ai.sandbox.ast_analyzer import analyze_code_ast

# Configure page layout
st.set_page_config(
    page_title="DevTeam AI | Observability Console",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS styling for premium enterprise agent look
st.markdown("""
<style>
    .main-title {
        font-size: 2.2rem;
        font-weight: 800;
        background: linear-gradient(90deg, #1E88E5 0%, #7B1FA2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0px;
    }
    .sub-title {
        font-size: 1.0rem;
        color: #718096;
        margin-bottom: 15px;
    }
    .agent-card {
        border-radius: 8px;
        padding: 12px 16px;
        margin-bottom: 10px;
        background-color: #f8fafc;
        border-left: 4px solid #3b82f6;
    }
    .terminal-box {
        background-color: #0f172a;
        color: #38bdf8;
        font-family: 'Courier New', monospace;
        padding: 16px;
        border-radius: 8px;
        font-size: 0.85rem;
        max-height: 420px;
        overflow-y: auto;
        white-space: pre-wrap;
    }
    .metric-badge {
        display: inline-block;
        padding: 4px 10px;
        border-radius: 12px;
        font-weight: 600;
        font-size: 0.85rem;
    }
</style>
""", unsafe_allow_html=True)

# App Header
st.markdown('<div class="main-title">DevTeam AI: Autonomous Multi-Agent System</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-title">Collaborative Software Development, Peer Review, and Self-Healing Code Verification | <b>Himadri Bahuguna (BT23GCS204)</b></div>', unsafe_allow_html=True)

# Sidebar Configuration
st.sidebar.title("⚙️ System Control Panel")

backend_choice = st.sidebar.selectbox(
    "LLM Backend Provider",
    ["Autonomous Engine (Default)", "Google Gemini API", "Local Ollama"],
    index=0
)

gemini_key = ""
ollama_url = "http://localhost:11434"
backend_mode = "autonomous"

if backend_choice == "Google Gemini API":
    backend_mode = "gemini"
    gemini_key = st.sidebar.text_input("Gemini API Key", type="password", help="Enter Google AI Studio Gemini API Key")
elif backend_choice == "Local Ollama":
    backend_mode = "ollama"
    ollama_url = st.sidebar.text_input("Ollama Server URL", value="http://localhost:11434")
else:
    backend_mode = "autonomous"
    st.sidebar.info("💡 Running in Autonomous Heuristic Engine mode. All 15 benchmark problems run with zero external API dependencies.")

max_retries = st.sidebar.slider("Max Self-Healing Iterations", min_value=1, max_value=5, value=3)
sandbox_timeout = st.sidebar.slider("Sandbox Timeout (seconds)", min_value=10, max_value=60, value=25)

st.sidebar.divider()
st.sidebar.subheader("📋 Task Specification")

challenge_names = ["Custom Prompt..."] + [f"#{c['id']}: {c['title']}" for c in BENCHMARK_CHALLENGES.values()]
selected_challenge = st.sidebar.selectbox("Select Benchmark Challenge", challenge_names, index=1)

default_prompt = ""
if selected_challenge == "Custom Prompt...":
    default_prompt = "Implement a Thread-Safe In-Memory LRU Cache with TTL Expiration."
else:
    ch_id = int(selected_challenge.split(":")[0].replace("#", ""))
    for k, v in BENCHMARK_CHALLENGES.items():
        if v["id"] == ch_id:
            default_prompt = v["prompt"]
            break

user_prompt = st.sidebar.text_area("Task Requirements", value=default_prompt, height=120)
run_button = st.sidebar.button("🚀 Run Multi-Agent Pipeline", type="primary", use_container_width=True)

# Session state initialization
if "pipeline_state" not in st.session_state:
    st.session_state.pipeline_state = None

# Pipeline execution trigger
if run_button and user_prompt:
    with st.spinner("Executing DevTeam AI LangGraph State Machine..."):
        provider = LLMProvider(mode=backend_mode, gemini_api_key=gemini_key, ollama_url=ollama_url)
        orchestrator = DevTeamOrchestrator(provider=provider, timeout_seconds=sandbox_timeout)
        state_result = orchestrator.run(prompt=user_prompt, max_retries=max_retries)
        st.session_state.pipeline_state = state_result
        st.toast("Pipeline execution completed!", icon="✅")

# If pipeline has executed, render dashboard
state = st.session_state.pipeline_state

if state:
    metrics = state.get("metrics", {})
    test_res = state.get("test_results", {})
    doc = state.get("documentation", {})
    spec = state.get("architect_spec", {})
    healing_iter = state.get("healing_iteration", 0)

    # Top KPI Metrics Cards
    col1, col2, col3, col4, col5 = st.columns(5)
    with col1:
        st.metric("System Status", state.get("status", "UNKNOWN"), delta="Ready" if state.get("status") == "VERIFIED" else None)
    with col2:
        st.metric("Current Phase", state.get("current_phase", "Completed")[:22])
    with col3:
        st.metric("Self-Healing Cycles", f"{healing_iter} / {max_retries}", delta=f"+{healing_iter} fixes" if healing_iter > 0 else "First-pass")
    with col4:
        st.metric("Tests Passed", f"{test_res.get('passed_count', 0)} / {test_res.get('total_count', 0)}", delta="100%" if test_res.get("is_success") else "Failed")
    with col5:
        st.metric("MTTR Latency", f"{metrics.get('total_duration', 0.0)}s")

    st.divider()

    # Main Tab Layout
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "💬 Blackboard & Agent Stream",
        "💻 Code & Architecture Spec",
        "🧪 Execution Sandbox & Terminal",
        "📊 Documentation & Big-O",
        "🏆 15-Problem Benchmark Suite"
    ])

    # Tab 1: Blackboard Message Bus & State Graph
    with tab1:
        st.subheader("LangGraph Cyclic State Machine Architecture")
        
        # State machine diagram
        st.markdown("""
        ```mermaid
        flowchart LR
            Start([START]) --> Arch[Architect Agent]
            Arch --> Dev[Developer Agent]
            Dev --> QA[QA Test Agent]
            QA --> Sandbox[Sandbox Subprocess Pytest]
            Sandbox --> Decision{Tests Passed?}
            Decision -- Yes --> Doc[Documenter Agent]
            Decision -- No & Retries < 3 --> Rev[Reviewer & Healer]
            Rev --> Dev
            Doc --> EndNode([END / VERIFIED])
            
            style Arch fill:#e1f5fe,stroke:#0288d1,stroke-width:2px
            style Dev fill:#e8f5e9,stroke:#388e3c,stroke-width:2px
            style QA fill:#fff3e0,stroke:#f57c00,stroke-width:2px
            style Sandbox fill:#f3e5f5,stroke:#8e24aa,stroke-width:2px
            style Rev fill:#ffebee,stroke:#d32f2f,stroke-width:2px
            style Doc fill:#e0f2f1,stroke:#00796b,stroke-width:2px
        ```
        """)

        st.subheader("Blackboard Bus Message Timeline")
        messages = state.get("messages", [])
        if messages:
            for idx, msg in enumerate(messages, 1):
                sender = msg.get("sender", "Agent")
                role = msg.get("role", "")
                phase = msg.get("phase", "")
                timestamp = msg.get("timestamp", "")
                content = msg.get("content", "")

                color_map = {
                    "ArchitectAgent": "blue",
                    "DeveloperAgent": "green",
                    "QATestAgent": "orange",
                    "SandboxExecutor": "purple",
                    "ReviewerAgent": "red",
                    "DocumenterAgent": "teal"
                }
                card_color = color_map.get(sender, "gray")

                with st.expander(f"[{timestamp}] **{sender}** — *{phase}*", expanded=(idx >= len(messages) - 2)):
                    st.caption(f"**Role:** {role} | **Phase:** {phase}")
                    st.markdown(content)
        else:
            st.info("No blackboard messages recorded yet.")

    # Tab 2: Code & Specification Viewer
    with tab2:
        st.subheader("Artifact Code & Architectural Specifications")
        code_tabs = st.tabs(["solution.py", "test_solution.py", "Architectural Spec (JSON)"])
        
        with code_tabs[0]:
            sol_code = state.get("solution_code", "# No code generated yet")
            st.code(sol_code, language="python", line_numbers=True)
            ast_info = analyze_code_ast(sol_code)
            st.caption(f"AST Verification: Syntactically Valid: {ast_info.is_valid} | Classes: {ast_info.classes} | Functions: {ast_info.functions}")

        with code_tabs[1]:
            test_code = state.get("test_code", "# No test code generated yet")
            st.code(test_code, language="python", line_numbers=True)

        with code_tabs[2]:
            st.json(spec)

    # Tab 3: Execution Sandbox & Terminal
    with tab3:
        st.subheader("Isolated Scratch Subprocess Runner (tempfile + pytest CLI)")
        
        col_sb1, col_sb2 = st.columns([1, 2])
        with col_sb1:
            exit_code = test_res.get("exit_code", -1)
            if exit_code == 0:
                st.success(f"Exit Code: 0 (PASSED) | Latency: {test_res.get('duration_seconds')}s")
            else:
                st.error(f"Exit Code: {exit_code} (FAILED) | Latency: {test_res.get('duration_seconds')}s")
            st.metric("Total Tests", test_res.get("total_count", 0))
            st.metric("Passed Tests", test_res.get("passed_count", 0))
            st.metric("Failed Tests", test_res.get("failed_count", 0))

        with col_sb2:
            st.markdown("<b>Raw Pytest STDOUT / STDERR Execution Terminal</b>", unsafe_allow_html=True)
            terminal_output = (test_res.get("stdout", "") + "\n" + test_res.get("stderr", "")).strip()
            if not terminal_output:
                terminal_output = "No terminal logs available."
            st.markdown(f'<div class="terminal-box">{terminal_output}</div>', unsafe_allow_html=True)

        if state.get("review_feedback"):
            st.divider()
            st.subheader("Reviewer Agent: AST Root-Cause Analysis")
            fb = state["review_feedback"]
            st.warning(f"**Root Cause Diagnosis:** {fb.get('root_cause')}")
            st.info(f"**AST Analysis:** {fb.get('ast_diagnosis')}")
            st.success(f"**Surgical Patch Guidance:** {fb.get('patch_guidance')}")

    # Tab 4: Documentation & Profiling
    with tab4:
        st.subheader("Documenter Agent: Algorithmic Complexity & Docstring Profiler")
        
        if doc:
            c1, c2 = st.columns(2)
            with c1:
                st.info(f"**Asymptotic Time Complexity:**\n\n### `{doc.get('time_complexity')}`")
            with c2:
                st.success(f"**Asymptotic Space Complexity:**\n\n### `{doc.get('space_complexity')}`")
            
            st.markdown("### Algorithmic Complexity Rationale")
            st.markdown(doc.get("complexity_rationale", "N/A"))

            st.markdown("### Sphinx / Google Docstrings Specification")
            st.markdown(doc.get("google_docstrings", "N/A"))

            st.markdown("### Generated Production README")
            st.markdown(doc.get("readme_markdown", "N/A"))
        else:
            st.info("Documentation artifact will be generated upon full test verification.")

    # Tab 5: Benchmark Evaluation Suite
    with tab5:
        st.subheader("Week 4 Evaluation Suite: 15 Classic CS & Software Engineering Challenges")
        st.markdown("""
        Evaluates the autonomous system across all 15 benchmark problems listed in Section 8 of the report:
        - **Target Pass@1 Rate:** > 70%
        - **Target Pass@2 (Self-Healed) Rate:** > 90%
        - **Target Mean Time to Resolve (MTTR):** < 45 seconds
        - **Target Autonomous Recovery Rate:** > 85%
        """)

        bm_col1, bm_col2 = st.columns([1, 3])
        with bm_col1:
            run_bm_all = st.button("▶ Run All 15 CS Benchmarks", type="primary", use_container_width=True)
            bm_limit = st.slider("Benchmark Challenge Count", min_value=1, max_value=15, value=15)

        if run_bm_all:
            progress_bar = st.progress(0)
            status_text = st.empty()

            provider = LLMProvider(mode=backend_mode, gemini_api_key=gemini_key, ollama_url=ollama_url)
            suite = BenchmarkSuite(provider=provider)
            keys = list(BENCHMARK_CHALLENGES.keys())[:bm_limit]
            bm_results = []

            for idx, k in enumerate(keys):
                status_text.text(f"Running Challenge #{idx+1}: {BENCHMARK_CHALLENGES[k]['title']}...")
                res = suite.run_single(k)
                bm_results.append(res)
                progress_bar.progress((idx + 1) / len(keys))

            status_text.text("15-Challenge Benchmark Run Completed!")
            
            from devteam_ai.benchmarks.metrics import calculate_benchmark_summary
            summary = calculate_benchmark_summary(bm_results)
            st.session_state.bm_summary = summary

        if "bm_summary" in st.session_state:
            s = st.session_state.bm_summary
            
            st.markdown("### Empirical Benchmark Metrics")
            kpi1, kpi2, kpi3, kpi4 = st.columns(4)
            with kpi1:
                st.metric("Pass@1 Rate", f"{s.pass_at_1_rate}%", delta="Target >70%" if s.pass_at_1_rate >= 70.0 else "Below")
            with kpi2:
                st.metric("Pass@2 Rate (Healed)", f"{s.pass_at_2_rate}%", delta="Target >90%" if s.pass_at_2_rate >= 90.0 else "Below")
            with kpi3:
                st.metric("Autonomous Recovery Rate", f"{s.autonomous_recovery_rate}%", delta="Target >85%" if s.autonomous_recovery_rate >= 85.0 else "Below")
            with kpi4:
                st.metric("Mean MTTR", f"{s.mean_time_to_resolve}s", delta="Target <45s" if s.mean_time_to_resolve < 45.0 else "Exceeded")

            # Table
            table_data = []
            for r in s.results:
                table_data.append({
                    "ID": r.challenge_id,
                    "Challenge Title": r.title,
                    "Pass@1": "✅" if r.pass_at_1 else "❌",
                    "Pass@2": "✅" if r.pass_at_2 else "❌",
                    "Healing Cycles": r.healing_cycles,
                    "Tests Passed": f"{r.passed_tests}/{r.total_tests}",
                    "Duration (s)": r.duration_seconds
                })
            df = pd.DataFrame(table_data)
            st.dataframe(df, use_container_width=True)

            # Export download buttons
            c_d1, c_d2 = st.columns(2)
            with c_d1:
                st.download_button(
                    "📥 Download Benchmark JSON",
                    data=json.dumps(s.model_dump(), indent=2),
                    file_name="devteam_benchmark_results.json",
                    mime="application/json",
                    use_container_width=True
                )
            with c_d2:
                report_file = "benchmark_report.md" if os.path.exists("benchmark_report.md") else "README.md"
                with open(report_file, "r", encoding="utf-8") as f:
                    rep_text = f.read()
                st.download_button(
                    "📄 Download Academic Report (Markdown)",
                    data=rep_text,
                    file_name="devteam_academic_report.md",
                    mime="text/markdown",
                    use_container_width=True
                )

else:
    st.info("👈 Select a benchmark problem from the sidebar and click **'Run Multi-Agent Pipeline'** to launch the LangGraph autonomous development loop.")
    
    # Preview of the 15 benchmark challenges
    st.subheader("15 Classic Computer Science & Software Engineering Challenges")
    cards = []
    for k, v in BENCHMARK_CHALLENGES.items():
        cards.append({
            "ID": v["id"],
            "Challenge Name": v["title"],
            "Algorithmic Approach": v["spec"].get("algorithmic_approach", "N/A"),
            "Boundary Edge Cases": len(v["spec"].get("edge_cases", []))
        })
    st.dataframe(pd.DataFrame(cards), use_container_width=True)
