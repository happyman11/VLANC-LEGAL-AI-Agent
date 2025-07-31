from datetime import datetime
from langchain.prompts import PromptTemplate

class Prefix_Suffix:
    def __init__(self):
        self.prefix="you are a legal expert think like a lawyer for this case:"
        self.suffix_IT_ACT="Which sections of the Information Technology (IT) Act 2000 are applicable?"
        self.suffix_BNS_ACT="Which sections of the the Bharatiya Nyaya Sanhita (BNS) are applicable?"
        self.suffix_BSA_ACT="Which sections of the  the Bharatiya Sakshya Adhiniyam (BSA) 2023 are applicable?"
        self.suffix="Which sections of the Information Technology (IT) Act 2000, the Bharatiya Sakshya Adhiniyam (BSA) 2023, and the Bharatiya Nyaya Sanhita (BNS) are applicable?"
    
    def get_prefix(self):
        return self.prefix   
    def get_suffix(self):
        return self.suffix
    def get_suffix_IT_Act(self):
        return self.suffix_IT_ACT
    def get_suffix_BNS_Act(self):
        return self.suffix_BNS_ACT
    def get_suffix_BSA_Act(self):
        return self.suffix_BSA_ACT
        
        
class BNS_Act_Prompt_Templates:
    def __init__(self):
        self.router_prompt= PromptTemplate(
                              template="""
                            You are a legal query router.

                            If the question involves **any of the following under Indian criminal law** as per the **Bharatiya Nyaya Sanhita (BNS), 2023**:
                            - Offenses against the human body (e.g., murder, culpable homicide, hurt, wrongful restraint, kidnapping, abduction),
                            - Offenses against women and children (e.g., sexual harassment, rape, voyeurism, stalking, molestation, acid attack, outraging modesty),
                            - Offenses against property (e.g., theft, robbery, dacoity, criminal breach of trust, extortion, cheating, mischief),
                            - Offenses against the state and public order (e.g., sedition, rioting, unlawful assembly, terrorism),
                            - Criminal conspiracy, abetment, attempt to commit an offense, or common intention,
                            - Offenses relating to documents and property marks (e.g., forgery, counterfeiting),
                            - Offenses relating to false evidence, criminal intimidation, defamation, insult, or obstruction of justice,
                            - Any legal query involving provisions **redefined or newly added under BNS (as replacement of IPC, 1860)**,

                            Then respond with: VECTORSTORE

                            Otherwise, respond with: NO_ANSWER

                            Question: {question}
                            """,
                            input_variables=["question"]
                        )
        
        self.grader_prompt = PromptTemplate(
                                template="""
                            You are a legal relevance grader.

                            Determine if the following document is relevant to the legal question in the context of the **Bharatiya Nyaya Sanhita (BNS), 2023** — the updated Indian criminal law that replaces the Indian Penal Code (IPC).

                            Focus on identifying content related to:
                            - Offenses against the human body (e.g., murder, culpable homicide, hurt, kidnapping, wrongful confinement, dowry death),
                            - Offenses against women and children (e.g., sexual harassment, stalking, voyeurism, rape, molestation, acid attack),
                            - Offenses against property (e.g., theft, robbery, dacoity, cheating, criminal breach of trust, extortion, mischief),
                            - Offenses affecting the state and public order (e.g., sedition, terrorism, rioting, unlawful assembly, promoting enmity),
                            - Criminal conspiracy, abetment, attempt to commit crimes, or common intention,
                            - Offenses related to public justice (e.g., false evidence, obstruction of justice, impersonation, criminal intimidation, defamation),
                            - Any provision, section, clause, or judicial interpretation explicitly under the **BNS, 2023**,
                            - General definitions, punishments, or classifications as introduced in the BNS.

                            Document:
                            {document}

                            Question:
                            {question}

                            If relevant, return: YES  
                            Otherwise, return: NO
                            """,
                                input_variables=["question", "document"]
                            )
        
        self.answer_prompt = PromptTemplate(
                        template="""
                    You are a senior Indian legal researcher.

                    Use the provided legal context to answer the question based on the **Bharatiya Nyaya Sanhita (BNS), 2023** — the Indian criminal code that replaces the Indian Penal Code (IPC), covering all major criminal offenses and classifications.

                    Structure your response as:

                    1. **Applicable Sections (BNS, 2023)**: Cite the relevant sections by number or name that directly apply to the scenario.  
                    2. **Interpretation and Legal Analysis**: Explain in depth how these sections apply, using legal reasoning, definitions, illustrations, or precedents if available.  
                    3. **Pros**: Legal protections, rights of victims, and safeguards under BNS.  
                    4. **Cons**: Punishments, liabilities, or legal consequences faced by the accused under BNS.  
                    5. **Procedural Notes**: Summarize how complaints are filed, charges framed, arrests made, or trials conducted under BNS (excluding BNSS unless contextually relevant).

                    Only refer to provisions under the BNS, 2023. Do not include references to the IT Act or the Bharatiya Sakshya Adhiniyam (BSA).

                    Context:  
                    {context}

                    Question:  
                    {question}

                    Answer:
                    """,
                        input_variables=["context", "question"]
                    )
    
    
    def get_grader_prompt(self,question,document):
        return self.grader_prompt.format(question=question,document=document)

    def get_answer_prompt(self,question,context):
        return self.answer_prompt.format(question=question,context=context)
    
    def get_router_prompt(self,question):
        return self.router_prompt.format(question=question)
    
    
    
class IT_Act_Prompt_Templates:
    def __init__(self):
        self.router_prompt= PromptTemplate(
                            template="""
                        You are a legal query router.

                        If the question involves **any of the following under Indian law**:
                        - Cybercrimes (e.g., OTP fraud, phishing, online banking fraud, hacking, identity theft),
                        - Online sexual harassment, cyberstalking, voyeurism, transmission of obscene or sexually explicit material via electronic means (e.g., phone, email, social media),
                        - Digital privacy, unauthorized access, surveillance, or breach of personal data,
                        - Use or misuse of electronic devices, computers, or digital platforms for illegal activity,
                        - Legal issues involving electronic records, digital signatures, intermediary liability, platform responsibility, or online content regulation,
                        - Any matter where the **Information Technology (IT) Act, 2000** or its associated rules may apply,

                        Then respond with: VECTORSTORE

                        Otherwise, respond with: NO_ANSWER

                        Question: {question}
                        """,
                            input_variables=["question"]
                        )
        
        self.grader_prompt =  PromptTemplate(
                                template="""
                            You are a legal relevance grader.

                            Determine if the following document is relevant to the legal question in the context of the **Information Technology (IT) Act, 2000**.

                            Focus on:
                            - Cybercrime-related provisions (e.g., phishing, identity theft, hacking, OTP fraud),
                            - Electronic records, digital signatures, and data protection,
                            - Responsibilities and liabilities of intermediaries (e.g., social media platforms, ISPs),
                            - Any rules or interpretations under the IT Act, 2000 regarding digital communication and online offenses.

                            Document:
                            {document}

                            Question:
                            {question}

                            If relevant, return: YES  
                            Otherwise, return: NO
                            """,
                                input_variables=["question", "document"]
                            )
        
        self.answer_prompt = PromptTemplate(
                                template="""
                            You are a senior Indian legal researcher.

                            Use the provided legal context to answer the question based on the **Information Technology (IT) Act, 2000** — the Indian law governing cybercrimes, electronic records, digital signatures, data protection, and online offenses.

                            Structure your response as:

                            1. **Applicable Sections (IT Act, 2000)**: Cite the relevant sections by name or number that directly apply to the question.  
                            2. **Interpretation and Legal Analysis**: Explain in depth-how the identified sections apply to the scenario, including legal reasoning, judicial interpretations, or precedent if applicable.  
                            3. **Pros**: Legal safeguards, digital rights, or protections offered under the IT Act.  
                            4. **Cons**: Penalties, liabilities, or risks faced by individuals or organizations under the IT Act.  
                            5. **Procedural Notes**: Outline processes for filing complaints, investigating digital offenses, or presenting electronic evidence in court.

                            Only refer to provisions under the IT Act, 2000. Do not include references to BSA or BNS.

                            Context:  
                            {context}

                            Question:  
                            {question}

                            Answer:
                            """,
                                input_variables=["context", "question"]
                            )

    
    
    def get_grader_prompt(self,question,document):
        return self.grader_prompt.format(question=question,document=document)

    def get_answer_prompt(self,question,context):
        return self.answer_prompt.format(question=question,context=context)
    
    def get_router_prompt(self,question):
        return self.router_prompt.format(question=question)


                     
class BSA_Act_Prompt_Templates:
    def __init__(self):
        self.router_prompt= PromptTemplate(
                            template="""
                        You are a legal query router.

                        If the question involves **any of the following** under Indian evidence law governed by the **Bharatiya Sakshya Adhiniyam (BSA), 2023**:

                        - Admissibility of evidence in Indian courts (e.g., primary vs. secondary evidence, documentary vs. oral evidence),
                        - Electronic or digital records (e.g., emails, CCTV footage, server logs, call recordings, digital contracts),
                        - Authentication or verification of documents or digital content (e.g., metadata, hash value, timestamps),
                        - Burden of proof and presumptions (e.g., who must prove, shifting burden, rebuttable presumptions),
                        - Chain of custody, forensic evidence, or expert opinions,
                        - Rules regarding confessions, statements, admissions, or witness examination,
                        - Use of certified copies, affidavits, and electronically signed documents in legal proceedings,
                        - Presentation, evaluation, and weight of evidence in trials,
                        - Any procedural or substantive issue where **BSA, 2023** governs the **rules of evidence** in criminal, civil, or special proceedings,

                        Then respond with: VECTORSTORE

                        Otherwise, respond with: NO_ANSWER

                        Question: {question}
                        """,
                            input_variables=["question"]
                        )
        
        self.grader_prompt =  PromptTemplate(
                                template="""
                            You are a legal relevance grader.

                            Determine if the following document is relevant to the legal question in the context of the **Bharatiya Sakshya Adhiniyam (BSA), 2023** — the Indian law governing evidentiary rules, admissibility, and evaluation of evidence in court proceedings.

                            Focus on whether the document involves:

                            - Admissibility of evidence (primary vs. secondary, documentary vs. oral, expert vs. circumstantial),
                            - Burden of proof, presumption of facts, and shifting burden,
                            - Rules regarding the examination, cross-examination, and re-examination of witnesses,
                            - Digital or electronic records (e.g., emails, metadata, logs, videos, signed PDFs, or forensic reports),
                            - Rules for authentication, certification, and validation of documents or digital evidence,
                            - Procedures for presenting evidence in court (e.g., submission of affidavits, certified copies, electronic formats),
                            - Relevancy and weight of evidence under BSA,
                            - Confessions, admissions, dying declarations, statements made to authorities,
                            - Chain of custody and expert testimony (e.g., medical, forensic, digital experts),
                            - Any legal provision, clause, or interpretation specifically derived from the **BSA, 2023** (including its replacement of the Indian Evidence Act, 1872).

                            Document:
                            {document}

                            Question:
                            {question}

                            If relevant, return: YES  
                            Otherwise, return: NO
                            """,
                                input_variables=["question", "document"]
                            )
        
        self.answer_prompt = PromptTemplate(
                                template="""
                            You are a senior Indian legal researcher specializing in evidence law.

                            Based on the provided legal context, answer the question strictly under the provisions of the **Bharatiya Sakshya Adhiniyam (BSA), 2023**, which governs the admissibility, evaluation, and procedural handling of evidence in Indian courts, including electronic records.

                            Your response should be structured as follows:

                            1. **Applicable Sections (BSA)**: Cite the exact section names or numbers relevant to the question.  
                            2. **Interpretation and Legal Analysis**: Provide a clear and in-depth explanation of how the cited sections apply to the scenario, including any judicial interpretation if applicable.  
                            3. **Pros (Legal Safeguards)**: Describe protections, rights, or procedural advantages offered to parties under BSA.  
                            4. **Cons (Legal Liabilities or Limitations)**: Highlight potential burdens, challenges in proving admissibility, or risks under BSA.  
                            5. **Procedural Considerations**: Mention rules regarding submission, verification, or authentication of evidence, including digital or electronic formats.

                            Only refer to provisions under the BSA. Do not include content from the IT Act or Bharatiya Nyaya Sanhita.

                            Context:  
                            {context}

                            Question:  
                            {question}

                            Answer:
                            """,
                                input_variables=["context", "question"]
                            )

    def get_grader_prompt(self,question,document):
        return self.grader_prompt.format(question=question,document=document)

    def get_answer_prompt(self,question,context):
        return self.answer_prompt.format(question=question,context=context)
    
    def get_router_prompt(self,question):
        return self.router_prompt.format(question=question)
    
    
class Reflexion_Prompt:
    def __init__(self):
        self.bare_act_reflexion_prompt=PromptTemplate(
                                                template="""
                                                    You are a senior Indian legal expert tasked with synthesizing outputs from three domain-specific legal researchers:

                                                    - The **IT Act Agent**, who responds based on the Information Technology Act, 2000.
                                                    - The **BNS Agent**, who responds based on the Bharatiya Nyaya Sanhita (BNS), 2023.
                                                    - The **BSA Agent**, who responds based on the Bharatiya Sakshya Adhiniyam (BSA), 2023.
                                    

                                                    Each agent has provided a structured response. Your job is to **combine them into one unified legal analysis** in a coherent, professional format for a legal or investigative audience.

                                                    Structure your response as:

                                                    ---

                                                    ### Information Technology (IT) Act, 2000  
                                                    1. **Applicable Sections**  
                                                    2. **Interpretation and Legal Analysis**  
                                                    3. **Pros**  
                                                    4. **Cons**  
                                                    5. **Procedural Notes**

                                                    ---

                                                    ### Bharatiya Nyaya Sanhita (BNS), 2023  
                                                    1. **Applicable Sections**  
                                                    2. **Interpretation and Legal Analysis**  
                                                    3. **Pros**  
                                                    4. **Cons**  
                                                    5. **Procedural Notes**

                                                    ---

                                                    ### Bharatiya Sakshya Adhiniyam (BSA), 2023  
                                                    1. **Applicable Sections**  
                                                    2. **Interpretation and Legal Analysis**  
                                                    3. **Pros**  
                                                    4. **Cons**  
                                                    5. **Procedural Notes**                                                     

                                                    ---

                                                    Use only the information provided by the sub-agents, but make the response consistent in tone and remove any redundancy. Do not introduce new interpretations.

                                                    ---

                                                    **IT Act Agent Output**:  
                                                    {it_act_answer}

                                                    **BNS Agent Output**:  
                                                    {bns_answer}

                                                    **BSA Agent Output**:  
                                                    {bsa_answer}

                                                    Answer:
                                                    """,
                                                        input_variables=["it_act_answer", "bns_answer", "bsa_answer"]
                                                    )
        
        self.reflexion_web_bare_act_prompt = PromptTemplate(
                                                            template="""
                                                                        You are an Indian legal expert and senior research assistant. Your task is to answer a user's question by carefully analyzing the information gathered from:
                                                                        1. Credible web results.
                                                                        2. Relevant Information Technology (IT) Act 2000 Sections
                                                                        3. Relevant Bharatiya Sakshya Adhiniyam (BSA) 2023 Sections
                                                                        4. Relevant Bharatiya Nyaya Sanhita (BNS) 2023 Sections
                                                                        5. Original User Query

                                                                        Use **only the information from the given data** to answer the legal question clearly, accurately, and with appropriate references.

                                                                        ---

                                                                        ### Web Search Summaries (Verifiable Data):
                                                                        {web_data}

                                                                        ### Relevant Information Technology (IT) Act 2000 Sections:
                                                                        {it_act_answer}

                                                                        ### Relevant Bharatiya Sakshya Adhiniyam (BSA) 2023 Sections:
                                                                        {bsa_answer}

                                                                        ### Relevant Bharatiya Nyaya Sanhita (BNS) 2023 Sections:
                                                                        {bns_answer}

                                                                        ### User's Question:
                                                                        {question}

                                                                        ---

                                                                        ### Final Answer Instructions:
                                                                        - Write a high-quality answer using the data above.
                                                                        - Address the user's legal question from the perspectives of **IT Act, 2000**, **BNS 2023**, and **BSA 2023**, if relevant.
                                                                        - Use structured headers (e.g., `## IT Act`, `## BNS`, etc.) for each Act.
                                                                        - Include citations to sources from web summaries using markdown format (e.g., [source name](https://example.com)).
                                                                        - If a reflection suggests a knowledge gap, mention what is still needed for a complete answer.
                                                                        - Suggest what is **not present in India** but **exists internationally** (if applicable).
                                                                        """,
                                                                            input_variables=["it_act_answer", "bns_answer", "bsa_answer", "web_data", "question"]
                                                                        )
    
    
    
    def get_reflexion_web_bare_act_prompt(self, it_act_answer, bns_answer, bsa_answer, web_data, question):
        return self.reflexion_web_bare_act_prompt.format(it_act_answer=it_act_answer,bns_answer=bns_answer,bsa_answer=bsa_answer,web_data=web_data,question=question)
        
    def get_bare_act_reflexion_prompt(self,it_act_answer,bns_answer,bsa_answer):
        return self.bare_act_reflexion_prompt.format(it_act_answer=it_act_answer,bns_answer=bns_answer,bsa_answer=bsa_answer)
    
    
    
# Get current date in a readable format
def get_current_date():
    return datetime.now().strftime("%B %d, %Y")


query_writer_instructions = """Your goal is to generate sophisticated and diverse web search queries. These queries are intended for an advanced automated web research tool capable of analyzing complex results, following links, and synthesizing information.

Instructions:
- Always prefer a single search query, only add another query if the original question requests multiple aspects or elements and one query is not enough.
- Each query should focus on one specific aspect of the original question.
- Don't produce more than {number_queries} queries.
- Queries should be diverse, if the topic is broad, generate more than 1 query.
- Don't generate multiple similar queries, 1 is enough.
- Query should ensure that the most current information is gathered. The current date is {current_date}.

Format: 
- Format your response as a JSON object with ALL two of these exact keys:
   - "rationale": Brief explanation of why these queries are relevant
   - "query": A list of search queries

Example:

Topic: What revenue grew more last year apple stock or the number of people buying an iphone
```json
{{
    "rationale": "To answer this comparative growth question accurately, we need specific data points on Apple's stock performance and iPhone sales metrics. These queries target the precise financial information needed: company revenue trends, product-specific unit sales figures, and stock price movement over the same fiscal period for direct comparison.",
    "query": ["Apple total revenue growth fiscal year 2024", "iPhone unit sales growth fiscal year 2024", "Apple stock price growth fiscal year 2024"],
}}
```

Context: {research_topic}"""


web_searcher_instructions = """Conduct targeted Google Searches to gather the most recent, credible information on "{research_topic}" and synthesize it into a verifiable text artifact.

Instructions:
- Query should ensure that the most current information is gathered. The current date is {current_date}.
- Conduct multiple, diverse searches to gather comprehensive information.
- Consolidate key findings while meticulously tracking the source(s) for each specific piece of information.
- The output should be a well-written summary or report based on your search findings. 
- Only include the information found in the search results, don't make up any information.

Research Topic:
{research_topic}
"""

reflection_instructions = """You are an expert research assistant analyzing summaries about "{research_topic}".

Instructions:
- Identify knowledge gaps or areas that need deeper exploration and generate a follow-up query. (1 or multiple).
- If provided summaries are sufficient to answer the user's question, don't generate a follow-up query.
- If there is a knowledge gap, generate a follow-up query that would help expand your understanding.
- Focus on technical details, implementation specifics, or emerging trends that weren't fully covered.

Requirements:
- Ensure the follow-up query is self-contained and includes necessary context for web search.

Output Format:
- Format your response as a JSON object with these exact keys:
   - "is_sufficient": true or false
   - "knowledge_gap": Describe what information is missing or needs clarification
   - "follow_up_queries": Write a specific question to address this gap

Example:
```json
{{
    "is_sufficient": true, // or false
    "knowledge_gap": "The summary lacks information about performance metrics and benchmarks", // "" if is_sufficient is true
    "follow_up_queries": ["What are typical performance benchmarks and metrics used to evaluate [specific technology]?"] // [] if is_sufficient is true
}}
```

Reflect carefully on the Summaries to identify knowledge gaps and produce a follow-up query. Then, produce your output following this JSON format:

Summaries:
{summaries}
"""

answer_instructions = """Generate a high-quality answer to the user's question based on the provided summaries.

Instructions:
- The current date is {current_date}.
- You are the final step of a multi-step research process, don't mention that you are the final step. 
- You have access to all the information gathered from the previous steps.
- You have access to the user's question.
- Generate a high-quality answer to the user's question based on the provided summaries and the user's question.
- Include the sources you used from the Summaries in the answer correctly, use markdown format (e.g. [apnews](https://vertexaisearch.cloud.google.com/id/1-0)). THIS IS A MUST.

User Context:
- {research_topic}

Summaries:
{summaries}"""