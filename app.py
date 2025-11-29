import streamlit as st
import pdfplumber
from docx import Document
import io
import json
import pandas as pd
from datetime import datetime
from resume_parser import ResumeParser
from embeddings import EmbeddingsManager
from scoring import ResumeScorer, explain_match
from supabase_client import SupabaseManager, check_supabase_connection
from bias_detection import generate_bias_report, BiasReport

# Page configuration
st.set_page_config(
    page_title="Resume Analyzer",
    page_icon="📄",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Enhanced Custom CSS with modern styling
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    * {
        font-family: 'Inter', sans-serif;
    }
    
    .main {
        padding: 1rem 2rem;
        background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
    }
    
    .hero-header {
        text-align: center;
        padding: 2rem 0;
        margin-bottom: 2rem;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border-radius: 20px;
        color: white;
        box-shadow: 0 10px 40px rgba(0,0,0,0.1);
    }
    
    .hero-header h1 {
        font-size: 3rem;
        font-weight: 700;
        margin: 0.5rem 0;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.2);
    }
    
    .hero-header p {
        font-size: 1.2rem;
        font-weight: 300;
        opacity: 0.95;
        margin-top: 0.5rem;
    }
    
    .card {
        background: white;
        border-radius: 15px;
        padding: 1.5rem;
        margin: 1rem 0;
        box-shadow: 0 4px 15px rgba(0,0,0,0.08);
        transition: transform 0.2s, box-shadow 0.2s;
    }
    
    .card:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 25px rgba(0,0,0,0.12);
    }
    
    .candidate-card {
        background: white;
        border-radius: 15px;
        padding: 1.5rem;
        margin: 1rem 0;
        box-shadow: 0 4px 15px rgba(0,0,0,0.08);
        border-left: 5px solid #667eea;
    }
    
    .score-badge {
        display: inline-block;
        padding: 0.5rem 1rem;
        border-radius: 25px;
        font-weight: 600;
        font-size: 1rem;
        margin: 0.5rem 0;
    }
    
    .score-high {
        background: linear-gradient(135deg, #10b981, #059669);
        color: white;
        box-shadow: 0 4px 10px rgba(16, 185, 129, 0.3);
    }
    
    .score-med {
        background: linear-gradient(135deg, #f59e0b, #d97706);
        color: white;
        box-shadow: 0 4px 10px rgba(245, 158, 11, 0.3);
    }
    
    .score-low {
        background: linear-gradient(135deg, #ef4444, #dc2626);
        color: white;
        box-shadow: 0 4px 10px rgba(239, 68, 68, 0.3);
    }
    
    .gradient-btn {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 0.75rem 2rem;
        border-radius: 10px;
        border: none;
        font-weight: 600;
        cursor: pointer;
        box-shadow: 0 4px 15px rgba(102, 126, 234, 0.4);
        transition: all 0.3s;
    }
    
    .gradient-btn:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(102, 126, 234, 0.5);
    }
    
    .stTextArea textarea {
        font-size: 14px;
        border-radius: 10px;
    }
    
    .upload-section {
        background: white;
        padding: 1.5rem;
        border-radius: 15px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.08);
        margin-bottom: 1rem;
    }
    
    .score-bar {
        background-color: #e5e7eb;
        border-radius: 10px;
        height: 25px;
        margin: 10px 0;
        overflow: hidden;
        box-shadow: inset 0 2px 4px rgba(0,0,0,0.06);
    }
    
    .score-fill {
        height: 100%;
        text-align: center;
        line-height: 25px;
        color: white;
        font-weight: 600;
        font-size: 14px;
        transition: width 0.5s ease;
    }
    
    .score-excellent {
        background: linear-gradient(90deg, #10b981, #059669);
    }
    
    .score-good {
        background: linear-gradient(90deg, #3b82f6, #2563eb);
    }
    
    .score-moderate {
        background: linear-gradient(90deg, #f59e0b, #d97706);
    }
    
    .score-weak {
        background: linear-gradient(90deg, #ef4444, #dc2626);
    }
    
    .explanation-box {
        background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
        border-left: 4px solid #667eea;
        padding: 1.5rem;
        border-radius: 10px;
        margin: 1rem 0;
        box-shadow: 0 2px 8px rgba(0,0,0,0.05);
    }
    
    .reason-item {
        padding: 0.75rem;
        margin: 0.5rem 0;
        background: white;
        border-radius: 8px;
        border-left: 3px solid #667eea;
        box-shadow: 0 2px 5px rgba(0,0,0,0.05);
    }
    
    .stat-card {
        background: white;
        padding: 1.5rem;
        border-radius: 12px;
        text-align: center;
        box-shadow: 0 4px 12px rgba(0,0,0,0.08);
        border-top: 4px solid #667eea;
    }
    
    .stat-card h3 {
        font-size: 2rem;
        font-weight: 700;
        color: #667eea;
        margin: 0.5rem 0;
    }
    
    .stat-card p {
        color: #6b7280;
        font-size: 0.9rem;
        margin: 0;
    }
    
    h1, h2, h3 {
        font-weight: 600;
    }
    </style>
    """, unsafe_allow_html=True)

def extract_text_from_pdf(file):
    """Extract text from PDF file"""
    text = ""
    try:
        with pdfplumber.open(io.BytesIO(file.read())) as pdf:
            for page in pdf.pages:
                text += page.extract_text() + "\n"
    except Exception as e:
        st.error(f"Error reading PDF: {str(e)}")
    return text

def extract_text_from_docx(file):
    """Extract text from DOCX file"""
    text = ""
    try:
        doc = Document(io.BytesIO(file.read()))
        for paragraph in doc.paragraphs:
            text += paragraph.text + "\n"
    except Exception as e:
        st.error(f"Error reading DOCX: {str(e)}")
    return text

def render_candidate_card(rank, name, score, breakdown, top_reasons, recommendation=""):
    """Render a modern candidate card with score badge and reasons"""
    
    # Determine score class and emoji
    if score >= 0.8:
        score_class = "score-high"
        emoji = "🌟"
        match_text = "EXCELLENT MATCH"
    elif score >= 0.6:
        score_class = "score-med"
        emoji = "👍"
        match_text = "GOOD MATCH"
    elif score >= 0.4:
        score_class = "score-med"
        emoji = "🤔"
        match_text = "MODERATE MATCH"
    else:
        score_class = "score-low"
        emoji = "❌"
        match_text = "WEAK MATCH"
    
    # Build reasons HTML
    reasons_html = ""
    for i, reason in enumerate(top_reasons[:5], 1):
        reasons_html += f"""
        <div class="reason-item">
            <strong>{i}.</strong> {reason}
        </div>
        """
    
    card_html = f"""
    <div class="candidate-card">
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 1rem;">
            <div>
                <h3 style="margin: 0; color: #1f2937;">#{rank} {emoji} {name}</h3>
                <p style="margin: 0.25rem 0; color: #6b7280; font-size: 0.9rem;">{match_text}</p>
            </div>
            <div class="score-badge {score_class}">
                {score:.1%}
            </div>
        </div>
        
        <div style="margin: 1rem 0;">
            <p style="font-weight: 600; color: #4b5563; margin-bottom: 0.5rem;">📊 Score Breakdown</p>
            <div style="display: grid; grid-template-columns: repeat(2, 1fr); gap: 0.5rem; font-size: 0.85rem;">
                <div>💡 Skills: <strong>{breakdown.skill_match_score:.0%}</strong></div>
                <div>💼 Experience: <strong>{breakdown.experience_score:.0%}</strong></div>
                <div>🎓 Education: <strong>{breakdown.education_score:.0%}</strong></div>
                <div>🔍 Semantic: <strong>{breakdown.semantic_similarity_score:.0%}</strong></div>
            </div>
        </div>
        
        <div style="margin-top: 1rem;">
            <p style="font-weight: 600; color: #4b5563; margin-bottom: 0.5rem;">✨ Top Reasons</p>
            {reasons_html}
        </div>
        
        {f'<div style="margin-top: 1rem; padding: 1rem; background: #f3f4f6; border-radius: 8px;"><strong>💡 Recommendation:</strong> {recommendation}</div>' if recommendation else ''}
    </div>
    """
    
    st.markdown(card_html, unsafe_allow_html=True)

def main():
    # Initialize session state
    if 'parsed_resumes' not in st.session_state:
        st.session_state.parsed_resumes = []
    
    if 'parser' not in st.session_state:
        st.session_state.parser = ResumeParser()
    
    if 'embeddings_manager' not in st.session_state:
        with st.spinner("Initializing embeddings model..."):
            st.session_state.embeddings_manager = EmbeddingsManager()
    
    if 'scorer' not in st.session_state:
        st.session_state.scorer = ResumeScorer(
            embeddings_manager=st.session_state.embeddings_manager
        )
    
    # Initialize Supabase manager (optional)
    if 'supabase_manager' not in st.session_state:
        try:
            if check_supabase_connection():
                st.session_state.supabase_manager = SupabaseManager()
                st.session_state.supabase_enabled = True
            else:
                st.session_state.supabase_enabled = False
        except Exception:
            st.session_state.supabase_enabled = False
    
    # Store analysis results
    if 'analysis_results' not in st.session_state:
        st.session_state.analysis_results = None
    
    # Hero Header
    st.markdown("""
        <div class="hero-header">
            <div style="font-size: 3rem;">📄</div>
            <h1>Resume Analyzer</h1>
            <p>AI-powered resume matching, scoring & bias detection</p>
        </div>
    """, unsafe_allow_html=True)
    
    # Create two columns for layout
    col_left, col_right = st.columns([1, 1])
    
    with col_left:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown("### 📂 Upload Resumes")
        
        # File uploader for resumes (supports multiple files)
        uploaded_files = st.file_uploader(
            "Choose resume files (PDF or DOCX)",
            type=["pdf", "docx"],
            accept_multiple_files=True,
            help="Upload one or more resume files in PDF or DOCX format"
        )
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Display uploaded files
        if uploaded_files:
            st.success(f"✅ {len(uploaded_files)} file(s) uploaded")
            
            with st.expander("View uploaded files"):
                for idx, file in enumerate(uploaded_files, 1):
                    st.write(f"{idx}. {file.name} ({file.type})")
            
            # Process files button
            if st.button("📖 Extract Text from Resumes", type="primary"):
                with st.spinner("Processing resumes..."):
                    st.session_state.parsed_resumes = []
                    
                    for file in uploaded_files:
                        st.markdown(f"**{file.name}**")
                        
                        # Extract text based on file type
                        if file.type == "application/pdf":
                            text = extract_text_from_pdf(file)
                        elif file.type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
                            text = extract_text_from_docx(file)
                        else:
                            text = "Unsupported file type"
                        
                        # Display extracted text
                        with st.expander(f"Preview: {file.name}"):
                            st.text_area(
                                "Extracted Text",
                                text[:1000] + "..." if len(text) > 1000 else text,
                                height=200,
                                key=f"preview_{file.name}",
                                disabled=True
                            )
                        
                        # Parse resume using resume_parser
                        try:
                            file.seek(0)
                            file_content = file.read()
                            file_type = "pdf" if file.type == "application/pdf" else "docx"
                            
                            parsed_data = st.session_state.parser.parse_resume(
                                file_content=file_content,
                                file_type=file_type
                            )
                            parsed_data['filename'] = file.name
                            st.session_state.parsed_resumes.append(parsed_data)
                            
                            # Show parsed data
                            with st.expander(f"📊 Parsed Data: {file.name}"):
                                st.json(parsed_data)
                            
                            st.success(f"✅ Successfully parsed {file.name}")
                            
                        except Exception as e:
                            st.error(f"Error parsing {file.name}: {str(e)}")
                        
                        # Reset file pointer for potential reprocessing
                        file.seek(0)
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col_right:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown("### 📝 Job Description")
        
        # Text area for job description
        job_description = st.text_area(
            "Enter or paste the job description",
            height=300,
            placeholder="Paste the job description here...\n\nExample:\n- Job Title: Senior Software Engineer\n- Requirements: Python, Machine Learning, 5+ years experience\n- Responsibilities: Design and implement ML systems...",
            help="Enter the complete job description including requirements, responsibilities, and qualifications"
        )
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Character count
        if job_description:
            char_count = len(job_description)
            word_count = len(job_description.split())
            st.caption(f"📊 {char_count} characters | {word_count} words")
    
    # Analysis section
    st.markdown("---")
    
    # Action buttons
    col_btn1, col_btn2, col_btn3 = st.columns([1, 1, 2])
    
    with col_btn1:
        analyze_button = st.button(
            "🔍 Analyze Resumes",
            type="primary",
            disabled=not (uploaded_files and job_description and st.session_state.parsed_resumes),
            help="Analyze uploaded resumes against the job description"
        )
    
    with col_btn2:
        clear_button = st.button("🗑️ Clear All")
    
    if clear_button:
        st.session_state.parsed_resumes = []
        st.rerun()
    
    if analyze_button:
        with st.spinner("🔍 Analyzing resumes..."):
            # Score all resumes
            scored_results = st.session_state.scorer.batch_score_resumes(
                st.session_state.parsed_resumes,
                job_description
            )
            
            # Generate bias report
            score_breakdown_dicts = [breakdown.to_dict() for _, breakdown in scored_results]
            bias_report = generate_bias_report(
                st.session_state.parsed_resumes,
                score_breakdown_dicts
            )
            st.session_state.bias_report = bias_report
            
            # Generate explanations for each candidate
            results_with_explanations = []
            for resume_data, breakdown in scored_results:
                try:
                    explanation = explain_match(
                        resume_data=resume_data,
                        job_description=job_description,
                        score_breakdown=breakdown
                    )
                    results_with_explanations.append((resume_data, breakdown, explanation))
                except Exception as e:
                    # If explanation fails, continue without it
                    print(f"Warning: Could not generate explanation for {resume_data.get('name')}: {e}")
                    results_with_explanations.append((resume_data, breakdown, None))
            
            # Store in session state
            st.session_state.analysis_results = results_with_explanations
            
            # Store in Supabase if enabled
            if st.session_state.supabase_enabled:
                try:
                    with st.spinner("💾 Saving to database..."):
                        st.session_state.supabase_manager.store_batch_analyses(
                            job_description,
                            [(r, b.to_dict(), e.to_dict() if e else None) 
                             for r, b, e in results_with_explanations]
                        )
                    st.toast("✅ Results saved to database!")
                except Exception as e:
                    st.warning(f"Could not save to database: {str(e)}")
        
        st.success("🎉 Analysis Complete!")
    
    # Display results if available
    if st.session_state.analysis_results:
        results_with_explanations = st.session_state.analysis_results
        
        # Create DataFrame for CSV export
        export_data = []
        for resume_data, breakdown, explanation in results_with_explanations:
            row = {
                "Rank": len([r_data for r_data, b_data, _ in results_with_explanations if b_data.final_score > breakdown.final_score]) + 1,
                "Name": resume_data.get("name", "Unknown"),
                "Email": resume_data.get("email", ""),
                "Phone": resume_data.get("phone", ""),
                "Final Score": f"{breakdown.final_score:.2%}",
                "Skills Match": f"{breakdown.skill_match_score:.2%}",
                "Experience Match": f"{breakdown.experience_score:.2%}",
                "Education Match": f"{breakdown.education_score:.2%}",
                "Semantic Match": f"{breakdown.semantic_similarity_score:.2%}",
                "Experience Years": breakdown.experience_years,
                "Required Experience": breakdown.required_experience or "N/A",
                "Has Required Degree": "Yes" if breakdown.has_required_degree else "No",
                "Matched Skills": ", ".join(breakdown.matched_skills),
                "Missing Skills": ", ".join(breakdown.missing_skills),
                "Recommendation": explanation.recommendation if explanation else "N/A",
                "Explanation": explanation.summary if explanation else "N/A",
                "Filename": resume_data.get("filename", "unknown")
            }
            export_data.append(row)
        
        df = pd.DataFrame(export_data)
        
        # Download CSV button
        csv = df.to_csv(index=False)
        st.download_button(
            label="📥 Download Results as CSV",
            data=csv,
            file_name=f"resume_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
            mime="text/csv",
            type="primary"
        )
        
        st.markdown("---")
        
        # Display Bias Detection Report
        if hasattr(st.session_state, 'bias_report') and st.session_state.bias_report:
            bias_report = st.session_state.bias_report
            
            st.markdown("### ⚖️ Bias Detection Report")
            
            # Summary banner
            if bias_report.has_critical_flags():
                st.error(f"🚨 {bias_report.summary}")
            elif bias_report.has_warnings():
                st.warning(f"⚠️  {bias_report.summary}")
            else:
                st.success(f"✅ {bias_report.summary}")
            
            # Display flags if any exist
            if bias_report.flags:
                with st.expander(f"📋 View Bias Report Details ({len(bias_report.flags)} flags)", expanded=bias_report.has_critical_flags()):
                    
                    # Group flags by severity
                    critical_flags = bias_report.get_flags_by_severity("critical")
                    warning_flags = bias_report.get_flags_by_severity("warning")
                    info_flags = bias_report.get_flags_by_severity("info")
                    
                    # Display critical flags
                    if critical_flags:
                        st.markdown("#### 🚨 Critical Issues")
                        for i, flag in enumerate(critical_flags, 1):
                            with st.container():
                                st.error(f"**{i}. {flag.message}**")
                                st.markdown(f"**Category:** {flag.category}")
                                st.markdown(f"**Recommendation:** {flag.recommendation}")
                                
                                if flag.affected_candidates:
                                    with st.container():
                                        st.markdown(f"**Affected candidates ({len(flag.affected_candidates)}):**")
                                        for candidate in flag.affected_candidates[:10]:
                                            st.write(f"• {candidate}")
                                        if len(flag.affected_candidates) > 10:
                                            st.caption(f"... and {len(flag.affected_candidates) - 10} more")
                                
                                if flag.details:
                                    with st.container():
                                        st.markdown("**Technical details:**")
                                        st.json(flag.details)
                                
                                st.markdown("---")
                    
                    # Display warnings
                    if warning_flags:
                        st.markdown("#### ⚠️  Warnings")
                        for i, flag in enumerate(warning_flags, 1):
                            with st.container():
                                st.warning(f"**{i}. {flag.message}**")
                                st.markdown(f"**Category:** {flag.category}")
                                st.markdown(f"**Recommendation:** {flag.recommendation}")
                                
                                if flag.affected_candidates:
                                    with st.container():
                                        st.markdown(f"**Affected candidates ({len(flag.affected_candidates)}):**")
                                        for candidate in flag.affected_candidates[:10]:
                                            st.write(f"• {candidate}")
                                        if len(flag.affected_candidates) > 10:
                                            st.caption(f"... and {len(flag.affected_candidates) - 10} more")
                                
                                if flag.details:
                                    with st.container():
                                        st.markdown("**Technical details:**")
                                        st.json(flag.details)
                                
                                st.markdown("---")
                    
                    # Display info flags
                    if info_flags:
                        st.markdown("#### ℹ️  Informational")
                        for i, flag in enumerate(info_flags, 1):
                            with st.container():
                                st.info(f"**{i}. {flag.message}**")
                                st.markdown(f"**Category:** {flag.category}")
                                st.markdown(f"**Recommendation:** {flag.recommendation}")
                                
                                if flag.affected_candidates:
                                    with st.container():
                                        st.markdown(f"**Affected candidates ({len(flag.affected_candidates)}):**")
                                        for candidate in flag.affected_candidates[:10]:
                                            st.write(f"• {candidate}")
                                        if len(flag.affected_candidates) > 10:
                                            st.caption(f"... and {len(flag.affected_candidates) - 10} more")
                                
                                if flag.details:
                                    with st.container():
                                        st.markdown("**Technical details:**")
                                        st.json(flag.details)
                                
                                st.markdown("---")
                    
                    # Disclaimer
                    st.markdown("---")
                    st.caption("⚖️ **Bias Detection Disclaimer**: This report identifies potential data quality issues and statistical patterns. It does not infer protected attributes (race, gender, age, etc.). Review all flags in context of your hiring process.")
        
        st.markdown("---")
        
        # Display ranked results
        st.markdown("### 🏆 Ranked Candidates")
        
        for rank, (resume_data, breakdown, explanation) in enumerate(results_with_explanations, 1):
            # Prepare top reasons
            top_reasons = []
            if explanation and hasattr(explanation, 'top_reasons'):
                top_reasons = explanation.top_reasons
            else:
                # Generate basic reasons from breakdown
                if breakdown.matched_skills:
                    top_reasons.append(f"Matches {len(breakdown.matched_skills)} required skills: {', '.join(breakdown.matched_skills[:3])}")
                if breakdown.experience_years:
                    top_reasons.append(f"Has {breakdown.experience_years} years of experience")
                if breakdown.has_required_degree:
                    top_reasons.append("Possesses required educational qualifications")
                if breakdown.semantic_similarity_score >= 0.7:
                    top_reasons.append(f"Strong semantic alignment ({breakdown.semantic_similarity_score:.0%}) with job description")
                if breakdown.missing_skills:
                    top_reasons.append(f"Missing {len(breakdown.missing_skills)} skills: {', '.join(breakdown.missing_skills[:2])}")
            
            # Get recommendation
            recommendation = explanation.recommendation if explanation and hasattr(explanation, 'recommendation') else ""
            
            # Render the candidate card
            render_candidate_card(
                rank=rank,
                name=resume_data.get('name', 'Unknown'),
                score=breakdown.final_score,
                breakdown=breakdown,
                top_reasons=top_reasons,
                recommendation=recommendation
            )
            
            # Add detailed view in an expander
            with st.expander(f"📄 View Full Details for {resume_data.get('name', 'Unknown')}"):
                # Determine score class for detailed view
                if breakdown.final_score >= 0.8:
                    score_class = "score-excellent"
                elif breakdown.final_score >= 0.6:
                    score_class = "score-good"
                elif breakdown.final_score >= 0.4:
                    score_class = "score-moderate"
                else:
                    score_class = "score-weak"
                
                # Overall score bar
                st.markdown("**🎯 Overall Match Score**")
                score_percentage = breakdown.final_score * 100
                st.markdown(
                    f"""
                    <div class="score-bar">
                        <div class="score-fill {score_class}" style="width: {score_percentage}%">
                            {score_percentage:.1f}%
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True
                )
                
                st.markdown("---")
                
                # Score breakdown with individual bars
                st.markdown("**📊 Score Breakdown**")
                
                col_bar1, col_bar2 = st.columns(2)
                
                with col_bar1:
                    # Skills match bar
                    st.markdown("**💡 Skills Match**")
                    skill_pct = breakdown.skill_match_score * 100
                    st.progress(breakdown.skill_match_score)
                    st.caption(f"{skill_pct:.1f}%")
                    
                    # Experience match bar
                    st.markdown("**💼 Experience Match**")
                    exp_pct = breakdown.experience_score * 100
                    st.progress(breakdown.experience_score)
                    st.caption(f"{exp_pct:.1f}%")
                
                with col_bar2:
                    # Education match bar
                    st.markdown("**🎓 Education Match**")
                    edu_pct = breakdown.education_score * 100
                    st.progress(breakdown.education_score)
                    st.caption(f"{edu_pct:.1f}%")
                    
                    # Semantic match bar
                    st.markdown("**🔍 Semantic Match**")
                    sem_pct = breakdown.semantic_similarity_score * 100
                    st.progress(breakdown.semantic_similarity_score)
                    st.caption(f"{sem_pct:.1f}%")
                
                st.markdown("---")
                
                # AI Explanation (if available)
                if explanation:
                    st.markdown("**🤖 AI Explanation**")
                    st.markdown(
                        f"""
                        <div class="explanation-box">
                            <p><strong>Summary:</strong> {explanation.summary}</p>
                        </div>
                        """,
                        unsafe_allow_html=True
                    )
                    
                    st.markdown("**📌 Top 3 Reasons:**")
                    for i, reason in enumerate(explanation.top_reasons, 1):
                        st.markdown(f"{i}. {reason}")
                    
                    st.markdown(f"**💡 Recommendation:** {explanation.recommendation}")
                    
                    st.markdown("---")
                
                # Detailed breakdown
                col_detail1, col_detail2 = st.columns(2)
                
                with col_detail1:
                    st.markdown("**📋 Basic Information**")
                    st.write(f"**Name:** {resume_data.get('name', 'N/A')}")
                    st.write(f"**Email:** {resume_data.get('email', 'N/A')}")
                    st.write(f"**Phone:** {resume_data.get('phone', 'N/A')}")
                    
                    st.markdown("**💼 Experience Analysis**")
                    st.write(f"**Candidate:** {breakdown.experience_years} years")
                    if breakdown.required_experience:
                        st.write(f"**Required:** {breakdown.required_experience} years")
                        diff = breakdown.experience_years - breakdown.required_experience
                        if diff >= 0:
                            st.success(f"✅ Exceeds by {diff} years")
                        else:
                            st.warning(f"⚠️ Below by {abs(diff)} years")
                    
                    st.markdown("**🎓 Education Analysis**")
                    education = resume_data.get('education', [])
                    if education:
                        for edu in education:
                            st.write(f"• {edu.get('degree', 'N/A')} ({edu.get('year', 'N/A')})")
                    if breakdown.has_required_degree:
                        st.success("✅ Has required degree")
                    else:
                        st.warning("⚠️ Missing required degree")
                
                with col_detail2:
                    st.markdown("**✅ Matched Skills**")
                    if breakdown.matched_skills:
                        for skill in breakdown.matched_skills:
                            st.success(f"✓ {skill}")
                    else:
                        st.write("No matched skills")
                    
                    st.markdown("**❌ Missing Skills**")
                    if breakdown.missing_skills:
                        for skill in breakdown.missing_skills:
                            st.error(f"✗ {skill}")
                    else:
                        st.write("No missing skills")
                
                # Summary and recommendation
                st.markdown("---")
                st.markdown("**💡 Quick Assessment**")
                
                if breakdown.final_score >= 0.8:
                    st.success("🌟 **STRONG MATCH** - Highly recommended for interview")
                elif breakdown.final_score >= 0.6:
                    st.info("👍 **GOOD MATCH** - Recommended for consideration")
                elif breakdown.final_score >= 0.4:
                    st.warning("🤔 **MODERATE MATCH** - Review carefully")
                else:
                    st.error("❌ **WEAK MATCH** - May not be suitable")
                
                # Show summary if available
                if resume_data.get('summary'):
                    st.markdown("**📝 Candidate Summary**")
                    st.write(resume_data['summary'])
                
                # Full JSON data
                with st.container():
                    st.markdown("**📄 Full Data**")
                    col_json1, col_json2 = st.columns(2)
                    with col_json1:
                        st.markdown("**Resume Data:**")
                        st.json(resume_data)
                    with col_json2:
                        st.markdown("**Score Breakdown:**")
                        st.json(breakdown.to_dict())
        
        # Summary statistics
        st.markdown("---")
        st.markdown("### 📊 Analysis Summary")
        
        col_stat1, col_stat2, col_stat3, col_stat4 = st.columns(4)
        
        with col_stat1:
            st.markdown(f"""
                <div class="stat-card">
                    <p>Total Candidates</p>
                    <h3>{len(results_with_explanations)}</h3>
                </div>
            """, unsafe_allow_html=True)
        
        with col_stat2:
            avg_score = sum([b.final_score for _, b, _ in results_with_explanations]) / len(results_with_explanations)
            st.markdown(f"""
                <div class="stat-card">
                    <p>Average Score</p>
                    <h3>{avg_score:.1%}</h3>
                </div>
            """, unsafe_allow_html=True)
        
        with col_stat3:
            strong_matches = sum(1 for _, b, _ in results_with_explanations if b.final_score >= 0.8)
            st.markdown(f"""
                <div class="stat-card">
                    <p>Strong Matches</p>
                    <h3>{strong_matches}</h3>
                </div>
            """, unsafe_allow_html=True)
        
        with col_stat4:
            avg_exp = sum([r.get('experience_years', 0) or 0 for r, _, _ in results_with_explanations]) / len(results_with_explanations)
            st.markdown(f"""
                <div class="stat-card">
                    <p>Avg Experience</p>
                    <h3>{avg_exp:.1f} yrs</h3>
                </div>
            """, unsafe_allow_html=True)
        
        # Skills overview
        st.markdown("### 💡 Skills Overview")
        
        all_matched_skills = set()
        all_missing_skills = set()
        
        for _, breakdown, _ in results_with_explanations:
            all_matched_skills.update(breakdown.matched_skills)
            all_missing_skills.update(breakdown.missing_skills)
        
        col_skill1, col_skill2 = st.columns(2)
        
        with col_skill1:
            st.markdown("**✅ Skills Found in Candidates**")
            if all_matched_skills:
                for skill in sorted(all_matched_skills):
                    # Count how many candidates have this skill
                    count = sum(1 for _, b, _ in results_with_explanations if skill in b.matched_skills)
                    st.write(f"• {skill} ({count}/{len(results_with_explanations)} candidates)")
            else:
                st.write("No matched skills")
        
        with col_skill2:
            st.markdown("**❌ Skills Needed**")
            if all_missing_skills:
                for skill in sorted(all_missing_skills):
                    # Count how many candidates are missing this skill
                    count = sum(1 for _, b, _ in results_with_explanations if skill in b.missing_skills)
                    if count == len(results_with_explanations):  # All candidates missing this
                        st.write(f"• {skill} (Missing in all candidates)")
            else:
                st.write("All required skills covered by candidates")
    
    # Sidebar with information
    with st.sidebar:
        st.markdown("### ℹ️ About")
        st.info("""
        This application helps you analyze resumes against job descriptions using AI.
        
        **Features:**
        - Upload multiple resumes (PDF/DOCX)
        - Enter job descriptions
        - AI-powered matching
        - Multi-signal scoring
        - LLM explanations
        - Candidate ranking
        - Skill gap analysis
        - CSV export
        - Database storage
        """)
        
        # Supabase status
        if st.session_state.supabase_enabled:
            st.success("💾 Database: Connected")
        else:
            st.warning("💾 Database: Not configured")
            with st.expander("Setup Supabase"):
                st.code("""
# Set environment variables:
export SUPABASE_URL="your-project-url"
export SUPABASE_KEY="your-api-key"
                """)
        
        st.markdown("### 🎯 Scoring Methodology")
        st.markdown("""
        Final score is calculated from:
        - **Skills Match** (35%): Overlap with required skills
        - **Experience** (25%): Years of experience
        - **Education** (15%): Required degree validation
        - **Semantic Match** (25%): AI-powered content similarity
        """)
        
        st.markdown("### 🤖 AI Features")
        st.markdown("""
        - **LLM Explanations**: GPT-4 powered insights
        - **Few-shot prompting**: Consistent, reliable results
        - **Semantic matching**: Deep content understanding
        - **Smart ranking**: Multi-signal algorithm
        """)
        
        st.markdown("### 🛠️ Tech Stack")
        st.markdown("""
        - **Streamlit** - UI Framework
        - **LangChain** - LLM Framework
        - **OpenAI** - AI Models
        - **Sentence Transformers** - Embeddings
        - **Supabase** - Database
        - **Pinecone** - Vector Database
        - **pdfplumber** - PDF Parsing
        - **python-docx** - DOCX Parsing
        """)
        
        st.markdown("---")
        st.caption("📅 2025 Resume Analyzer • Built with ❤️")

if __name__ == "__main__":
    main()
