import asyncio
from dotenv import load_dotenv
from typing import Any

from google.adk.agents import LlmAgent, SequentialAgent
from google.adk.runners import InMemoryRunner
from google.adk.tools import google_search

load_dotenv()

core_deconstructor_agent = LlmAgent(
    name="CoreConceptDeconstructorAgent",
    model="gemini-2.5-flash-lite",
    description="Phá vỡ một chủ đề thành các yếu tố cơ bản, định nghĩa và giả định.",
    instruction="""
Bạn là một nhà phân tích khái niệm. Dựa trên chủ đề người dùng cung cấp,
hãy sử dụng `google_search` để tìm hiểu sâu về bản chất của nó.
Trình bày các yếu tố cốt lõi, định nghĩa quan trọng, các nguyên tắc cơ bản,
và bất kỳ giả định ngầm nào liên quan đến chủ đề.
Sử dụng ngôn ngữ rõ ràng, chính xác và có cấu trúc.
Lưu phần phân tích này vào khóa state có tên 'core_analysis'.
""",
    tools=[google_search],
    output_key="core_analysis",
)

critical_question_agent = LlmAgent(
    name="CriticalQuestionGeneratorAgent",
    model="gemini-2.5-flash",
    description="Tạo ra các câu hỏi sâu sắc, phản biện và mở rộng dựa trên phân tích cốt lõi.",
    instruction="""
Bạn là một người chất vấn. Dựa vào nội dung phân tích cốt lõi trong khóa 'core_analysis' từ bước trước,
hãy đặt ít nhất 5-7 câu hỏi phản biện, sâu sắc theo phong cách Feynman.
Các câu hỏi này nên tập trung vào:
-   **Tại sao lại như vậy?** (Chất vấn nguyên nhân sâu xa)
-   **Điều kiện nào để điều này đúng/sai?** (Phân tích bối cảnh, giới hạn)
-   **Nếu như này thì sao?** (Kịch bản giả định, kiểm tra tính nhất quán)
-   **Như vậy có đúng không và làm sao để kiểm chứng?** (Thách thức giả định, đề xuất kiểm tra)
-   **Có cách giải thích nào khác không?** (Tìm kiếm đa chiều)
-   **Điểm yếu/hạn chế của cách hiểu hiện tại là gì?**
Không đưa ra câu trả lời, chỉ tạo các câu hỏi.
Lưu các câu hỏi này vào khóa state có tên 'critical_questions'.
""",
    output_key="critical_questions",
)

feynman_elaboration_agent = LlmAgent(
    name="FeynmanElaborationAgent",
    model="gemini-2.5-flash",
    description="Suy luận và phân tích chuyên sâu các câu hỏi phản biện, mở rộng vấn đề theo phong cách Feynman.",
    instruction="""
Bạn là một nhà suy luận theo phong cách Feynman. Dựa trên các câu hỏi phản biện trong khóa 'critical_questions'
và phân tích cốt lõi trong 'core_analysis' từ các bước trước, hãy chọn 2-3 câu hỏi quan trọng nhất.
Đối với mỗi câu hỏi đã chọn, hãy:
1.  **Suy luận logic và phân tích:** Cố gắng trả lời hoặc mở rộng câu hỏi bằng cách suy luận từ các nguyên tắc cơ bản,
    phá vỡ nó thành các phần đơn giản nhất (giống như giải thích cho trẻ nhỏ).
2.  **Đưa ra các kịch bản 'What if':** Khám phá các tình huống giả định để kiểm tra tính vững chắc của khái niệm.
3.  **Xác định các vùng kiến thức còn thiếu:** Chỉ ra những điểm mà cần nghiên cứu hoặc làm rõ thêm.
4.  **Sử dụng `google_search`** nếu cần tra cứu thông tin cụ thể để hỗ trợ suy luận hoặc kiểm chứng một giả định.
Kết quả phải thể hiện một quá trình tư duy sâu sắc, đặt ra nhiều câu hỏi hơn cả câu trả lời,
nhằm làm rõ bản chất vấn đề.
Lưu phần suy luận và mở rộng này vào khóa state có tên 'feynman_insights'.
""",
    tools=[google_search],
    output_key="feynman_insights",
)

feynman_brainstorming_flow = SequentialAgent(
    name="FeynmanBrainstormingFlow",
    sub_agents=[
        core_deconstructor_agent,
        critical_question_agent,
        feynman_elaboration_agent
    ],
    description="Một luồng động não và phân tích kiến thức chuyên sâu theo phong cách Feynman.",
)

scientific_report_generator_agent = LlmAgent(
    name="ScientificReportGeneratorAgent",
    model="gemini-2.5-flash",
    description="Tổng hợp các phân tích, câu hỏi và suy luận chuyên sâu để tạo báo cáo khoa học.",
    instruction="""
Bạn là một nhà khoa học và người viết báo cáo.
Dựa trên các kết quả phân tích có sẵn trong state từ quá trình động não trước đó (cụ thể là 'core_analysis', 'critical_questions', và 'feynman_insights'),
hãy tổng hợp tất cả các thông tin, vấn đề, câu hỏi chưa được giải quyết và suy luận chuyên sâu.
Trình bày tổng hợp này dưới dạng một báo cáo khoa học ngắn gọn, có cấu trúc rõ ràng, bao gồm các phần sau:

1.  **Tiêu đề Báo cáo:** Tóm tắt chủ đề chính từ truy vấn ban đầu.
2.  **Tóm tắt (Abstract):** Giới thiệu ngắn gọn về chủ đề, các vấn đề chính được nêu và những điểm suy luận quan trọng.
3.  **Giới thiệu:** Đặt vấn đề, nêu tầm quan trọng của chủ đề, dựa trên 'core_analysis'.
4.  **Phân tích Cốt lõi và Giả định:** Trình bày các định nghĩa, nguyên tắc và giả định đã được xác định từ 'core_analysis'.
5.  **Các Vấn đề và Câu hỏi Phản biện:** Liệt kê và giải thích các câu hỏi quan trọng, các thách thức đã được đặt ra từ 'critical_questions'.
6.  **Suy luận và Thảo luận Chuyên sâu:** Trình bày các kịch bản 'what if', các phân tích logic và những điểm cần làm rõ hơn từ 'feynman_insights'.
7.  **Kết luận và Hướng Nghiên cứu Tiếp theo:** Tóm tắt các điểm chính và đề xuất các lĩnh vực cần nghiên cứu thêm hoặc những câu hỏi lớn còn bỏ ngỏ.

Sử dụng ngôn ngữ khoa học, khách quan và chính xác.
Sử dụng `google_search` nếu cần để bổ sung dữ kiện hoặc tìm kiếm các ví dụ hỗ trợ cho báo cáo.
Đảm bảo báo cáo mạch lạc, có luận lý và dựa trên các thông tin đã được phân tích.
""",
    tools=[google_search],
    output_key="scientific_report",
)

super_study_and_report_flow = SequentialAgent(
    name="SuperStudyAndReportFlow",
    sub_agents=[
        feynman_brainstorming_flow,        
        scientific_report_generator_agent  
    ],
    description="Một luồng toàn diện để động não kiến thức theo phong cách Feynman và tạo báo cáo khoa học tổng hợp.",
)

root_agent = super_study_and_report_flow

async def main_super_flow():
    runner = InMemoryRunner(root_agent)

    topic_for_study = "Đạo đức trong Phát triển Trí tuệ Nhân tạo"
    print(f"Bắt đầu luồng toàn diện cho chủ đề: '{topic_for_study}'")

    final_mega_result = await runner.run(topic_for_study)

    print("\n--- KẾT QUẢ ĐỘNG NÃO & BÁO CÁO KHOA HỌC ---")

    print("\n=== [GIAI ĐOẠN ĐỘNG NÃO] ===")
    if 'core_analysis' in final_mega_result.state:
        print("\n=== 1. Phân tích Cốt lõi Khái niệm ===")
        print(final_mega_result.state["core_analysis"])
        print("\n------------------------------")
    if 'critical_questions' in final_mega_result.state:
        print("=== 2. Các Câu hỏi Phản biện ===")
        print(final_mega_result.state["critical_questions"])
        print("\n------------------------------")
    if 'feynman_insights' in final_mega_result.state:
        print("=== 3. Suy luận và Mở rộng Sâu (Phong cách Feynman) ===")
        print(final_mega_result.state["feynman_insights"])
        print("\n------------------------------")

    print("\n=== [GIAI ĐOẠN BÁO CÁO] ===")
    if 'scientific_report' in final_mega_result.state:
        print("=== Báo cáo Khoa học Tổng hợp ===")
        print(final_mega_result.state["scientific_report"])
        print("\n------------------------------")
    else:
        print("\nKhông thể tạo báo cáo khoa học.")

    print("\n--- HOÀN TẤT LUỒNG TOÀN DIỆN ---")

if __name__ == "__main__":
    asyncio.run(main_super_flow())