def generate_mcqs(topics):
    # Mock generation of 5 MCQs based on selected topics
    mcqs = [
        {
            "question": f"What is related to {topic}?",
            "options": ["Option A", "Option B", "Option C", "Option D"],
            "correct_option": "Option A"
        }
        for topic in topics[:4]  # Just take the first 5 topics for demo
    ]
    return mcqs
