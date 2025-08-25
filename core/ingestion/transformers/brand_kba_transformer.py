"""
Brand KBA transformer for creating brand knowledge base files using real AI.
"""

import logging
from typing import Dict, Any, List
from .base import BaseTransformer, TransformedContent
from .factory import register_transformer

# Real AI integration imports
import asyncio
import re
from collections import Counter
from core.infrastructure.factories.provider_factory import LLMProviderFactory, ProviderManager
from core.domain.value_objects.provider_config import LLMProvider
from core.infrastructure.config.settings import get_settings

logger = logging.getLogger(__name__)


@register_transformer('brand_kba_4docs')
class BrandKBATransformer(BaseTransformer):
    """
    Transformer for brand_kba_4docs workflow mode using real AI.

    Creates 4 structured files:
    1. company_profile_brand_voice.md - Company profile and brand voice
    2. production_guide.md - Content production guidelines
    3. quality_standards.md - Quality standards and compliance
    4. voice_examples.md - Voice examples and cultural context
    """

    def __init__(self, workflow_mode: str = 'brand_kba_4docs'):
        super().__init__(workflow_mode)
        self.settings = get_settings()
        self.provider_manager = ProviderManager(self.settings)
        self.total_tokens_used = 0
        self.total_cost = 0.0

    def can_transform(self, workflow_mode: str) -> bool:
        """Check if this transformer can handle the workflow mode."""
        return workflow_mode == 'brand_kba_4docs'
    
    async def transform(self,
                       parsed_contents: List['ParsedContent'],
                       context: Dict[str, Any]) -> TransformedContent:
        """
        Transform parsed content into brand KBA files using real AI.

        Args:
            parsed_contents: List of ParsedContent objects
            context: Workflow context

        Returns:
            TransformedContent with 4 brand KBA files
        """
        self.logger.info(f"🎨 Starting REAL AI brand KBA transformation for {len(parsed_contents)} sources")

        try:
            # Real content analysis using AI
            self.logger.info("🤖 Starting AI-powered content analysis...")

            # Merge all content and analyze
            merged_content = self._merge_content(parsed_contents)
            content_analysis = await self._ai_analyze_content(merged_content, parsed_contents, context)

            self.logger.info(f"📊 AI content analysis complete: {content_analysis['summary']}")

            # Create the 4 required files with real AI generation
            files = {}

            # 1. Company Profile & Brand Voice
            self.logger.info("🤖 AI generating company profile & brand voice...")
            files['company_profile_brand_voice.md'] = await self._ai_create_company_profile(
                merged_content, parsed_contents, context, content_analysis
            )

            # 2. Production Guide
            self.logger.info("🤖 AI generating production guide...")
            files['production_guide.md'] = await self._ai_create_production_guide(
                merged_content, parsed_contents, context, content_analysis
            )

            # 3. Quality Standards
            self.logger.info("🤖 AI generating quality standards...")
            files['quality_standards.md'] = await self._ai_create_quality_standards(
                merged_content, parsed_contents, context, content_analysis
            )

            # 4. Voice Examples
            self.logger.info("🤖 AI generating voice examples...")
            files['voice_examples.md'] = await self._ai_create_voice_examples(
                merged_content, parsed_contents, context, content_analysis
            )

            # Create metadata with AI usage stats
            metadata = self._create_metadata(parsed_contents, context)
            metadata['transformer'] = 'brand_kba_4docs'
            metadata['output_files'] = list(files.keys())
            metadata['ai_tokens_used'] = self.total_tokens_used
            metadata['ai_cost'] = self.total_cost
            metadata['ai_provider'] = context.get('model_provider', 'openai')
            metadata['ai_model'] = context.get('model_name', 'gpt-4o')

            # Generate summary
            summary = self._generate_summary(files)

            transformed_content = TransformedContent(
                files=files,
                metadata=metadata,
                summary=summary
            )

            self.logger.info(f"✅ AI Brand KBA transformation completed: {transformed_content.get_summary()}")
            self.logger.info(f"💰 AI Usage: {self.total_tokens_used} tokens, ${self.total_cost:.4f}")
            return transformed_content

        except Exception as e:
            self.logger.error(f"❌ AI Brand KBA transformation failed: {str(e)}")
            raise ValueError(f"Failed to transform content for brand KBA: {str(e)}")
    
    async def _get_ai_provider(self, context: Dict[str, Any]):
        """Get AI provider based on context settings."""
        provider_name = context.get('model_provider', 'openai').lower()

        if provider_name == 'openai':
            provider_type = LLMProvider.OPENAI
        elif provider_name == 'anthropic':
            provider_type = LLMProvider.ANTHROPIC
        elif provider_name == 'deepseek':
            provider_type = LLMProvider.DEEPSEEK
        elif provider_name == 'gemini':
            provider_type = LLMProvider.GEMINI
        else:
            provider_type = LLMProvider.OPENAI  # Default fallback

        provider = self.provider_manager.get_provider(provider_type)
        config = LLMProviderFactory.create_provider_config(
            provider_type=provider_type,
            settings=self.settings,
            model=context.get('model_name', 'gpt-4o')
        )

        return provider, config

    async def _ai_generate_content(self, prompt: str, system_message: str, context: Dict[str, Any]) -> str:
        """Generate content using AI with cost tracking."""
        try:
            provider, config = await self._get_ai_provider(context)

            self.logger.debug(f"🤖 Making AI request to {config.provider.value} with model {config.model}")

            # Generate content with detailed response for cost tracking
            response = await provider.generate_content_detailed(
                prompt=prompt,
                config=config,
                system_message=system_message
            )

            # Track usage
            tokens_used = response.usage.get('total_tokens', 0)
            self.total_tokens_used += tokens_used

            # Estimate cost (rough calculation)
            cost_per_token = 0.00003  # Approximate for GPT-4
            cost = tokens_used * cost_per_token
            self.total_cost += cost

            self.logger.debug(f"💰 AI request: {tokens_used} tokens, ${cost:.4f}")

            return response.content

        except Exception as e:
            self.logger.error(f"❌ AI generation failed: {str(e)}")
            raise
    
    async def _ai_analyze_content(self, merged_content: str, parsed_contents: List['ParsedContent'], context: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze content using AI to extract key information."""

        system_message = """You are an expert content analyst specializing in brand analysis and knowledge extraction.
        Analyze the provided content and extract key information about the company, brand, processes, and quality standards.
        Return your analysis in a structured JSON format."""

        prompt = f"""
        Please analyze the following content from {len(parsed_contents)} source documents and extract:

        1. Company Information:
           - Mission and vision statements
           - Core values
           - Target audience
           - Business focus areas

        2. Brand Elements:
           - Brand voice and tone characteristics
           - Brand personality traits
           - Communication style
           - Key messaging themes

        3. Process Information:
           - Workflow steps and procedures
           - Guidelines and best practices
           - Tools and resources mentioned
           - Quality control processes

        4. Key Themes:
           - Main topics and focus areas
           - Industry-specific elements
           - Cultural aspects
           - Innovation areas

        Content to analyze:
        {merged_content[:8000]}  # Limit content to avoid token limits

        Please provide a comprehensive analysis in JSON format with the above categories.
        """

        try:
            analysis_result = await self._ai_generate_content(prompt, system_message, context)

            # Try to parse JSON, fallback to basic analysis if parsing fails
            try:
                import json
                analysis_data = json.loads(analysis_result)
            except:
                # Fallback to basic analysis
                analysis_data = self._basic_content_analysis(merged_content, parsed_contents)

            # Add summary
            analysis_data['summary'] = f"{len(parsed_contents)} sources, {len(merged_content.split())} words, AI-analyzed"

            return analysis_data

        except Exception as e:
            self.logger.warning(f"⚠️ AI analysis failed, using basic analysis: {str(e)}")
            return self._basic_content_analysis(merged_content, parsed_contents)
    
    async def _ai_create_company_profile(self, merged_content: str, parsed_contents: List['ParsedContent'],
                                        context: Dict[str, Any], content_analysis: Dict[str, Any]) -> str:
        """Create company profile using AI."""

        client = context.get('client', 'Company')
        custom_instructions = context.get('custom_instructions', '')

        system_message = f"""You are an expert brand strategist creating a comprehensive company profile and brand voice document for {client}.
        Create a professional, well-structured markdown document that captures the essence of the company's brand identity."""

        prompt = f"""
        Create a comprehensive Company Profile & Brand Voice document for {client} based on the following analysis and source content.

        CONTENT ANALYSIS:
        {content_analysis}

        CUSTOM INSTRUCTIONS:
        {custom_instructions}

        SOURCE CONTENT (first 6000 chars):
        {merged_content[:6000]}

        Please create a markdown document with the following structure:
        # {client} - Company Profile & Brand Voice

        ## Company Overview
        - Mission and vision
        - Core business focus
        - Key differentiators

        ## Brand Voice & Tone
        - Voice characteristics
        - Tone guidelines
        - Communication style

        ## Core Values & Mission
        - Fundamental values
        - Mission statement
        - Vision for the future

        ## Target Audience
        - Primary audience segments
        - Customer personas
        - Market positioning

        ## Brand Personality
        - Personality traits
        - Brand character
        - Emotional connection

        ## Communication Guidelines
        - Key messaging principles
        - Do's and don'ts
        - Brand consistency rules

        Make it comprehensive, professional, and actionable. Use specific examples from the source content where possible.
        """

        return await self._ai_generate_content(prompt, system_message, context)
    
    async def _ai_create_production_guide(self, merged_content: str, parsed_contents: List['ParsedContent'],
                                          context: Dict[str, Any], content_analysis: Dict[str, Any]) -> str:
        """Create production guide using AI."""

        client = context.get('client', 'Company')
        custom_instructions = context.get('custom_instructions', '')

        system_message = f"""You are an expert content strategist creating a comprehensive content production guide for {client}.
        Focus on practical, actionable guidelines that content creators can follow."""

        prompt = f"""
        Create a comprehensive Content Production Guide for {client} based on the analysis and source content.

        CONTENT ANALYSIS:
        {content_analysis}

        CUSTOM INSTRUCTIONS:
        {custom_instructions}

        SOURCE CONTENT (first 6000 chars):
        {merged_content[:6000]}

        Create a markdown document with this structure:
        # {client} - Content Production Guide

        ## Content Strategy
        - Strategic approach to content
        - Content objectives and goals
        - Alignment with business objectives

        ## Content Types & Formats
        - Preferred content formats
        - Channel-specific guidelines
        - Content hierarchy and structure

        ## Production Workflow
        - Step-by-step production process
        - Roles and responsibilities
        - Timeline and milestones

        ## Style Guidelines
        - Writing style requirements
        - Formatting standards
        - Visual and design guidelines

        ## Content Calendar & Planning
        - Planning methodology
        - Content scheduling approach
        - Review and approval process

        ## Tools & Resources
        - Recommended tools and platforms
        - Templates and resources
        - Training and support materials

        Make it practical and actionable for content creators.
        """

        return await self._ai_generate_content(prompt, system_message, context)
    
    async def _ai_create_quality_standards(self, merged_content: str, parsed_contents: List['ParsedContent'],
                                           context: Dict[str, Any], content_analysis: Dict[str, Any]) -> str:
        """Create quality standards using AI."""

        client = context.get('client', 'Company')
        custom_instructions = context.get('custom_instructions', '')

        system_message = f"""You are an expert quality assurance specialist creating comprehensive quality standards for {client}.
        Focus on measurable, enforceable standards that ensure consistent quality."""

        prompt = f"""
        Create comprehensive Quality Standards & Compliance document for {client} based on the analysis and source content.

        CONTENT ANALYSIS:
        {content_analysis}

        CUSTOM INSTRUCTIONS:
        {custom_instructions}

        SOURCE CONTENT (first 6000 chars):
        {merged_content[:6000]}

        Create a markdown document with this structure:
        # {client} - Quality Standards & Compliance

        ## Quality Criteria
        - Specific quality metrics
        - Measurable standards
        - Acceptance criteria

        ## Review Process
        - Review workflow and stages
        - Reviewer roles and responsibilities
        - Quality checkpoints

        ## Compliance Requirements
        - Regulatory compliance needs
        - Industry standards
        - Legal requirements

        ## Brand Consistency
        - Brand alignment requirements
        - Consistency checkpoints
        - Brand compliance metrics

        ## Performance Metrics
        - Key performance indicators
        - Quality measurement methods
        - Reporting and tracking

        ## Error Prevention
        - Common error patterns
        - Prevention strategies
        - Quality assurance protocols

        Make it specific, measurable, and actionable.
        """

        return await self._ai_generate_content(prompt, system_message, context)
    
    async def _ai_create_voice_examples(self, merged_content: str, parsed_contents: List['ParsedContent'],
                                       context: Dict[str, Any], content_analysis: Dict[str, Any]) -> str:
        """Create voice examples using AI."""

        client = context.get('client', 'Company')
        custom_instructions = context.get('custom_instructions', '')

        system_message = f"""You are an expert brand voice specialist creating practical voice examples and guidelines for {client}.
        Focus on concrete, usable examples that demonstrate the brand voice in action."""

        prompt = f"""
        Create comprehensive Voice Examples & Cultural Context document for {client} based on the analysis and source content.

        CONTENT ANALYSIS:
        {content_analysis}

        CUSTOM INSTRUCTIONS:
        {custom_instructions}

        SOURCE CONTENT (first 6000 chars):
        {merged_content[:6000]}

        Create a markdown document with this structure:
        # {client} - Voice Examples & Cultural Context

        ## Voice Examples
        - Concrete examples of brand voice in action
        - Before/after examples showing voice application
        - Context-specific voice demonstrations

        ## Tone Variations
        - Different tones for different situations
        - Formal vs. informal applications
        - Emotional tone variations

        ## Cultural Context
        - Cultural considerations and sensitivities
        - Regional adaptations
        - Inclusive language guidelines

        ## Do's and Don'ts
        - Specific examples of what to do
        - Clear examples of what to avoid
        - Common mistakes and corrections

        ## Sample Content
        - Sample headlines, taglines, and copy
        - Email templates and social media examples
        - Customer communication samples

        ## Adaptation Guidelines
        - How to adapt voice for different channels
        - Audience-specific adaptations
        - Context-sensitive modifications

        Provide specific, actionable examples throughout.
        """

        return await self._ai_generate_content(prompt, system_message, context)
    
    def _basic_content_analysis(self, merged_content: str, parsed_contents: List['ParsedContent']) -> Dict[str, Any]:
        """Basic content analysis fallback when AI fails."""
        analysis = {
            'total_words': len(merged_content.split()),
            'source_count': len(parsed_contents),
            'languages': list(set(pc.metadata.get('language', 'en') for pc in parsed_contents)),
            'source_types': list(set(pc.metadata.get('source_type', 'unknown') for pc in parsed_contents)),
            'key_themes': [],
            'company_info': {
                'mission': [],
                'values': [],
                'vision': [],
                'target_audience': []
            },
            'brand_elements': {
                'voice': [],
                'tone': [],
                'personality': [],
                'style': []
            },
            'process_info': {
                'steps': [],
                'workflows': [],
                'guidelines': [],
                'tools': []
            },
            'quality_info': {
                'standards': [],
                'requirements': [],
                'criteria': [],
                'metrics': []
            }
        }

        # Extract key themes using simple keyword analysis
        content_lower = merged_content.lower()
        theme_keywords = {
            'brand': ['brand', 'branding', 'identity', 'voice', 'tone', 'personality'],
            'quality': ['quality', 'standard', 'excellence', 'compliance', 'review'],
            'process': ['process', 'workflow', 'procedure', 'step', 'guide', 'method'],
            'customer': ['customer', 'client', 'audience', 'target', 'user'],
            'marketing': ['marketing', 'promotion', 'campaign', 'content', 'communication'],
            'technology': ['technology', 'digital', 'platform', 'tool', 'system'],
            'innovation': ['innovation', 'innovative', 'creative', 'new', 'advanced'],
            'service': ['service', 'support', 'help', 'assistance', 'care']
        }

        for theme, keywords in theme_keywords.items():
            if any(keyword in content_lower for keyword in keywords):
                analysis['key_themes'].append(theme.title())

        # Add summary
        analysis['summary'] = f"{analysis['source_count']} sources, {analysis['total_words']} words, basic analysis"

        return analysis
    
    def _clean_and_format(self, content: str) -> str:
        """Clean and format AI-generated content."""
        # Remove any markdown code blocks if present
        content = content.replace('```markdown', '').replace('```', '')

        # Clean up extra whitespace
        lines = content.split('\n')
        cleaned_lines = []

        for line in lines:
            line = line.strip()
            if line:
                cleaned_lines.append(line)
            elif cleaned_lines and cleaned_lines[-1] != '':
                cleaned_lines.append('')

        # Ensure proper markdown formatting
        result = '\n'.join(cleaned_lines)

        # Add final newline if missing
        if not result.endswith('\n'):
            result += '\n'

        return result



    def _extract_company_info(self, content: str) -> Dict[str, Any]:
        """Extract company information from content."""
        info = {
            'mission': [],
            'values': [],
            'vision': [],
            'target_audience': []
        }

        # Simple pattern matching for common sections
        lines = content.split('\n')
        current_section = None

        for line in lines:
            line = line.strip()
            if not line:
                continue

            # Detect section headers
            line_lower = line.lower()
            if any(word in line_lower for word in ['mission', 'missione']):
                current_section = 'mission'
            elif any(word in line_lower for word in ['value', 'valori', 'principi']):
                current_section = 'values'
            elif any(word in line_lower for word in ['vision', 'visione']):
                current_section = 'vision'
            elif any(word in line_lower for word in ['target', 'audience', 'clienti']):
                current_section = 'target_audience'
            elif line.startswith('#'):
                current_section = None
            elif current_section and line and not line.startswith('#'):
                # Clean and add content
                clean_line = re.sub(r'^[-*•]\s*', '', line).strip()
                if clean_line and len(clean_line) > 3:
                    info[current_section].append(clean_line)

        return info

    def _extract_brand_elements(self, content: str) -> Dict[str, Any]:
        """Extract brand elements from content."""
        elements = {
            'voice': [],
            'tone': [],
            'personality': [],
            'style': []
        }

        content_lower = content.lower()

        # Look for brand voice indicators
        voice_patterns = [
            r'voice[:\s]+([^.\n]+)',
            r'tono[:\s]+([^.\n]+)',
            r'comunicazione[:\s]+([^.\n]+)'
        ]

        for pattern in voice_patterns:
            matches = re.findall(pattern, content_lower)
            elements['voice'].extend([m.strip() for m in matches if len(m.strip()) > 5])

        # Look for personality traits
        personality_keywords = [
            'professionale', 'amichevole', 'innovativo', 'affidabile',
            'trasparente', 'creativo', 'esperto', 'accessibile'
        ]

        for keyword in personality_keywords:
            if keyword in content_lower:
                elements['personality'].append(keyword.title())

        return elements

    def _extract_process_info(self, content: str) -> Dict[str, Any]:
        """Extract process information from content."""
        info = {
            'steps': [],
            'workflows': [],
            'guidelines': [],
            'tools': []
        }

        lines = content.split('\n')

        for line in lines:
            line = line.strip()
            if not line:
                continue

            # Look for numbered steps
            if re.match(r'^\d+\.', line):
                clean_step = re.sub(r'^\d+\.\s*', '', line).strip()
                if len(clean_step) > 5:
                    info['steps'].append(clean_step)

            # Look for bullet points that might be guidelines
            elif line.startswith(('-', '*', '•')):
                clean_item = re.sub(r'^[-*•]\s*', '', line).strip()
                if len(clean_item) > 5:
                    info['guidelines'].append(clean_item)

        return info

    def _extract_quality_info(self, content: str) -> Dict[str, Any]:
        """Extract quality information from content."""
        info = {
            'standards': [],
            'requirements': [],
            'criteria': [],
            'metrics': []
        }

        content_lower = content.lower()

        # Look for quality-related terms
        quality_patterns = [
            r'standard[:\s]+([^.\n]+)',
            r'qualità[:\s]+([^.\n]+)',
            r'requisit[:\s]+([^.\n]+)',
            r'criteri[:\s]+([^.\n]+)'
        ]

        for pattern in quality_patterns:
            matches = re.findall(pattern, content_lower)
            info['standards'].extend([m.strip() for m in matches if len(m.strip()) > 5])

        return info








