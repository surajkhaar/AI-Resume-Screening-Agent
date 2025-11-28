-- Supabase Database Setup for Resume Analyzer
-- Run this SQL in your Supabase SQL Editor to create the required table

-- Create the resume_analyses table
CREATE TABLE IF NOT EXISTS resume_analyses (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    job_description TEXT NOT NULL,
    candidate_name TEXT NOT NULL,
    candidate_email TEXT,
    candidate_phone TEXT,
    final_score FLOAT NOT NULL,
    skill_match_score FLOAT,
    experience_score FLOAT,
    education_score FLOAT,
    semantic_score FLOAT,
    experience_years INTEGER,
    required_experience INTEGER,
    has_required_degree BOOLEAN,
    matched_skills TEXT[],
    missing_skills TEXT[],
    resume_data JSONB,
    score_breakdown JSONB,
    explanation_summary TEXT,
    explanation_reasons TEXT[],
    explanation_recommendation TEXT,
    filename TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create indexes for better query performance
CREATE INDEX IF NOT EXISTS idx_timestamp ON resume_analyses(timestamp DESC);
CREATE INDEX IF NOT EXISTS idx_candidate_name ON resume_analyses(candidate_name);
CREATE INDEX IF NOT EXISTS idx_final_score ON resume_analyses(final_score DESC);
CREATE INDEX IF NOT EXISTS idx_created_at ON resume_analyses(created_at DESC);

-- Enable Row Level Security (RLS) - OPTIONAL
ALTER TABLE resume_analyses ENABLE ROW LEVEL SECURITY;

-- Create a policy to allow all operations for authenticated users
-- Modify this based on your security requirements
CREATE POLICY "Enable all access for authenticated users" ON resume_analyses
    FOR ALL
    USING (auth.role() = 'authenticated')
    WITH CHECK (auth.role() = 'authenticated');

-- Alternatively, allow public access (NOT RECOMMENDED for production)
-- Uncomment the following if you want to allow public access
-- CREATE POLICY "Enable all access for all users" ON resume_analyses
--     FOR ALL
--     USING (true)
--     WITH CHECK (true);

-- Create a view for summary statistics
CREATE OR REPLACE VIEW resume_analysis_stats AS
SELECT 
    COUNT(*) as total_analyses,
    AVG(final_score) as average_score,
    COUNT(CASE WHEN final_score >= 0.8 THEN 1 END) as strong_matches,
    COUNT(CASE WHEN final_score >= 0.6 AND final_score < 0.8 THEN 1 END) as good_matches,
    COUNT(CASE WHEN final_score >= 0.4 AND final_score < 0.6 THEN 1 END) as moderate_matches,
    COUNT(CASE WHEN final_score < 0.4 THEN 1 END) as weak_matches,
    AVG(experience_years) as average_experience,
    MAX(timestamp) as last_analysis_date
FROM resume_analyses;

-- Create a function to get top candidates
CREATE OR REPLACE FUNCTION get_top_candidates(limit_count INTEGER DEFAULT 10)
RETURNS TABLE (
    candidate_name TEXT,
    final_score FLOAT,
    matched_skills TEXT[],
    experience_years INTEGER,
    recommendation TEXT
)
LANGUAGE SQL
AS $$
    SELECT 
        candidate_name,
        final_score,
        matched_skills,
        experience_years,
        explanation_recommendation
    FROM resume_analyses
    ORDER BY final_score DESC
    LIMIT limit_count;
$$;

-- Create a function to clean old records (older than 90 days)
CREATE OR REPLACE FUNCTION clean_old_analyses(days_to_keep INTEGER DEFAULT 90)
RETURNS INTEGER
LANGUAGE plpgsql
AS $$
DECLARE
    deleted_count INTEGER;
BEGIN
    DELETE FROM resume_analyses
    WHERE timestamp < NOW() - (days_to_keep || ' days')::INTERVAL;
    
    GET DIAGNOSTICS deleted_count = ROW_COUNT;
    RETURN deleted_count;
END;
$$;

-- Grant permissions (adjust based on your setup)
GRANT SELECT, INSERT, UPDATE, DELETE ON resume_analyses TO authenticated;
GRANT SELECT ON resume_analysis_stats TO authenticated;
GRANT EXECUTE ON FUNCTION get_top_candidates TO authenticated;
GRANT EXECUTE ON FUNCTION clean_old_analyses TO authenticated;

-- For public access (NOT RECOMMENDED for production), uncomment:
-- GRANT SELECT, INSERT ON resume_analyses TO anon;

COMMENT ON TABLE resume_analyses IS 'Stores resume analysis results with scores, explanations, and metadata';
COMMENT ON COLUMN resume_analyses.timestamp IS 'When the analysis was performed';
COMMENT ON COLUMN resume_analyses.final_score IS 'Overall match score (0-1)';
COMMENT ON COLUMN resume_analyses.resume_data IS 'Complete parsed resume data in JSON format';
COMMENT ON COLUMN resume_analyses.score_breakdown IS 'Detailed score breakdown in JSON format';
COMMENT ON COLUMN resume_analyses.explanation_summary IS 'AI-generated explanation summary';
COMMENT ON COLUMN resume_analyses.explanation_reasons IS 'Top 3 reasons for match/mismatch';
