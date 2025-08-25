"""
Vision-Language Model (VLM) Processor for PPTX Images

This module uses Google's Gemini Vision API (already integrated) to perform advanced
image analysis, particularly for partner logo recognition and complex visual content.
"""

import io
import base64
from typing import Dict, List, Optional
from PIL import Image

# Google Gemini imports (reusing existing integration)
import google.generativeai as genai
from config import GEMINI_API_KEY, GEMINI_MODEL_NAME, PPTX_PROCESSING


class GeminiVLMProcessor:
    """
    Uses Gemini Vision API for advanced image analysis and logo recognition.
    Leverages the existing Gemini integration from llm_manager.py
    """
    
    def __init__(self):
        self.model = None
        self.config = PPTX_PROCESSING
        self._initialize_gemini_vision()
    
    def _initialize_gemini_vision(self):
        """Initialize Gemini Vision API using existing configuration."""
        try:
            if not GEMINI_API_KEY or GEMINI_API_KEY == "YOUR_GEMINI_API_KEY":
                print("Gemini API Key not configured for VLM processing")
                return
            
            genai.configure(api_key=GEMINI_API_KEY)
            self.model = genai.GenerativeModel(GEMINI_MODEL_NAME)
            print(f"Gemini VLM processor initialized with model: {GEMINI_MODEL_NAME}")
            
        except Exception as e:
            print(f"Error initializing Gemini VLM: {e}")
            self.model = None
    
    def analyze_image_for_partners(self, pil_image: Image.Image, metadata: Dict) -> Dict:
        """
        Analyze an image specifically for partner information using Gemini Vision.
        
        Args:
            pil_image: PIL Image object
            metadata: Image metadata including slide context
            
        Returns:
            Dictionary with partner analysis results
        """
        if not self.model:
            return self._create_error_result("Gemini VLM not initialized", metadata)
        
        try:
            # Prepare the prompt for partner detection
            partner_prompt = self._create_partner_analysis_prompt(metadata)
            
            # Convert PIL image to format suitable for Gemini
            image_data = self._pil_to_gemini_format(pil_image)
            
            # Generate analysis
            response = self.model.generate_content([partner_prompt, image_data])
            
            # Parse response
            return self._parse_partner_response(response, metadata)
            
        except Exception as e:
            print(f"Error in Gemini VLM partner analysis: {e}")
            return self._create_error_result(str(e), metadata)
    
    def analyze_image_for_text(self, pil_image: Image.Image, metadata: Dict) -> Dict:
        """
        Analyze an image for text content using Gemini Vision.
        
        Args:
            pil_image: PIL Image object
            metadata: Image metadata
            
        Returns:
            Dictionary with text analysis results
        """
        if not self.model:
            return self._create_error_result("Gemini VLM not initialized", metadata)
        
        try:
            # Prepare text extraction prompt
            text_prompt = self._create_text_extraction_prompt(metadata)
            
            # Convert PIL image to Gemini format
            image_data = self._pil_to_gemini_format(pil_image)
            
            # Generate analysis
            response = self.model.generate_content([text_prompt, image_data])
            
            # Parse response
            return self._parse_text_response(response, metadata)
            
        except Exception as e:
            print(f"Error in Gemini VLM text analysis: {e}")
            return self._create_error_result(str(e), metadata)
    
    def _create_partner_analysis_prompt(self, metadata: Dict) -> str:
        """Create a specialized prompt for partner logo recognition."""
        slide_context = f"slide {metadata.get('slide_number', 'unknown')}"
        
        return f"""
You are analyzing an image from {slide_context} of an IDC Technologies presentation. 
Your task is to identify partner companies, logos, or business relationships shown in this image.

Please analyze this image and provide:
1. Company names or logos visible in the image
2. Any partnership-related text or indicators
3. Technology company logos or brand names
4. Business relationship indicators

Focus specifically on:
- Technology company logos (like Microsoft, AWS, Google, Oracle, Salesforce, etc.)
- Consulting firm partnerships
- Software vendor relationships
- Any text mentioning partnerships, alliances, or collaborations

Return your findings in this JSON format:
{
    "partners_found": [
        {"name": "CompanyName", "type": "logo/text", "confidence": "high/medium/low"},
        ...
    ],
    "partnership_text": "any partnership-related text found",
    "image_type": "logos/partnership_slide/other",
    "confidence_overall": "high/medium/low"
}

If no partner information is found, return empty partners_found array.
"""
    
    def _create_text_extraction_prompt(self, metadata: Dict) -> str:
        """Create a prompt for general text extraction."""
        slide_context = f"slide {metadata.get('slide_number', 'unknown')}"
        
        return f"""
Extract all visible text from this image from {slide_context} of an IDC Technologies presentation.

Please provide:
1. All readable text in the image
2. Any company names, product names, or technical terms
3. Headers, titles, or important labels
4. Any text that might be partially visible or stylized

Return the extracted text in clean, readable format. If no text is visible, return "No readable text found."
"""
    
    def _pil_to_gemini_format(self, pil_image: Image.Image):
        """Convert PIL Image to format suitable for Gemini API."""
        # Convert to RGB if needed
        if pil_image.mode != 'RGB':
            pil_image = pil_image.convert('RGB')
        
        # Convert to bytes
        img_byte_arr = io.BytesIO()
        pil_image.save(img_byte_arr, format='PNG')
        img_byte_arr = img_byte_arr.getvalue()
        
        return {
            "mime_type": "image/png",
            "data": img_byte_arr
        }
    
    def _parse_partner_response(self, response, metadata: Dict) -> Dict:
        """Parse Gemini response for partner information."""
        try:
            response_text = response.text if hasattr(response, 'text') else str(response)
            
            # Try to extract JSON if present
            partners_info = self._extract_partner_info_from_text(response_text)
            
            return {
                'extracted_partners': partners_info.get('partners_found', []),
                'partnership_text': partners_info.get('partnership_text', ''),
                'image_type': partners_info.get('image_type', 'unknown'),
                'confidence': partners_info.get('confidence_overall', 'medium'),
                'raw_response': response_text,
                'method': 'gemini_vlm',
                'metadata': metadata
            }
            
        except Exception as e:
            return self._create_error_result(f"Response parsing error: {e}", metadata)
    
    def _parse_text_response(self, response, metadata: Dict) -> Dict:
        """Parse Gemini response for text extraction."""
        try:
            extracted_text = response.text if hasattr(response, 'text') else str(response)
            
            return {
                'extracted_text': extracted_text.strip(),
                'method': 'gemini_vlm',
                'confidence': 'high',  # VLM generally has high confidence
                'metadata': metadata
            }
            
        except Exception as e:
            return self._create_error_result(f"Text parsing error: {e}", metadata)
    
    def _extract_partner_info_from_text(self, response_text: str) -> Dict:
        """Extract structured partner information from VLM response."""
        import json
        import re
        
        # Try to find JSON in the response
        json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
        if json_match:
            try:
                return json.loads(json_match.group())
            except json.JSONDecodeError:
                pass
        
        # Fallback: parse text manually for partner names
        partners_found = []
        
        # Common partner indicators
        partner_keywords = [
            'microsoft', 'aws', 'amazon', 'google', 'oracle', 'salesforce',
            'ibm', 'azure', 'snowflake', 'redington', 'wipro', 'infosys',
            'accenture', 'dell', 'hp', 'cisco', 'vmware', 'meta', 'facebook'
        ]
        
        response_lower = response_text.lower()
        for keyword in partner_keywords:
            if keyword in response_lower:
                partners_found.append({
                    'name': keyword.title(),
                    'type': 'text_detection',
                    'confidence': 'medium'
                })
        
        return {
            'partners_found': partners_found,
            'partnership_text': response_text,
            'image_type': 'text_analysis',
            'confidence_overall': 'medium' if partners_found else 'low'
        }
    
    def _create_error_result(self, error_msg: str, metadata: Dict) -> Dict:
        """Create standardized error result."""
        return {
            'extracted_partners': [],
            'partnership_text': '',
            'error': error_msg,
            'method': 'gemini_vlm',
            'metadata': metadata
        }


class HybridVLMProcessor:
    """
    Combines OCR and VLM processing for optimal results.
    Uses OCR for clear text and VLM for logos and complex visuals.
    """
    
    def __init__(self):
        self.vlm_processor = GeminiVLMProcessor()
        print("Hybrid VLM Processor initialized")
    
    def process_image_for_partners(self, pil_image: Image.Image, metadata: Dict, 
                                 ocr_result: Optional[Dict] = None) -> Dict:
        """
        Process an image using both OCR and VLM approaches for partner detection.
        
        Args:
            pil_image: PIL Image object
            metadata: Image metadata
            ocr_result: Optional OCR result to combine with VLM
            
        Returns:
            Combined analysis result
        """
        # Get VLM analysis
        vlm_result = self.vlm_processor.analyze_image_for_partners(pil_image, metadata)
        
        # Combine with OCR if available
        if ocr_result and ocr_result.get('extracted_text'):
            combined_result = self._combine_ocr_vlm_results(ocr_result, vlm_result)
        else:
            combined_result = vlm_result
        
        return combined_result
    
    def _combine_ocr_vlm_results(self, ocr_result: Dict, vlm_result: Dict) -> Dict:
        """Combine OCR and VLM results for comprehensive analysis."""
        # Get partners from both sources
        ocr_partners = self._extract_partners_from_ocr_text(ocr_result.get('extracted_text', ''))
        vlm_partners = vlm_result.get('extracted_partners', [])
        
        # Combine and deduplicate partners
        all_partners = []
        partner_names = set()
        
        for partner in vlm_partners + ocr_partners:
            name_lower = partner['name'].lower()
            if name_lower not in partner_names:
                all_partners.append(partner)
                partner_names.add(name_lower)
        
        # Create combined result
        return {
            'extracted_partners': all_partners,
            'partnership_text': f"OCR: {ocr_result.get('extracted_text', '')} | VLM: {vlm_result.get('partnership_text', '')}",
            'confidence': self._calculate_combined_confidence(ocr_result, vlm_result),
            'method': 'hybrid_ocr_vlm',
            'ocr_confidence': ocr_result.get('confidence', 0),
            'vlm_confidence': vlm_result.get('confidence', 'medium'),
            'metadata': vlm_result.get('metadata', {})
        }
    
    def _extract_partners_from_ocr_text(self, ocr_text: str) -> List[Dict]:
        """Extract partner names from OCR text."""
        partners = []
        
        # Common partner keywords in OCR text
        partner_keywords = [
            'microsoft', 'aws', 'amazon', 'google', 'oracle', 'salesforce',
            'ibm', 'azure', 'snowflake', 'redington', 'wipro', 'infosys'
        ]
        
        ocr_text_lower = ocr_text.lower()
        for keyword in partner_keywords:
            if keyword in ocr_text_lower:
                partners.append({
                    'name': keyword.title(),
                    'type': 'ocr_text',
                    'confidence': 'high'
                })
        
        return partners
    
    def _calculate_combined_confidence(self, ocr_result: Dict, vlm_result: Dict) -> str:
        """Calculate overall confidence from combined results."""
        ocr_conf = ocr_result.get('confidence', 0)
        vlm_conf = vlm_result.get('confidence', 'medium')
        
        # Convert VLM confidence to numeric
        vlm_conf_num = {'high': 90, 'medium': 70, 'low': 50}.get(vlm_conf, 70)
        
        # Calculate average confidence
        avg_conf = (ocr_conf + vlm_conf_num) / 2
        
        if avg_conf >= 80:
            return 'high'
        elif avg_conf >= 60:
            return 'medium'
        else:
            return 'low'


# Utility function for integration
def analyze_pptx_image_with_vlm(pil_image: Image.Image, metadata: Dict) -> Dict:
    """
    Analyze a PPTX image using VLM processing for partner detection.
    
    Args:
        pil_image: PIL Image object
        metadata: Image metadata
        
    Returns:
        VLM analysis result
    """
    processor = HybridVLMProcessor()
    return processor.process_image_for_partners(pil_image, metadata)


if __name__ == "__main__":
    # Test the VLM processor
    print("VLM Processor ready for integration")
    
    # Initialize to test configuration
    vlm = GeminiVLMProcessor()
    if vlm.model:
        print("Gemini VLM initialized successfully")
    else:
        print("Gemini VLM initialization failed - check API key")