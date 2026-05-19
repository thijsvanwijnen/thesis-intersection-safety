from .questions.multiple_choice_gen import MultipleChoiceCard
from .questions.open_text_gen import OpenTextCard

QUESTION_REGISTRY = {
    'multiple_choice': MultipleChoiceCard,
    'open_text': OpenTextCard
}

class QuestionnaireCards:
    """Class to generate questionnaire cards code"""

    @staticmethod
    def generate_questionnaire_content(questions_list):
        """Generate both cards layout and callbacks code for a list of questions"""
        layouts = []
        callbacks = []
        
        for question in questions_list:
            q_type = question.get('type')
            if q_type in QUESTION_REGISTRY:
                CardClass = QUESTION_REGISTRY[q_type]
                generator = CardClass(question)
                
                # Get layout
                layouts.append(generator.generate())
                
                # Get optional callbacks
                if hasattr(generator, 'generate_callbacks'):
                    callbacks.append(generator.generate_callbacks())
            else:
                raise ValueError(f"Question type '{q_type}' is not supported. Please register it in QUESTION_REGISTRY.")
        
        layout_code = ",\n        ".join(layouts)
        callback_code = "\n\n".join(callbacks)
        
        return layout_code, callback_code
