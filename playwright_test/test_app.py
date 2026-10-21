"""Pytest Playwright Test Suite for AI Autonomous DevOps Platform.
Can be executed with:
    pytest playwright_test/test_app.py -v
"""

import time
import pytest
from playwright.sync_api import Page, expect

BASE_URL = "http://localhost:8501"


def test_01_page_load_and_branding(page: Page):
    """Verify application loads with correct branding and clean sidebar."""
    page.goto(BASE_URL, wait_until="networkidle", timeout=30000)
    page.wait_for_selector("h1", timeout=20000)

    title = page.locator("h1").first.text_content()
    assert "AI-Driven Autonomous DevOps Platform" in title

    sidebar = page.locator('[data-testid="stSidebar"]')
    expect(sidebar).to_be_visible()

    # Confirm .env expander is not in sidebar
    env_visible = page.locator("text=Cloud & Environment Config (.env)").is_visible()
    assert not env_visible


def test_02_tab1_codebase_characterization(page: Page):
    """Verify Tab 1: AST Codebase Characterization on FastAPI microservice."""
    page.goto(BASE_URL, wait_until="networkidle", timeout=30000)
    page.locator('[role="tab"]:has-text("1. Codebase Analysis")').click()
    page.wait_for_selector('[data-testid="stMetricValue"]', timeout=20000)

    metrics = page.locator('[data-testid="stMetricValue"]').all_text_contents()
    assert any("Python" in m for m in metrics)
    assert any("FastAPI" in m for m in metrics)
    assert any("PostgreSQL" in m for m in metrics)
    assert page.locator("text=Discovered HTTP Routes").is_visible()


def test_03_tab2_ml_recommendation_and_costing(page: Page):
    """Verify Tab 2: Multi-Cloud Recommendation, Sizing and DevSecOps Gates."""
    page.goto(BASE_URL, wait_until="networkidle", timeout=30000)
    page.locator('[role="tab"]:has-text("2. ML Recommendation & Sizing")').click()
    page.wait_for_selector("text=Target Cloud:", timeout=20000)

    target_cloud = page.locator('[data-testid="stAlert"]:has-text("Target Cloud:")').first.text_content()
    assert "GCP" in target_cloud

    compute_service = page.locator('[data-testid="stAlert"]:has-text("Compute Service:")').first.text_content()
    assert "Cloud Run" in compute_service

    assert page.locator("text=Monthly Cost Sizing Breakdown").is_visible()
    assert page.locator("text=DevSecOps Validation Gates").is_visible()


def test_04_rule_engine_override_aws(page: Page):
    """Verify Rule Engine Arbitration when user enforces 'AWS Only'."""
    page.goto(BASE_URL, wait_until="networkidle", timeout=30000)
    page.locator('[role="tab"]:has-text("2. ML Recommendation & Sizing")').click()
    page.wait_for_selector("text=Target Cloud:", timeout=20000)

    # Force AWS in sidebar
    constraint_box = page.locator('[data-testid="stSidebar"] [data-testid="stSelectbox"]').nth(1)
    constraint_box.click()
    page.locator('[role="option"]:has-text("AWS Only")').click()
    page.wait_for_selector("text=AWS ECS Fargate", timeout=15000)

    aws_cloud = page.locator('[data-testid="stAlert"]:has-text("Target Cloud:")').first.text_content()
    assert "AWS" in aws_cloud

    rule_notice = page.locator('[data-testid="stCaptionContainer"]:has-text("Rule Layer Notice:")').first.text_content()
    assert "User hard constraint enforced" in rule_notice


def test_05_codebase_switching_java_enterprise(page: Page):
    """Verify Codebase Switching and Enterprise AWS Stack Affinity."""
    page.goto(BASE_URL, wait_until="networkidle", timeout=30000)
    codebase_box = page.locator('[data-testid="stSidebar"] [data-testid="stSelectbox"]').first
    codebase_box.click()
    page.locator('[role="option"]:has-text("Enterprise Billing Service")').click()
    time.sleep(2)
    page.locator('[role="tab"]:has-text("2. ML Recommendation & Sizing")').click()
    page.wait_for_selector("text=AWS ECS Fargate", timeout=25000)

    java_cloud = page.locator('[data-testid="stAlert"]:has-text("Target Cloud:")').first.text_content()
    assert "AWS" in java_cloud


def test_06_tab3_context_aware_rag_qa(page: Page):
    """Verify Tab 3: Context-Aware RAG Synthesis and Grounded Citations."""
    page.goto(BASE_URL, wait_until="networkidle", timeout=30000)
    page.locator('[role="tab"]:has-text("3. Context-Aware Q&A (RAG)")').click()
    page.wait_for_selector("text=Suggested Context-Specific Diagnostic Questions:", timeout=20000)

    query_input = page.locator('input[placeholder*="Why was GCP chosen over AWS"]')
    query_input.fill("Why was GCP chosen over AWS and what database is provisioned?")
    query_input.press("Enter")
    time.sleep(1)

    gen_btn = page.locator('button:has-text("Generate Answer")')
    if gen_btn.is_visible():
        gen_btn.click()

    page.wait_for_selector("text=Grounded Citations & Evidence", timeout=30000)
    assert page.locator("text=Grounded Citations & Evidence").is_visible()


def test_07_tab4_model_evaluation_metrics(page: Page):
    """Verify Tab 4: ML Benchmarks, Accuracy Scores, and Classification Reports."""
    page.goto(BASE_URL, wait_until="networkidle", timeout=30000)
    page.locator('[role="tab"]:has-text("4. Model Training & Validation")').click()
    page.wait_for_selector("text=Top Predictive Features for Cloud Recommendation", timeout=20000)

    # Verify model evaluation benchmarks are visible
    expect(page.locator("text=Archetype Model Accuracy")).to_be_visible()
    expect(page.locator("text=Cloud Model Accuracy")).to_be_visible()
    expect(page.locator("text=Compute Model Accuracy")).to_be_visible()
    expect(page.locator("text=Top Predictive Features for Cloud Recommendation")).to_be_visible()
