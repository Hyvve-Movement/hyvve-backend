import base64
import mimetypes
import openai
import logging
from langchain_core.prompt_values import ChatPromptValue
from langchain_core.messages import SystemMessage, HumanMessage
import PyPDF2
import pandas as pd
from pydantic import BaseModel
from langchain_core.prompts import ChatPromptTemplate
from docx import Document
import os
import subprocess

from app.campaigns.models import Campaign
from app.ai_verification.llm import get_long_context_llm


class SimilarityScore(BaseModel):
    score: float


class AIVerificationSystem:
    def __init__(self, openai_api_key: str):
        self.openai_api_key = openai_api_key
        openai.api_key = openai_api_key
        
        # Set up logging
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.INFO)
        
        # Create a console handler and set level to debug
        ch = logging.StreamHandler()
        ch.setLevel(logging.INFO)
        
        # Create a formatter and add it to the handler
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        ch.setFormatter(formatter)
        
        # Add the handler to the logger
        self.logger.addHandler(ch)

    def verify(self, campaign, file_path: str) -> float:
        """
        Verify the provided file against the campaign description.
        Supports image, text, PDF, CSV, .doc, and .docx files.
        Returns a similarity score between 0 and 100.
        """
        mime_type, _ = mimetypes.guess_type(file_path)
        self.logger.info(f"Verifying file: {file_path} with MIME type: {mime_type}")

        try:
            if mime_type:
                if mime_type.startswith("image"):
                    self.logger.info("Processing image file for verification.")
                    return self.verify_image(campaign, file_path)
                elif mime_type.startswith("text") or file_path.endswith(('.pdf', '.csv', '.txt', '.doc', '.docx')):
                    self.logger.info("Processing text-based document for verification.")
                    return self.verify_text_document(campaign, file_path)
                else:
                    raise ValueError("Unsupported file type: " + mime_type)
            else:
                self.logger.warning("MIME type not detected. Falling back to text document verification.")
                return self.verify_text_document(campaign, file_path)
        except Exception as e:
            self.logger.error(f"Error during verification process: {e}")
            raise

    def encode_image(self, image_path: str) -> str:
        """
        Encodes an image file to a Base64 string.
        """
        self.logger.info(f"Encoding image: {image_path}")
        with open(image_path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode("utf-8")

    def verify_image(self, campaign, file_path: str) -> float:
        """
        Process an image by encoding it and sending a multimodal prompt
        to OpenAI's Chat Completion API to obtain a similarity score.
        """
        self.logger.info(f"Verifying image file: {file_path}")
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
        try:
            response = openai.ChatCompletion.create(
                model="gpt-4o-mini",  # Adjust model name if necessary.
                messages=messages,
            )
            response_content = response.choices[0].message['content']
            score = float(response_content.strip())
            self.logger.info(f"Image verification score: {score}")
            return score
        except Exception as e:
            self.logger.error(f"Error during image verification: {e}")
            return 0.0

    def verify_text_document(self, campaign, file_path: str) -> float:
        """
        Extracts text from a document (text, PDF, CSV, DOC, DOCX) and generates a similarity score.
        """
        self.logger.info(f"Verifying text document: {file_path}")
        content = ""

        # Handling PDF files
        if file_path.endswith('.pdf'):
            with open(file_path, "rb") as pdf_file:
                reader = PyPDF2.PdfReader(pdf_file)
                for page in reader.pages:
                    text = page.extract_text()
                    if text:
                        content += text + "\n"

        # Handling CSV files
        elif file_path.endswith('.csv'):
            df = pd.read_csv(file_path)
            content = df.to_string(index=False)

        # Handling Text files
        elif file_path.endswith('.txt'):
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()

        # Handling .docx files (Word documents)
        elif file_path.endswith('.docx'):
            doc = Document(file_path)
            content = "\n".join([para.text for para in doc.paragraphs])

        # Handling .doc files (older Word documents, usually requires conversion)
        elif file_path.endswith('.doc'):
            content = self.extract_text_from_doc(file_path)

        else:
            raise ValueError("Unsupported document format")

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

        self.logger.info(f"Document verification score: {result.score}")
        return result.score

    def extract_text_from_doc(self, file_path: str) -> str:
        """
        Extracts text from a .doc file using antiword (or similar method).
        You may want to replace this method with a more robust implementation based on your environment.
        """
        self.logger.info(f"Extracting text from .doc file: {file_path}")
        try:
            result = subprocess.run(
                ['antiword', file_path], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
            )
            if result.returncode == 0:
                return result.stdout
            else:
                raise Exception(f"Error reading .doc file: {result.stderr}")
        except Exception as e:
            self.logger.error(f"Failed to extract text from .doc file: {str(e)}")
            raise ValueError(f"Failed to extract text from .doc file: {str(e)}")
