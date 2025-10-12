from langchain_anthropic import ChatAnthropic
from langchain.agents import AgentExecutor, initialize_agent, AgentType
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from app.tools.web_search_tool import web_search
from app.tools.image_search_tool import image_search
from app.tools.file_writer_tool import write_blog_file, read_blog_file
from app.config import get_settings
from typing import Dict, Any


class BlogAssistantAgent:
    """
    AI Blog Assistant Agent that can research, write, and save blog posts.

    This agent uses the ReAct (Reasoning + Acting) pattern to autonomously:
    1. Search the web for latest information about a topic
    2. Find appropriate cover images
    3. Write well-structured blog posts
    4. Save the final content to MDX files
    """

    def __init__(self):
        settings = get_settings()

        # Initialize Claude model as the "brain" of the agent
        self.llm = ChatAnthropic(
            model="claude-3-5-sonnet-20241022",
            anthropic_api_key=settings.anthropic_api_key,
            temperature=0.7,
        )

        # Define the tools (hands and feet) the agent can use
        self.tools = [web_search, image_search, write_blog_file, read_blog_file]

        # System message for the agent
        system_message = """You are an expert blog writing assistant with access to powerful tools.

Your role is to create high-quality, well-researched blog posts by:
1. Using web_search to research the topic thoroughly and get latest information
2. Using image_search to find appropriate cover images
3. Writing engaging, informative content in MDX format
4. Using write_blog_file to save the final result

When writing blog posts, always:
- Start with frontmatter in YAML format (title, description, date, image)
- Write engaging and informative content
- Use proper markdown formatting
- Include relevant examples and insights
- Create SEO-friendly titles and descriptions

Example MDX format:
---
title: "Your Blog Title"
description: "Brief description of the blog post"
date: "2025-01-12"
image: "https://example.com/image.jpg"
tags: ["tag1", "tag2"]
---

# Your Blog Title

Introduction paragraph...

## Section 1

Content here...

IMPORTANT: Always save the final blog post using write_blog_file with file_name and content parameters.

Think step-by-step and use the tools available to accomplish your task."""

        # Create the agent executor using initialize_agent
        # Use STRUCTURED_CHAT_ZERO_SHOT_REACT_DESCRIPTION for multi-input tools support
        self.agent_executor = initialize_agent(
            tools=self.tools,
            llm=self.llm,
            agent=AgentType.STRUCTURED_CHAT_ZERO_SHOT_REACT_DESCRIPTION,
            verbose=True,
            max_iterations=15,
            handle_parsing_errors=True,
            agent_kwargs={"prefix": system_message},
            return_intermediate_steps=True,
        )

    def generate_blog_post(self, topic: str, additional_instructions: str = "") -> Dict[str, Any]:
        """
        Generate a complete blog post about the given topic.

        Args:
            topic: The topic to write about
            additional_instructions: Any additional instructions for the agent

        Returns:
            A dictionary containing the result and metadata
        """
        # Construct a simpler, more direct message
        user_message = f"""Write a blog post about: {topic}

Requirements:
- Create a short blog post (200-300 words)
- Search for an image
- Save to a file named: {topic.lower().replace(' ', '-')[:30]}.mdx

{additional_instructions if additional_instructions else ''}

Step by step:
1. Search for an image about the topic
2. Write a brief blog post with MDX frontmatter
3. Save it using write_blog_file with TWO parameters: file_name and content"""

        try:
            # Execute the agent
            result = self.agent_executor.invoke({"input": user_message})

            return {
                "success": True,
                "result": result.get("output", ""),
                "steps": result.get("intermediate_steps", []),
            }

        except Exception as e:
            return {"success": False, "error": str(e), "result": ""}

    def chat(self, message: str) -> str:
        """
        Simple chat interface with the agent.

        Args:
            message: The user's message

        Returns:
            The agent's response
        """
        try:
            result = self.agent_executor.invoke({"input": message})
            return result.get("output", "")
        except Exception as e:
            return f"Error: {str(e)}"


# Singleton instance
_agent_instance = None


def get_blog_assistant_agent() -> BlogAssistantAgent:
    """Get or create the singleton agent instance."""
    global _agent_instance
    if _agent_instance is None:
        _agent_instance = BlogAssistantAgent()
    return _agent_instance
