import streamlit as st
import pandas as pd
import io
import re
from os.path import join
from processing import * 

# Title of the application
st.title("Cosnetix Demo")

# Section: Environmental Factors Questionnaire
st.header("Environmental Factors Questionnaire")

# Age input
age = st.number_input("What is your age?", min_value=0,
                      max_value=120, value=25)

# Gender selection
gender = st.selectbox("What is your gender?", ["Male", "Female", "Other"])

# Sun exposure level
sun_exposure = st.selectbox(
    "How much sun exposure do you get daily?", ["Low", "Moderate", "High"]
)

# Pollution exposure level
pollution_exposure = st.selectbox(
    "How polluted is your environment?", ["Low", "Moderate", "High"]
)

# Stress level
stress_level = st.selectbox(
    "What is your current stress level?", ["Low", "Moderate", "High"]
)

# Section: Skin Conditions
st.header("Skin Conditions")

# Multiple selection for skin conditions
skin_conditions = st.multiselect(
    "Select any skin conditions you have:",
    [
        "Acne",
        "Eczema",
        "Rosacea",
        "Psoriasis",
        "Dermatitis",
        "Hyperpigmentation",
        "Other",
    ],
)

# Additional input if 'Other' is selected
if "Other" in skin_conditions:
    other_conditions = st.text_input("Please specify other skin conditions:")

# Section: Ingredient Allergies
st.header("Ingredient Allergies")

# Text area for listing ingredient allergies
ingredient_allergies = st.text_area(
    "List any ingredient allergies you have (separated by commas):"
)

# Section: Input Ingredients
# st.header("Input Ingredients")

# Text area for listing ingredients
# input_ingredients = st.text_area(
#     "List the ingredients (separated by commas):"
# )
input_ingredients = ""
# Section: Upload 23andMe Genome Data
st.header("Upload Your 23andMe Genome Data")

# File uploader for genome txt file
genome_file = st.file_uploader(
    "Upload your 23andMe genome txt file:", type=["txt"]
)

# Placeholder for genome data
genome_data = None

# Check if a file has been uploaded
if genome_file is not None:
    
    # Read the genome file into a DataFrame
    st.success("Genome file uploaded successfully!")
    genome_data = get_genome_data(genome_file)
    st.write("Genome data loaded.")
    st.write(genome_data.head())


# Submit button
if st.button("Submit"):
    st.write("Processing your data...")

    # Process ingredient allergies
    allergy_list = [
        allergy.strip().lower()
        for allergy in ingredient_allergies.split(",")
        if allergy.strip()
    ]

    # Process input ingredients
    input_ingredient_list = [
        ingredient.strip()
        for ingredient in input_ingredients.split(",")
        if ingredient.strip()
    ]

    # Convert ingredient list to lowercase for comparison
    input_ingredient_list_lower = [ingredient.lower()
                                   for ingredient in input_ingredient_list]

    # Initialize flagged ingredients and ingredient info
    flagged_ingredients = []
    ingredient_info = {}

    # Process genome data
    if genome_data is not None:
        # Read the SNP mapping table
        try:

            # Apply the filtering
            user_risk_df = get_risk_genotypes(genome_data)

            # Display the filtered data
            st.write(f"Found {len(user_risk_df)} SNPs with matching risk genotypes.")
            columns = [
                "Gene", "Risk Description", "Affected Ingredients", "Alternative Ingredients"
            ]
            user_risk_df = user_risk_df[columns]

            # Apply text wrapping to the DataFrame
            styled_df = user_risk_df.style.set_properties(**{
                'white-space': 'pre-wrap'
            })

            # Display the styled DataFrame
            st.write(styled_df.to_html(), unsafe_allow_html=True)

            # Compile list of affected ingredients
            affected_ingredients = set()
            for ingredients in user_risk_df['Affected Ingredients']:
                if pd.notna(ingredients):
                    ingredients_list = [i.strip().lower()
                                        for i in re.split(r',\s*', ingredients)]
                    affected_ingredients.update(ingredients_list)

            # Map ingredients to risk descriptions and alternatives
            for idx, row in user_risk_df.iterrows():
                if pd.notna(row['Affected Ingredients']):
                    ingredients_list = [i.strip().lower() for i in re.split(
                        r',\s*', row['Affected Ingredients'])]
                    for ingredient in ingredients_list:
                        ingredient_info[ingredient] = {
                            'Risk Description': row['Risk Description'],
                            'Alternative Ingredients': row['Alternative Ingredients']
                        }

            # Identify and flag ingredients in user's list
            for ingredient in input_ingredient_list_lower:
                if ingredient in affected_ingredients:
                    flagged_ingredients.append(ingredient)

        except FileNotFoundError:
            st.error("SNP mapping file not found. Please ensure 'snp_mapping.csv' is in the app directory.")
    else:
        st.warning("No genome data to process.")

    # Section: Display Ingredients with Highlighted Allergens
    # st.header("Ingredients Analysis")
    # CSS for tooltip functionality
    st.markdown(
        """
        <style>
        .tooltip {
            position: relative;
            display: inline-block;
            cursor: pointer;
            margin-bottom: 5px;
        }

        .tooltip .tooltiptext {
            visibility: hidden;
            width: 300px;
            background-color: #555;
            color: #fff;
            text-align: left;
            border-radius: 6px;
            padding: 5px;
            position: absolute;
            z-index: 1;
            bottom: 125%; /* Adjust as needed */
            left: 50%;
            margin-left: -150px; /* Adjust as needed */
            opacity: 0;
            transition: opacity 0.3s;
            font-size: 12px;
        }

        .tooltip:hover .tooltiptext {
            visibility: visible;
            opacity: 1;
        }

        .tooltip .tooltiptext::after {
            content: "";
            position: absolute;
            top: 100%; /* At the bottom of the tooltip */
            left: 50%;
            margin-left: -5px;
            border-width: 5px;
            border-style: solid;
            border-color: #555 transparent transparent transparent;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

    # st.write(input_ingredient_list)

    # Display the ingredients
    for ingredient in input_ingredient_list:
        ingredient_lower = ingredient.lower()
        if ingredient_lower in flagged_ingredients:
            # Get risk description and alternative ingredients
            info = ingredient_info.get(ingredient_lower, {})
            risk_description = info.get(
                'Risk Description', 'No description available.')
            alternatives = info.get(
                'Alternative Ingredients', 'No alternatives available.')

            # Create tooltip content
            tooltip_content = f"<strong>Risk:</strong> {risk_description}<br><strong>Alternatives:</strong> {alternatives}"

            # Display ingredient in red with tooltip
            st.markdown(
                f"""
                <div class="tooltip">
                    <span style="color:red">{ingredient}</span>
                    <span class="tooltiptext">{tooltip_content}</span>
                </div>
                """,
                unsafe_allow_html=True,
            )
        elif ingredient_lower in allergy_list:
            # Display allergen ingredients in red font
            st.markdown(
                f"<span style='color:red'>{ingredient}</span>",
                unsafe_allow_html=True,
            )
        else:
            # Display ingredient normally
            st.write(ingredient)

    # Placeholder for further analysis
    # You can add code here to analyze other data
