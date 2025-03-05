from fpdf import FPDF
import pandas as pd

class PDFReport(FPDF):
    def country_page(self, country_data: pd.DataFrame):
        self.add_page()
        self.set_font('Arial', 'B', 16)
        self.cell(0, 10, f"{country_data['name']} Investment Summary", 0, 1)
        
        # Add table with key metrics
        metrics = country_data[['GDP_growth', 'Inflation', 'Debt_to_GDP']]
        self.set_font('Arial', size=12)
        for index, row in metrics.iterrows():
            self.cell(0, 10, f"{row.name}: {row.value}%", 0, 1)