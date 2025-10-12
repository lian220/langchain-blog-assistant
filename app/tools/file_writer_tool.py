from langchain.tools import StructuredTool, tool
from langchain.pydantic_v1 import BaseModel, Field
import os
from pathlib import Path
from datetime import datetime


class BlogFileInput(BaseModel):
    """Input schema for writing blog files."""

    file_name: str = Field(description="The name of the file to save (should end with .mdx)")
    content: str = Field(description="The complete blog post content including frontmatter and body")


def write_blog_file_func(file_name: str, content: str) -> str:
    """Save the completed blog post content to an MDX file."""
    try:
        # Ensure file name ends with .mdx
        if not file_name.endswith(".mdx"):
            file_name = f"{file_name}.mdx"

        # Create the full path
        blog_dir = Path("content/blog")
        blog_dir.mkdir(parents=True, exist_ok=True)

        file_path = blog_dir / file_name

        # Write the content to the file
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(content)

        print(f">>> Writing to file: {file_path}")
        return f"File '{file_name}' saved successfully at {file_path}"

    except Exception as e:
        error_msg = f"Error saving file: {str(e)}"
        print(f">>> {error_msg}")
        return error_msg


# Create the structured tool
write_blog_file = StructuredTool.from_function(
    func=write_blog_file_func,
    name="write_blog_file",
    description="Save the completed blog post content to an MDX file in the content/blog directory",
    args_schema=BlogFileInput,
    return_direct=False,
)


@tool
def read_blog_file(file_name: str) -> str:
    """Read the content of an existing blog post file.

    This tool reads and returns the content of a blog post file from the content/blog directory.

    Args:
        file_name: The name of the file to read (should end with .mdx)

    Returns:
        The content of the file, or an error message if the file doesn't exist
    """
    try:
        # Ensure file name ends with .mdx
        if not file_name.endswith(".mdx"):
            file_name = f"{file_name}.mdx"

        file_path = Path("content/blog") / file_name

        if not file_path.exists():
            return f"File '{file_name}' does not exist."

        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()

        print(f">>> Reading from file: {file_path}")
        return content

    except Exception as e:
        error_msg = f"Error reading file: {str(e)}"
        print(f">>> {error_msg}")
        return error_msg
