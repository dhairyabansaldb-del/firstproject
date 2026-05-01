# Problem Statement: AI-Powered Restaurant Recommendation System (Zomato-Inspired)

## Goal
Build an AI-powered restaurant recommendation service that combines structured restaurant data with an LLM to generate personalized, explainable recommendations.

## Core Objective
Given a user's dining preferences, the system should:
- identify the most relevant restaurants from a real-world dataset,
- rank them intelligently,
- and present clear, human-friendly recommendations with reasons.

## Required Inputs
The system must collect and use the following user preferences:
- **Location** (for example: Delhi, Bangalore)
- **Budget** (low, medium, high)
- **Cuisine preference** (for example: Italian, Chinese)
- **Minimum rating**
- **Optional constraints** (for example: family-friendly, quick service)

## Data Source
Use and preprocess the Zomato dataset from Hugging Face:
- [ManikaSaini/zomato-restaurant-recommendation](https://huggingface.co/datasets/ManikaSaini/zomato-restaurant-recommendation)

At minimum, extract fields such as:
- restaurant name
- location
- cuisine
- average cost
- rating
- any other metadata useful for recommendation quality

## System Workflow
1. **Data ingestion and preprocessing**
   - Load dataset.
   - Clean and normalize restaurant attributes.
2. **Preference collection**
   - Capture user inputs listed above.
3. **Candidate filtering**
   - Apply deterministic filters (location, budget, rating, cuisine, etc.) to shortlist candidates.
4. **LLM-based recommendation**
   - Pass structured candidate data and user preferences to the LLM using a well-designed prompt.
   - Ask the LLM to rank candidates and justify each recommendation.
5. **Result presentation**
   - Display top recommendations in a clean and useful format.

## Expected Output Format
For each recommended restaurant, show:
- **Restaurant name**
- **Cuisine**
- **Rating**
- **Estimated cost**
- **AI-generated explanation** of why it matches user preferences

## Success Criteria
The solution is successful if it:
- returns relevant recommendations aligned with user constraints,
- provides understandable and trustworthy reasoning,
- and presents results in a simple, user-friendly way.

## Architecture Document
The detailed phase-wise architecture is available at `docs/architecture.md`.
