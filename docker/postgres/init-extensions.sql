-- Engineering Intelligence Hub - PostgreSQL Initialization
-- Create required extensions for the application

-- Enable pgvector extension for vector similarity search
CREATE EXTENSION IF NOT EXISTS vector;

-- Enable uuid-ossp for UUID generation (if needed)
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Enable pg_trgm for text search improvements (if needed)
CREATE EXTENSION IF NOT EXISTS pg_trgm;

-- Log successful initialization
DO $$
BEGIN
    RAISE NOTICE 'Engineering Intelligence Hub: PostgreSQL extensions initialized successfully';
END $$;