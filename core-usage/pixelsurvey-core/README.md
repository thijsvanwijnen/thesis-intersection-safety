# PixelSurvey Core

A Python-based survey generation system that creates structured Dash web applications for research studies using YAML configuration files.

## 📋 Survey Architecture

Every PixelSurvey follows a **standardized 3-section architecture** designed for user experience and data collection:

- **Onboarding**: 
  - 🏠 Home - Welcome and study overview
  - 📜 Consent - Informed consent with validation
  - 🔍 Screening - Participants eligibility
- **Body**: 
  - 🧭 Instructions - Study guidance and preparation
  - 📖 Activities:
    - 🔬 Experiment - Interactive research tasks
    - 📝 Questionnaire - Survey questions  
- **Closure**: 
  - 🏁 End - Completion and thank you

This architecture ensures **consistency across studies** while providing **flexibility** in the main research content (Body section).

---

## 📄 YAML Configuration Structure

The PixelSurvey configuration uses a hierarchical YAML structure that defines every aspect of your survey, from metadata to detailed page content.

---

### 1. Survey Metadata

Essential information that appears throughout your survey interface and defines the visual identity:

```yaml
survey:
  banner:
    name: "My Survey"
    title: "My Survey Title"
    subtitle: "My Survey Subtitle"
    logo: "logo.png"
    color: "#00A6D6"
  sections:
    ...
```

### 2. Survey Sections

Every PixelSurvey **must contain exactly three sections** in this specific order to ensure proper flow and data collection:

```yaml
survey:
  ...
  sections:
    onboarding:
      ...
    body:
      ...
    closure:
      ...
```

#### 2.1. Onboarding Section

The **Onboarding section** prepares participants for the study through a standardized sequence of three mandatory pages. This section establishes trust, obtains consent, and ensures participant eligibility.

```yaml
survey:
  ...
  sections:
    onboarding:
      home:
        ...
      consent:
        ...
      screening:
        ...
```

##### 2.1.1 🏠 Home Page

The **entry point** of your survey that welcomes participants and provides essential study information. Content is provided in Markdown format, allowing for rich text formatting including headers, lists, and emphasis.

```yaml
home:
  content: home_content.md
```

##### 2.1.2 📜 Consent Page

**Critical for ethical research compliance.** This page presents the informed consent information and requires explicit participant agreement before proceeding. The consent statement creates a mandatory checkbox that participants must check to continue.

```yaml
consent:
  content: consent_content.md
  consent_statement: "I have read and agree to the terms and conditions"
```

##### 2.1.3 🔍 Screening Page

**Determines participant eligibility** through a series of multiple-choice questions. This page filters participants based on your study criteria and ensures data quality. Only participants who meet your screening requirements (quotas) can proceed to the main study. Here also you can choose between three quotas versions: 'no_limit', 'uniform', or 'custom'.

```yaml
screening:
  content: screening_content.md
  questions:
    - id: 1
      ...
    - id: 2
      ...
  quotas:
      ...
```

*Quotas options*
**no_limit** - There no restrictions for respondents
```yaml
  ...
  quotas:
    method: no_limit
    fullquota_content:  |
          # Thank you for your interest
          However, you are not eligible for continuing replying this survey
```
**uniform** - Every bin is limited by a value
```yaml
  ...
  quotas:
    method: uniform
    limit: 100
    fullquota_content:  |
          # Thank you for your interest
          However, you are not eligible for continuing replying this survey
```

**custom** - You can submit
```yaml
  ...
  quotas:
    method: custom 
    limit: assets/quotas.csv
    fullquota_content:  |
          # Thank you for your interest
          However, you are not eligible for continuing replying this survey
```

#### 2.2. Body Section

The **core research content** where your actual data collection occurs. This section is **highly flexible** and can contain multiple activities in any order. Every Body section must begin with instructions, followed by your choice of experiments and questionnaires.

```yaml
survey:
  ...
  sections:
    ...
    body:
       instructions:
          ...
       activity_1:
         order: i
         type: experiment
         ...
       activity_2:
         order: i
         type: experiment
         ...
       activity_3: 
         order: i
         type: questionnaire
         ...
```

##### 2.2.1 🧭 Instructions Page

**Mandatory first page** of the Body section that prepares participants for the research tasks ahead. This page should clearly explain what participants will be doing, how to interact with different elements, and what is expected of them.

```yaml
instructions:
  content: instructions_content.md
```

##### 2.2.2 Activity Page: 🔬 Experiments

**Interactive research tasks** designed for behavioral studies and preference elicitation. PixelSurvey supports three validated experimental paradigms, each optimized for different research questions:

**Experiment Types Available:**
 
- **Stated Choice Experiment (SC)** - *Preference through choice tasks*
 ```yaml
  activity_i:
    order: i
    type: experiment
    experiment_type: stated_choice
    persistent_instructions: sc_instructions.md
    task:
      query: "Which option do you prefer?"
      instance: "Instance"
      n_alternatives: 2
      attributes:
        - label: "Attribute 1"
          type: standard
          unit: "unit"
        - label: "Attribute 2"
          type: image
          unit: "image"
```
*Experimental design options:*
**Random Design** - Attributes are randomized automatically:
```yaml
    ...
    settings:
      tasks_per_respondent: 8
      experimental_design_mode: random
      number_of_sets: 100 
      attributes_values: attributes_values.csv
```
**Custom Design** - Use your own experimental design:
 ```yaml
    ...
    settings:
      tasks_per_respondent: 8
      experimental_design_mode: custom 
      custom_design: custom_design.csv
```

 - **Similarity Judgment Experiment (SJ)** - *Perceptual similarity and categorization tasks*
 ```yaml
  activity_i:
    order: i
    type: experiment
    experiment_type: similarity_judgment
    persistent_instructions: sj_instructions.md
    task:
      query: "Which is the odd one out?"
      instance: "Instance"
      images_per_instance: 3
```
*Experimental design options:*
**Random Design** - Attributes are randomized automatically:
```yaml
    ...
    settings:
      tasks_per_respondent: 8
      experimental_design_mode: random
      number_of_sets: 100
      instances: instances.csv 
```
**Custom Design** - Use your own experimental design:
 ```yaml
    ...
    settings:
      tasks_per_respondent: 8
      experimental_design_mode: custom 
      custom_design: custom_design.csv
```

 - **Likert Scale Experiment (LS)** - *Attitude and perception rating tasks*
 ```yaml
  activity_i:
    order: i
    type: experiment
    experiment_type: likert_scale
    persistent_instructions: ls_instructions.md
    task:
      query: "How much do you agree with the following statement?"
      instance: "Instance"
      likert_scale: 5
      evaluations:
        - label: "Criteria 1"
        - label: "Criteria 2"
```
*Experimental design options:*
**Random Design** - Attributes are randomized automatically:
```yaml
    ...
    settings:
      tasks_per_respondent: 8
      experimental_design_mode: random
      number_of_sets: 100
      instances: instances.csv 
```
**Custom Design** - Use your own experimental design:
 ```yaml
    ...
    settings:
      tasks_per_respondent: 8
      experimental_design_mode: custom 
      custom_design: custom_design.csv
```

##### 2.2.3 Activity Page: 📝 Questionnaire

**Traditional survey questions** for collecting demographic data, opinions, and structured responses. Questionnaires support two question types and can be used multiple times throughout your study.

 ```yaml
  activity_i:
    order: i
    type: questionnaire
    persistent_instructions: q_instructions.md
    questions:
      questions:
        - id: 1
          ...
        - id: 2
          ...
```
**Question Types Available:**

*Multiple Choice Questions* - Radio buttons, checkboxes, or dropdown selections (also used in screening):
 ```yaml
questions:
  - id: 1
    type: multiple_choice
    order: 1
    question: "Question 1?"
    alternatives:
      - "option 1"
      - "option 2"
      - "option 3"
    required: true
    variable_name: question
```

*Open Text Questions* - Free-form text input for qualitative responses:
 ```yaml
questions:
  - id: 1
    type: open_text
    order: 1
    question: "Question 1?"
    required: true
    variable_name: question
```

*Likert Scale Questions* - Table-based rating for multiple items:
 ```yaml
questions:
  - id: 1
    type: likert_scale
    order: 1
    question: "Evaluate the comfort of these items (1=Low, 3=High)"
    likert_scale: 3
    evaluations:
      - label: "sofa"
      - label: "bed"
    required: true
    variable_name: furniture_comfort
```

#### 2.3. Closure Section

The **final section** that provides closure to the research experience. This section contains a single page that thanks participants and provides any necessary follow-up information.

```yaml
survey:
  ...
  sections:
    ...
    closure:
      end:
      ...
```

##### 2.3.1 🏁 End Page

**Final thank you page** that concludes the participant's journey. Use this space to thank participants, provide contact information for questions, and include any necessary debriefing information.

```yaml
end:
  content: end_content.md
```

---

## 📋 Complete YAML Example

Here's a comprehensive example showing all components working together in a fruit preferences research study:

```yaml
survey:
  name: "Fruit Preferences Study"
  title: "Understanding Consumer Preferences for Fresh Fruits"
  subtitle: "A comprehensive study on fruit consumption patterns and preferences"
  logo: "fruit_logo.png"
  color: "#FF6B35"
  
  sections:
    onboarding:
      home:
        content: |
          # Welcome to the Fruit Preferences Study! 🍎🍌🍊
          
          ## About This Research
          We are conducting a comprehensive study to understand consumer preferences for fresh fruits. Your participation will help us better understand:
          
          - Fruit purchasing decisions
          - Preference patterns across different demographics
          - Factors that influence fruit consumption
          
          ## What to Expect
          This study will take approximately **15-20 minutes** and consists of:
          - Brief screening questions
          - Interactive preference tasks
          - Questions about your fruit consumption habits
          
          ## Compensation
          Participants will receive **$5** upon completion.
          
          Your responses are completely **anonymous** and will only be used for research purposes.

      consent:
        content: |
          # Informed Consent
          
          ## Purpose of the Study
          This research studies consumer preferences for fresh fruits to understand purchasing decisions and consumption patterns.
          
          ## Procedures
          You will be asked to:
          - Answer questions about your demographics and fruit consumption
          - Complete preference tasks involving fruit images and attributes
          - Provide opinions about fruit characteristics
          
          ## Risks and Benefits
          There are no known risks to participation. Results may contribute to better understanding of consumer preferences.
          
          ## Confidentiality
          All responses are anonymous. No personal identifying information will be collected.
          
          ## Contact Information
          For questions, contact: researcher@university.edu
          
        consent_statement: "I have read and understood the information above and consent to participate in this research study"

      screening:
        content: |
          # Participant Screening
          
          Please answer the following questions to determine your eligibility for this study.
          
        questions:
          - id: 1
            type: multiple_choice
            order: 1
            question: "What is your age group?"
            alternatives:
              - "18-25"
              - "26-35"
              - "36-45"
              - "46-55"
              - "56-65"
              - "Over 65"
            required: true
            variable_name: age_group

          - id: 2
            type: multiple_choice
            order: 2
            question: "What is your gender?"
            alternatives:
              - "Male"
              - "Female"
              - "Non-binary"
              - "Prefer not to say"
            required: true
            variable_name: gender

          - id: 3
            type: multiple_choice
            order: 3
            question: "Which continent do you currently live in?"
            alternatives:
              - "North America"
              - "South America"
              - "Europe"
              - "Asia"
              - "Africa"
              - "Australia/Oceania"
            required: true
            variable_name: continent

        quotas: quotas.csv

    body:
      instructions:
        content: |
          # Study Instructions
          
          You will now complete several activities related to fruit preferences. Please read the instructions carefully for each section.
          
          ## Types of Activities
          
          1. **Choice Tasks**: You'll see different fruit options and choose your preference
          2. **Similarity Tasks**: You'll identify similarities between fruit images
          3. **Rating Tasks**: You'll rate fruits on different characteristics
          4. **Questions**: You'll answer questions about your fruit consumption habits
          
          Take your time and answer based on your honest preferences.

      activity_1:
        order: 1
        type: experiment
        experiment_type: stated_choice
        persistent_instructions: |
          ## Fruit Choice Task - Random Design
          
          You will see pairs of fruits with different characteristics. Please choose the fruit you would prefer to purchase.
          
        task:
          query: "Which fruit would you prefer to purchase?"
          n_alternatives: 2
          attributes:
            - label: "Fruit Image"
              type: image
            - label: "Size"
              type: standard
            - label: "Price per lb"
              type: standard
        settings:
          tasks_per_respondent: 8
          experimental_design_mode: random
          attribute_values: fruit_sc_random_values.csv

      activity_2:
        order: 2
        type: experiment
        experiment_type: stated_choice
        persistent_instructions: |
          ## Fruit Choice Task - Custom Design
          
          You will see pairs of fruits with availability and freshness information. Choose your preference.
          
        task:
          query: "Which fruit would you choose based on availability and freshness?"
          n_alternatives: 2
          attributes:
            - label: "Fruit Image"
              type: image
            - label: "Available Locations"
              type: standard
            - label: "Days Until Expiration"
              type: standard
        settings:
          tasks_per_respondent: 8
          experimental_design_mode: custom
          custom_design: fruit_sc_custom_design.csv

      activity_3:
        order: 3
        type: experiment
        experiment_type: similarity_judgment
        persistent_instructions: |
          ## Fruit Similarity Task - Random Design
          
          You will see sets of fruit images. Please identify which fruit is most different from the others.
          
        task:
          query: "Which fruit is the odd one out?"
          images_per_instance: 2
        settings:
          tasks_per_respondent: 8
          experimental_design_mode: random
          instances: fruit_sj_random_instances.csv

      activity_4:
        order: 4
        type: experiment
        experiment_type: similarity_judgment
        persistent_instructions: |
          ## Fruit Similarity Task - Custom Design
          
          Look at the fruit image and compare it with others in your mind.
          
        task:
          query: "How similar is this fruit to your ideal fruit?"
          images_per_instance: 1
        settings:
          tasks_per_respondent: 8
          experimental_design_mode: custom
          custom_design: fruit_sj_custom_design.csv

      activity_5:
        order: 5
        type: experiment
        experiment_type: likert_scale
        persistent_instructions: |
          ## Fruit Rating Task - Random Design
          
          You will rate fruits on different taste characteristics using a 5-point scale.
          
        task:
          query: "Please rate this fruit on the following characteristics:"
          likert_scale: 5
          evaluations:
            - label: "Flavor Intensity"
            - label: "Color Appeal"
        settings:
          tasks_per_respondent: 8
          experimental_design_mode: random
          instances: fruit_ls_random_instances.csv

      activity_6:
        order: 6
        type: experiment
        experiment_type: likert_scale
        persistent_instructions: |
          ## Fruit Rating Task - Custom Design
          
          Rate fruits on specific taste characteristics using a 3-point scale.
          
        task:
          query: "Please rate this fruit on the following taste characteristics:"
          likert_scale: 3
          evaluations:
            - label: "Acidity Level"
            - label: "Sweetness Level"
        settings:
          tasks_per_respondent: 8
          experimental_design_mode: custom
          custom_design: fruit_ls_custom_design.csv

      activity_7:
        order: 7
        type: questionnaire
        persistent_instructions: |
          ## Background Questions
          
          Please answer the following questions about your fruit consumption habits and preferences.
          
        questions:
          - id: 1
            type: multiple_choice
            order: 1
            question: "What is your household's socioeconomic status?"
            alternatives:
              - "Low income (Under $25,000)"
              - "Lower-middle income ($25,000-$49,999)"
              - "Middle income ($50,000-$74,999)"
              - "Upper-middle income ($75,000-$99,999)"
              - "High income ($100,000+)"
              - "Prefer not to say"
            required: true
            variable_name: socioeconomic_status

          - id: 2
            type: multiple_choice
            order: 2
            question: "What is your preferred fruit flavor profile?"
            alternatives:
              - "Sweet"
              - "Tart/Sour"
              - "Mild/Subtle"
              - "Rich/Intense"
              - "Varies by mood"
            required: true
            variable_name: preferred_flavor

          - id: 3
            type: multiple_choice
            order: 3
            question: "How often do you visit restaurants or cafes?"
            alternatives:
              - "Daily"
              - "Several times per week"
              - "Weekly"
              - "Monthly"
              - "Rarely"
              - "Never"
            required: true
            variable_name: restaurant_visits

          - id: 4
            type: open_text
            order: 4
            question: "Please share your opinion about the role of fresh fruits in a healthy diet. What factors influence your fruit purchasing decisions?"
            required: false
            variable_name: fruit_opinion

    closure:
      end:
        content: |
          # Thank You! 🎉
          
          ## Study Complete
          Thank you for participating in our Fruit Preferences Study! Your responses will help us better understand consumer preferences and purchasing decisions.
          
          ## What's Next?
          Your compensation will be processed within 2-3 business days.
          
          ## Questions?
          If you have any questions about this research, please contact:
          - Email: researcher@university.edu
          - Phone: (555) 123-4567
          
          ## Share Your Experience
          If you enjoyed participating in this study, feel free to share it with friends who might also be interested in research participation.
          
          **Thank you again for your valuable contribution to our research!**
```

---

## 🛠️ Developer Guide

PixelSurvey Core is designed to be easily extensible. If you want to add new question types or experimental designs, please refer to our [CONTRIBUTING.md](CONTRIBUTING.md) for a step-by-step tutorial on using the Registry Pattern and Jinja2 templates.

