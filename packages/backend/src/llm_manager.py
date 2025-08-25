import google.generativeai as genai
from config import GEMINI_API_KEY, GEMINI_MODEL_NAME, IDC_CONTACT_EMAIL
from langchain.memory import ConversationBufferMemory
from langchain_core.messages import HumanMessage, AIMessage
from typing import List, Optional

class LLMManager:
    """
    Manages Google Gemini LLM for generating chatbot responses.
    Handles conversation memory and response generation with RAG context.
    """
    
    def __init__(self):
        """Initialize Gemini model and conversation memory."""
        self.model = None
        self.memory = None
        self._initialize_gemini()

    def _initialize_gemini(self):
        """Initialize Google Gemini API and conversation memory."""
        # Validate API key
        if not GEMINI_API_KEY or GEMINI_API_KEY == "YOUR_GEMINI_API_KEY":
            print("Gemini API Key not configured. Please set GEMINI_API_KEY in config.py")
            return

        try:
            # Configure Gemini API
            genai.configure(api_key=GEMINI_API_KEY)
            self.model = genai.GenerativeModel(GEMINI_MODEL_NAME)
            print(f"Loaded Gemini model: {GEMINI_MODEL_NAME}")

            # Initialize conversation memory
            self.memory = ConversationBufferMemory(return_messages=True)
            print("ConversationBufferMemory initialized.")

        except Exception as e:
            print(f"Error initializing Gemini: {e}")
            self.model = None
            self.memory = None

    def _handle_common_queries(self, query: str) -> Optional[str]:
        """Handle common predefined queries with direct responses."""
        lower_query = query.lower()
        
        # Contact information queries
        contact_phrases = [
            "how can i contact idc", "how to contact idc", "how do i contact idc",
            "idc contact", "contact information", "idc phone", "idc email"
        ]
        if any(phrase in lower_query for phrase in contact_phrases):
            return f"You can contact IDC Technologies in several ways:\n\n• Email: {IDC_CONTACT_EMAIL}\n• Visit our 'Contact Us' page on the website\n\nOur team will be happy to assist you with your inquiries!"
        
        # Company overview queries
        if any(phrase in lower_query for phrase in ["who are you", "what do you do", "about idc"]):
            return "IDC Technologies is a global leader in IT staffing and workforce solutions, delivering talent across multiple industries with permanent, temporary, and temporary-to-permanent employment opportunities."
        
        return None

    def generate_response(self, query: str, context: List[str]) -> str:
        """
        Generate a response using Gemini LLM with RAG context and conversation memory.
        
        Args:
            query: User's question
            context: List of relevant document contexts
            
        Returns:
            Generated response from Gemini
        """
        # Check if components are properly initialized
        if not self.model or not self.memory:
            return "I'm sorry, the chatbot system is not fully initialized. Please try again later."
        
        # Handle common queries with predefined responses
        common_response = self._handle_common_queries(query)
        if common_response:
            self.memory.save_context({"input": query}, {"output": common_response})
            return common_response
        
        # Prepare context text for LLM
        if not context:
            fallback_response = f"I don't have enough information in my knowledge base to answer that question. Please try asking about IDC's services, global presence, or employment opportunities.\n\nFor more detailed assistance, you can contact IDC directly at {IDC_CONTACT_EMAIL}."
            self.memory.save_context({"input": query}, {"output": fallback_response})
            return fallback_response
        
        try:
            # Get conversation history
            chat_history_messages = self.memory.load_memory_variables({})["history"]
            
            # Convert LangChain messages to Gemini format
            gemini_chat_history = []
            for msg in chat_history_messages:
                if isinstance(msg, HumanMessage):
                    gemini_chat_history.append({"role": "user", "parts": [{"text": msg.content}]})
                elif isinstance(msg, AIMessage):
                    gemini_chat_history.append({"role": "model", "parts": [{"text": msg.content}]})
            
            # System instruction for the chatbot
            system_instruction = (
                "You are a helpful and professional assistant for IDC Technologies. "
                "Answer questions based ONLY on the provided context. "
                "Provide comprehensive answers (aim for 75+ words when context allows). "
                "Always mention the sources of your information. "
                f"If the answer is not in the context, politely state you don't have that information and suggest contacting IDC directly at {IDC_CONTACT_EMAIL} for more detailed assistance. "
                "Be friendly, polite, and professional in your responses."
            )
            
            # Build the conversation payload for Gemini
            contents_payload = [{"role": "user", "parts": [{"text": system_instruction}]}]
            contents_payload.extend(gemini_chat_history)
            
            # Add current query with context
            current_prompt = (
                f"Context Information:\n" + 
                "\n---\n".join(context) + 
                f"\n\nUser Question: {query}\n\n" +
                "Please provide a helpful, comprehensive answer based on the context above:"
            )
            contents_payload.append({"role": "user", "parts": [{"text": current_prompt}]})
            
            # Generate response from Gemini
            print("Generating response with Gemini...")
            response = self.model.generate_content(contents_payload)
            
            # Extract response text
            bot_response = ""
            if response.candidates and response.candidates[0].content.parts:
                bot_response = response.candidates[0].content.parts[0].text
            else:
                bot_response = f"I apologize, but I couldn't generate a clear answer based on the available information. For more detailed assistance, please contact IDC directly at {IDC_CONTACT_EMAIL}."
            
            print("Response generated successfully.")
            
        except Exception as e:
            print(f"Error generating Gemini response: {e}")
            bot_response = f"I'm sorry, I encountered a technical issue while processing your question. Please try again or contact IDC directly at {IDC_CONTACT_EMAIL} for assistance."
        
        # Save conversation to memory
        self.memory.save_context({"input": query}, {"output": bot_response})
        
        return bot_response