from shared.schemas import BlogPost
from datetime import datetime, timezone


def create_base_markdown(blog_post: BlogPost) -> str:
    """
    Crea el string de Markdown base, incluyendo el Frontmatter YAML
    requerido por Gatsby, a partir del objeto BlogPost.
    """
    markdown_parts = []

    now = datetime.now(timezone.utc)
    date_formatted = now.isoformat()[:-6] + "Z"

    description = blog_post.introduction[:150].split('\n')[0].strip() + "..."

    markdown_parts.append("---\n")
    markdown_parts.append(f"title: {blog_post.main_title}\n")
    markdown_parts.append(f"date: \"{date_formatted}\"\n")
    markdown_parts.append(f"description: \"{description}\"\n")

    markdown_parts.append("tags:\n")
    if hasattr(blog_post, 'tags') and blog_post.tags:
        for tag in blog_post.tags:
            markdown_parts.append(f"  - {tag}\n")

    IMAGE_FILENAME = "featured_image.jpg"
    markdown_parts.append(f"featuredImage: \"./{IMAGE_FILENAME}\"\n")

    markdown_parts.append("---\n")
    markdown_parts.append(f"![{blog_post.main_title}](./{IMAGE_FILENAME})\n")

    markdown_parts.append(f"{blog_post.introduction}\n")

    for section in blog_post.sections:
        markdown_parts.append(f"## {section.section_title}\n")
        markdown_parts.append(f"{section.content}\n")

    markdown_parts.append(f"{blog_post.call_to_action}\n")

    if blog_post.sources:
        markdown_parts.append("---\n")
        markdown_parts.append("### Fuentes\n")
        for source in blog_post.sources:
            markdown_parts.append(f"* [{source.title}]({source.resolved_url})")

    return "\n".join(markdown_parts)