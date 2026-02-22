# Auto-generated — do not edit function signatures
import json as _json
import joblib, numpy as np, pandas as pd

ID_COL       = "User_ID"
FEATURE_COLS = ["Policy_Cancelled_Post_Purchase", "Policy_Start_Year", "Policy_Start_Week", "Policy_Start_Day", "Grace_Period_Extensions", "Previous_Policy_Duration_Months", "Adult_Dependents", "Child_Dependents", "Infant_Dependents", "Region_Code", "Existing_Policyholder", "Previous_Claims_Filed", "Years_Without_Claims", "Policy_Amendments_Count", "Broker_ID", "Employer_ID", "Underwriting_Processing_Days", "Vehicles_on_Policy", "Custom_Riders_Requested", "Broker_Agency_Type", "Deductible_Tier", "Acquisition_Channel", "Payment_Schedule", "Employment_Status", "Estimated_Annual_Income", "Days_Since_Quote", "Policy_Start_Month", "Total_Dependents", "Dependents_per_Income", "Income_per_Dependent", "Adult_Child_Ratio", "Vehicles_per_Adult", "Has_Infants", "Has_Children", "Has_Employer", "Log_Income", "Income_Bucket", "Claims_per_NoClaimYears", "Duration_per_Claim", "Claims_per_Month", "Loyalty_Score", "High_Claims_Flag", "Is_New_Policy", "Risk_Score", "Cancelled_x_Claims", "Grace_x_Claims", "Existing_Policyholder_01", "Claims_if_existing", "Cancelled_01", "Deductible_x_Riders", "High_Coverage_Flag", "Grace_plus_Amendments", "Amendments_per_Month", "Policy_Start_Quarter", "Is_Year_End", "Is_Summer", "Month_sin", "Month_cos", "Policy_Year_Normalized", "Policy_Start_Week_Bucket", "Week_sin", "Week_cos", "Is_Month_Start", "Is_Month_End", "Quote_to_UW_Ratio", "Quote_plus_UW", "Long_UW_Flag", "Quote_Urgency", "Log_DSQ", "Vehicles_x_Riders", "Riders_per_Vehicle", "Policy_Complexity", "Coverage_Need", "Affordability", "Income_x_Dependents", "Claims_Squared", "Claims_Acceleration", "No_Claims_Ratio", "Claim_Gap", "Claims_NCY_Interact", "Sqrt_Income", "Income_Risk_Ratio", "Income_Volatility_Proxy", "Is_Spring", "Is_Fall", "Is_Winter", "Is_Q1", "Is_Q4", "Day_sin", "Day_cos", "Day_of_Month_Bucket", "Is_Year_Start_Week", "Is_Year_End_Week", "Log_UW", "UW_Efficiency", "DSQ_Bucket", "Avg_Process_Step", "Riders_x_Dependents", "Policy_Load", "Dep_Coverage_Density", "Grace_x_Amended", "Cancelled_x_Duration", "Cancelled_x_Amended", "Risk_x_Income", "Is_Top_Broker", "Is_Rare_Broker", "Employer_x_Income", "Policy_Age_2025", "Is_Recent_Policy", "High_Amendment_Flag", "Amend_x_Claims", "Amend_x_Grace", "Broker_ID_freq", "Employer_ID_freq"]
CAT_COLS     = ["Region_Code", "Broker_Agency_Type", "Deductible_Tier", "Acquisition_Channel", "Payment_Schedule", "Employment_Status", "Policy_Start_Month"]
NUM_COLS     = ["Policy_Cancelled_Post_Purchase", "Policy_Start_Year", "Policy_Start_Week", "Policy_Start_Day", "Grace_Period_Extensions", "Previous_Policy_Duration_Months", "Adult_Dependents", "Child_Dependents", "Infant_Dependents", "Existing_Policyholder", "Previous_Claims_Filed", "Years_Without_Claims", "Policy_Amendments_Count", "Broker_ID", "Employer_ID", "Underwriting_Processing_Days", "Vehicles_on_Policy", "Custom_Riders_Requested", "Estimated_Annual_Income", "Days_Since_Quote", "Total_Dependents", "Dependents_per_Income", "Income_per_Dependent", "Adult_Child_Ratio", "Vehicles_per_Adult", "Has_Infants", "Has_Children", "Has_Employer", "Log_Income", "Income_Bucket", "Claims_per_NoClaimYears", "Duration_per_Claim", "Claims_per_Month", "Loyalty_Score", "High_Claims_Flag", "Is_New_Policy", "Risk_Score", "Cancelled_x_Claims", "Grace_x_Claims", "Existing_Policyholder_01", "Claims_if_existing", "Cancelled_01", "Deductible_x_Riders", "High_Coverage_Flag", "Grace_plus_Amendments", "Amendments_per_Month", "Policy_Start_Quarter", "Is_Year_End", "Is_Summer", "Month_sin", "Month_cos", "Policy_Year_Normalized", "Policy_Start_Week_Bucket", "Week_sin", "Week_cos", "Is_Month_Start", "Is_Month_End", "Quote_to_UW_Ratio", "Quote_plus_UW", "Long_UW_Flag", "Quote_Urgency", "Log_DSQ", "Vehicles_x_Riders", "Riders_per_Vehicle", "Policy_Complexity", "Coverage_Need", "Affordability", "Income_x_Dependents", "Claims_Squared", "Claims_Acceleration", "No_Claims_Ratio", "Claim_Gap", "Claims_NCY_Interact", "Sqrt_Income", "Income_Risk_Ratio", "Income_Volatility_Proxy", "Is_Spring", "Is_Fall", "Is_Winter", "Is_Q1", "Is_Q4", "Day_sin", "Day_cos", "Day_of_Month_Bucket", "Is_Year_Start_Week", "Is_Year_End_Week", "Log_UW", "UW_Efficiency", "DSQ_Bucket", "Avg_Process_Step", "Riders_x_Dependents", "Policy_Load", "Dep_Coverage_Density", "Grace_x_Amended", "Cancelled_x_Duration", "Cancelled_x_Amended", "Risk_x_Income", "Is_Top_Broker", "Is_Rare_Broker", "Employer_x_Income", "Policy_Age_2025", "Is_Recent_Policy", "High_Amendment_Flag", "Amend_x_Claims", "Amend_x_Grace"]
THRESHOLDS   = [1.0885129669437037, 0.9436062855636809, 1.2760704253204227, 1.2572429920638353, 1.3862572410798712, 0.7413116767142085, 1.0136464926987796, 0.9367958106468444, 0.8078082111182814, 0.969628011172425]

# Frequency maps for high-cardinality ID columns (computed from training data)
_FREQ_MAPS_RAW = '{"Broker_ID": {"9.0": 0.3296477623710324, "14.0": 0.1757738056121443, "240.0": 0.15306893605835578, "7.0": 0.03790168890057173, "250.0": 0.034106591312348035, "241.0": 0.019747650653873957, "28.0": 0.016691857790628904, "8.0": 0.015426825261221003, "1.0": 0.013323914043503976, "6.0": 0.011861733587435105, "40.0": 0.011779588617993034, "314.0": 0.010005257278044292, "242.0": 0.008773082736413222, "83.0": 0.006620884537030952, "85.0": 0.006144443714266938, "243.0": 0.0057172898731681675, "171.0": 0.004468686337648683, "3.0": 0.004287967404876125, "27.0": 0.004238680423210883, "22.0": 0.0038279555760005256, "11.0": 0.003433659722678583, "15.0": 0.003367943747124926, "177.0": 0.0030557928632450547, "96.0": 0.0029900768876913978, "196.0": 0.0029079319182493263, "138.0": 0.002743641979365184, "229.0": 0.0024314910954853124, "5.0": 0.0024150621015968984, "16.0": 0.002349346126043241, "115.0": 0.002332917132154827, "37.0": 0.0023164881382664124, "10.0": 0.0023000591443779984, "21.0": 0.002217914174935927, "251.0": 0.0022014851810475125, "273.0": 0.0021850561871590984, "42.0": 0.002168627193270684, "26.0": 0.0021357692054938555, "175.0": 0.002102911217717027, "156.0": 0.002053624236051784, "195.0": 0.002053624236051784, "86.0": 0.00192219228494447, "143.0": 0.0019057632910560558, "134.0": 0.0018564763093908128, "298.0": 0.0018236183216139843, "315.0": 0.001741473352171913, "19.0": 0.0017086153643950846, "168.0": 0.0016593283827298416, "152.0": 0.0016100414010645988, "147.0": 0.001560754419399356, "2.0": 0.0015443254255109416, "95.0": 0.0013307485049615562, "12.0": 0.001314319511073142, "30.0": 0.0012486035355194847, "142.0": 0.0012321745416310704, "20.0": 0.0012157455477426562, "330.0": 0.0011664585660774135, "410.0": 0.0011500295721889992, "146.0": 0.0011007425905237562, "89.0": 0.0011007425905237562, "94.0": 0.001084313596635342, "69.0": 0.0010350266149700992, "159.0": 0.0010021686271932707, "36.0": 0.0009693106394164421, "13.0": 0.000903594663862785, "75.0": 0.0008707366760859565, "185.0": 0.0008543076821975423, "191.0": 0.0008543076821975423, "52.0": 0.0008378786883091279, "39.0": 0.0008214496944207137, "132.0": 0.0008050207005322994, "17.0": 0.0008050207005322994, "29.0": 0.0007721627127554708, "531.0": 0.0007557337188670566, "464.0": 0.0007393047249786423, "220.0": 0.0007064467372018138, "98.0": 0.0006900177433133995, "339.0": 0.0006900177433133995, "34.0": 0.000657159755536571, "118.0": 0.0006407307616481567, "181.0": 0.0006407307616481567, "38.0": 0.0006407307616481567, "436.0": 0.0006407307616481567, "253.0": 0.0006078727738713281, "184.0": 0.0006078727738713281, "91.0": 0.0005914437799829139, "157.0": 0.0005750147860944996, "155.0": 0.0005750147860944996, "71.0": 0.0005750147860944996, "208.0": 0.000542156798317671, "56.0": 0.0005257278044292567, "104.0": 0.0005092988105408425, "234.0": 0.0005092988105408425, "79.0": 0.0004928698166524282, "468.0": 0.00046001182887559964, "58.0": 0.0004435828349871854, "87.0": 0.0004435828349871854, "467.0": 0.0004435828349871854, "127.0": 0.0004435828349871854, "281.0": 0.00042715384109877114, "306.0": 0.00041072484721035683, "121.0": 0.00041072484721035683, "394.0": 0.0003942958533219426, "248.0": 0.0003942958533219426, "261.0": 0.0003942958533219426, "479.0": 0.00036143786554511403, "68.0": 0.00036143786554511403, "119.0": 0.00034500887165669973, "527.0": 0.00034500887165669973, "57.0": 0.00034500887165669973, "434.0": 0.0003285798777682855, "66.0": 0.0003285798777682855, "493.0": 0.0003285798777682855, "45.0": 0.0003121508838798712, "173.0": 0.0002957218899914569, "149.0": 0.0002957218899914569, "153.0": 0.0002957218899914569, "44.0": 0.0002957218899914569, "336.0": 0.0002957218899914569, "440.0": 0.0002792928961030427, "201.0": 0.00026286390221462837, "128.0": 0.00026286390221462837, "327.0": 0.0002464349083262141, "334.0": 0.0002464349083262141, "47.0": 0.00023000591443779982, "308.0": 0.00023000591443779982, "154.0": 0.00023000591443779982, "262.0": 0.00021357692054938557, "35.0": 0.00021357692054938557, "67.0": 0.00021357692054938557, "82.0": 0.00021357692054938557, "375.0": 0.00021357692054938557, "423.0": 0.00021357692054938557, "254.0": 0.0001971479266609713, "88.0": 0.0001971479266609713, "425.0": 0.0001971479266609713, "31.0": 0.00018071893277255702, "77.0": 0.00018071893277255702, "290.0": 0.00018071893277255702, "360.0": 0.00018071893277255702, "4.0": 0.00018071893277255702, "354.0": 0.00018071893277255702, "385.0": 0.00018071893277255702, "23.0": 0.00018071893277255702, "170.0": 0.00016428993888414274, "151.0": 0.00016428993888414274, "223.0": 0.00016428993888414274, "174.0": 0.00016428993888414274, "368.0": 0.00016428993888414274, "474.0": 0.00014786094499572846, "105.0": 0.00014786094499572846, "455.0": 0.00014786094499572846, "183.0": 0.00014786094499572846, "305.0": 0.00014786094499572846, "103.0": 0.00014786094499572846, "24.0": 0.00014786094499572846, "187.0": 0.00014786094499572846, "111.0": 0.00014786094499572846, "390.0": 0.00014786094499572846, "249.0": 0.00013143195110731419, "110.0": 0.00013143195110731419, "526.0": 0.00013143195110731419, "215.0": 0.00013143195110731419, "275.0": 0.00013143195110731419, "296.0": 0.00013143195110731419, "99.0": 0.00013143195110731419, "63.0": 0.00011500295721889991, "324.0": 0.00011500295721889991, "126.0": 0.00011500295721889991, "307.0": 0.00011500295721889991, "332.0": 0.00011500295721889991, "502.0": 0.00011500295721889991, "256.0": 0.00011500295721889991, "50.0": 9.857396333048565e-05, "310.0": 9.857396333048565e-05, "387.0": 9.857396333048565e-05, "205.0": 9.857396333048565e-05, "459.0": 9.857396333048565e-05, "276.0": 9.857396333048565e-05, "363.0": 9.857396333048565e-05, "78.0": 9.857396333048565e-05, "508.0": 9.857396333048565e-05, "393.0": 9.857396333048565e-05, "509.0": 9.857396333048565e-05, "495.0": 9.857396333048565e-05, "236.0": 8.214496944207137e-05, "129.0": 8.214496944207137e-05, "193.0": 8.214496944207137e-05, "350.0": 8.214496944207137e-05, "33.0": 8.214496944207137e-05, "192.0": 8.214496944207137e-05, "245.0": 8.214496944207137e-05, "348.0": 8.214496944207137e-05, "74.0": 8.214496944207137e-05, "328.0": 8.214496944207137e-05, "326.0": 8.214496944207137e-05, "481.0": 8.214496944207137e-05, "429.0": 8.214496944207137e-05, "163.0": 8.214496944207137e-05, "210.0": 6.571597555365709e-05, "418.0": 6.571597555365709e-05, "252.0": 6.571597555365709e-05, "411.0": 6.571597555365709e-05, "378.0": 6.571597555365709e-05, "244.0": 6.571597555365709e-05, "430.0": 6.571597555365709e-05, "32.0": 6.571597555365709e-05, "139.0": 6.571597555365709e-05, "270.0": 6.571597555365709e-05, "325.0": 4.928698166524282e-05, "148.0": 4.928698166524282e-05, "214.0": 4.928698166524282e-05, "364.0": 4.928698166524282e-05, "288.0": 4.928698166524282e-05, "133.0": 4.928698166524282e-05, "286.0": 4.928698166524282e-05, "441.0": 4.928698166524282e-05, "92.0": 4.928698166524282e-05, "182.0": 4.928698166524282e-05, "313.0": 4.928698166524282e-05, "81.0": 4.928698166524282e-05, "384.0": 3.2857987776828546e-05, "179.0": 3.2857987776828546e-05, "344.0": 3.2857987776828546e-05, "535.0": 3.2857987776828546e-05, "405.0": 3.2857987776828546e-05, "323.0": 3.2857987776828546e-05, "302.0": 3.2857987776828546e-05, "211.0": 3.2857987776828546e-05, "303.0": 3.2857987776828546e-05, "335.0": 3.2857987776828546e-05, "331.0": 3.2857987776828546e-05, "403.0": 3.2857987776828546e-05, "219.0": 3.2857987776828546e-05, "287.0": 3.2857987776828546e-05, "420.0": 3.2857987776828546e-05, "72.0": 3.2857987776828546e-05, "426.0": 3.2857987776828546e-05, "150.0": 3.2857987776828546e-05, "461.0": 3.2857987776828546e-05, "180.0": 3.2857987776828546e-05, "60.0": 3.2857987776828546e-05, "112.0": 3.2857987776828546e-05, "162.0": 3.2857987776828546e-05, "427.0": 3.2857987776828546e-05, "341.0": 3.2857987776828546e-05, "235.0": 3.2857987776828546e-05, "449.0": 1.6428993888414273e-05, "472.0": 1.6428993888414273e-05, "321.0": 1.6428993888414273e-05, "476.0": 1.6428993888414273e-05, "107.0": 1.6428993888414273e-05, "64.0": 1.6428993888414273e-05, "433.0": 1.6428993888414273e-05, "492.0": 1.6428993888414273e-05, "55.0": 1.6428993888414273e-05, "391.0": 1.6428993888414273e-05, "352.0": 1.6428993888414273e-05, "267.0": 1.6428993888414273e-05, "355.0": 1.6428993888414273e-05, "291.0": 1.6428993888414273e-05, "53.0": 1.6428993888414273e-05, "484.0": 1.6428993888414273e-05, "265.0": 1.6428993888414273e-05, "301.0": 1.6428993888414273e-05, "416.0": 1.6428993888414273e-05, "480.0": 1.6428993888414273e-05, "141.0": 1.6428993888414273e-05, "497.0": 1.6428993888414273e-05, "122.0": 1.6428993888414273e-05, "397.0": 1.6428993888414273e-05, "106.0": 1.6428993888414273e-05, "41.0": 1.6428993888414273e-05, "406.0": 1.6428993888414273e-05, "283.0": 1.6428993888414273e-05, "232.0": 1.6428993888414273e-05, "346.0": 1.6428993888414273e-05, "213.0": 1.6428993888414273e-05, "388.0": 1.6428993888414273e-05, "282.0": 1.6428993888414273e-05, "370.0": 1.6428993888414273e-05, "167.0": 1.6428993888414273e-05, "431.0": 1.6428993888414273e-05, "510.0": 1.6428993888414273e-05, "304.0": 1.6428993888414273e-05, "135.0": 1.6428993888414273e-05, "158.0": 1.6428993888414273e-05, "289.0": 1.6428993888414273e-05, "61.0": 1.6428993888414273e-05, "117.0": 1.6428993888414273e-05, "278.0": 1.6428993888414273e-05, "358.0": 1.6428993888414273e-05, "333.0": 1.6428993888414273e-05, "285.0": 1.6428993888414273e-05, "280.0": 1.6428993888414273e-05, "258.0": 1.6428993888414273e-05, "414.0": 1.6428993888414273e-05, "454.0": 1.6428993888414273e-05, "483.0": 1.6428993888414273e-05, "247.0": 1.6428993888414273e-05, "371.0": 1.6428993888414273e-05, "165.0": 1.6428993888414273e-05, "216.0": 1.6428993888414273e-05, "70.0": 1.6428993888414273e-05, "450.0": 1.6428993888414273e-05, "475.0": 1.6428993888414273e-05, "408.0": 1.6428993888414273e-05, "269.0": 1.6428993888414273e-05, "59.0": 1.6428993888414273e-05, "404.0": 1.6428993888414273e-05, "54.0": 1.6428993888414273e-05, "90.0": 1.6428993888414273e-05, "469.0": 1.6428993888414273e-05, "227.0": 1.6428993888414273e-05, "73.0": 1.6428993888414273e-05, "25.0": 1.6428993888414273e-05}, "Employer_ID": {"174.0": 0.9442728527304988, "40.0": 0.008986659656962607, "223.0": 0.005487283958730368, "45.0": 0.0027929289610304263, "153.0": 0.0024807780771505554, "281.0": 0.0014457514621804561, "219.0": 0.0014293224682920419, "154.0": 0.0013471774988499704, "233.0": 0.0010678846027469277, "51.0": 0.0009857396333048565, "94.0": 0.0008871656699743708, "405.0": 0.0007393047249786423, "331.0": 0.000657159755536571, "47.0": 0.0005750147860944996, "110.0": 0.0005585857922060854, "91.0": 0.0005257278044292567, "67.0": 0.0005092988105408425, "62.0": 0.0005092988105408425, "135.0": 0.00046001182887559964, "169.0": 0.0004435828349871854, "280.0": 0.00042715384109877114, "270.0": 0.00042715384109877114, "148.0": 0.0003942958533219426, "9.0": 0.0003942958533219426, "218.0": 0.0003778668594335283, "498.0": 0.0003778668594335283, "86.0": 0.00036143786554511403, "238.0": 0.00036143786554511403, "269.0": 0.00034500887165669973, "113.0": 0.00034500887165669973, "178.0": 0.0003285798777682855, "204.0": 0.0003121508838798712, "195.0": 0.0003121508838798712, "20.0": 0.0003121508838798712, "72.0": 0.0002957218899914569, "81.0": 0.0002957218899914569, "307.0": 0.0002957218899914569, "227.0": 0.0002792928961030427, "418.0": 0.00026286390221462837, "46.0": 0.0002464349083262141, "144.0": 0.0002464349083262141, "342.0": 0.0002464349083262141, "179.0": 0.0002464349083262141, "221.0": 0.0002464349083262141, "150.0": 0.00023000591443779982, "78.0": 0.00021357692054938557, "88.0": 0.00021357692054938557, "365.0": 0.00021357692054938557, "183.0": 0.00021357692054938557, "38.0": 0.00021357692054938557, "216.0": 0.0001971479266609713, "242.0": 0.00018071893277255702, "82.0": 0.00018071893277255702, "290.0": 0.00018071893277255702, "68.0": 0.00018071893277255702, "396.0": 0.00018071893277255702, "525.0": 0.00016428993888414274, "477.0": 0.00016428993888414274, "209.0": 0.00016428993888414274, "197.0": 0.00016428993888414274, "112.0": 0.00016428993888414274, "408.0": 0.00016428993888414274, "120.0": 0.00016428993888414274, "292.0": 0.00014786094499572846, "343.0": 0.00014786094499572846, "12.0": 0.00014786094499572846, "274.0": 0.00014786094499572846, "337.0": 0.00014786094499572846, "103.0": 0.00014786094499572846, "251.0": 0.00014786094499572846, "83.0": 0.00014786094499572846, "399.0": 0.00014786094499572846, "338.0": 0.00014786094499572846, "360.0": 0.00014786094499572846, "435.0": 0.00013143195110731419, "504.0": 0.00013143195110731419, "356.0": 0.00013143195110731419, "371.0": 0.00013143195110731419, "92.0": 0.00013143195110731419, "31.0": 0.00013143195110731419, "380.0": 0.00013143195110731419, "485.0": 0.00013143195110731419, "390.0": 0.00013143195110731419, "186.0": 0.00013143195110731419, "99.0": 0.00013143195110731419, "203.0": 0.00011500295721889991, "163.0": 0.00011500295721889991, "407.0": 0.00011500295721889991, "43.0": 0.00011500295721889991, "324.0": 0.00011500295721889991, "428.0": 0.00011500295721889991, "507.0": 0.00011500295721889991, "286.0": 0.00011500295721889991, "317.0": 0.00011500295721889991, "127.0": 0.00011500295721889991, "355.0": 0.00011500295721889991, "367.0": 9.857396333048565e-05, "379.0": 9.857396333048565e-05, "346.0": 9.857396333048565e-05, "439.0": 9.857396333048565e-05, "523.0": 9.857396333048565e-05, "366.0": 9.857396333048565e-05, "53.0": 9.857396333048565e-05, "291.0": 9.857396333048565e-05, "39.0": 9.857396333048565e-05, "263.0": 9.857396333048565e-05, "450.0": 9.857396333048565e-05, "388.0": 8.214496944207137e-05, "329.0": 8.214496944207137e-05, "297.0": 8.214496944207137e-05, "465.0": 8.214496944207137e-05, "107.0": 8.214496944207137e-05, "14.0": 8.214496944207137e-05, "421.0": 8.214496944207137e-05, "490.0": 8.214496944207137e-05, "308.0": 8.214496944207137e-05, "143.0": 8.214496944207137e-05, "358.0": 8.214496944207137e-05, "384.0": 8.214496944207137e-05, "437.0": 8.214496944207137e-05, "323.0": 8.214496944207137e-05, "364.0": 8.214496944207137e-05, "451.0": 6.571597555365709e-05, "494.0": 6.571597555365709e-05, "159.0": 6.571597555365709e-05, "137.0": 6.571597555365709e-05, "459.0": 6.571597555365709e-05, "448.0": 6.571597555365709e-05, "293.0": 6.571597555365709e-05, "424.0": 6.571597555365709e-05, "130.0": 6.571597555365709e-05, "470.0": 6.571597555365709e-05, "225.0": 6.571597555365709e-05, "207.0": 6.571597555365709e-05, "277.0": 6.571597555365709e-05, "34.0": 6.571597555365709e-05, "426.0": 6.571597555365709e-05, "59.0": 6.571597555365709e-05, "348.0": 6.571597555365709e-05, "521.0": 6.571597555365709e-05, "515.0": 6.571597555365709e-05, "397.0": 6.571597555365709e-05, "287.0": 6.571597555365709e-05, "268.0": 6.571597555365709e-05, "108.0": 6.571597555365709e-05, "385.0": 4.928698166524282e-05, "93.0": 4.928698166524282e-05, "272.0": 4.928698166524282e-05, "224.0": 4.928698166524282e-05, "443.0": 4.928698166524282e-05, "353.0": 4.928698166524282e-05, "319.0": 4.928698166524282e-05, "279.0": 4.928698166524282e-05, "220.0": 4.928698166524282e-05, "116.0": 4.928698166524282e-05, "255.0": 4.928698166524282e-05, "282.0": 4.928698166524282e-05, "357.0": 4.928698166524282e-05, "146.0": 4.928698166524282e-05, "16.0": 4.928698166524282e-05, "409.0": 4.928698166524282e-05, "167.0": 4.928698166524282e-05, "530.0": 4.928698166524282e-05, "275.0": 4.928698166524282e-05, "466.0": 4.928698166524282e-05, "240.0": 4.928698166524282e-05, "302.0": 4.928698166524282e-05, "180.0": 4.928698166524282e-05, "457.0": 4.928698166524282e-05, "383.0": 4.928698166524282e-05, "254.0": 4.928698166524282e-05, "511.0": 4.928698166524282e-05, "394.0": 4.928698166524282e-05, "48.0": 3.2857987776828546e-05, "350.0": 3.2857987776828546e-05, "139.0": 3.2857987776828546e-05, "528.0": 3.2857987776828546e-05, "429.0": 3.2857987776828546e-05, "85.0": 3.2857987776828546e-05, "118.0": 3.2857987776828546e-05, "333.0": 3.2857987776828546e-05, "447.0": 3.2857987776828546e-05, "543.0": 3.2857987776828546e-05, "168.0": 3.2857987776828546e-05, "73.0": 3.2857987776828546e-05, "259.0": 3.2857987776828546e-05, "245.0": 3.2857987776828546e-05, "395.0": 3.2857987776828546e-05, "215.0": 3.2857987776828546e-05, "484.0": 3.2857987776828546e-05, "325.0": 3.2857987776828546e-05, "200.0": 3.2857987776828546e-05, "378.0": 3.2857987776828546e-05, "217.0": 3.2857987776828546e-05, "193.0": 3.2857987776828546e-05, "316.0": 3.2857987776828546e-05, "158.0": 3.2857987776828546e-05, "289.0": 3.2857987776828546e-05, "458.0": 3.2857987776828546e-05, "334.0": 3.2857987776828546e-05, "410.0": 3.2857987776828546e-05, "311.0": 3.2857987776828546e-05, "411.0": 3.2857987776828546e-05, "222.0": 3.2857987776828546e-05, "84.0": 3.2857987776828546e-05, "115.0": 3.2857987776828546e-05, "105.0": 3.2857987776828546e-05, "22.0": 3.2857987776828546e-05, "482.0": 3.2857987776828546e-05, "452.0": 3.2857987776828546e-05, "192.0": 3.2857987776828546e-05, "491.0": 3.2857987776828546e-05, "392.0": 3.2857987776828546e-05, "361.0": 3.2857987776828546e-05, "232.0": 3.2857987776828546e-05, "436.0": 3.2857987776828546e-05, "149.0": 3.2857987776828546e-05, "456.0": 3.2857987776828546e-05, "492.0": 3.2857987776828546e-05, "210.0": 3.2857987776828546e-05, "483.0": 1.6428993888414273e-05, "320.0": 1.6428993888414273e-05, "49.0": 1.6428993888414273e-05, "433.0": 1.6428993888414273e-05, "160.0": 1.6428993888414273e-05, "80.0": 1.6428993888414273e-05, "512.0": 1.6428993888414273e-05, "230.0": 1.6428993888414273e-05, "520.0": 1.6428993888414273e-05, "273.0": 1.6428993888414273e-05, "250.0": 1.6428993888414273e-05, "185.0": 1.6428993888414273e-05, "423.0": 1.6428993888414273e-05, "304.0": 1.6428993888414273e-05, "32.0": 1.6428993888414273e-05, "382.0": 1.6428993888414273e-05, "514.0": 1.6428993888414273e-05, "486.0": 1.6428993888414273e-05, "341.0": 1.6428993888414273e-05, "461.0": 1.6428993888414273e-05, "288.0": 1.6428993888414273e-05, "413.0": 1.6428993888414273e-05, "368.0": 1.6428993888414273e-05, "455.0": 1.6428993888414273e-05, "516.0": 1.6428993888414273e-05, "100.0": 1.6428993888414273e-05, "446.0": 1.6428993888414273e-05, "402.0": 1.6428993888414273e-05, "132.0": 1.6428993888414273e-05, "445.0": 1.6428993888414273e-05, "420.0": 1.6428993888414273e-05, "212.0": 1.6428993888414273e-05, "165.0": 1.6428993888414273e-05, "332.0": 1.6428993888414273e-05, "64.0": 1.6428993888414273e-05, "481.0": 1.6428993888414273e-05, "37.0": 1.6428993888414273e-05, "246.0": 1.6428993888414273e-05, "264.0": 1.6428993888414273e-05, "313.0": 1.6428993888414273e-05, "401.0": 1.6428993888414273e-05, "271.0": 1.6428993888414273e-05, "415.0": 1.6428993888414273e-05, "369.0": 1.6428993888414273e-05, "534.0": 1.6428993888414273e-05, "386.0": 1.6428993888414273e-05, "284.0": 1.6428993888414273e-05, "422.0": 1.6428993888414273e-05, "28.0": 1.6428993888414273e-05, "101.0": 1.6428993888414273e-05, "400.0": 1.6428993888414273e-05, "478.0": 1.6428993888414273e-05, "347.0": 1.6428993888414273e-05, "393.0": 1.6428993888414273e-05, "349.0": 1.6428993888414273e-05, "425.0": 1.6428993888414273e-05, "278.0": 1.6428993888414273e-05, "499.0": 1.6428993888414273e-05, "257.0": 1.6428993888414273e-05, "96.0": 1.6428993888414273e-05, "460.0": 1.6428993888414273e-05, "487.0": 1.6428993888414273e-05, "541.0": 1.6428993888414273e-05, "106.0": 1.6428993888414273e-05, "391.0": 1.6428993888414273e-05, "54.0": 1.6428993888414273e-05, "539.0": 1.6428993888414273e-05, "376.0": 1.6428993888414273e-05, "184.0": 1.6428993888414273e-05, "61.0": 1.6428993888414273e-05, "442.0": 1.6428993888414273e-05, "373.0": 1.6428993888414273e-05, "398.0": 1.6428993888414273e-05, "234.0": 1.6428993888414273e-05, "501.0": 1.6428993888414273e-05, "372.0": 1.6428993888414273e-05, "370.0": 1.6428993888414273e-05, "506.0": 1.6428993888414273e-05, "419.0": 1.6428993888414273e-05, "518.0": 1.6428993888414273e-05, "330.0": 1.6428993888414273e-05, "314.0": 1.6428993888414273e-05, "301.0": 1.6428993888414273e-05, "444.0": 1.6428993888414273e-05, "202.0": 1.6428993888414273e-05, "258.0": 1.6428993888414273e-05, "142.0": 1.6428993888414273e-05, "104.0": 1.6428993888414273e-05, "362.0": 1.6428993888414273e-05}}'
FREQ_MAPS = {col: {eval(k): v for k, v in fmap.items()} for col, fmap in _json.loads(_FREQ_MAPS_RAW).items()}


def _to_bool01(series):
    s = series.astype("string").str.lower().str.strip()
    yes, no = {"1","true","yes","y","t"}, {"0","false","no","n","f"}
    out = pd.Series(np.zeros(len(s), dtype=np.float32), index=series.index)
    out[s.isin(yes)] = 1.0; out[s.isin(no)] = 0.0
    num = pd.to_numeric(series, errors="coerce")
    out[num.notna()] = (num[num.notna()] != 0).astype(np.float32)
    return out


def _build_features(df):
    out = df.copy()
    dep_cols = [c for c in ["Adult_Dependents","Child_Dependents","Infant_Dependents"] if c in out.columns]
    if dep_cols:
        out["Total_Dependents"] = out[dep_cols].sum(axis=1)
        if "Estimated_Annual_Income" in out.columns:
            inc = pd.to_numeric(out["Estimated_Annual_Income"], errors="coerce").clip(lower=0).fillna(0)
            out["Dependents_per_Income"] = out["Total_Dependents"] / (inc / 10000 + 1.0)
            out["Income_per_Dependent"]  = inc / (out["Total_Dependents"] + 1.0)
    if "Adult_Dependents" in out.columns and "Child_Dependents" in out.columns:
        adult = pd.to_numeric(out["Adult_Dependents"], errors="coerce").fillna(0)
        child = pd.to_numeric(out["Child_Dependents"], errors="coerce").fillna(0)
        out["Adult_Child_Ratio"] = adult / (child + 1.0)
        if "Vehicles_on_Policy" in out.columns:
            veh = pd.to_numeric(out["Vehicles_on_Policy"], errors="coerce").fillna(0)
            out["Vehicles_per_Adult"] = veh / (adult + 1.0)
    # Family composition
    if "Infant_Dependents" in out.columns:
        infant_n = pd.to_numeric(out["Infant_Dependents"], errors="coerce").fillna(0)
        out["Has_Infants"] = (infant_n > 0).astype("float")
    if "Child_Dependents" in out.columns:
        child_n = pd.to_numeric(out["Child_Dependents"], errors="coerce").fillna(0)
        out["Has_Children"] = (child_n > 0).astype("float")
    if "Employer_ID" in out.columns:
        out["Has_Employer"] = out["Employer_ID"].notna().astype("float")
    # Income
    if "Estimated_Annual_Income" in out.columns:
        inc = pd.to_numeric(out["Estimated_Annual_Income"], errors="coerce").clip(lower=0).fillna(0)
        out["Log_Income"] = np.log1p(inc)
        out["Income_Bucket"] = pd.cut(inc, bins=[-1,10000,25000,50000,100000,200000,np.inf], labels=False).astype("float")
    claims = pd.to_numeric(out.get("Previous_Claims_Filed", pd.Series(0, index=out.index)), errors="coerce").fillna(0)
    ncy    = pd.to_numeric(out.get("Years_Without_Claims",  pd.Series(0, index=out.index)), errors="coerce").fillna(0)
    dur    = pd.to_numeric(out.get("Previous_Policy_Duration_Months", pd.Series(0, index=out.index)), errors="coerce").fillna(0)
    if "Previous_Claims_Filed" in out.columns and "Years_Without_Claims" in out.columns:
        out["Claims_per_NoClaimYears"] = claims / (ncy + 1.0)
    if "Previous_Policy_Duration_Months" in out.columns and "Previous_Claims_Filed" in out.columns:
        out["Duration_per_Claim"] = dur / (claims + 1.0)
        out["Claims_per_Month"]   = claims / (dur + 1.0)
        out["Loyalty_Score"]      = ncy * dur / (claims + 1.0)
        out["High_Claims_Flag"]   = (claims >= 3).astype("float")
    out["Is_New_Policy"] = (dur == 0).astype("float")
    cancelled = _to_bool01(out["Policy_Cancelled_Post_Purchase"]) if "Policy_Cancelled_Post_Purchase" in out.columns else pd.Series(0.0, index=out.index)
    grace     = pd.to_numeric(out.get("Grace_Period_Extensions", pd.Series(0, index=out.index)), errors="coerce").fillna(0)
    out["Risk_Score"] = claims + cancelled + grace
    out["Cancelled_x_Claims"] = cancelled * claims
    out["Grace_x_Claims"]     = grace * claims
    if "Existing_Policyholder" in out.columns:
        out["Existing_Policyholder_01"] = _to_bool01(out["Existing_Policyholder"])
        out["Claims_if_existing"] = claims * out["Existing_Policyholder_01"]
    if "Policy_Cancelled_Post_Purchase" in out.columns:
        out["Cancelled_01"] = cancelled
    if "Deductible_Tier" in out.columns and "Custom_Riders_Requested" in out.columns:
        ded = pd.to_numeric(out["Deductible_Tier"], errors="coerce").fillna(0)
        rid = pd.to_numeric(out["Custom_Riders_Requested"], errors="coerce").fillna(0)
        out["Deductible_x_Riders"] = ded * rid
        out["High_Coverage_Flag"]  = ((ded == ded.min()) & (rid > 0)).astype("float")
    amend = pd.to_numeric(out.get("Policy_Amendments_Count", pd.Series(0, index=out.index)), errors="coerce").fillna(0)
    if "Grace_Period_Extensions" in out.columns and "Policy_Amendments_Count" in out.columns:
        out["Grace_plus_Amendments"] = grace + amend
    if "Policy_Amendments_Count" in out.columns and "Previous_Policy_Duration_Months" in out.columns:
        out["Amendments_per_Month"] = amend / (dur + 1.0)
    if "Policy_Start_Month" in out.columns:
        _month_map = {"january":1,"february":2,"march":3,"april":4,"may":5,"june":6,
                      "july":7,"august":8,"september":9,"october":10,"november":11,"december":12}
        m = out["Policy_Start_Month"].astype(str).str.lower().str.strip().map(_month_map)
        m = m.fillna(pd.to_numeric(out["Policy_Start_Month"], errors="coerce"))
        out["Policy_Start_Quarter"] = ((m - 1) // 3 + 1).clip(1, 4)
        out["Is_Year_End"] = m.isin([11,12]).astype("float")
        out["Is_Summer"]   = m.isin([6,7,8]).astype("float")
        out["Month_sin"]   = np.sin(2 * np.pi * m / 12)
        out["Month_cos"]   = np.cos(2 * np.pi * m / 12)
        out["Is_Spring"]   = m.isin([3,4,5]).astype("float")
        out["Is_Fall"]     = m.isin([9,10,11]).astype("float")
        out["Is_Winter"]   = m.isin([12,1,2]).astype("float")
        out["Is_Q1"]       = m.isin([1,2,3]).astype("float")
        out["Is_Q4"]       = m.isin([10,11,12]).astype("float")
    if "Policy_Start_Year" in out.columns:
        yr = pd.to_numeric(out["Policy_Start_Year"], errors="coerce")
        out["Policy_Year_Normalized"] = yr - yr.min()
        out["Policy_Age_2025"]  = (2025 - yr).clip(lower=0)
        out["Is_Recent_Policy"] = (yr >= 2017).astype("float")
    if "Policy_Start_Week" in out.columns:
        w = pd.to_numeric(out["Policy_Start_Week"], errors="coerce")
        out["Policy_Start_Week_Bucket"] = pd.cut(w, bins=[-1,13,26,39,53], labels=False).astype("float")
        out["Week_sin"] = np.sin(2 * np.pi * w / 52)
        out["Week_cos"] = np.cos(2 * np.pi * w / 52)
        out["Is_Year_Start_Week"] = (w <= 4).astype("float")
        out["Is_Year_End_Week"]   = (w >= 49).astype("float")
    if "Policy_Start_Day" in out.columns:
        d = pd.to_numeric(out["Policy_Start_Day"], errors="coerce").fillna(15)
        out["Is_Month_Start"]      = (d <= 5).astype("float")
        out["Is_Month_End"]        = (d >= 25).astype("float")
        out["Day_sin"]             = np.sin(2 * np.pi * d / 31)
        out["Day_cos"]             = np.cos(2 * np.pi * d / 31)
        out["Day_of_Month_Bucket"] = pd.cut(d, bins=[-1,10,20,31], labels=False).astype("float")
    if "Days_Since_Quote" in out.columns and "Underwriting_Processing_Days" in out.columns:
        dsq = pd.to_numeric(out["Days_Since_Quote"], errors="coerce").fillna(0).clip(lower=0)
        uw  = pd.to_numeric(out["Underwriting_Processing_Days"], errors="coerce").fillna(0).clip(lower=0)
        out["Quote_to_UW_Ratio"] = dsq / (uw + 1.0)
        out["Quote_plus_UW"]     = (dsq + uw).astype("float")
        out["Long_UW_Flag"]      = (uw > uw.quantile(0.75)).astype("float")
        out["Quote_Urgency"]     = dsq / (dsq + uw + 1.0)
        out["Log_DSQ"]           = np.log1p(dsq)
        out["Log_UW"]            = np.log1p(uw)
        out["UW_Efficiency"]     = uw / (dsq + 1.0)
        out["DSQ_Bucket"]        = pd.cut(dsq, bins=[-1,0,7,30,90,365,np.inf], labels=False).astype("float")
        out["Avg_Process_Step"]  = (dsq + uw) / 2.0
    if "Vehicles_on_Policy" in out.columns and "Custom_Riders_Requested" in out.columns:
        veh = pd.to_numeric(out["Vehicles_on_Policy"], errors="coerce").fillna(0)
        rid = pd.to_numeric(out["Custom_Riders_Requested"], errors="coerce").fillna(0)
        out["Vehicles_x_Riders"]  = veh * rid
        out["Riders_per_Vehicle"] = rid / (veh + 1.0)
    # Complexity & need proxies
    total_dep = pd.to_numeric(out.get("Total_Dependents", pd.Series(0, index=out.index)), errors="coerce").fillna(0)
    veh_n = pd.to_numeric(out.get("Vehicles_on_Policy", pd.Series(0, index=out.index)), errors="coerce").fillna(0)
    rid_n = pd.to_numeric(out.get("Custom_Riders_Requested", pd.Series(0, index=out.index)), errors="coerce").fillna(0)
    out["Policy_Complexity"] = total_dep + veh_n + rid_n
    if "Estimated_Annual_Income" in out.columns:
        income_n = pd.to_numeric(out["Estimated_Annual_Income"], errors="coerce").clip(lower=0).fillna(0)
        out["Coverage_Need"]       = np.log1p(income_n) * (total_dep + 1)
        out["Affordability"]       = income_n / (out["Policy_Complexity"] + 1)
        out["Income_x_Dependents"] = income_n * total_dep
        out["Sqrt_Income"]         = np.sqrt(income_n)
        out["Income_Risk_Ratio"]   = income_n / (out["Risk_Score"] + 1.0)
        ibucket = pd.cut(income_n, bins=[-1,10000,25000,50000,100000,200000,np.inf], labels=False).fillna(0).astype("float")
        out["Income_Volatility_Proxy"] = np.log1p(income_n) / (ibucket + 1.0)
        out["Income_Risk_Ratio"]   = income_n / (out["Risk_Score"] + 1.0)
        if "Has_Employer" in out.columns:
            out["Employer_x_Income"] = out["Has_Employer"] * income_n
        if "Custom_Riders_Requested" in out.columns:
            out["Policy_Load"] = out["Policy_Complexity"] / (income_n / 50000.0 + 1.0)
    # Extra claims intensity
    if "Previous_Claims_Filed" in out.columns:
        out["Claims_Squared"]      = claims ** 2
        out["Claims_Acceleration"] = (claims ** 2) / (dur + 1.0)
        out["No_Claims_Ratio"]     = ncy / (ncy + claims + 1.0)
    if "Previous_Claims_Filed" in out.columns and "Previous_Policy_Duration_Months" in out.columns:
        out["Claim_Gap"]           = ncy - dur
    if "Previous_Claims_Filed" in out.columns and "Years_Without_Claims" in out.columns:
        out["Claims_NCY_Interact"] = claims * ncy
    # Coverage interactions
    if "Custom_Riders_Requested" in out.columns:
        rid = pd.to_numeric(out["Custom_Riders_Requested"], errors="coerce").fillna(0)
        out["Riders_x_Dependents"]  = rid * total_dep
        out["Dep_Coverage_Density"] = (total_dep + veh_n) / (rid + 1.0)
    # Cross-interactions
    if "Grace_Period_Extensions" in out.columns and "Policy_Amendments_Count" in out.columns:
        out["Grace_x_Amended"]      = grace * amend
    if "Policy_Cancelled_Post_Purchase" in out.columns:
        out["Cancelled_x_Duration"] = cancelled * dur
        out["Cancelled_x_Amended"]  = cancelled * amend
        if "Estimated_Annual_Income" in out.columns:
            income_n = pd.to_numeric(out["Estimated_Annual_Income"], errors="coerce").clip(lower=0).fillna(0)
            out["Risk_x_Income"]    = out["Risk_Score"] / (np.log1p(income_n) + 1.0)
    # Broker dominance
    if "Broker_ID" in out.columns:
        top5_brokers = {9.0, 14.0, 240.0, 7.0, 250.0}
        bid = pd.to_numeric(out["Broker_ID"], errors="coerce")
        out["Is_Top_Broker"]  = bid.isin(top5_brokers).astype("float")
        out["Is_Rare_Broker"] = (~bid.isin(top5_brokers) & bid.notna()).astype("float")
    # Amendment intensity
    if "Policy_Amendments_Count" in out.columns:
        out["High_Amendment_Flag"] = (amend >= 2).astype("float")
        out["Amend_x_Claims"]      = amend * claims
        out["Amend_x_Grace"]       = amend * grace
    return out


def preprocess(df):
    out = _build_features(df)
    for c in FEATURE_COLS:
        if c not in out.columns: out[c] = np.nan
    for c in CAT_COLS:
        if c in out.columns: out[c] = out[c].astype("string").fillna("__MISSING__")
    for c in NUM_COLS:
        if c in out.columns: out[c] = pd.to_numeric(out[c], errors="coerce").fillna(0.0)
    return out


def load_model():
    return joblib.load("model.pkl")


def predict(df, model):
    clf        = model["model"]
    thresholds = np.array(model["thresholds"])
    # Apply frequency encoding from training-time maps
    freq_maps  = model.get("freq_maps", {})
    for c, fmap in freq_maps.items():
        if c in df.columns:
            df[f"{c}_freq"] = df[c].map(fmap).fillna(0).astype(np.float32)
    X          = df[FEATURE_COLS]
    proba      = clf.predict_proba(X)
    adjusted   = proba * thresholds[np.newaxis, :]
    preds      = np.argmax(adjusted, axis=1).astype(int)
    return pd.DataFrame({
        "User_ID": df[ID_COL].values,
        "Purchased_Coverage_Bundle": preds
    })
