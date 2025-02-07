import logging
from typing import Dict, Optional
from app.llm import LLMModule, LLMRequest, ResponseType
from app.retriever.search import SearchEngine
from app.retriever.types import SearchQuery

logger = logging.getLogger(__name__)

class RAGOrchestrator:
    def __init__(self, llm: LLMModule, search_engine: SearchEngine):
        """Initialize the RAG Orchestrator"""
        self.llm = llm
        self.search_engine = search_engine
        self.logger = logging.getLogger(__name__)

    def _validate_query(self, query: str):
        """Validate input query"""
        if not query.strip():
            raise ValueError("Query cannot be empty")

    async def process_query(
        self,
        query: str,
        response_type: ResponseType,
        additional_context: Optional[Dict] = None
    ):
        """
        Process a query through the RAG pipeline:
        1. Search for relevant context
        2. Enhance query with context
        3. Get LLM response
        """
        try:
            self._validate_query(query)
            
            # 1. Get relevant context
            search_query = SearchQuery(query=query, top_k=3)
            search_result = await self.search_engine.search(search_query)
            
            # 2. Prepare context
            context = {
                "retrieved_contexts": [
                    {
                        "content": ctx.content,
                        "source": ctx.source,
                        "relevance": ctx.relevance_score
                    }
                    for ctx in search_result.contexts
                ]
            }
            
            if additional_context:
                context.update(additional_context)
            
            # 3. Prepare and send request to LLM
            llm_request = LLMRequest(
                query=query,
                response_type=response_type,
                context=context
            )
            
            return await self.llm.process_request(llm_request)
            
        except Exception as e:
            self.logger.error(f"Error processing query: {str(e)}")
            raise