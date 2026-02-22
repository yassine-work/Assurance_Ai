"""Application configuration constants."""

# Bundle ID → human-readable name
BUNDLE_NAMES = {
    0: "Auto Comprehensive",
    1: "Auto Liability Basic",
    2: "Basic Health",
    3: "Family Comprehensive",
    4: "Health Dental Vision",
    5: "Home Premium",
    6: "Home Standard",
    7: "Premium Health Life",
    8: "Renter Basic",
    9: "Renter Premium",
}

# Bundle categories and icons (for frontend display)
BUNDLE_META = {
    0: {"category": "Auto", "icon": "car", "color": "#3B82F6"},
    1: {"category": "Auto", "icon": "car", "color": "#60A5FA"},
    2: {"category": "Health", "icon": "heart", "color": "#10B981"},
    3: {"category": "Family", "icon": "users", "color": "#8B5CF6"},
    4: {"category": "Health", "icon": "heart", "color": "#34D399"},
    5: {"category": "Home", "icon": "home", "color": "#F59E0B"},
    6: {"category": "Home", "icon": "home", "color": "#FBBF24"},
    7: {"category": "Health", "icon": "shield", "color": "#06B6D4"},
    8: {"category": "Renter", "icon": "building", "color": "#EC4899"},
    9: {"category": "Renter", "icon": "building", "color": "#F472B6"},
}

# Input field metadata for the frontend form
INPUT_FIELDS = {
    "demographics": {
        "label": "About You & Your Household",
        "fields": [
            {"name": "Adult_Dependents", "label": "Adults in your household (besides you)", "type": "number", "min": 0, "max": 10, "default": 0},
            {"name": "Child_Dependents", "label": "Children (ages 2–17) in your household", "type": "number", "min": 0, "max": 10, "default": 0},
            {"name": "Infant_Dependents", "label": "Infants (under 2) in your household", "type": "number", "min": 0, "max": 5, "default": 0},
            {"name": "Estimated_Annual_Income", "label": "Your estimated yearly income ($)", "type": "number", "min": 0, "max": 1000000, "default": 50000},
            {"name": "Employment_Status", "label": "What is your current work status?", "type": "select", "options": ["Employed", "Self-Employed", "Unemployed", "Retired", "Student"]},
            {"name": "Region_Code", "label": "Your region / area code (1–50)", "type": "number", "min": 1, "max": 50, "default": 1},
        ],
    },
    "history": {
        "label": "Your Insurance History",
        "fields": [
            {"name": "Existing_Policyholder", "label": "Do you currently have an insurance policy?", "type": "select", "options": ["Yes", "No"]},
            {"name": "Previous_Claims_Filed", "label": "How many insurance claims have you filed before?", "type": "number", "min": 0, "max": 50, "default": 0},
            {"name": "Years_Without_Claims", "label": "How many years since your last claim?", "type": "number", "min": 0, "max": 30, "default": 0},
            {"name": "Previous_Policy_Duration_Months", "label": "How long was your last policy? (months)", "type": "number", "min": 0, "max": 360, "default": 0},
            {"name": "Policy_Cancelled_Post_Purchase", "label": "Have you ever cancelled a policy after buying it?", "type": "select", "options": ["Yes", "No"]},
        ],
    },
    "policy": {
        "label": "Coverage Preferences",
        "fields": [
            {"name": "Deductible_Tier", "label": "Deductible level (1 = lowest, 5 = highest)", "type": "number", "min": 1, "max": 5, "default": 3},
            {"name": "Payment_Schedule", "label": "How often do you prefer to pay?", "type": "select", "options": ["Monthly", "Quarterly", "Semi-Annual", "Annual"]},
            {"name": "Vehicles_on_Policy", "label": "How many vehicles do you want covered?", "type": "number", "min": 0, "max": 10, "default": 1},
            {"name": "Custom_Riders_Requested", "label": "Any extra add-ons you want? (count)", "type": "number", "min": 0, "max": 10, "default": 0},
            {"name": "Grace_Period_Extensions", "label": "Late payment extensions requested", "type": "number", "min": 0, "max": 10, "default": 0},
        ],
    },
    "sales": {
        "label": "How You Found Us",
        "fields": [
            {"name": "Days_Since_Quote", "label": "Days since you got your quote", "type": "number", "min": 0, "max": 365, "default": 7},
            {"name": "Underwriting_Processing_Days", "label": "Days spent in review process", "type": "number", "min": 0, "max": 60, "default": 5},
            {"name": "Policy_Amendments_Count", "label": "How many times was your policy changed?", "type": "number", "min": 0, "max": 20, "default": 0},
            {"name": "Acquisition_Channel", "label": "How did you find us?", "type": "select", "options": ["Online", "Agent", "Broker", "Direct", "Referral"]},
            {"name": "Broker_Agency_Type", "label": "What type of agency helped you?", "type": "select", "options": ["Large", "Medium", "Small", "Independent"]},
            {"name": "Broker_ID", "label": "Your broker's reference number", "type": "number", "min": 1, "max": 600, "default": 9},
            {"name": "Employer_ID", "label": "Your employer's reference number", "type": "number", "min": 1, "max": 600, "default": 174},
        ],
    },
    "timeline": {
        "label": "When Do You Want Coverage?",
        "fields": [
            {"name": "Policy_Start_Year", "label": "Start year", "type": "number", "min": 2000, "max": 2026, "default": 2024},
            {"name": "Policy_Start_Month", "label": "Start month", "type": "select", "options": ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"]},
            {"name": "Policy_Start_Week", "label": "Week of the month (1–5)", "type": "number", "min": 1, "max": 53, "default": 1},
            {"name": "Policy_Start_Day", "label": "Day of the month", "type": "number", "min": 1, "max": 31, "default": 15},
        ],
    },
}
