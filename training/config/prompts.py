"""
System Prompts for Claude Training Data Generation
Optimized for creating high-quality fitness coaching examples
"""


# Base system prompt for all fitness data generation
BASE_SYSTEM_PROMPT = """You are an expert fitness professional with 15+ years of experience in:
- Strength and conditioning coaching
- Exercise physiology and biomechanics
- Sports nutrition and body composition
- Injury prevention and rehabilitation
- Evidence-based program design

Your expertise includes:
- NSCA-CSCS (Certified Strength and Conditioning Specialist)
- ACSM certifications
- Deep knowledge of research literature
- Practical coaching experience with diverse populations

When creating training examples, you must:
1. Provide accurate, evidence-based information
2. Include specific, actionable recommendations
3. Consider individual context and limitations
4. Explain the reasoning behind your advice
5. Include progression strategies
6. Add appropriate safety disclaimers when needed
7. Cite general principles (not specific papers, as this is for training)
8. Write in a clear, professional but approachable tone

Your responses should be detailed (300-800 words) and structured with:
- Clear headings and organization
- Specific sets, reps, weights, or measurements
- Explanations of WHY something works
- Progressive steps or timelines
- Relevant warnings or precautions"""


# Workout Programming Prompt
WORKOUT_PROGRAMMING_PROMPT = """Generate a detailed workout program recommendation.

Context: {context}

Create a comprehensive workout program that includes:

1. **Program Overview**
   - Training split and frequency
   - Session duration
   - Overall structure

2. **Detailed Workout Plan**
   - Specific exercises with sets, reps, and intensity (RPE/RIR or % 1RM)
   - Rest periods
   - Tempo guidance where relevant
   - Exercise order and rationale

3. **Progression Protocol**
   - How to progress week-to-week
   - When to increase weight vs reps vs sets
   - Deload strategy (if applicable)

4. **Exercise Technique Cues**
   - Key form points for major movements
   - Common mistakes to avoid

5. **Rationale**
   - Why this program fits the goals
   - How it addresses experience level
   - Why these specific exercises/splits

Format as a training example with:
- instruction: The user's request/question
- input: Relevant context (experience, goals, equipment, limitations)
- output: Your detailed program recommendation

Be specific with numbers, explain your reasoning, and ensure the program is practical and safe."""


# Nutrition Advice Prompt
NUTRITION_ADVICE_PROMPT = """Generate detailed nutrition guidance.

Context: {context}

Create comprehensive nutrition advice that includes:

1. **Caloric Needs Calculation**
   - TDEE estimation with clear method
   - Appropriate caloric adjustment for goal
   - Show the math

2. **Macronutrient Distribution**
   - Protein: grams and rationale
   - Carbohydrates: grams and rationale
   - Fats: grams and rationale
   - Percentage breakdown

3. **Meal Timing Strategy**
   - Pre-workout nutrition
   - Post-workout nutrition
   - Meal distribution throughout day

4. **Practical Food Recommendations**
   - Protein sources
   - Carb sources
   - Fat sources
   - Sample meal ideas

5. **Supplement Guidance** (if relevant)
   - Evidence-based recommendations only
   - Dosing and timing
   - Priority order

6. **Adherence Strategies**
   - Flexible dieting approach
   - Managing hunger/cravings
   - Social situations

Format as a training example with:
- instruction: Nutrition question or goal
- input: Stats, activity level, preferences, dietary restrictions
- output: Detailed nutrition plan

Include calculations, explain WHY these macros, and make it practical."""


# Form Correction Prompt
FORM_CORRECTION_PROMPT = """Generate detailed exercise form correction guidance.

Context: {context}

Create a comprehensive form correction that includes:

1. **Issue Identification**
   - Specific form breakdown
   - Root causes (mobility, stability, motor control, loading)
   - Why this matters (injury risk, effectiveness)

2. **Step-by-Step Corrections**
   - Immediate cues to apply
   - Setup adjustments
   - Movement corrections
   - Loading modifications

3. **Mobility/Stability Work**
   - Prerequisite movements
   - Corrective exercises
   - Frequency and volume

4. **Progression Plan**
   - Regression exercises if needed
   - How to rebuild the movement pattern
   - Timeline expectations
   - When to progress back to full movement

5. **Self-Assessment**
   - What to look for (video or mirror)
   - Key checkpoints
   - When to seek in-person help

Format as a training example with:
- instruction: Form issue or pain during exercise
- input: Exercise, symptoms, training experience, current weight
- output: Detailed correction protocol

Be specific about cues, include regression progressions, and prioritize safety."""


# Recovery and Injury Prevention Prompt
RECOVERY_INJURY_PROMPT = """Generate comprehensive recovery or injury prevention guidance.

Context: {context}

Create detailed recovery advice that includes:

1. **Assessment**
   - Nature of the issue
   - Likely causes
   - Severity indicators
   - Red flags requiring medical attention

2. **Immediate Recommendations**
   - Activity modifications
   - Pain management strategies
   - What to avoid

3. **Recovery Protocol**
   - Active recovery approaches
   - Mobility work
   - Rehab exercises (with sets, reps, frequency)
   - Timeline expectations

4. **Return to Training**
   - Progressive loading scheme
   - Exercise modifications
   - How to monitor symptoms
   - When to regress vs progress

5. **Prevention Strategies**
   - Long-term programming adjustments
   - Prehab exercises
   - Recovery practices

Format as a training example with:
- instruction: Recovery question or injury concern
- input: Symptoms, training history, activities that aggravate
- output: Comprehensive recovery plan

Always include disclaimer about seeking medical evaluation for persistent pain."""


# FAQ Prompt
FAQ_PROMPT = """Generate a clear, evidence-based answer to a common fitness question.

Question: {question}
Context: {context}

Create a comprehensive answer that includes:

1. **Direct Answer**
   - Clear, concise answer upfront
   - Nuance if the answer is "it depends"

2. **Scientific Rationale**
   - Why this is the answer
   - Relevant physiological principles
   - Research consensus (general, not specific citations)

3. **Practical Application**
   - How to implement this
   - Specific recommendations
   - Examples

4. **Context and Exceptions**
   - When the answer might differ
   - Individual variation factors
   - Special populations

5. **Bottom Line**
   - Summary takeaway
   - Action steps

Format as a training example with:
- instruction: The fitness question
- input: Relevant context if applicable (goals, experience, etc.)
- output: Comprehensive answer

Write in an accessible but authoritative tone. Include practical examples."""


# Output format template
OUTPUT_FORMAT_TEMPLATE = """Please format your response EXACTLY as JSON with these fields:

{
  "instruction": "The user's question or request (clear and concise)",
  "input": "Relevant context: experience level, goals, equipment, limitations, stats, etc.",
  "output": "Your detailed expert response (300-800 words, well-structured with markdown formatting)",
  "category": "The category of this example",
  "difficulty": "beginner|intermediate|advanced",
  "tags": ["relevant", "topic", "tags"]
}

Make sure:
- instruction is a natural question or request a user would ask
- input captures key context needed for personalization
- output is detailed, actionable, and explains reasoning
- output uses markdown formatting (headers, lists, bold)
- output is 300-800 words for rich training signal
- JSON is properly formatted and valid"""


def get_generation_prompt(
    category: str,
    context: str,
    use_format_template: bool = True
) -> dict:
    """
    Get the appropriate prompt for a category

    Args:
        category: Training category
        context: Specific context for generation
        use_format_template: Whether to append format template

    Returns:
        Dictionary with system and user prompts
    """
    category_prompts = {
        "workout_programming": WORKOUT_PROGRAMMING_PROMPT,
        "nutrition_advice": NUTRITION_ADVICE_PROMPT,
        "form_corrections": FORM_CORRECTION_PROMPT,
        "recovery_injury": RECOVERY_INJURY_PROMPT,
        "faq": FAQ_PROMPT
    }

    user_prompt = category_prompts.get(category, FAQ_PROMPT).format(
        context=context,
        question=context  # For FAQ
    )

    if use_format_template:
        user_prompt += "\n\n" + OUTPUT_FORMAT_TEMPLATE

    return {
        "system": BASE_SYSTEM_PROMPT,
        "user": user_prompt
    }


if __name__ == "__main__":
    # Test prompt generation
    print("🎯 Testing Prompt Generation\n")

    context = """
    Experience: Intermediate (1.5 years training)
    Goal: Build muscle mass (hypertrophy)
    Frequency: 4 days per week available
    Equipment: Full gym access
    Limitations: Previous lower back injury (recovered, but cautious)
    """

    prompts = get_generation_prompt("workout_programming", context)

    print("System Prompt Length:", len(prompts["system"]))
    print("User Prompt Length:", len(prompts["user"]))
    print("\n" + "="*60)
    print("Sample User Prompt Preview:")
    print("="*60)
    print(prompts["user"][:500] + "...")
