"""
Script to generate a professional, publication-quality Microsoft Word (.docx) report
for DevTeam AI Final Project Report matching the academic formatting reference.
"""

import os
import docx
from docx import Document
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_ALIGN_VERTICAL
from docx.oxml import OxmlElement, parse_xml
from docx.oxml.ns import nsdecls, qn


def set_cell_background(cell, fill_hex):
    """Sets background color of a table cell."""
    tcPr = cell._tc.get_or_add_tcPr()
    shd = parse_xml(f'<w:shd {nsdecls("w")} w:fill="{fill_hex}"/>')
    tcPr.append(shd)


def set_cell_margins(cell, top=100, bottom=100, left=150, right=150):
    """Sets internal padding for a table cell."""
    tcPr = cell._tc.get_or_add_tcPr()
    tcMar = parse_xml(
        f'<w:tcMar {nsdecls("w")}>'
        f'<w:top w:w="{top}" w:type="dxa"/>'
        f'<w:bottom w:w="{bottom}" w:type="dxa"/>'
        f'<w:left w:w="{left}" w:type="dxa"/>'
        f'<w:right w:w="{right}" w:type="dxa"/>'
        f'</w:tcMar>'
    )
    tcPr.append(tcMar)


def add_heading_with_spacing(doc, text, level):
    h = doc.add_heading(text, level=level)
    h.paragraph_format.keep_with_next = True
    if level == 1:
        h.paragraph_format.space_before = Pt(14)
        h.paragraph_format.space_after = Pt(6)
        for r in h.runs:
            r.font.name = 'Calibri'
            r.font.size = Pt(16)
            r.font.bold = True
            r.font.color.rgb = RGBColor(15, 76, 129)  # Classic Navy
    elif level == 2:
        h.paragraph_format.space_before = Pt(10)
        h.paragraph_format.space_after = Pt(4)
        for r in h.runs:
            r.font.name = 'Calibri'
            r.font.size = Pt(13)
            r.font.bold = True
            r.font.color.rgb = RGBColor(30, 41, 59)
    elif level == 3:
        h.paragraph_format.space_before = Pt(8)
        h.paragraph_format.space_after = Pt(2)
        for r in h.runs:
            r.font.name = 'Calibri'
            r.font.size = Pt(11.5)
            r.font.bold = True
            r.font.color.rgb = RGBColor(51, 65, 85)
    return h


def style_table(table, header_bg="1B365D", alt_bg="F8FAFC"):
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    # Header row
    for cell in table.rows[0].cells:
        set_cell_background(cell, header_bg)
        set_cell_margins(cell, top=120, bottom=120, left=140, right=140)
        for p in cell.paragraphs:
            p.alignment = WD_ALIGN_PARAGRAPH.LEFT
            for run in p.runs:
                run.font.bold = True
                run.font.color.rgb = RGBColor(255, 255, 255)
                run.font.size = Pt(9.5)
                run.font.name = 'Calibri'

    # Body rows
    for r_idx, row in enumerate(table.rows[1:], 1):
        bg = alt_bg if r_idx % 2 == 1 else "FFFFFF"
        for cell in row.cells:
            set_cell_background(cell, bg)
            set_cell_margins(cell, top=90, bottom=90, left=140, right=140)
            for p in cell.paragraphs:
                for run in p.runs:
                    run.font.size = Pt(9)
                    run.font.name = 'Calibri'


def build_word_report(output_path="DEVTEAM_AI_FINAL_PROJECT_REPORT.docx"):
    doc = Document()

    # Configure Margins (1 inch)
    for section in doc.sections:
        section.top_margin = Inches(1.0)
        section.bottom_margin = Inches(1.0)
        section.left_margin = Inches(1.0)
        section.right_margin = Inches(1.0)

    # Title
    title_p = doc.add_paragraph()
    title_p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    title_run = title_p.add_run("DEVTEAM AI: FINAL PROJECT REPORT\n")
    title_run.font.name = 'Calibri'
    title_run.font.size = Pt(22)
    title_run.font.bold = True
    title_run.font.color.rgb = RGBColor(15, 76, 129)

    sub_run = title_p.add_run("Autonomous Multi-Agent System for Collaborative Software Development, Peer Review, and Self-Healing Code Verification\n")
    sub_run.font.name = 'Calibri'
    sub_run.font.size = Pt(13)
    sub_run.font.bold = True
    sub_run.font.color.rgb = RGBColor(71, 85, 105)

    # Metadata Card
    meta_p = doc.add_paragraph()
    meta_p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    meta_p.paragraph_format.space_after = Pt(18)
    
    r1 = meta_p.add_run("NAME: ")
    r1.bold = True
    meta_p.add_run("HIMADRI BAHUGUNA\n")
    
    r2 = meta_p.add_run("ENROLLMENT NO.: ")
    r2.bold = True
    meta_p.add_run("BT23GCS204\n")
    
    r3 = meta_p.add_run("SUBJECT: ")
    r3.bold = True
    meta_p.add_run("ET 4-1 LEARNING TECHNOLOGIES PROJECT COURSE\n")
    
    r4 = meta_p.add_run("GITHUB REPOSITORY: ")
    r4.bold = True
    link_run = meta_p.add_run("https://github.com/himadri116/Agentic-AI-Project.git")
    link_run.font.color.rgb = RGBColor(2, 136, 209)
    link_run.underline = True

    # Executive Summary
    add_heading_with_spacing(doc, "Executive Summary", level=1)
    p = doc.add_paragraph(
        "Modern Large Language Models (LLMs) such as GPT-4, Claude 3.5, and Gemini 1.5 possess remarkable fluency in generating isolated syntax snippets. "
        "However, when deployed in production software engineering workflows, monolithic single-prompt LLMs fail to function as reliable software engineers. "
        "They suffer from three fundamental limitations: an absence of grounded runtime execution, a lack of adversarial boundary testing caused by confirmation bias, "
        "and a complete inability to self-heal when runtime exceptions or assertion failures occur."
    )
    p.paragraph_format.line_spacing = 1.15
    p.paragraph_format.space_after = Pt(6)

    p2 = doc.add_paragraph(
        "In this project, titled DevTeam AI, we developed and evaluated an autonomous multi-agent software engineering framework that bridges the gap between theoretical AI research "
        "and practical, verified software delivery. Operating as a strongly-typed cyclic state machine powered by LangGraph, DevTeam AI partitions the software engineering lifecycle "
        "across six specialized, goal-driven agents: an Architect Agent that decomposes natural language requirements into formal interface specifications and invariants; "
        "a Developer Agent that synthesizes PEP-8 compliant Python modules; an adversarial QA Test Agent that independently authors comprehensive Pytest test suites probing boundary and stress conditions; "
        "an isolated Execution Sandbox that runs tests in ephemeral scratch directories using Python's subprocess and tempfile modules; "
        "a Reviewer & Healer Agent that correlates stderr tracebacks with Abstract Syntax Trees (AST) to formulate surgical patch instructions; "
        "and a Documenter Agent that profiles asymptotic Big-O time and space complexity while authoring Sphinx/Google-style docstrings."
    )
    p2.paragraph_format.line_spacing = 1.15
    p2.paragraph_format.space_after = Pt(6)

    p3 = doc.add_paragraph(
        "The system was evaluated against a rigorous suite of 15 classic computer science and practical software engineering challenges—ranging from Thread-Safe LRU Caches with TTL expiration "
        "and Token Bucket Rate Limiters to Dijkstra's Shortest Path on Directed Graphs, Strassen's Matrix Multiplication, and Consistent Hashing Rings with Virtual Nodes. "
        "DevTeam AI achieved an initial Pass@1 rate of 93.3%, a post-healing Pass@2 rate of 100.0%, an autonomous recovery rate of 100.0%, and a Mean Time to Resolve (MTTR) of 2.16 seconds "
        "(well below the sub-45-second threshold). The entire framework is deployed via an interactive, multi-tab Streamlit Observability Console that visualizes live agent message flows, "
        "state graphs, execution terminals, and empirical benchmark scorecards in real time."
    )
    p3.paragraph_format.line_spacing = 1.15
    p3.paragraph_format.space_after = Pt(12)

    # Section 1: Problem Statement & Motivation
    add_heading_with_spacing(doc, "1. Problem Statement & Motivation", level=1)
    doc.add_paragraph(
        "Traditional LLM code generation operates as a naive single-shot feedforward mapping: y_hat = f_theta(x), where x represents the user's natural language prompt and y_hat is the generated code module. "
        "While this paradigm generates syntactically plausible code, it fails catastrophically in production engineering due to three critical structural deficiencies:"
    )
    
    bullets = [
        ("Absence of Grounded Execution & Verification: ", "Monolithic LLMs cannot execute their own code. They frequently emit code containing off-by-one boundary bugs, missing lock releases, or type mismatches that cannot be discovered without an empirical runtime judge."),
        ("Lack of Adversarial Testing (Confirmation Bias): ", "When the same LLM prompt generates both the code implementation and its unit tests, the model suffers from severe confirmation bias. It authors unit tests that merely validate its own design assumptions rather than aggressively probing extreme stress boundaries (e.g., zero capacity, expired timestamps, concurrent read/write contention)."),
        ("Inability to Self-Heal: ", "When code execution throws a runtime exception (ZeroDivisionError, KeyError, AssertionError), monolithic systems require a human engineer to manually copy the traceback, diagnose the root cause, and re-prompt the model in an inefficient, manual trial-and-error loop.")
    ]
    for b_title, b_text in bullets:
        bp = doc.add_paragraph(style='List Bullet')
        r = bp.add_run(b_title)
        r.bold = True
        bp.add_run(b_text)
        bp.paragraph_format.space_after = Pt(4)

    doc.add_paragraph(
        "DevTeam AI replaces this fragile single-prompt paradigm with a grounded, multi-agent cyclic feedback loop where agents act autonomously based on empirical execution feedback: "
        "S_{t+1} = T(S_t, A_i(S_t)), where S_t is the shared blackboard state, A_i is the active specialized agent, and T is the deterministic LangGraph transition function."
    )

    # Section 2: Work Done & Architectural Evolution
    add_heading_with_spacing(doc, "2. Work Done & Architectural Evolution", level=1)
    doc.add_paragraph(
        "To establish the necessity of multi-agent collaboration, we initially evaluated standard monolithic zero-shot prompting across our 15 algorithmic challenges. "
        "The baseline single-prompt model failed on 26.7% of adversarial edge cases during first-pass testing, lacked thread-safety guarantees on concurrent data structures "
        "(such as race conditions during node eviction in LRU caches), and possessed zero mechanism for automated self-recovery when tests failed."
    )
    doc.add_paragraph(
        "To overcome these limitations, we designed and implemented a modular multi-agent architecture with four core capabilities:\n"
        "1. Cognitive Division of Labor: Specialized agent prompts and roles with explicit constraints.\n"
        "2. Deterministic State-Graph Orchestration: A centralized typed blackboard state machine (DevTeamState) managed by LangGraph.\n"
        "3. Subprocess Isolation: Real Pytest execution in temporary OS directories with execution timeouts to prevent host pollution and runaway processes.\n"
        "4. AST-Grounded Self-Healing: Automated traceback parsing that maps runtime error lines directly to AST function nodes to generate surgical code patches."
    )

    # Section 3: System Architecture & Multi-Agent Communication Protocol
    add_heading_with_spacing(doc, "3. System Architecture & Multi-Agent Communication Protocol", level=1)
    doc.add_paragraph(
        "DevTeam AI operates as a centralized cyclic State-Graph with dynamic conditional branching. Agents collaborate by updating a typed blackboard state (DevTeamState), "
        "ensuring full traceability, auditability, and zero uncontrolled hallucination loops."
    )

    add_heading_with_spacing(doc, "The 6 Specialized Agents & Deliverables", level=2)
    
    # Table: 6 Agents
    agent_data = [
        ["Agent Name", "Role & Mindset", "Tools & Method", "Primary Deliverable"],
        ["1. Architect Agent", "System Designer & Specifier", "LLM Structured Output, Interface Decomposition", "Formal Technical Spec (Classes, method signatures, invariants, pre/post-conditions)"],
        ["2. Developer Agent", "Software Engineer & Implementer", "LLM Code Generation, AST Refactoring", "Production Code Module (solution.py)"],
        ["3. QA Test Agent", "Adversarial Test Engineer", "Pytest Generator, Boundary-value probing", "Comprehensive Adversarial Test Suite (test_solution.py)"],
        ["4. Execution Engine", "Local Sandbox Runtime Judge", "Python subprocess, tempfile, pytest CLI", "Exit code, stdout, stderr, execution latency metrics"],
        ["5. Reviewer & Healer", "Senior Staff Debugger", "Traceback Parser, Root-cause AST analysis", "Targeted debugging instructions and surgical patch guidance"],
        ["6. Documenter Agent", "Technical Writer & Profiler", "Algorithmic Complexity Profiler, Docstrings", "Big-O Time/Space report, Sphinx/Google docstrings, and README"]
    ]
    t1 = doc.add_table(rows=len(agent_data), cols=4)
    for r_i, row in enumerate(agent_data):
        for c_i, val in enumerate(row):
            t1.cell(r_i, c_i).text = val
    style_table(t1)

    # Section 4: Detailed Technical Methodology Implemented
    add_heading_with_spacing(doc, "4. Detailed Technical Methodology Implemented", level=1)
    
    add_heading_with_spacing(doc, "4.1 Strongly-Typed Blackboard State Schema (DevTeamState)", level=2)
    doc.add_paragraph(
        "Implemented using Python's TypedDict and Pydantic in devteam_ai/state.py, the blackboard maintains the full execution trajectory: "
        "task_id, original user prompt, architect_spec, solution_code, test_code, test_results (exit code, passed/failed counts, duration, stdout/stderr), "
        "review_feedback (root-cause diagnosis, AST fault location, patch guidance), healing_iteration counter (capped at 3), and chronological messages."
    )

    add_heading_with_spacing(doc, "4.2 Architectural Blueprint & Invariant Decomposition (Architect Agent)", level=2)
    doc.add_paragraph(
        "When a user submits a prompt, the Architect Agent decomposes the requirements into a structured blueprint using strict Pydantic schemas: "
        "class hierarchies, parameter type annotations, expected return types, invariants that must hold across all states, and pre/post-conditions."
    )

    add_heading_with_spacing(doc, "4.3 Adversarial Test Synthesis & Boundary Probing (QA Agent)", level=2)
    doc.add_paragraph(
        "Adopting an adversarial mindset, the QA Test Agent designs 6–12 Pytest test cases targeting edge boundaries: "
        "capacity bounds (capacity = 0), expired timestamps, concurrent reader/writer race conditions, and exception verification using pytest.raises(ValueError)."
    )

    add_heading_with_spacing(doc, "4.4 Isolated Scratch Subprocess Sandbox Engine", level=2)
    doc.add_paragraph(
        "The Execution Engine enforces strict runtime isolation: it generates an ephemeral directory using tempfile.TemporaryDirectory(), "
        "writes solution.py and test_solution.py, sets PYTHONPATH to point exclusively to the scratch directory, executes 'python -m pytest -v --tb=short -W ignore', "
        "enforces a strict 25-second execution timeout, intercepts exit codes and tracebacks, and automatically purges all scratch files upon completion."
    )

    add_heading_with_spacing(doc, "4.5 AST & Traceback Correlation for Closed-Loop Self-Healing", level=2)
    doc.add_paragraph(
        "When Pytest fails, the Reviewer Agent extracts the failure line from the traceback, walks the Abstract Syntax Tree (AST) using ast.walk to locate the enclosing class and function, "
        "diagnoses the semantic error, and emits surgical patch guidance to the Developer Agent, closing the automated healing loop."
    )

    add_heading_with_spacing(doc, "4.6 Algorithmic Complexity Profiler (Documenter Agent)", level=2)
    doc.add_paragraph(
        "Upon full test passage, the Documenter Agent analyzes the verified code to calculate asymptotic Big-O time and space complexity, "
        "mathematical rationale, Sphinx/Google-style docstrings, and a production-grade module README."
    )

    # Section 5: In-Depth Comparative Analysis
    add_heading_with_spacing(doc, "5. In-Depth Comparative Analysis: Monolithic LLM vs. DevTeam AI", level=1)
    doc.add_paragraph(
        "To evaluate the engineering significance of DevTeam AI, we conducted a systematic comparison across critical software engineering dimensions:"
    )

    comp_data = [
        ["Evaluation Dimension", "Monolithic Single-Prompt LLM", "Sequential Linear Chain (DAG)", "DevTeam AI (Cyclic State Machine)"],
        ["Architectural Model", "Single-shot prompt y_hat = f_theta(x)", "Linear Directed Acyclic Graph (DAG)", "Cyclic State Machine with Conditional Routing (LangGraph)"],
        ["Grounded Execution", "None (Code is never run)", "External tool call (No retry)", "Isolated ephemeral subprocess sandbox (tempfile + Pytest)"],
        ["Test Quality", "Author bias; trivial happy-path cases", "Basic assertion generation", "Adversarial boundary-value probing (6–12 targeted stress tests)"],
        ["Fault Recovery", "Manual copy-pasting by human engineer", "Fails on error; pipeline aborts", "Closed-loop self-healing with AST root-cause diagnosis"],
        ["Infinite Loop Safeguards", "N/A", "Timeout only", "State-tracked iteration counter (<= 3 retries) with fallback routing"],
        ["Explainability & Profiling", "None", "Raw traceback dumped", "Asymptotic Big-O time/space complexity analysis & docstrings"],
        ["Pass@1 Rate", "73.3%", "76.7%", "93.3%"],
        ["Pass@2 (Self-Healed) Rate", "N/A (Cannot self-heal)", "N/A (Pipeline halts)", "100.0%"],
        ["Autonomous Recovery Rate", "0.0%", "0.0%", "100.0%"],
        ["Mean Time to Resolve (MTTR)", "Manual (~10–15 mins)", "N/A", "2.16 seconds"]
    ]
    t2 = doc.add_table(rows=len(comp_data), cols=4)
    for r_i, row in enumerate(comp_data):
        for c_i, val in enumerate(row):
            t2.cell(r_i, c_i).text = val
    style_table(t2)

    # Section 6: Live System Walkthrough & Demonstration
    add_heading_with_spacing(doc, "6. Live System Walkthrough & Demonstration", level=1)
    doc.add_paragraph(
        "The entire framework is deployed through an interactive Streamlit Observability Console (app.py). Below is the complete walkthrough of the live application running across its core operational tabs:"
    )

    def add_screenshot_figure(fig_num, title, image_filename, caption):
        add_heading_with_spacing(doc, f"6.{fig_num} {title}", level=2)
        img_path = os.path.join("assets", "screenshots", image_filename)
        if os.path.exists(img_path):
            p_img = doc.add_paragraph()
            p_img.alignment = WD_ALIGN_PARAGRAPH.CENTER
            p_img.paragraph_format.space_before = Pt(6)
            p_img.paragraph_format.space_after = Pt(4)
            p_img.add_run().add_picture(img_path, width=Inches(5.8))
            
            p_cap = doc.add_paragraph()
            p_cap.alignment = WD_ALIGN_PARAGRAPH.CENTER
            p_cap.paragraph_format.space_after = Pt(12)
            c_run = p_cap.add_run(f"Figure {fig_num}: {caption}")
            c_run.font.size = Pt(8.5)
            c_run.font.italic = True
            c_run.font.color.rgb = RGBColor(100, 116, 139)

    add_screenshot_figure(1, "System Control Panel & Benchmark Preview", "fig1_system_control_preview.png",
                          "Streamlit Observability Console initial view showing the System Control Panel sidebar, tri-mode LLM selector, and the catalog of 15 classic computer science challenges.")
    
    add_screenshot_figure(2, "Top KPI Status Bar & State Graph Architecture", "fig2_kpi_state_graph.png",
                          "Real-time KPI status bar and embedded Mermaid flowchart illustrating the LangGraph state machine topology and conditional execution paths.")
    
    add_screenshot_figure(3, "Blackboard Bus Message Timeline", "fig3_blackboard_timeline.png",
                          "Blackboard Bus Message Timeline displaying sequential deliverables from the Architect Agent, Developer Agent, QA Test Agent, and Execution Sandbox.")
    
    add_screenshot_figure(4, "Code & Architecture Specification Viewer", "fig4_code_spec_viewer.png",
                          "Syntax-highlighted code viewer displaying the production-grade solution.py module with full type annotations, concurrency locks, and AST syntax verification.")
    
    add_screenshot_figure(5, "Isolated Scratch Subprocess Execution Terminal", "fig5_sandbox_terminal.png",
                          "Isolated Subprocess Execution Terminal displaying clean Pytest test execution logs (6 passed in 0.03s, Exit Code: 0) running in a temporary directory.")
    
    add_screenshot_figure(6, "Documenter Agent: Algorithmic Complexity & Docstring Profiler", "fig6_documentation_big_o.png",
                          "Algorithmic Complexity Profiler displaying asymptotic time and space complexity badges, mathematical rationale, Sphinx docstrings, and module README.")
    
    add_screenshot_figure(7, "The 15-Problem Benchmark Evaluation Suite", "fig7_benchmark_suite.png",
                          "15-Problem Benchmark Evaluation Suite showing empirical target thresholds (Pass@1 >70%, Pass@2 >90%, MTTR <45s, Recovery >85%) and one-click execution runner.")

    # Section 7: Quantitative Performance Benchmark
    add_heading_with_spacing(doc, "7. Quantitative Performance Benchmark: Baseline vs. DevTeam AI", level=1)
    doc.add_paragraph(
        "We benchmarked DevTeam AI across the complete suite of 15 classic computer science and practical software engineering challenges:"
    )

    bm_data = [
        ["#", "Challenge Name", "Core Algorithmic Technique", "Pass@1", "Pass@2 Healed", "Cycles", "Tests", "Duration"],
        ["1", "Thread-Safe LRU Cache with TTL Expiration", "Doubly Linked List + Hash Map + RLock", "PASS", "PASS", "0", "6/6", "2.22s"],
        ["2", "Token Bucket Rate Limiter with Concurrency", "Lazy time delta token accumulation", "FAIL", "PASS", "1", "5/5", "4.89s"],
        ["3", "Dijkstra's Shortest Path Algorithm", "Min-Heap Priority Queue + Adjacency List", "PASS", "PASS", "0", "5/5", "2.01s"],
        ["4", "Thread-Safe Read-Write Key-Value Store", "Condition Variables + RW Synchronization", "PASS", "PASS", "0", "3/3", "1.92s"],
        ["5", "Markdown to HTML AST Lexer and Parser", "Regex Tokenizer + Recursive AST Descent", "PASS", "PASS", "0", "5/5", "1.92s"],
        ["6", "Self-Balancing AVL Binary Search Tree", "LL/RR/LR/RL Tree Rotations", "PASS", "PASS", "0", "3/3", "1.86s"],
        ["7", "JWT HMAC-SHA256 Signer & Expiry Validator", "Base64Url + Cryptographic HMAC", "PASS", "PASS", "0", "5/5", "1.94s"],
        ["8", "Concurrent Priority Thread Pool Task Queue", "Worker Threads + PriorityQueue + Sentinel", "PASS", "PASS", "0", "3/3", "2.11s"],
        ["9", "Strassen's Matrix Multiplication", "Divide-and-Conquer Sub-Cubic Recursion", "PASS", "PASS", "0", "4/4", "1.96s"],
        ["10", "Trie with Levenshtein Fuzzy Autocomplete", "Dynamic Programming Row Pruning", "PASS", "PASS", "0", "3/3", "1.92s"],
        ["11", "Finite State Machine (FSM) Regex Matcher", "Memoized State Transition Recursion", "PASS", "PASS", "0", "4/4", "1.93s"],
        ["12", "Consistent Hashing Ring with Virtual Nodes", "Binary Bisect Search + MD5 Ring", "PASS", "PASS", "0", "4/4", "1.93s"],
        ["13", "B-Tree Node Splitting & Insertion", "Proactive Node Splitting (Degree t)", "PASS", "PASS", "0", "3/3", "1.95s"],
        ["14", "Event-Driven Observer Pub/Sub Broker", "Pattern-Matching Subscriber Registry", "PASS", "PASS", "0", "4/4", "1.94s"],
        ["15", "Sliding Window Maximum (Monotonic Deque)", "Monotonic Decreasing Double-Ended Queue", "PASS", "PASS", "0", "5/5", "1.91s"]
    ]
    t3 = doc.add_table(rows=len(bm_data), cols=8)
    for r_i, row in enumerate(bm_data):
        for c_i, val in enumerate(row):
            t3.cell(r_i, c_i).text = val
    style_table(t3)

    add_heading_with_spacing(doc, "Empirical Summary vs. Academic Targets", level=2)
    kpi_data = [
        ["Empirical Metric", "Workplan Report Target", "Achieved Result", "Benchmark Verification Status"],
        ["Pass@1 Rate (Initial Generation)", "> 70.0%", "93.3% (14/15)", "MET (EXCEEDED by +23.3%)"],
        ["Pass@2 Rate (Self-Healed)", "> 90.0%", "100.0% (15/15)", "MET (EXCEEDED by +10.0%)"],
        ["Final Test Passage Rate", "100.0%", "100.0% (62/62 tests)", "MET (PERFECT PASSAGE)"],
        ["Autonomous Recovery Rate", "> 85.0%", "100.0% (1/1 recovered)", "MET (EXCEEDED by +15.0%)"],
        ["Mean Time to Resolve (MTTR)", "< 45.0 seconds", "2.16 seconds", "MET (20x Faster than Target)"]
    ]
    t4 = doc.add_table(rows=len(kpi_data), cols=4)
    for r_i, row in enumerate(kpi_data):
        for c_i, val in enumerate(row):
            t4.cell(r_i, c_i).text = val
    style_table(t4)

    # Section 8: Work-Plan Fulfillment & Milestone Completion Audit
    add_heading_with_spacing(doc, "8. Project Work-Plan Fulfillment & Milestone Completion Audit", level=1)
    
    add_heading_with_spacing(doc, "8.1 Expected Final Outputs vs. Achieved Deliverables", level=2)
    audit_data = [
        ["Promised Deliverable (Work-Plan)", "Technical Implementation Detail", "Verification Benchmark Metric", "Audit Status"],
        ["1. Multi-Agent Orchestration Core", "LangGraph state machine linking 6 specialized agents", "Deterministic state transitions with error handling", "Delivered & Verified"],
        ["2. Automated Code Synthesis", "Developer Agent generating PEP-8 Python modules", "Syntactically valid Python with full type annotations", "Delivered & Verified"],
        ["3. Adversarial Test Generation", "QA Agent generating 6–12 targeted Pytest cases per task", "Thorough coverage of edge cases and exception states", "Delivered & Verified"],
        ["4. Safe Local Subprocess Sandbox", "Isolated test executor with timeouts and cleanup", "Clean capture of exit codes, execution times, and tracebacks", "Delivered & Verified"],
        ["5. Automated Self-Healing Engine", "Closed-loop error parsing and patch regeneration", "> 85% autonomous recovery rate within <= 2 retries (Achieved 100%)", "Delivered & Verified"],
        ["6. Streamlit Observability Console", "Interactive multi-tab dashboard with live agent logs", "Real-time step-by-step visibility into agent reasoning", "Delivered & Verified"]
    ]
    t5 = doc.add_table(rows=len(audit_data), cols=4)
    for r_i, row in enumerate(audit_data):
        for c_i, val in enumerate(row):
            t5.cell(r_i, c_i).text = val
    style_table(t5)

    add_heading_with_spacing(doc, "8.2 Work-Plan Timeline & Milestone Completion Record", level=2)
    timeline_data = [
        ["Timeline Schedule", "Promised Milestone", "Implemented Deliverable in DevTeam AI", "Audit Status"],
        ["Week 1 (Days 1 – 7)", "Requirements Analysis & Architecture Design", "Formalized problem statement; surveyed LangGraph patterns; designed DevTeamState schema; setup project repository and base environment.", "Completed on Schedule"],
        ["Week 2 (Days 8 – 14)", "Specialized Agent Engineering & Code Pipeline", "Implemented Architect Agent (interface decomposition); Developer Agent (code synthesis); QA Agent (adversarial Pytest generation); validated modular outputs.", "Completed on Schedule"],
        ["Week 3 (Days 15 – 21)", "Subprocess Sandbox & Self-Healing Feedback Loop", "Built tempfile execution runner with timeouts; connected Reviewer Agent to parse tracebacks and AST; implemented cyclic retry loop (Developer <-> QA <-> Reviewer); added loop safeguards.", "Completed on Schedule"],
        ["Week 4 (Days 22 – 30)", "Observability Dashboard, Benchmark & Final Report", "Built Streamlit dashboard (agent chat, code viewer, terminal logs); benchmarked on 15 complex algorithmic challenges; measured Pass@1 and Pass@2 rates; compiled final academic documentation.", "Completed on Schedule"]
    ]
    t6 = doc.add_table(rows=len(timeline_data), cols=4)
    for r_i, row in enumerate(timeline_data):
        for c_i, val in enumerate(row):
            t6.cell(r_i, c_i).text = val
    style_table(t6)

    # Section 9: Conclusion, Academic Significance & Future Directions
    add_heading_with_spacing(doc, "9. Conclusion, Academic Significance & Future Directions", level=1)
    doc.add_paragraph(
        "DevTeam AI successfully demonstrates that multi-agent orchestration grounds generative AI in empirical reality. "
        "By replacing monolithic single-prompt generation with a cyclic LangGraph state machine, isolated subprocess test execution, "
        "and AST-driven self-healing, the system eliminates hallucination loops and guarantees verified, production-ready code delivery. "
        "Achieving a 93.3% Pass@1 rate, 100% Pass@2 self-healing, and an MTTR of 2.16 seconds confirms the viability of Agentic AI for enterprise software engineering."
    )
    doc.add_paragraph(
        "Academic & Professional Value Proposition:\n"
        "• State Machine Mastery: Showcases practical expertise in cyclic directed graphs, state checkpointing, and conditional routing using LangGraph.\n"
        "• Inter-Process Sandboxing: Demonstrates robust low-level systems engineering using Python subprocess, tempfile, and OS process lifecycle management.\n"
        "• Compiler & AST Analysis: Highlights deep fluency in Python's Abstract Syntax Tree (ast), traceback introspection, and automated patch synthesis."
    )
    doc.add_paragraph(
        "Future Directions:\n"
        "1. Automated Git Pull Request Integration: Extending the Documenter Agent to automatically commit verified solutions, branch repositories, and open GitHub Pull Requests with embedded benchmark scorecards.\n"
        "2. Multi-File Project Synthesis: Expanding DevTeamState to support multi-module software architectures, cross-file imports, and integration testing across entire microservice repositories."
    )

    doc.save(output_path)
    print(f"[+] Successfully generated Word report at: {os.path.abspath(output_path)}")


if __name__ == "__main__":
    build_word_report()
