import asyncio
from dotenv import load_dotenv
from typing import Any

from google.adk.agents import LlmAgent
from google.adk.runners import InMemoryRunner
from google.adk.tools import google_search

load_dotenv()

news_reporter_agent = LlmAgent(
    name="NewsReporterAgent",
    model="gemini-2.5-flash",
    description="Tìm kiếm và tóm tắt các tin tức mới nhất về một chủ đề.",
    instruction="""
Bạn là một phóng viên tin tức. Nhiệm vụ của bạn là tìm kiếm các tin tức gần đây về chủ đề được cung cấp.
Sử dụng công cụ `google_search` để tìm kiếm thông tin mới nhất.
Sau khi tìm được, hãy tóm tắt các điểm chính thành một đoạn văn ngắn gọn (khoảng 3-5 câu),
và cung cấp ít nhất 2-3 trích dẫn (tiêu đề và URL) từ các nguồn tin tức uy tín.
Nếu không tìm thấy tin tức liên quan, hãy thông báo cho người dùng.
""",
    tools=[google_search],
    output_key="news_summary",
)

root_agent = news_reporter_agent

async def main_news_reporter():
    runner = InMemoryRunner(root_agent)

    print("Running NewsReporterAgent with query: 'Tin tức mới nhất về AI tạo sinh'")
    result_ai_news = await runner.run("Tin tức mới nhất về AI tạo sinh")
    print("\n--- Kết quả Tin tức AI ---")
    print(result_ai_news.state["news_summary"])

    print("\nRunning NewsReporterAgent with query: 'Cập nhật về thị trường chứng khoán Việt Nam'")
    result_stock_news = await runner.run("Cập nhật về thị trường chứng khoán Việt Nam")
    print("\n--- Kết quả Tin tức Chứng khoán ---")
    print(result_stock_news.state["news_summary"])

if __name__ == "__main__":
    asyncio.run(main_news_reporter())