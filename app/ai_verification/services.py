import base64
import mimetypes
import openai
from langchain_core.prompt_values import ChatPromptValue
from langchain_core.messages import SystemMessage, HumanMessage
import PyPDF2
import pandas as pd


from app.ai_verification.llm import LLMWrapper

class AIVerificationSystem:
    def __init__(self, openai_api_key: str):
        self.openai_api_key = openai_api_key
        openai.api_key = openai_api_key
        # Image verification still uses OpenAI's ChatCompletion API directly.

    def verify(self, campaign, file_path: str) -> float:
        """
        Verifies the provided file against the campaign description.
        Returns a similarity score (0–100).
        """
        mime_type, _ = mimetypes.guess_type(file_path)
        if mime_type:
            if mime_type.startswith("image"):
                score = self.verify_image(campaign, file_path)
            elif mime_type.startswith("text") or file_path.endswith('.pdf') or file_path.endswith('.csv'):
                score = self.verify_text_document(campaign, file_path)
            else:
                raise ValueError("Unsupported file type: " + mime_type)
        else:
            # Fallback to text processing if MIME type cannot be determined.
            score = self.verify_text_document(campaign, file_path)
        return score

    def encode_image(self, image_path: str) -> str:
        """
        Encodes an image file to a Base64 string.
        """
        with open(image_path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode("utf-8")

    def verify_image(self, campaign, file_path: str) -> float:
        """
        Processes an image file by encoding it and sending it along with the campaign description
        to OpenAI's Chat Completion API for similarity scoring.
        """
        # Encode the image.
        base64_image = self.encode_image(file_path)
        
        # Build the multimodal message payload.
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

        # Call the OpenAI Chat Completion API.
        response = openai.ChatCompletion.create(
            model="gpt-4o-mini",  # Adjust model name as needed.
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
        Extracts text from a document (plain text, PDF, or CSV) and uses the LLMWrapper
        (OpenAI provider) to compute a similarity score comparing it with the campaign description.
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

        # Build the prompt messages in a style similar to your outline_episode function.
        system_message = SystemMessage(
            content=(
                "You are an expert at evaluating textual similarity. "
                "Evaluate how well the following document content aligns with the given campaign description. "
                "Provide a single numeric score between 0 and 100, where 100 indicates perfect alignment."
            )
        )

        human_message = HumanMessage(
            content=(
                f"Campaign Description:\n{campaign.description}\n\n"
                f"Document Content:\n{content}\n\n"
                "Similarity Score:"
            )
        )

        prompt_value = ChatPromptValue(messages=[system_message, human_message])

        # Instantiate the LLMWrapper using the OpenAI provider (gpt-4o-mini model).
        llm_wrapper = LLMWrapper(provider="openai", model="gpt-4o-mini", temperature=0.0)

        # Invoke the LLM to obtain a similarity score.
        response_message = llm_wrapper.invoke(prompt_value)
        response_content = response_message.content.strip()

        try:
            score = float(response_content)
        except ValueError:
            score = 0.0
        return score

# Example usage:
if __name__ == "__main__":
    # A simple Campaign object; in production, use your SQLAlchemy Campaign model.
    class Campaign:
        def __init__(self, description):
            self.description = description

    campaign = Campaign(
        description="A scenic landscape featuring majestic mountains, a clear blue sky, and a tranquil lake."
    )
    
    api_key = "your-openai-api-key"
    verifier = AIVerificationSystem(openai_api_key=api_key)
    
    file_path = "path/to/your/document_or_image.jpg"  # Adjust the path accordingly.
    
    score = verifier.verify(campaign, file_path)
    print(f"Verification Score: {score}")