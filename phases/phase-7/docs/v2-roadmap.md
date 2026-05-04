# V2 Roadmap: Future Features

Now that Phase 7 is complete and the application is deployed, the foundation is stable. Here are the prioritized features for Version 2 (V2):

### 1. Semantic Search (Vector Embeddings)
- **Current State:** Filtering relies on strict string matching (e.g. `Biryani`).
- **V2 Goal:** Integrate a vector database (like Pinecone or Qdrant) so users can search with natural language (e.g. "Spicy food with a nice view").
- **Implementation:** Generate embeddings for all 33,000 restaurants and replace the Phase 3 deterministic filter with a semantic nearest-neighbor search.

### 2. Personalization & Memory
- **Current State:** Each request is completely stateless.
- **V2 Goal:** Remember user preferences across sessions.
- **Implementation:** Introduce a user authentication layer (e.g. Clerk or Firebase). Store user history and pass their past highly-rated restaurants to the Groq LLM as implicit context.

### 3. Hybrid Ranking System
- **Current State:** Deterministic ranking selects top 15, LLM ranks and explains them.
- **V2 Goal:** Implement a weighted scoring system that combines:
  - Vector Similarity Score (Semantic match)
  - Popularity Score (Votes & Rating)
  - LLM Re-ranking (Contextual match)
- **Implementation:** Adjust the Phase 4 Orchestrator to weigh these three scores before passing the final list to the LLM for explanation generation.

### 4. Direct Database Connection
- **Current State:** The 12MB JSON dataset is loaded entirely into RAM.
- **V2 Goal:** Migrate to a managed PostgreSQL instance (e.g. Supabase or Railway Postgres) to allow horizontal scaling and real-time review updates without memory bloat.
