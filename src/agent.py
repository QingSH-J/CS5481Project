"""
Agent Module
Implements the agentic RAG system using LangChain agents.
"""

import yaml
from typing import Optional
from langchain_openai import ChatOpenAI
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.agents import AgentExecutor, create_openai_tools_agent, create_react_agent
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder, PromptTemplate
from langchain.memory import ConversationBufferMemory

from src.vector_store import VectorStoreManager
from src.agent_tools import create_agent_tools


class AgenticRAG:
    """Agentic RAG system that uses LangChain agents with custom tools."""

    def __init__(self, config_path: str = "config.yaml"):
        """
        Initialize the agentic RAG system.

        Args:
            config_path: Path to the configuration file
        """
        with open(config_path, 'r') as f:
            self.config = yaml.safe_load(f)

        # Initialize vector store manager
        print("Initializing vector store...")
        self.vector_store_manager = VectorStoreManager(config_path)

        # Initialize LLM
        print("Initializing LLM...")
        self.llm = self._initialize_llm()

        # Create tools
        print("Creating agent tools...")
        self.tools = create_agent_tools(self.vector_store_manager)

        # Initialize memory
        self.memory = ConversationBufferMemory(
            memory_key="chat_history",
            return_messages=True
        )

        # Create agent
        print("Creating agent...")
        self.agent = self._create_agent()

        # Create agent executor
        self.agent_executor = AgentExecutor(
            agent=self.agent,
            tools=self.tools,
            memory=self.memory,
            verbose=self.config['agent']['verbose'],
            max_iterations=self.config['agent']['max_iterations'],
            handle_parsing_errors=True
        )

        print("Agentic RAG system initialized successfully!")

    def _initialize_llm(self):
        """Initialize the language model based on configuration."""
        provider = self.config['llm']['provider']

        if provider == 'gemini':
            model = self.config['llm']['model']
            temperature = self.config['llm']['temperature']
            max_tokens = self.config['llm']['max_tokens']

            return ChatGoogleGenerativeAI(
                model=model,
                temperature=temperature,
                max_output_tokens=max_tokens
            )

        elif provider == 'openai':
            model = self.config['llm'].get('openai_model', self.config['llm'].get('model'))
            temperature = self.config['llm']['temperature']
            max_tokens = self.config['llm']['max_tokens']

            return ChatOpenAI(
                model=model,
                temperature=temperature,
                max_tokens=max_tokens
            )

        # Add support for other providers like Ollama
        elif provider == 'ollama':
            # Requires langchain-ollama package
            from langchain_community.llms import Ollama
            model = self.config['llm'].get('ollama_model', 'llama2')
            return Ollama(model=model)

        else:
            raise ValueError(f"Unsupported LLM provider: {provider}")

    def _create_agent(self):
        """Create the LangChain agent with custom prompt."""
        agent_type = self.config['agent'].get('agent_type', 'react')

        if agent_type == 'openai-tools':
            # OpenAI tools agent (for OpenAI models with function calling)
            system_prompt = """You are a helpful AI assistant with access to a knowledge base.
Your goal is to answer user questions accurately based on the information in the knowledge base.

When answering questions:
1. Always search the knowledge base first using the knowledge_base_search tool
2. Base your answers ONLY on the information retrieved from the knowledge base
3. If the information is not in the knowledge base, clearly state that you don't have that information
4. Cite the sources when providing information
5. If the user asks about what's in the knowledge base, use the knowledge_base_stats tool

Be conversational but accurate. If you're not sure about something, say so.
"""

            prompt = ChatPromptTemplate.from_messages([
                ("system", system_prompt),
                MessagesPlaceholder(variable_name="chat_history", optional=True),
                ("human", "{input}"),
                MessagesPlaceholder(variable_name="agent_scratchpad"),
            ])

            agent = create_openai_tools_agent(
                llm=self.llm,
                tools=self.tools,
                prompt=prompt
            )

        else:  # react agent (for Gemini and other models)
            template = """You are a helpful AI assistant with access to a knowledge base.
Your goal is to answer user questions accurately based on the information in the knowledge base.

When answering questions:
1. Always search the knowledge base first using the knowledge_base_search tool
2. Base your answers ONLY on the information retrieved from the knowledge base
3. If the information is not in the knowledge base, clearly state that you don't have that information
4. Cite the sources when providing information
5. If the user asks about what's in the knowledge base, use the knowledge_base_stats tool

Be conversational but accurate. If you're not sure about something, say so.

TOOLS:
------
You have access to the following tools:

{tools}

To use a tool, please use the following format:

```
Thought: Do I need to use a tool? Yes
Action: the action to take, should be one of [{tool_names}]
Action Input: the input to the action
Observation: the result of the action
```

When you have a response to say to the Human, or if you do not need to use a tool, you MUST use the format:

```
Thought: Do I need to use a tool? No
Final Answer: [your response here]
```

Begin!

Question: {input}
Thought: {agent_scratchpad}"""

            prompt = PromptTemplate.from_template(template)

            agent = create_react_agent(
                llm=self.llm,
                tools=self.tools,
                prompt=prompt
            )

        return agent

    def query(self, question: str) -> str:
        """
        Query the agentic RAG system.

        Args:
            question: User's question

        Returns:
            Agent's response
        """
        try:
            response = self.agent_executor.invoke({"input": question})
            return response['output']
        except Exception as e:
            return f"Error processing query: {str(e)}"

    def reset_memory(self):
        """Clear conversation memory."""
        self.memory.clear()
        print("Conversation memory cleared")

    def get_conversation_history(self):
        """Get the current conversation history."""
        return self.memory.load_memory_variables({})


if __name__ == "__main__":
    # Test the agent
    try:
        agent = AgenticRAG()
        print("\n" + "="*50)
        print("Agentic RAG System Ready!")
        print("="*50)

        # Test query
        test_question = "What information is available in the knowledge base?"
        print(f"\nTest Question: {test_question}")
        response = agent.query(test_question)
        print(f"\nResponse: {response}")

    except Exception as e:
        print(f"Error: {e}")
