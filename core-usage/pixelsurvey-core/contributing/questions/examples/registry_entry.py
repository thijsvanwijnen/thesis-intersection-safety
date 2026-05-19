# Add these lines to generators/elements/questionnaire/questionnaire_gen.py

# 1. Import your class at the top
from .questions.likert_scale_gen import LikertScaleCard

# 2. Add it to the QUESTION_REGISTRY dictionary
QUESTION_REGISTRY = {
    'multiple_choice': MultipleChoiceCard,
    'open_text': OpenTextCard,
    'likert_scale': LikertScaleCard  # Your new type here!
}
