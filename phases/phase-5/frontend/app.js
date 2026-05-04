// Phase 5 Restaurant Recommendation App JavaScript

class RestaurantRecommendationApp {
    constructor() {
        this.initializeElements();
        this.bindEvents();
        this.currentRecommendations = [];
        this.currentPreferences = {};
    }

    initializeElements() {
        // Form elements
        this.preferenceForm = document.getElementById('preference-form');
        this.locationSelect = document.getElementById('location');
        this.budgetRadios = document.querySelectorAll('input[name="budget"]');
        this.cuisineSelect = document.getElementById('cuisine');
        this.ratingSlider = document.getElementById('min-rating');
        this.ratingValue = document.getElementById('rating-value');
        this.ratingStars = document.getElementById('rating-stars');
        this.additionalCheckboxes = document.querySelectorAll('input[name="additional_preferences"]');
        
        // Section elements
        this.preferenceSection = document.getElementById('preference-section');
        this.loadingSection = document.getElementById('loading-section');
        this.resultsSection = document.getElementById('results-section');
        this.errorSection = document.getElementById('error-section');
        
        // Results elements
        this.resultsSummary = document.getElementById('results-summary');
        this.recommendationsGrid = document.getElementById('recommendations-grid');
        this.progressFill = document.getElementById('progress-fill');
        this.progressText = document.getElementById('progress-text');
        
        // Button elements
        this.getRecommendationsBtn = document.getElementById('get-recommendations');
        this.refineSearchBtn = document.getElementById('refine-search');
        this.regenerateBtn = document.getElementById('regenerate');
        this.retryBtn = document.getElementById('retry-btn');
    }

    bindEvents() {
        // Form submission
        this.preferenceForm.addEventListener('submit', (e) => {
            e.preventDefault();
            this.handleFormSubmission();
        });

        // Rating slider
        this.ratingSlider.addEventListener('input', (e) => {
            this.updateRatingDisplay(e.target.value);
        });

        // Action buttons
        this.refineSearchBtn.addEventListener('click', () => {
            this.showPreferencesForm();
        });

        this.regenerateBtn.addEventListener('click', () => {
            this.regenerateRecommendations();
        });

        this.retryBtn.addEventListener('click', () => {
            this.showPreferencesForm();
        });

        // Initialize rating display
        this.updateRatingDisplay(this.ratingSlider.value);
    }

    updateRatingDisplay(value) {
        this.ratingValue.textContent = value;
        const stars = Math.round(parseFloat(value));
        this.ratingStars.textContent = '⭐'.repeat(stars);
    }

    handleFormSubmission() {
        const preferences = this.collectPreferences();
        
        if (!this.validatePreferences(preferences)) {
            return;
        }

        this.currentPreferences = preferences;
        this.showLoadingState();
        this.fetchRecommendations(preferences);
    }

    collectPreferences() {
        const additionalPreferences = Array.from(this.additionalCheckboxes)
            .filter(checkbox => checkbox.checked)
            .map(checkbox => checkbox.value);

        return {
            location: this.locationSelect.value,
            budget: document.querySelector('input[name="budget"]:checked')?.value,
            cuisine: this.cuisineSelect.value,
            min_rating: parseFloat(this.ratingSlider.value),
            additional_preferences: additionalPreferences,
            limit: 5
        };
    }

    validatePreferences(preferences) {
        const required = ['location', 'budget', 'cuisine'];
        for (const field of required) {
            if (!preferences[field]) {
                this.showError(`Please select a ${field.replace('_', ' ')}`);
                return false;
            }
        }
        return true;
    }

    showPreferencesForm() {
        this.hideAllSections();
        this.preferenceSection.classList.remove('hidden');
    }

    showLoadingState() {
        this.hideAllSections();
        this.loadingSection.classList.remove('hidden');
        this.animateProgress();
    }

    animateProgress() {
        const progressSteps = [
            { progress: 20, text: 'Analyzing your preferences...' },
            { progress: 40, text: 'Searching restaurants...' },
            { progress: 60, text: 'Filtering candidates...' },
            { progress: 80, text: 'AI ranking in progress...' },
            { progress: 100, text: 'Finalizing recommendations...' }
        ];

        let stepIndex = 0;
        const interval = setInterval(() => {
            if (stepIndex < progressSteps.length) {
                const step = progressSteps[stepIndex];
                this.progressFill.style.width = `${step.progress}%`;
                this.progressText.textContent = step.text;
                stepIndex++;
            } else {
                clearInterval(interval);
            }
        }, 600);
    }

    async fetchRecommendations(preferences) {
        // Dynamic Base URL: Use Vercel proxy (/api) if deployed, else localhost
        const isLocal = window.location.hostname === '127.0.0.1' || window.location.hostname === 'localhost';
        const API_BASE_URL = isLocal ? 'http://127.0.0.1:8500' : '/api';

        try {
            const response = await fetch(`${API_BASE_URL}/recommendations`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(preferences)
            });

            if (!response.ok) {
                if (response.status === 404) {
                    throw new Error('No restaurant found for the given criteria. Please try relaxing your filters.');
                }
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            const data = await response.json();
            this.currentRecommendations = data.recommendations;
            this.showResults(data);
        } catch (error) {
            console.error('Error fetching recommendations:', error);
            if (error.message.includes('No restaurant found')) {
                this.showError(error.message);
            } else {
                this.showError('Unable to fetch recommendations. Please check your internet connection and try again.');
            }
        }
    }

    showResults(data) {
        this.hideAllSections();
        this.resultsSection.classList.remove('hidden');

        // Update results summary
        this.updateResultsSummary(data);

        // Render recommendation cards
        this.renderRecommendationCards(data.recommendations, data.candidate_lookup);
    }

    updateResultsSummary(data) {
        const summary = `Found ${data.total_candidates_considered} restaurants, showing top ${data.recommendations.length} recommendations`;
        if (data.used_fallback) {
            this.resultsSummary.textContent = `${summary} (Using smart filtering)`;
        } else {
            this.resultsSummary.textContent = `${summary} (AI-powered recommendations)`;
        }
    }

    renderRecommendationCards(recommendations, candidateLookup) {
        this.recommendationsGrid.innerHTML = '';

        recommendations.forEach((recommendation, index) => {
            const restaurant = candidateLookup.find(r => r.restaurant_id === recommendation.restaurant_id);
            if (!restaurant) return;

            const card = this.createRecommendationCard(restaurant, recommendation, index + 1);
            this.recommendationsGrid.appendChild(card);
        });
    }

    createRecommendationCard(restaurant, recommendation, rank) {
        const card = document.createElement('div');
        card.className = 'recommendation-card';
        card.dataset.restaurantId = restaurant.restaurant_id;

        const cuisines = restaurant.cuisines.slice(0, 3).join(', ');
        const rating = restaurant.rating.toFixed(1);
        const cost = restaurant.average_cost_for_two;

        card.innerHTML = `
            <div class="recommendation-header">
                <div>
                    <div class="restaurant-name">${rank}. ${restaurant.name}</div>
                    <div class="restaurant-location">📍 ${restaurant.location}, ${restaurant.city}</div>
                </div>
                <div class="rating-badge">
                    <span class="stars">⭐</span>
                    <span>${rating}</span>
                </div>
            </div>
            
            <div class="restaurant-meta">
                <div class="meta-item">
                    <span>💰</span>
                    <span>₹${cost} for two</span>
                </div>
                <div class="meta-item">
                    <span>👥</span>
                    <span>${restaurant.votes} votes</span>
                </div>
            </div>
            
            <div class="cuisine-tags">
                ${restaurant.cuisines.map(cuisine => 
                    `<span class="cuisine-tag">${cuisine}</span>`
                ).join('')}
            </div>
            
            <div class="explanation">
                <div class="explanation-title">🤖 Why this restaurant?</div>
                <div class="explanation-text">${recommendation.explanation}</div>
            </div>
            
            <div class="feedback-section">
                <div class="feedback-buttons">
                    <button class="feedback-btn helpful" data-restaurant-id="${restaurant.restaurant_id}" data-feedback="helpful">
                        👍 Helpful
                    </button>
                    <button class="feedback-btn not-helpful" data-restaurant-id="${restaurant.restaurant_id}" data-feedback="not-helpful">
                        👎 Not Helpful
                    </button>
                </div>
                <small class="feedback-status" id="feedback-${restaurant.restaurant_id}"></small>
            </div>
        `;

        // Bind feedback events
        this.bindFeedbackEvents(card);
        
        return card;
    }

    bindFeedbackEvents(card) {
        const feedbackButtons = card.querySelectorAll('.feedback-btn');
        
        feedbackButtons.forEach(button => {
            button.addEventListener('click', (e) => {
                const restaurantId = e.target.dataset.restaurantId;
                const feedback = e.target.dataset.feedback;
                this.handleFeedback(restaurantId, feedback, e.target);
            });
        });
    }

    async handleFeedback(restaurantId, feedback, buttonElement) {
        try {
            const response = await fetch('http://127.0.0.1:8500/feedback', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    restaurant_id: restaurantId,
                    feedback: feedback,
                    preferences: this.currentPreferences,
                    timestamp: new Date().toISOString()
                })
            });

            if (!response.ok) {
                throw new Error('Failed to submit feedback');
            }

            // Update UI
            const feedbackStatus = document.getElementById(`feedback-${restaurantId}`);
            const buttons = buttonElement.parentElement.querySelectorAll('.feedback-btn');
            
            buttons.forEach(btn => btn.disabled = true);
            
            if (feedback === 'helpful') {
                buttonElement.style.background = 'var(--success-color)';
                buttonElement.style.color = 'white';
                buttonElement.style.borderColor = 'var(--success-color)';
                feedbackStatus.textContent = '✓ Thanks for your feedback!';
                feedbackStatus.style.color = 'var(--success-color)';
            } else {
                buttonElement.style.background = 'var(--error-color)';
                buttonElement.style.color = 'white';
                buttonElement.style.borderColor = 'var(--error-color)';
                feedbackStatus.textContent = '✓ Thanks for helping us improve!';
                feedbackStatus.style.color = 'var(--text-secondary)';
            }

        } catch (error) {
            console.error('Error submitting feedback:', error);
            const feedbackStatus = document.getElementById(`feedback-${restaurantId}`);
            feedbackStatus.textContent = 'Failed to submit feedback';
            feedbackStatus.style.color = 'var(--error-color)';
        }
    }

    regenerateRecommendations() {
        if (Object.keys(this.currentPreferences).length > 0) {
            this.showLoadingState();
            this.fetchRecommendations(this.currentPreferences);
        } else {
            this.showPreferencesForm();
        }
    }

    showError(message) {
        this.hideAllSections();
        this.errorSection.classList.remove('hidden');
        
        const errorMessage = document.getElementById('error-message');
        errorMessage.textContent = message;
    }

    hideAllSections() {
        this.preferenceSection.classList.add('hidden');
        this.loadingSection.classList.add('hidden');
        this.resultsSection.classList.add('hidden');
        this.errorSection.classList.add('hidden');
    }
}

// Initialize the app when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    new RestaurantRecommendationApp();
});

// Add some utility functions
function formatCurrency(amount) {
    return new Intl.NumberFormat('en-IN', {
        style: 'currency',
        currency: 'INR',
        maximumFractionDigits: 0
    }).format(amount);
}

function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}
