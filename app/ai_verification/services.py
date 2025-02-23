# import base64
# import mimetypes
# import openai
# from langchain.llms import OpenAI as LangChainOpenAI
# from langchain import PromptTemplate, LLMChain
# import PyPDF2
# import pandas as pd

# class AIVerificationSystem:
#     def __init__(self, openai_api_key: str):
#         self.openai_api_key = openai_api_key
#         openai.api_key = openai_api_key
        
#         # Initialize LangChain LLM for text-based similarity evaluation.
#         self.llm = LangChainOpenAI(api_key=openai_api_key, temperature=0)
#         self.prompt_template = PromptTemplate(
#             input_variables=["description", "content"],
#             template=(
#                 "You are an AI tasked with evaluating how similar a contribution is to a campaign description. "
#                 "Based on the content below, please provide a similarity score between 0 and 100, where 100 means a perfect match.\n\n"
#                 "Campaign Description:\n{description}\n\n"
#                 "Contribution Content:\n{content}\n\n"
#                 "Similarity Score:"
#             )
#         )
#         self.llm_chain = LLMChain(llm=self.llm, prompt=self.prompt_template)

#     def verify(self, campaign, file_path: str) -> float:
#         """
#         Verifies the provided file against the campaign description.
#         Returns a similarity score (0–100).
#         """
#         mime_type, _ = mimetypes.guess_type(file_path)
#         if mime_type:
#             if mime_type.startswith("image"):
#                 score = self.verify_image(campaign, file_path)
#             elif mime_type.startswith("text") or file_path.endswith('.pdf') or file_path.endswith('.csv'):
#                 score = self.verify_text_document(campaign, file_path)
#             else:
#                 raise ValueError("Unsupported file type: " + mime_type)
#         else:
#             # Fallback to text processing if MIME type cannot be determined.
#             score = self.verify_text_document(campaign, file_path)
#         return score

#     def encode_image(self, image_path: str) -> str:
#         """
#         Encodes an image file to a Base64 string.
#         """
#         with open(image_path, "rb") as image_file:
#             return base64.b64encode(image_file.read()).decode("utf-8")

#     def verify_image(self, campaign, file_path: str) -> float:
#         """
#         Process an image file by encoding it and sending it along with the campaign description
#         to OpenAI's Chat Completion API for similarity scoring.
#         """
#         # Encode the image
#         base64_image = self.encode_image(file_path)
        
#         # Build the multimodal message payload.
#         messages = [
#             {
#                 "role": "user",
#                 "content": [
#                     {
#                         "type": "text",
#                         "text": (
#                             "Compare the following image with the campaign description and provide a similarity score between 0 and 100. "
#                             f"Campaign Description: {campaign.description}"
#                         ),
#                     },
#                     {
#                         "type": "image_url",
#                         "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"},
#                     },
#                 ],
#             }
#         ]

#         # Call the OpenAI Chat Completion API.
#         response = openai.ChatCompletion.create(
#             model="gpt-4o-mini",  # Adjust this model name as needed.
#             messages=messages,
#         )
#         try:
#             # Expect the response content to be a numeric score.
#             response_content = response.choices[0].message['content']
#             score = float(response_content.strip())
#         except Exception as e:
#             score = 0.0  # Default to 0.0 if parsing fails.
#         return score

#     def verify_text_document(self, campaign, file_path: str) -> float:
#         """
#         Extract text from a document (plain text, PDF, or CSV) and uses LangChain with an LLM
#         to compute a similarity score comparing it with the campaign description.
#         """
#         content = ""
#         if file_path.endswith('.pdf'):
#             with open(file_path, "rb") as pdf_file:
#                 reader = PyPDF2.PdfReader(pdf_file)
#                 for page in reader.pages:
#                     text = page.extract_text()
#                     if text:
#                         content += text + "\n"
#         elif file_path.endswith('.csv'):
#             df = pd.read_csv(file_path)
#             content = df.to_string(index=False)
#         else:
#             with open(file_path, "r", encoding="utf-8") as f:
#                 content = f.read()
        
#         result = self.llm_chain.run(description=campaign.description, content=content)
#         try:
#             score = float(result.strip())
#         except ValueError:
#             score = 0.0  # Default score if parsing fails.
#         return score