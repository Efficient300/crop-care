import re
class MarkdownProcessor:

    @staticmethod
    async def strip_markdown(text):

        if not text:
            return text

        text = re.sub(r'^#{1,6}\s+', '', text, flags=re.MULTILINE)
        text = re.sub(r'(\*\*|__)(.*?)\1', r'\2', text)
        text = re.sub(r'(\*|_)(.*?)\1', r'\2', text)
        text = re.sub(r'^[-*]\s+', '', text, flags=re.MULTILINE)
        text = re.sub(r'\[([^\]]+)\]\([^)]+\)', r'\1', text)
        text = re.sub(r'!\[([^\]]*)\]\([^)]+\)', '', text)
        text = re.sub(r'^---$', '', text, flags=re.MULTILINE)
        text = re.sub(r'`', '', text)
        text = re.sub(r'\n{3,}', '\n\n', text)
        return text.strip()