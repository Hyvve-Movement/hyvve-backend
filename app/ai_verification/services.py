import base64
import mimetypes
import openai
from langchain_core.prompt_values import ChatPromptValue
from langchain_core.messages import SystemMessage, HumanMessage
import PyPDF2
import pandas as pd
from pydantic import BaseModel
from langchain_core.prompts import ChatPromptTemplate

from app.campaigns.models import Campaign
from app.ai_verification.llm import get_long_context_llm



class SimilarityScore(BaseModel):
    score: float

class AIVerificationSystem:
    def __init__(self, openai_api_key: str):
        self.openai_api_key = openai_api_key
        openai.api_key = openai_api_key

    def verify(self, campaign, file_path: str) -> float:
        """
        Verify the provided file against the campaign description.
        Supports image, text, PDF, and CSV files.
        Returns a similarity score between 0 and 100.
        """
        mime_type, _ = mimetypes.guess_type(file_path)
        if mime_type:
            if mime_type.startswith("image"):
                return self.verify_image(campaign, file_path)
            elif mime_type.startswith("text") or file_path.endswith('.pdf') or file_path.endswith('.csv'):
                return self.verify_text_document(campaign, file_path)
            else:
                raise ValueError("Unsupported file type: " + mime_type)
        else:
            # Fallback to text processing if MIME type cannot be determined.
            return self.verify_text_document(campaign, file_path)

    def encode_image(self, image_path: str) -> str:
        """
        Encodes an image file to a Base64 string.
        """
        with open(image_path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode("utf-8")

    def verify_image(self, campaign, file_path: str) -> float:
        """
        Process an image by encoding it and sending a multimodal prompt
        to OpenAI's Chat Completion API to obtain a similarity score.
        """
        base64_image = self.encode_image(file_path)
        messages = [
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": (
                            "Compare the following image with the campaign description and provide a similarity score between 0 and 100. "
                            f"Campaign Description: {campaign.description}"
                        ),
                    },
                    {
                        "type": "image_url",
                        "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"},
                    },
                ],
            }
        ]
        response = openai.ChatCompletion.create(
            model="gpt-4o-mini",  # Adjust model name if necessary.
            messages=messages,
        )
        try:
            response_content = response.choices[0].message['content']
            score = float(response_content.strip())
        except Exception:
            score = 0.0
        return score

    def verify_text_document(self, campaign, file_path: str) -> float:
        """
        Extracts text from a plain text file, PDF, or CSV file and uses an LLM-based prompt,
        following the same format as our podcast outline prompt, to generate a similarity score.
        """
        # Extract content based on file type.
        content = ""
        if file_path.endswith('.pdf'):
            with open(file_path, "rb") as pdf_file:
                reader = PyPDF2.PdfReader(pdf_file)
                for page in reader.pages:
                    text = page.extract_text()
                    if text:
                        content += text + "\n"
        elif file_path.endswith('.csv'):
            df = pd.read_csv(file_path)
            content = df.to_string(index=False)
        else:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()

        # Build a prompt using a format similar to the podcast outline prompt.
        prompt = ChatPromptTemplate.from_messages(
            [
                (
                    "system",
                    (
                        "IDENTITY:\n"
                        "You are an expert evaluator tasked with determining how well a document aligns with a campaign description. "
                        "Evaluate the provided document content against the campaign description and return a single numeric similarity score between 0 and 100. "
                        "A score of 100 indicates perfect alignment, and 0 indicates no alignment."
                    )
                ),
                (
                    "human",
                    (
                        "Campaign Description:\n{campaign_description}\n\n"
                        "Document Content:\n{document_content}\n\n"
                        "Similarity Score:"
                    )
                ),
            ]
        )

        # Retrieve an LLM instance configured for long context using our project utility.
        llm = get_long_context_llm()
        # Chain the prompt with the LLM, specifying structured output.
        chain = prompt | llm.with_structured_output(SimilarityScore)
        result = chain.invoke({
            "campaign_description": campaign.description,
            "document_content": content,
        })
        return result.score