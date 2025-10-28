from shared.schemas import BlogPost

def create_base_markdown(blog_post: BlogPost) -> str:
    """
    Crea el string de Markdown base de forma determinista a partir del objeto BlogPost.
    """
    markdown_parts = []

    markdown_parts.append(f"# {blog_post.main_title}\n")
    markdown_parts.append(f"{blog_post.introduction}\n")

    for section in blog_post.sections:
        markdown_parts.append(f"## {section.section_title}\n")
        markdown_parts.append(f"{section.content}\n")

    markdown_parts.append(f"{blog_post.call_to_action}\n")

    if blog_post.sources:
        markdown_parts.append("---\n")
        markdown_parts.append("### Fuentes\n")
        for source in blog_post.sources:
            markdown_parts.append(f"* [{source.title}]({source.original_url})")

    return "\n".join(markdown_parts)