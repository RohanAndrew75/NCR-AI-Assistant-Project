import pandas as pd

def load_champion_examples(file="feedback_log.csv", top_n=3):
    try:
        df = pd.read_csv(file)

        # Filter GOOD examples
        df_good = df[
            (df["feedback"] == "Good") 
        ]

        # Take latest top examples
        df_good = df_good.sort_values(by="final_score", ascending=False).head(top_n)

        examples = ""

        for _, row in df_good.iterrows():
            examples += f"\nExample NCR:\n{row['improved_ncr']}\n"

        return examples if examples else "No prior examples available."

    except:
        return "No prior examples available."