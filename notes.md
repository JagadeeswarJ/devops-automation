objective 1:
recommend suitable cloud services and deployment strategies.	

objective 2:
create qna -> to get insights about the decisions, Exaplainability


Ai-based source code analysis, extract:  programming language, framework, dependencies, architecture, and infrastructure requirements, and uses knowledge of cloud services and DevOps practices to determine an appropriate deployment strategy.



why llms fails:
The Deployability Gap (Zhang et al. [10]): In an empirical study of 4,200 real-world IaC deployments, pure LLMs achieved only 20.8% to 30.2% first-attempt deployment success. The remaining 70%+ crashed due to parameter mismatches and invalid cloud references.
https://arxiv.org/abs/2506.05623?utm_source=chatgpt.com
The Security Compliance Gap (Vargas et al. [7]): LLMs produce code that compiles syntactically but fails security audits. Out of 2,640 LLM-generated Terraform scripts tested with Checkov, raw models scored 0% security compliance.
https://arxiv.org/abs/2608.02672?utm_source=chatgpt.com
The Hallucination Gap (Paulo et al. [5]): Unconstrained LLMs frequently invent non-existent machine types, quote outdated pricing, and hallucinate cloud features.
https://sol.sbc.org.br/index.php/webmedia/article/view/37949


1. uses 3 coordinated Random Forest pipelines -> recommend -> in 5 ms, 99% accuracy
2. AWS vs GCP comparision
3. 




questions:
1. how are question generated, 
`Local Context-Aware RAG Engine (The Explainer): A dense vector search subsystem (sentence-transformers/all-MiniLM-L6-v2) that generates project-tailored diagnostic questions and delivers answers backed by verifiable source file and line citations.`

how does it work!

2. devsecops policy gateway , VPC subnets, Secrets, Liveness, probes