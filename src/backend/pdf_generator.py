"""
PDF Report Generator
Generates comprehensive legal reports with appendices for lawyers
"""

import os
from datetime import datetime
from typing import Dict, List, Any, Optional
from xml.sax.saxutils import escape
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, PageBreak,
    Table, TableStyle, KeepTogether
)
from reportlab.pdfgen import canvas


class PDFReportGenerator:
    """Generate PDF reports for refugee case analysis"""
    
    def __init__(self):
        self.styles = getSampleStyleSheet()
        self._setup_custom_styles()
    
    def _escape_text(self, text: str) -> str:
        """
        Convert markdown to HTML and escape text for ReportLab Paragraph.
        
        ReportLab Paragraph uses HTML-like markup:
        - <b>text</b> for bold
        - <i>text</i> for italic
        - <u>text</u> for underline
        
        This function:
        1. Converts markdown syntax to HTML
        2. Escapes special characters
        3. Preserves HTML tags
        """
        if not text:
            return ""
        
        # Replace problematic dash characters with standard hyphen
        text = text.replace('–', '-').replace('—', '-').replace('−', '-')
        
        # Convert markdown to HTML BEFORE escaping
        # Bold: **text** -> <b>text</b>
        import re
        text = re.sub(r'\*\*(.+?)\*\*', r'<b>\1</b>', text)
        
        # Italic: *text* (but not ** which we already handled)
        # Use negative lookbehind/lookahead to avoid matching **
        text = re.sub(r'(?<!\*)\*(?!\*)(.+?)(?<!\*)\*(?!\*)', r'<i>\1</i>', text)
        
        # Now escape HTML special characters EXCEPT our tags
        # Split by tags, escape content between tags
        parts = re.split(r'(<[^>]+>)', text)
        escaped_parts = []
        for part in parts:
            if part.startswith('<') and part.endswith('>'):
                # Keep HTML tags as-is
                escaped_parts.append(part)
            else:
                # Escape content
                escaped_parts.append(escape(part))
        text = ''.join(escaped_parts)
        
        # Convert markdown-style bullets to HTML bullets
        lines = text.split('\n')
        converted_lines = []
        for line in lines:
            stripped = line.lstrip()
            # Check if line starts with markdown bullet
            if stripped.startswith('- ') or stripped.startswith('• '):
                # Remove the bullet and add bullet point
                content = stripped[2:].strip()
                converted_lines.append(f"• {content}")
            else:
                converted_lines.append(line)
        
        return '\n'.join(converted_lines)
    
    def _setup_custom_styles(self):
        """Setup custom paragraph styles"""
        # Title style
        self.styles.add(ParagraphStyle(
            name='CustomTitle',
            parent=self.styles['Heading1'],
            fontSize=20,
            textColor=colors.HexColor('#1e3a8a'),
            spaceAfter=30,
            alignment=TA_CENTER,
            fontName='Helvetica-Bold'
        ))
        
        # Section heading
        self.styles.add(ParagraphStyle(
            name='SectionHeading',
            parent=self.styles['Heading2'],
            fontSize=14,
            textColor=colors.HexColor('#1e40af'),
            spaceAfter=12,
            spaceBefore=20,
            fontName='Helvetica-Bold'
        ))
        
        # Subsection heading
        self.styles.add(ParagraphStyle(
            name='SubsectionHeading',
            parent=self.styles['Heading3'],
            fontSize=12,
            textColor=colors.HexColor('#1e40af'),
            spaceAfter=8,
            spaceBefore=12,
            fontName='Helvetica-Bold'
        ))
        
        # Body text
        self.styles.add(ParagraphStyle(
            name='BodyJustify',
            parent=self.styles['BodyText'],
            fontSize=10,
            alignment=TA_JUSTIFY,
            spaceAfter=10
        ))
        
        # Reference style
        self.styles.add(ParagraphStyle(
            name='Reference',
            parent=self.styles['BodyText'],
            fontSize=9,
            leftIndent=20,
            spaceAfter=6,
            textColor=colors.HexColor('#4b5563')
        ))
    
    def generate_report(
        self,
        output_path: str,
        case_data: Dict[str, Any],
        legal_analysis: Dict[str, Any],
        transcription: Optional[str] = None,
        forms_text: Optional[str] = None,
        forms_files: Optional[List[str]] = None
    ) -> str:
        """
        Generate comprehensive PDF report
        
        Args:
            output_path: Path to save PDF
            case_data: Dictionary with case information (name, UNHCR number, etc.)
            legal_analysis: Dictionary with legal analysis results
            transcription: Transcribed interview text
            forms_text: Extracted text from forms
            forms_files: List of original form file paths
            
        Returns:
            Path to generated PDF
        """
        doc = SimpleDocTemplate(
            output_path,
            pagesize=A4,
            rightMargin=72,
            leftMargin=72,
            topMargin=72,
            bottomMargin=72
        )
        
        story = []
        
        # Title page
        story.extend(self._build_title_page(case_data))
        story.append(PageBreak())
        
        # Executive Summary
        story.extend(self._build_executive_summary(case_data, legal_analysis))
        story.append(PageBreak())
        
        # Legal Analysis
        story.extend(self._build_legal_analysis(legal_analysis))
        story.append(PageBreak())
        
        # Bibliography
        if legal_analysis.get("bibliography"):
            story.extend(self._build_bibliography(legal_analysis["bibliography"]))
            story.append(PageBreak())
        
        # Appendix I: Asylum Seeker Forms
        if forms_text or forms_files:
            story.extend(self._build_appendix_forms(forms_text, forms_files))
            story.append(PageBreak())
        
        # Appendix II: Interview Transcript
        if transcription:
            story.extend(self._build_appendix_transcript(transcription))
            story.append(PageBreak())
        
        # Appendix III: Case Law and Legislation
        story.extend(self._build_appendix_case_law(legal_analysis))
        
        # Build PDF
        doc.build(story)
        
        return output_path
    
    def _build_title_page(self, case_data: Dict[str, Any]) -> List:
        """Build title page"""
        elements = []
        
        # Title
        elements.append(Spacer(1, 2*inch))
        elements.append(Paragraph(
            "REFUGEE CASE LEGAL ANALYSIS",
            self.styles['CustomTitle']
        ))
        elements.append(Spacer(1, 0.5*inch))
        
        # Case information table
        case_info = [
            ["Asylum Seeker Name:", case_data.get("name", "N/A")],
            ["UNHCR Registration Number:", case_data.get("unhcr_number", "N/A")],
            ["Report Generated:", datetime.now().strftime("%B %d, %Y at %H:%M")],
            ["Prepared For:", "Pro Bono Legal Counsel"]
        ]
        
        table = Table(case_info, colWidths=[2.5*inch, 3.5*inch])
        table.setStyle(TableStyle([
            ('FONT', (0, 0), (-1, -1), 'Helvetica', 10),
            ('FONT', (0, 0), (0, -1), 'Helvetica-Bold', 10),
            ('TEXTCOLOR', (0, 0), (0, -1), colors.HexColor('#1e40af')),
            ('ALIGN', (0, 0), (0, -1), 'RIGHT'),
            ('ALIGN', (1, 0), (1, -1), 'LEFT'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('TOPPADDING', (0, 0), (-1, -1), 8),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ]))
        
        elements.append(table)
        elements.append(Spacer(1, 1*inch))
        
        # Confidentiality notice
        elements.append(Paragraph(
            "<b>CONFIDENTIAL LEGAL DOCUMENT</b>",
            self.styles['BodyText']
        ))
        elements.append(Paragraph(
            "This document contains privileged legal analysis prepared for legal counsel. "
            "It should be treated as confidential and used solely for the purpose of "
            "providing legal representation to the named asylum seeker.",
            self.styles['BodyText']
        ))
        
        return elements
    
    def _build_executive_summary(
        self,
        case_data: Dict[str, Any],
        legal_analysis: Dict[str, Any]
    ) -> List:
        """Build executive summary section"""
        elements = []
        
        elements.append(Paragraph("EXECUTIVE SUMMARY", self.styles['SectionHeading']))
        
        # Personal Data
        elements.append(Paragraph("Personal Data", self.styles['SubsectionHeading']))
        personal_info = case_data.get("personal_info", {})
        
        if personal_info:
            for key, value in personal_info.items():
                elements.append(Paragraph(
                    f"<b>{key}:</b> {value}",
                    self.styles['BodyJustify']
                ))
        
        elements.append(Spacer(1, 12))
        
        # Overview of Situation
        elements.append(Paragraph("Overview of Situation", self.styles['SubsectionHeading']))
        overview = case_data.get("overview", "Case overview not provided.")
        elements.append(Paragraph(self._escape_text(overview), self.styles['BodyJustify']))
        
        elements.append(Spacer(1, 12))
        
        # Family Composition
        if case_data.get("family_composition"):
            elements.append(Paragraph("Family Composition", self.styles['SubsectionHeading']))
            elements.append(Paragraph(
                self._escape_text(case_data["family_composition"]),
                self.styles['BodyJustify']
            ))
        
        return elements
    
    def _build_legal_analysis(self, legal_analysis: Dict[str, Any]) -> List:
        """Build legal analysis section"""
        elements = []
        
        elements.append(Paragraph(
            "LEGAL ANALYSIS AND RECOMMENDATIONS",
            self.styles['SectionHeading']
        ))
        
        # Summary of Legally Relevant Facts
        elements.append(Paragraph(
            "Summary of Legally Relevant Facts",
            self.styles['SubsectionHeading']
        ))
        
        legal_summary = legal_analysis.get("legal_summary", {})
        summary_text = legal_summary.get("full_summary", legal_analysis.get("legal_analysis", ""))
        
        # Split into paragraphs and format
        for para in summary_text.split('\n\n'):
            if para.strip():
                # Check if it's a heading
                if para.strip().isupper() or para.strip().startswith('#'):
                    elements.append(Paragraph(
                        self._escape_text(para.strip().lstrip('#').strip()),
                        self.styles['SubsectionHeading']
                    ))
                else:
                    elements.append(Paragraph(
                        self._escape_text(para.strip()),
                        self.styles['BodyJustify']
                    ))
        
        return elements
    
    def _build_bibliography(self, bibliography: List[Dict[str, str]]) -> List:
        """Build bibliography section"""
        elements = []
        
        elements.append(Paragraph("BIBLIOGRAPHY", self.styles['SectionHeading']))
        
        # Group by type
        general_docs = [b for b in bibliography if b.get("type") == "General Legal Document"]
        swiss_laws = [b for b in bibliography if b.get("type") == "Swiss Federal Legislation"]
        
        if general_docs:
            elements.append(Paragraph(
                "General Legal Documents",
                self.styles['SubsectionHeading']
            ))
            
            for doc in general_docs:
                ref = self._escape_text(doc.get('reference', ''))
                title = self._escape_text(doc.get('title', ''))
                ref_text = f"<b>{ref}</b> {title}"
                if doc.get('path'):
                    path = self._escape_text(doc['path'])
                    ref_text += f"<br/><i>Source: {path}</i>"
                
                elements.append(Paragraph(ref_text, self.styles['Reference']))
        
        if swiss_laws:
            elements.append(Spacer(1, 12))
            elements.append(Paragraph(
                "Swiss Federal Legislation",
                self.styles['SubsectionHeading']
            ))
            
            for law in swiss_laws:
                ref = self._escape_text(law.get('reference', ''))
                title = self._escape_text(law.get('title', ''))
                sr_num = self._escape_text(law.get('sr_number', ''))
                ref_text = f"<b>{ref}</b> {title}"
                if sr_num:
                    ref_text += f" (SR {sr_num})"
                # Note: Links available in Appendix III
                elements.append(Paragraph(ref_text, self.styles['Reference']))
        
        return elements
    
    def _build_appendix_forms(
        self,
        forms_text: Optional[str] = None,
        forms_files: Optional[List[str]] = None
    ) -> List:
        """Build Appendix I: Asylum Seeker Forms"""
        elements = []
        
        elements.append(Paragraph(
            "APPENDIX I: ASYLUM SEEKER FORMS",
            self.styles['SectionHeading']
        ))
        
        if forms_files:
            elements.append(Paragraph(
                f"<b>Original Files:</b> {len(forms_files)} document(s) submitted",
                self.styles['BodyJustify']
            ))
            
            for i, file_path in enumerate(forms_files, 1):
                elements.append(Paragraph(
                    f"{i}. {os.path.basename(file_path)}",
                    self.styles['Reference']
                ))
        
        if forms_text:
            elements.append(Spacer(1, 12))
            elements.append(Paragraph(
                "<b>Extracted Content:</b>",
                self.styles['SubsectionHeading']
            ))
            
            # Split into manageable chunks
            for para in forms_text.split('\n\n'):
                if para.strip():
                    elements.append(Paragraph(self._escape_text(para.strip()), self.styles['BodyJustify']))
        
        return elements
    
    def _build_appendix_transcript(self, transcription: str) -> List:
        """Build Appendix II: Interview Transcript"""
        elements = []
        
        elements.append(Paragraph(
            "APPENDIX II: TRANSCRIBED AND TRANSLATED INTERVIEW",
            self.styles['SectionHeading']
        ))
        
        elements.append(Paragraph(
            "<i>Note: This interview was transcribed from audio and translated to English.</i>",
            self.styles['BodyText']
        ))
        
        elements.append(Spacer(1, 12))
        
        # Format transcript
        for para in transcription.split('\n\n'):
            if para.strip():
                elements.append(Paragraph(self._escape_text(para.strip()), self.styles['BodyJustify']))
        
        return elements
    
    def _build_appendix_case_law(self, legal_analysis: Dict[str, Any]) -> List:
        """Build Appendix III: Relevant Case Law"""
        elements = []
        
        elements.append(Paragraph(
            "APPENDIX III: RELEVANT CASE LAW AND LEGAL SOURCES",
            self.styles['SectionHeading']
        ))
        
        # Case law summary
        case_law = legal_analysis.get("case_law_summary", "")
        
        if case_law and case_law != "No specific case law cited.":
            elements.append(Paragraph(
                "Summary of Relevant Case Law",
                self.styles['SubsectionHeading']
            ))
            
            for para in case_law.split('\n\n'):
                if para.strip():
                    elements.append(Paragraph(self._escape_text(para.strip()), self.styles['BodyJustify']))
        else:
            elements.append(Paragraph(
                "No specific case law was cited in the analysis. "
                "The legal recommendations are based on applicable statutes and regulations.",
                self.styles['BodyJustify']
            ))
        
        elements.append(Spacer(1, 12))
        
        # Source documents
        if legal_analysis.get("source_documents"):
            elements.append(Paragraph(
                "Referenced Legal Documents",
                self.styles['SubsectionHeading']
            ))
            
            for i, doc in enumerate(legal_analysis["source_documents"][:5], 1):  # Limit to 5
                source = self._escape_text(doc.get('source', 'Unknown'))
                elements.append(Paragraph(
                    f"<b>Document {i}:</b> {source}",
                    self.styles['Reference']
                ))
                
                # Add excerpt - properly escaped, showing original text
                raw_content = doc.get('content', '')[:400]
                content = self._escape_text(raw_content)
                
                # Display the excerpt with label
                elements.append(Paragraph(
                    "<i>Excerpt:</i>",
                    self.styles['Reference']
                ))
                elements.append(Paragraph(
                    f"{content}...",
                    self.styles['Reference']
                ))
                
                elements.append(Spacer(1, 6))
        
        # Swiss Federal Legislation Links
        bibliography = legal_analysis.get("bibliography", [])
        swiss_laws = [b for b in bibliography if b.get("type") == "Swiss Federal Legislation" and b.get("link")]
        
        if swiss_laws:
            elements.append(Spacer(1, 12))
            elements.append(Paragraph(
                "Swiss Federal Legislation Links",
                self.styles['SubsectionHeading']
            ))
            
            elements.append(Paragraph(
                "<i>Note: Swiss federal legislation is available in German, French, Italian, and Romansh. "
                "Links below provide access to all language versions.</i>",
                self.styles['BodyText']
            ))
            elements.append(Spacer(1, 6))
            
            for law in swiss_laws:
                ref_num = self._escape_text(law.get('reference', ''))
                title = self._escape_text(law.get('title', 'Unknown'))
                sr_num = self._escape_text(law.get('sr_number', ''))
                link = self._escape_text(law.get('link', ''))
                
                # Format: [L1] Title (SR X.XXX)
                # Available at: https://...
                ref_text = f"<b>{ref_num}</b> {title}"
                if sr_num:
                    ref_text += f" (SR {sr_num})"
                
                elements.append(Paragraph(ref_text, self.styles['Reference']))
                
                if link:
                    # Add link on separate line, not clickable but copyable
                    elements.append(Paragraph(
                        f"<i>Available at: {link}</i>",
                        self.styles['Reference']
                    ))
                
                elements.append(Spacer(1, 6))
        
        return elements

