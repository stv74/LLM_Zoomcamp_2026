INSTRUCTIONS = """
Your task is to answer questions from the course participants
based on the provided context.

Use the context to find relevant information and provide accurate
answers. If the answer is not found in the context,
respond with "I don't know."
"""

PROMPT_TEMPLATE = """
Question: {question}

Context: 
{context}
""".strip()

class RAGBase:

    def __init__(
            self,
            index,
            llm_client,
            instructions=INSTRUCTIONS,
            prompt_template=PROMPT_TEMPLATE,
            course='llm-zoomcamp',
            model='gemini-3.1-flash-lite'
    ):
        self.index = index
        self.llm_client = llm_client
        self.instructions = instructions
        self.prompt_template = prompt_template
        self.course = course
        self.model = model

    def search(self, query, num_results=5):
        """
        Search the MinSearch index for relevant documents based on the query.
        Returns a list of documents.
        """
        boost_dict = {"question": 3.0, "section": 0.5}
        filter_dict = {"course": self.course}

        return self.index.search(
            query, 
            num_results=num_results,
            boost_dict=boost_dict,
            filter_dict=filter_dict
        )
    
    def build_context(self, search_results):
        '''
        Build a context string from the search results.
        '''
        lines = []

        for doc in search_results:
            lines.append(doc["section"])
            lines.append("Q: " + doc["question"])
            lines.append("A: " + doc["answer"])
            lines.append("")

        return "\n".join(lines).strip()

    def build_prompt(self, query, search_results):
        '''
        Build a prompt string from the query and search results.
        '''
        context = self.build_context(search_results)
        return self.prompt_template.format(
            question=query,
            context=context
        )

    def llm(self, prompt):
        '''
        Call the LLM client with the prompt and return the output text.'''
        interaction = self.llm_client.interactions.create(
            model=self.model,
            system_instruction=self.instructions,
            input=prompt
        )
        return interaction.output_text
    
    def rag(self, query):
        '''
        Perform retrieval-augmented generation (RAG) for the given query.
        '''
        search_results = self.search(query)
        prompt = self.build_prompt(query, search_results)
        answer = self.llm(prompt)
        return answer