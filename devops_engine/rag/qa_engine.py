try:
    from devops_engine.config import load_env
    load_env()
except ImportError:
    try:
        from config import load_env
        load_env()
    except ImportError:
        pass

"""Context-Aware Application Question Answering (Objective 2).
Generates context-specific architectural questions and provides citation-grounded answers
using Retrieval-Augmented Generation (RAG) over codebase chunks and cloud knowledge.
"""

import os
import json
try:
    import requests
except ImportError:
    requests = None
from typing import List, Dict, Any, Tuple
from .retriever import ContextRetriever


class DevOpsQAEngine:
    """Orchestrates diagnostic question generation and context-aware RAG answering."""

    def __init__(self, retriever: ContextRetriever = None):
        self.retriever = retriever or ContextRetriever()
        self.active_context: Dict[str, Any] = {}

    def set_context(self, project_path: str, scan_result: Dict[str, Any], decision_result: Dict[str, Any]):
        """Index the project and store high-level metadata."""
        self.retriever.index_project(project_path, scan_result, decision_result)
        self.active_context = {
            "project_name": os.path.basename(os.path.abspath(project_path)),
            "project_path": project_path,
            "scan_result": scan_result,
            "decision_result": decision_result,
        }

    def generate_contextual_questions(self) -> List[str]:
        """Generate 5 to 7 dynamic, context-specific questions tailored to the analyzed application."""
        if not self.active_context:
            return [
                "What is the recommended cloud deployment architecture and why?",
                "What database and storage resources are required?",
                "What are the estimated monthly cloud costs between AWS and GCP?",
                "What containerization or packaging steps are needed?",
                "What security and compliance policies apply to this deployment?"
            ]

        scan = self.active_context["scan_result"]
        dec = self.active_context["decision_result"]

        lang = scan.get("primary_language", "Application")
        framework = scan.get("primary_framework", "Framework")
        db = scan.get("primary_database", "Database")
        final_cloud = dec.get("final_cloud", "Cloud")
        final_compute = dec.get("final_compute", "Compute")
        alt_cloud = "GCP" if final_cloud == "AWS" else "AWS"
        is_docker = scan.get("is_containerized", False)

        questions = [
            f"Why did the AI decision engine recommend {final_cloud} ({final_compute}) over {alt_cloud} for this {lang} {framework} application?",
            f"What database, caching, and storage services are required for this app ({db} detected), and how are they configured on {final_cloud} vs {alt_cloud}?",
            f"What are the estimated monthly operating costs across AWS and GCP, and what are the main cost drivers under medium traffic?",
            f"How does the codebase handle containerization and networking (Dockerfile present: {is_docker}), and what ports or routes are exposed?",
            f"What security validations, sensitive environment variables, or health check configurations must be enforced prior to production deployment?"
        ]

        if scan.get("has_cache", False):
            questions.append(f"How is the detected Redis cache provisioned and connected securely in {final_cloud}?")

        return questions

    def _call_gemini_api(self, prompt: str, api_key: str) -> str:
        """Call Gemini API via direct REST endpoint if key is provided."""
        model = "gemini-2.5-flash"
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={api_key}"
        payload = {
            "contents": [{"parts": [{"text": prompt}]}],
            "generationConfig": {"temperature": 0.2, "maxOutputTokens": 1000}
        }
        if requests is not None:
            resp = requests.post(url, json=payload, timeout=12)
            if resp.status_code == 200:
                data = resp.json()
                return data["candidates"][0]["content"]["parts"][0]["text"]
            else:
                raise RuntimeError(f"Gemini API error ({resp.status_code}): {resp.text}")
        else:
            import urllib.request
            data = json.dumps(payload).encode("utf-8")
            req = urllib.request.Request(url, data=data, headers={"Content-Type": "application/json"})
            try:
                with urllib.request.urlopen(req, timeout=12) as resp:
                    res = json.loads(resp.read().decode("utf-8"))
                    return res["candidates"][0]["content"]["parts"][0]["text"]
            except Exception as e:
                raise RuntimeError(f"Gemini API request failed: {e}")

    def _synthesize_local_answer(
        self,
        query: str,
        retrieved_chunks: List[Dict[str, Any]]
    ) -> str:
        """Synthesize a factual, citation-grounded response using retrieved context chunks."""
        scan = self.active_context.get("scan_result", {})
        dec = self.active_context.get("decision_result", {})
        final_cloud = dec.get("final_cloud", "AWS")
        final_compute = dec.get("final_compute", "AWS ECS Fargate")
        infra = dec.get("final_infrastructure", {})
        costs = dec.get("cost_comparison", {})
        query_lower = query.lower()

        answer_lines = []

        # Domain query routing:
        if any(w in query_lower for w in ["why", "recommend", "chosen", "selected", "versus", "vs", "compare"]):
            answer_lines.append(f"### Architectural Decision: {final_cloud} ({final_compute})\n")
            answer_lines.append(
                f"The AI decision engine selected **{final_cloud}** running **{final_compute}** as the primary deployment architecture."
            )
            gcp_proj = os.environ.get("GOOGLE_CLOUD_PROJECT", "mcp-test-sreenivas")
            gcp_loc = os.environ.get("GOOGLE_CLOUD_LOCATION", "us-central1")
            aws_reg = os.environ.get("AWS_DEFAULT_REGION", "us-east-1")
            target_env_str = f"GCP Project `{gcp_proj}` (Region: `{gcp_loc}`)" if final_cloud == "GCP" else f"AWS (Region: `{aws_reg}`)"
            answer_lines.append(f"- **Deployment Target:** {target_env_str}.")
            answer_lines.append(
                f"- **Application Characteristics:** Detected {scan.get('primary_language', 'N/A')} with {scan.get('primary_framework', 'N/A')} "
                f"framework, {scan.get('total_loc', 0)} lines of code, and {scan.get('route_count', 0)} exposed API endpoints."
            )
            answer_lines.append(
                f"- **Packaging:** Containerized status is `{scan.get('is_containerized', False)}`. "
                f"The compute service `{final_compute}` provides horizontal auto-scaling and zero-downtime rolling updates."
            )
            if costs:
                answer_lines.append(
                    f"- **Cost Efficiency:** The comparative analysis projects monthly expenditure of "
                    f"**${costs.get(final_cloud, {}).get('total_estimated_monthly_usd', 0)}/mo** on {final_cloud} vs "
                    f"**${costs.get('GCP' if final_cloud == 'AWS' else 'AWS', {}).get('total_estimated_monthly_usd', 0)}/mo** on "
                    f"{'GCP' if final_cloud == 'AWS' else 'AWS'}."
                )

        elif any(w in query_lower for w in ["cost", "price", "bill", "difference", "saving", "cheapest"]):
            answer_lines.append("### Cost & Sizing Breakdown (AWS vs GCP)\n")
            aws_c = costs.get("AWS", {})
            gcp_c = costs.get("GCP", {})
            answer_lines.append(f"Under standard medium traffic (~2.5 million monthly requests):")
            answer_lines.append(f"- **AWS Total:** ${aws_c.get('total_estimated_monthly_usd', 0)}/month")
            answer_lines.append(f"  - Compute ({dec.get('final_compute', 'AWS Compute')}): ${aws_c.get('breakdown', {}).get('compute', 0)}")
            answer_lines.append(f"  - Database: ${aws_c.get('breakdown', {}).get('database', 0)}")
            answer_lines.append(f"  - Cache / Storage / Egress: ${round(aws_c.get('breakdown', {}).get('cache', 0) + aws_c.get('breakdown', {}).get('storage', 0) + aws_c.get('breakdown', {}).get('network_egress', 0), 2)}")
            answer_lines.append(f"\n- **GCP Total:** ${gcp_c.get('total_estimated_monthly_usd', 0)}/month")
            answer_lines.append(f"  - Compute: ${gcp_c.get('breakdown', {}).get('compute', 0)}")
            answer_lines.append(f"  - Database: ${gcp_c.get('breakdown', {}).get('database', 0)}")
            answer_lines.append(f"  - Cache / Storage / Egress: ${round(gcp_c.get('breakdown', {}).get('cache', 0) + gcp_c.get('breakdown', {}).get('storage', 0) + gcp_c.get('breakdown', {}).get('network_egress', 0), 2)}")
            answer_lines.append(
                f"\n**Cost Leader:** **{costs.get('cheaper_provider', 'N/A')}** saves approximately "
                f"**${costs.get('monthly_difference_usd', 0)}/month ({costs.get('percentage_savings', 0)}%)**."
            )

        elif any(w in query_lower for w in ["database", "storage", "cache", "redis", "postgres", "mongo", "persistence"]):
            db_name = scan.get("primary_database", "None")
            has_c = scan.get("has_cache", False)
            answer_lines.append(f"### Persistence & Storage Architecture\n")
            answer_lines.append(f"- **Primary Database Detected:** `{db_name}`")
            answer_lines.append(f"  - **AWS Provisioning:** {infra.get('database_service', 'None')}")
            answer_lines.append(f"  - **GCP Alternative:** {dec.get('alternate_infrastructure', {}).get('database_service', 'None')}")
            if has_c:
                answer_lines.append(f"- **In-Memory Cache:** Redis detected.")
                answer_lines.append(f"  - **AWS:** Amazon ElastiCache for Redis (cache.t3.micro)")
                answer_lines.append(f"  - **GCP:** Google Cloud Memorystore for Redis (1 GB tier)")
            answer_lines.append(f"- **Object Storage:** {infra.get('storage_service', 'S3/GCS')} for static assets or media uploads.")

        elif any(w in query_lower for w in ["security", "policy", "vulnerability", "variable", "gate", "secret"]):
            answer_lines.append("### DevSecOps Policy & Security Gates\n")
            for check in dec.get("policy_checks", []):
                badge = "PASS" if check["status"] == "PASS" else check["status"]
                answer_lines.append(f"- **{check['gate']}** `[{badge}]`: {check['message']}")
            if scan.get("env_vars"):
                answer_lines.append(f"\n- **Discovered Environment Variables:** {', '.join(scan.get('env_vars')[:8])}")

        else:
            # General answer synthesizing top retrieved chunk
            answer_lines.append("### Context-Aware Application Insights\n")
            if retrieved_chunks:
                top = retrieved_chunks[0]
                answer_lines.append(f"Based on the analysis of **{top['title']}**:")
                answer_lines.append(top['content'])
            else:
                answer_lines.append("Application architecture and cloud provisioning profile synthesized.")

        # Append citations
        citations = []
        for c in retrieved_chunks:
            source_tag = c["source"]
            if c["line_range"]:
                source_tag += f" (lines {c['line_range']})"
            citations.append(f"- `{source_tag}`: {c['title']} (relevance: {c.get('relevance_score', 1.0)})")

        answer_lines.append("\n#### Grounded Citations & Evidence:")
        answer_lines.extend(citations)

        return "\n".join(answer_lines)

    def answer_question(self, question: str, api_key: str = None) -> Dict[str, Any]:
        """Retrieve relevant context and generate grounded answer with citations."""
        api_key = api_key or os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY")
        retrieved_chunks = self.retriever.retrieve(question, top_k=4)

        prompt_context = "\n\n".join([
            f"--- Document: {c['title']} (Source: {c['source']}) ---\n{c['content']}"
            for c in retrieved_chunks
        ])

        system_prompt = (
            "You are an AI DevOps Architect expert in AWS and GCP cloud infrastructure provisioning. "
            "Answer the user's question using ONLY the provided context documents. "
            "Cite the specific files, lines, and cloud architecture docs used. "
            "If the information is not in the context, clearly say so.\n\n"
            f"Context Documents:\n{prompt_context}\n\n"
            f"User Question: {question}\n\n"
            "Grounded Answer:"
        )

        answer_text = ""
        source_mode = "Local Contextual Synthesis"

        if api_key:
            try:
                answer_text = self._call_gemini_api(system_prompt, api_key)
                source_mode = "Gemini LLM (RAG-Augmented)"
            except Exception as e:
                # Fallback to local synthesis
                answer_text = self._synthesize_local_answer(question, retrieved_chunks)
                source_mode = f"Local Contextual Synthesis (LLM fallback: {e})"
        else:
            answer_text = self._synthesize_local_answer(question, retrieved_chunks)

        return {
            "question": question,
            "answer": answer_text,
            "source_mode": source_mode,
            "retrieved_chunks": retrieved_chunks,
        }
