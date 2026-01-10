from pydantic import BaseModel, Field, field_validator
from typing import Optional, List

# 1. Metadata del proyecto
class ProjectMetadata(BaseModel):
    project_name: Optional[str] = Field(None, description=(
            "Name of the mining project. "
            "Look for: 'Project Name', '[Name] Project', 'Property Name'. "
            "Example: 'Guadalupe Project', 'San Marcos Gold Operation'. "
            "If not found, return null."
        ))
    company_name: Optional[str] = Field(None, description=(
            "Name of the company owning or operating the project. "
            "Look for: 'Owner', 'Operator', 'Company', header/footer of pages. "
            "Example: 'Aris Mining Corporation', 'SSR Mining Inc.'. "
            "If not found, return null."
        ))
    location_country: Optional[str] = Field(None, description=(
            "Country where the project is located. "
            "Look for: 'Location', 'Country', 'Jurisdiction'. "
            "Example: 'Argentina', 'Mexico', 'Colombia', 'Peru'. "
            "Return ONLY the country name. If not found, return null."
        ))
    location_region: Optional[str] = Field(None, description=(
            "State, province, or region within the country. "
            "Look for: 'Province', 'State', 'Region', 'Department'. "
            "Example: 'Antioquia', 'Caldas', 'Santander'. "
            "If not found, return null."
        )
    )
    report_date: Optional[str] = Field(None, description=(
            "Effective date or publication date of the technical report. "
            "Look for: 'Effective Date', 'Report Date', 'Date of Report'. "
            "Format: YYYY-MM-DD preferred (e.g., '2023-06-30'). "
            "Also accept formats like 'June 30, 2023' or '30-Jun-2023'. "
            "If not found, return null."
        ))

# 2.Recursos minerales
class MineralResource(BaseModel):
    category: str = Field(..., description=(
            "Resource classification. MUST be one of: 'Measured', 'Indicated', or 'Inferred'. "
            "Look for exact matches or abbreviations like 'M&I', 'Ind.', 'Inf.'. "
            "This field is REQUIRED - if category is unclear, skip this resource entry."
        ))
    tonnage_mt: Optional[float] = Field(None, description=(
            "Total tonnage in millions of metric tonnes (Mt). "
            "Look for: columns labeled 'Tonnes', 'Tonnage (Mt)', 'Quantity'. "
            "Convert to Mt if given in tonnes (divide by 1,000,000). "
            "Example: 5.2 (means 5.2 million tonnes), 0.45 Mt"
            "If tonnage not found or unclear, return null."
        ))
    grade_primary: Optional[float] = Field(None, description=(
            "Average grade of the primary metal. "
            "For GOLD: typically in g/t (grams per tonne). Example: 2.5 (means 2.5 g/t Au). "
            "For COPPER: typically in % (percent). Example: 0.8 (means 0.8% Cu). "
            "For SILVER: typically in g/t. Example: 85 (means 85 g/t Ag). "
            "Return ONLY the numeric value without units. Units should be clear from context. "
            "If grade not found, return null."
        ))
    
    contained_metal: Optional[str] = Field(None, description=(
            "Contained metal estimate WITH units. "
            "Look for: columns like 'Contained Gold', 'Contained Ounces', 'Metal Content'. "
            "Include units in the string. "
            "Examples: '2.5 Moz Au', '425,000 oz Au', '150 Mlb Cu', '3.2M oz Ag'. "
            "Common units: Moz (million ounces), oz (ounces), Mlb (million pounds), kg, tonnes. "
            "If not stated explicitly, return null."
        ))

    @field_validator('category') # algunos validadores de forma debido a que no hay un estandar claro en la nomenclatura
    @classmethod
    def validate_category(cls, v):
        if v is None:
            return "Unknown"
        
        v_clean = str(v).strip()
        v_lower = v_clean.lower()

        if 'meas' in v_lower:
            return 'Measured'
        if 'ind' in v_lower or 'm&i' in v_lower:
            return 'Indicated'
        if 'inf' in v_lower:
            return 'Inferred'
            
        return v_clean

# 3. Reservas minerales
class MineralReserve(BaseModel):
    category: str = Field(..., description=(
            "Reserve classification. MUST be one of: 'Proven' or 'Probable'. "
            "Look for exact matches or abbreviations like 'Prov.', 'Prob.', 'P&P'. "
            "Sometimes written as 'Proved'. "
            "This field is REQUIRED - if category is unclear, skip this reserve entry."
        ))
    tonnage_mt: Optional[float] = Field(None, description=(
            "Total tonnage in millions of metric tonnes (Mt). "
            "Same instructions as mineral resources. "
            "Reserves are typically SMALLER than resources. "
            "If tonnage not found, return null."
        ))
    grade_primary: Optional[float] = Field(None, description=(
            "Average grade of the primary metal. "
            "Same format as resources: numeric value only, no units. "
            "Example: 3.2 for gold, 1.1 for copper. "
            "If grade not found, return null."
        ))
    contained_metal: Optional[str] = Field(None, description=(
            "Contained metal estimate WITH units. "
            "Same format as resources. "
            "Examples: '1.8 Moz Au', '280,000 oz Au', '95 Mlb Cu'. "
            "If not found, return null."
        ))
    
    @field_validator('category') # algunos validadores de forma debido a que no hay un estandar claro en la nomenclatura
    @classmethod
    def validate_reserve_category(cls, v: str) -> str:
        if not v:
            return "Unknown"
        v_clean = str(v).strip()
        v_lower = v_clean.lower()

        if 'prov' in v_lower:
            return 'Proven'
        
        if 'prob' in v_lower or 'p&p' in v_lower:
            return 'Probable'
            
        return v_clean

# 4. Información Económica
class EconomicAnalysis(BaseModel):
    capex_initial: Optional[str] = Field(None, description=(
            "Initial Capital Expenditure (CAPEX) WITH currency and scale. "
            "Look for: 'Initial CAPEX', 'Capital Cost', 'Pre-production Capital', "
            "'Upfront Capital', 'Construction Capital'. "
            "Include currency (USD, CAD, etc.) and scale (M for millions, B for billions). "
            "Examples: '$150M USD', '$1.2B CAD', 'US$245 million'. "
            "If not found or unclear, return null."
        )
    )
    opex_life_of_mine: Optional[str] = Field(None, description=(
            "Operating Expenditure (OPEX) or All-In Sustaining Cost (AISC) WITH units. "
            "Look for: 'Life of Mine OPEX', 'Operating Cost', 'AISC', 'Cash Cost', "
            "'Operating Cost per tonne', 'per ounce'. "
            "Include units clearly. "
            "Examples: '$45/t', '$850/oz Au', '$12.50 per tonne', 'US$725/oz AISC'. "
            "If not found, return null."
        ))
    npv_discounted: Optional[str] = Field(None, description=(
            "Net Present Value (NPV) WITH discount rate and currency. "
            "Look for: 'NPV', 'Net Present Value', often with discount rate like 'NPV5%', 'NPV@5%'. "
            "MUST include discount rate if available and currency. "
            "Examples: 'NPV@5% $200M USD', '$185M at 5% discount', 'US$320M NPV (5%)'. "
            "Common discount rates: 5%, 8%, 10%. "
            "After-tax vs pre-tax should be noted if stated. "
            "If not found, return null."
        ))
    irr_after_tax: Optional[str] = Field(None, description=(
            "Internal Rate of Return (IRR) after tax. "
            "Look for: 'IRR', 'After-Tax IRR', 'Post-Tax IRR', 'Return on Investment'. "
            "Include % symbol and specify if after-tax or pre-tax if stated. "
            "Examples: '22.5% after-tax', '18% IRR', '25.3% (post-tax)'. "
            "After-tax is preferred over pre-tax. "
            "If not found, return null."
        ))

# Esquema para facilitar la busqueda de listas en recursos y reservas
class MineralResourceList(BaseModel):
    resources: List[MineralResource] = Field(..., description=(
            "List of mineral resource classifications. "
            "Each entry represents a different category (Measured, Indicated, Inferred). "
            "If no resources section found, return empty list. "
            "DO NOT create fake entries - only include what is explicitly stated."
        ))

class MineralReserveList(BaseModel):
    reserves: List[MineralReserve] = Field(..., description=(
            "List of mineral reserve classifications. "
            "Each entry represents a different category (Proven, Probable). "
            "If no reserves section found, return empty list. "
            "DO NOT create fake entries - only include what is explicitly stated."
        ))



# MASTER SCHEMA: The root object capable of holding everything
# class TechnicalReportExtraction(BaseModel):
#     metadata: ProjectMetadata
#     resources: List[MineralResource] = Field(default_factory=list, description=(
#             "List of mineral resource classifications. "
#             "Each entry represents a different category (Measured, Indicated, Inferred). "
#             "If no resources section found, return empty list. "
#             "DO NOT create fake entries - only include what is explicitly stated."
#         ))
#     reserves: List[MineralReserve] = Field(default_factory=list, description=(
#             "List of mineral reserve classifications. "
#             "Each entry represents a different category (Proven, Probable). "
#             "If no reserves section found, return empty list. "
#             "DO NOT create fake entries - only include what is explicitly stated."
#         ))
#     economics: EconomicAnalysis

#     class Config:
#         json_schema_extra = {
#             "example": {
#                 "metadata": {
#                     "project_name": "Juanicipio Project",
#                     "company_name": "MAG Silver Corp",
#                     "location_country": "Mexico",
#                     "location_region": "Zacatecas",
#                     "report_date": "2023-03-31"
#                 },
#                 "resources": [
#                     {
#                         "category": "Measured",
#                         "tonnage_mt": 2.5,
#                         "grade_primary": 450,
#                         "contained_metal": "36 Moz Ag"
#                     },
#                     {
#                         "category": "Indicated",
#                         "tonnage_mt": 3.8,
#                         "grade_primary": 385,
#                         "contained_metal": "47 Moz Ag"
#                     }
#                 ],
#                 "reserves": [
#                     {
#                         "category": "Proven",
#                         "tonnage_mt": 1.8,
#                         "grade_primary": 475,
#                         "contained_metal": "27 Moz Ag"
#                     }
#                 ],
#                 "economics": {
#                     "capex_initial": "$185M USD",
#                     "opex_life_of_mine": "$725/oz AISC",
#                     "npv_discounted": "NPV@5% $320M USD",
#                     "irr_after_tax": "28.5% after-tax"
#                 }
#             }
#         }
