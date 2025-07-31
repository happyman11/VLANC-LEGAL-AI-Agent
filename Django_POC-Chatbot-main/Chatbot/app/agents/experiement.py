from some_ollama_library import OllamaChat  # make sure you install the right library

class Websearch_Agent:
    def __init__(self):
        self.Get_API = Get_API_Keys()

    def _get_llm(self, model_name, temperature=1.0, max_retries=2):
        """Returns the correct LLM client based on model_name."""
        if model_name.lower().startswith("ollama/"):
            return OllamaChat(
                model=model_name.split("ollama/")[1],  # e.g., "llama3"
                temperature=temperature,
                max_retries=max_retries,
                api_key=None  # Ollama usually runs locally, so no API key
            )
        else:
            return ChatGoogleGenerativeAI(
                model=model_name,
                temperature=temperature,
                max_retries=max_retries,
                api_key=self.Get_API.get_Web_Search_API()
            )

    @traceable(name="generate_query")
    def generate_query(self, state: OverallAgentsState, config: RunnableConfig) -> QueryGenerationState:
        configurable = Configuration.from_runnable_config(config)

        if state.get("initial_search_query_count") is None:
            state["initial_search_query_count"] = configurable.number_of_initial_queries

        llm = self._get_llm(configurable.query_generator_model, temperature=1.0)
        structured_llm = llm.with_structured_output(SearchQueryList)

        current_date = get_current_date()
        formatted_prompt = query_writer_instructions.format(
            current_date=current_date,
            research_topic=get_research_topic(state["messages"]),
            number_queries=state["initial_search_query_count"],
        )
        result = structured_llm.invoke(formatted_prompt)
        return {"search_query": result.query}

    @traceable(name="continue_to_web_research")
    def continue_to_web_research(self, state: QueryGenerationState):
        return [
            Send("web_research", {"search_query": search_query, "id": int(idx)})
            for idx, search_query in enumerate(state["search_query"])
        ]

    @traceable(name="web_research")
    def web_research(self, state: WebSearchState, config: RunnableConfig) -> OverallAgentsState:
        configurable = Configuration.from_runnable_config(config)
        formatted_prompt = web_searcher_instructions.format(
            current_date=get_current_date(),
            research_topic=state["search_query"],
        )

        llm = self._get_llm(configurable.query_generator_model, temperature=0)
        response = llm.invoke(formatted_prompt)

        resolved_urls = resolve_urls(
            getattr(response, "grounding_metadata", {}).get("grounding_chunks", []),
            state["id"]
        )
        citations = get_citations(response, resolved_urls)
        modified_text = insert_citation_markers(response.text, citations)
        sources_gathered = [item for citation in citations for item in citation["segments"]]

        return {
            "sources_gathered": sources_gathered,
            "search_query": [state["search_query"]],
            "web_research_result": [modified_text],
        }

    @traceable(name="knowledge_reflexion")
    def reflection(self, state: OverallAgentsState, config: RunnableConfig) -> ReflectionState:
        configurable = Configuration.from_runnable_config(config)
        state["research_loop_count"] = state.get("research_loop_count", 0) + 1

        reasoning_model = state.get("reasoning_model", configurable.reflection_model)
        current_date = get_current_date()
        formatted_prompt = reflection_instructions.format(
            current_date=current_date,
            research_topic=get_research_topic(state["messages"]),
            summaries="\n\n---\n\n".join(state["web_research_result"]),
        )
        llm = self._get_llm(reasoning_model, temperature=1.0)
        result = llm.with_structured_output(Reflection).invoke(formatted_prompt)

        return {
            "is_sufficient": result.is_sufficient,
            "knowledge_gap": result.knowledge_gap,
            "follow_up_queries": result.follow_up_queries,
            "research_loop_count": state["research_loop_count"],
            "number_of_ran_queries": len(state["search_query"]),
        }

    @traceable(name="evaluate_research")
    def evaluate_research(self, state: ReflectionState, config: RunnableConfig) -> OverallAgentsState:
        configurable = Configuration.from_runnable_config(config)
        max_research_loops = (
            state.get("max_research_loops")
            if state.get("max_research_loops") is not None
            else configurable.max_research_loops
        )
        if state["is_sufficient"] or state["research_loop_count"] >= max_research_loops:
            return "finalize_answer"
        else:
            return [
                Send(
                    "web_research",
                    {
                        "search_query": follow_up_query,
                        "id": state["number_of_ran_queries"] + int(idx),
                    },
                )
                for idx, follow_up_query in enumerate(state["follow_up_queries"])
            ]

    @traceable(name="finalize_answer")
    def finalize_answer(self, state: OverallAgentsState, config: RunnableConfig):
        configurable = Configuration.from_runnable_config(config)
        reasoning_model = state.get("reasoning_model") or configurable.answer_model

        current_date = get_current_date()
        formatted_prompt = answer_instructions.format(
            current_date=current_date,
            research_topic=get_research_topic(state["messages"]),
            summaries="\n---\n\n".join(state["web_research_result"]),
        )

        llm = self._get_llm(reasoning_model, temperature=0)
        result = llm.invoke(formatted_prompt)

        unique_sources = []
        for source in state["sources_gathered"]:
            if source["short_url"] in result.content:
                result.content = result.content.replace(source["short_url"], source["value"])
                unique_sources.append(source)

        return {
            "Web_Search_answer": result.content,
            "sources_gathered": unique_sources,
        }
