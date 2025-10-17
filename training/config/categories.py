"""
Training Data Categories and Distribution
Defines the structure and variety of training examples
"""

from enum import Enum
from typing import List, Dict


class TrainingCategory(Enum):
    """Main categories for training data"""
    WORKOUT_PROGRAMMING = "workout_programming"
    NUTRITION_ADVICE = "nutrition_advice"
    FORM_CORRECTIONS = "form_corrections"
    RECOVERY_INJURY = "recovery_injury"
    FAQ = "faq"


class ExperienceLevel(Enum):
    """User experience levels"""
    BEGINNER = "beginner"  # 0-6 months
    INTERMEDIATE = "intermediate"  # 6 months - 2 years
    ADVANCED = "advanced"  # 2+ years


class FitnessGoal(Enum):
    """Primary fitness goals"""
    STRENGTH = "strength"
    HYPERTROPHY = "hypertrophy"
    ENDURANCE = "endurance"
    WEIGHT_LOSS = "weight_loss"
    ATHLETIC_PERFORMANCE = "athletic_performance"
    GENERAL_FITNESS = "general_fitness"


class EquipmentType(Enum):
    """Available equipment"""
    FULL_GYM = "full_gym"
    HOME_GYM = "home_gym"
    MINIMAL = "minimal"
    BODYWEIGHT = "bodyweight"


# Distribution targets for 1500 examples
CATEGORY_DISTRIBUTION = {
    TrainingCategory.WORKOUT_PROGRAMMING: {
        "count": 400,
        "subcategories": {
            "program_design": 150,
            "exercise_selection": 80,
            "periodization": 70,
            "progression": 60,
            "deloads": 40
        }
    },
    TrainingCategory.NUTRITION_ADVICE: {
        "count": 300,
        "subcategories": {
            "macro_calculation": 80,
            "cutting": 60,
            "bulking": 60,
            "maintenance": 40,
            "meal_timing": 30,
            "supplements": 30
        }
    },
    TrainingCategory.FORM_CORRECTIONS: {
        "count": 200,
        "subcategories": {
            "squat": 40,
            "deadlift": 40,
            "bench_press": 30,
            "overhead_press": 25,
            "rows": 25,
            "pullups": 20,
            "accessories": 20
        }
    },
    TrainingCategory.RECOVERY_INJURY: {
        "count": 300,
        "subcategories": {
            "injury_prevention": 80,
            "recovery_protocols": 70,
            "pain_management": 60,
            "mobility_work": 50,
            "return_to_training": 40
        }
    },
    TrainingCategory.FAQ: {
        "count": 300,
        "subcategories": {
            "training_frequency": 60,
            "cardio_timing": 50,
            "muscle_soreness": 40,
            "plateaus": 40,
            "lifestyle_factors": 60,
            "common_myths": 50
        }
    }
}


# Workout programming variations
WORKOUT_VARIATIONS = {
    "splits": [
        "full_body",
        "upper_lower",
        "push_pull_legs",
        "body_part_split",
        "upper_lower_full"
    ],
    "frequencies": [2, 3, 4, 5, 6],  # days per week
    "goals": [goal.value for goal in FitnessGoal],
    "experience": [level.value for level in ExperienceLevel],
    "equipment": [eq.value for eq in EquipmentType]
}


# Nutrition variations
NUTRITION_VARIATIONS = {
    "goals": ["cutting", "bulking", "maintenance", "recomposition"],
    "dietary_preferences": [
        "standard",
        "vegetarian",
        "vegan",
        "keto",
        "intermittent_fasting",
        "paleo"
    ],
    "activity_levels": [
        "sedentary",
        "lightly_active",
        "moderately_active",
        "very_active",
        "extremely_active"
    ]
}


# Major exercises for form corrections
MAJOR_EXERCISES = {
    "lower_body": [
        "squat",
        "front_squat",
        "deadlift",
        "romanian_deadlift",
        "bulgarian_split_squat",
        "leg_press",
        "lunges"
    ],
    "upper_body_push": [
        "bench_press",
        "incline_bench",
        "overhead_press",
        "dips",
        "push_ups"
    ],
    "upper_body_pull": [
        "pull_ups",
        "chin_ups",
        "barbell_rows",
        "dumbbell_rows",
        "lat_pulldowns"
    ],
    "accessories": [
        "bicep_curls",
        "tricep_extensions",
        "lateral_raises",
        "face_pulls",
        "calf_raises"
    ]
}


# Common injuries and pain points
INJURY_TOPICS = [
    "lower_back_pain",
    "knee_pain",
    "shoulder_impingement",
    "elbow_tendinitis",
    "wrist_pain",
    "hip_flexor_strain",
    "muscle_strains",
    "overtraining_syndrome"
]


# FAQ categories
FAQ_CATEGORIES = {
    "training": [
        "how_often_to_train",
        "rest_days",
        "cardio_vs_weights",
        "morning_vs_evening",
        "fasted_training"
    ],
    "progress": [
        "how_long_to_see_results",
        "breaking_plateaus",
        "tracking_progress",
        "strength_vs_size_gains"
    ],
    "lifestyle": [
        "sleep_and_recovery",
        "stress_management",
        "alcohol_effects",
        "training_while_sick"
    ],
    "nutrition": [
        "protein_timing",
        "pre_workout_meals",
        "post_workout_nutrition",
        "cheat_meals"
    ]
}


def get_category_stats() -> Dict:
    """Get statistics about category distribution"""
    total = sum(cat["count"] for cat in CATEGORY_DISTRIBUTION.values())

    stats = {
        "total_examples": total,
        "categories": {}
    }

    for category, info in CATEGORY_DISTRIBUTION.items():
        stats["categories"][category.value] = {
            "count": info["count"],
            "percentage": f"{(info['count'] / total * 100):.1f}%",
            "subcategories": len(info["subcategories"])
        }

    return stats


if __name__ == "__main__":
    print("📊 Training Data Distribution Plan\n")

    stats = get_category_stats()
    print(f"Total Examples: {stats['total_examples']}\n")

    for category, info in stats["categories"].items():
        print(f"{category.replace('_', ' ').title()}:")
        print(f"  Count: {info['count']}")
        print(f"  Percentage: {info['percentage']}")
        print(f"  Subcategories: {info['subcategories']}\n")
