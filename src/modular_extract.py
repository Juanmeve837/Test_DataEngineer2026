## llamadas a LLM y estructuracion con Pyndantic
from llama_index.core.output_parsers import PydanticOutputParser
from llama_index.llms.openai import OpenAI
from llama_index.core import Settings

# Manejo de ratelimit limitación de la estructura que estamos usando
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
from openai import RateLimitError
import time

# Salida estructurada usando Pyndantic
from src.schema import (
    ProjectMetadata,
    MineralResource, 
    MineralReserve,
    MineralResourceList,
    MineralReserveList,
    EconomicAnalysis
)

# Variables de entorno
from src.settings import GITHUB_TOKEN, MODEL_NAME


# Politica de intentos para manejar ratelimit, estable para trabajo Expediente a expediente
retry_policy = retry(
    stop=stop_after_attempt(5),
    wait=wait_exponential(multiplier=1, min=4, max=60),
    retry=retry_if_exception_type(RateLimitError)
)

## Se va crear una clase debido a que se va usar el mismo motor de LLM
class ModularExtractor:

    def __init__(self):
        """Initialize LLM."""
        self.llm = OpenAI(
            model=MODEL_NAME,
            api_key=GITHUB_TOKEN,
            api_base="https://models.github.ai/inference",  # <--- Si se cambia el llm se debe cambiar o dejar vacio por defecto 
            temperature=0, # <-- El terror de los llm, para buscar "las mismas respuestas" dejar en 0
        )
        Settings.llm = self.llm
        
        self.query_config = {
            "llm": self.llm,
            "response_mode": "compact",  # <--- El alma del asunto se puede particularizar para cada "extract" si se busca agentizar
            "similarity_top_k": 10,
        }

    @retry_policy
    def extract_metadata(self, index) -> ProjectMetadata:
     
        parser = PydanticOutputParser(output_cls=ProjectMetadata)
        
        query_engine = index.as_query_engine(
            output_parser=parser,
            output_cls=ProjectMetadata, 
            **self.query_config
            )
        
        query = """
        Find project metadata in the first 10 pages (cover, title, summary):

        project_name: Full name of the mining project
        company_name: Owner or operator company
        ocation_country: Country only
        location_region: State/province/region
        report_date: Date of report (YYYY-MM-DD format)

        Look in: Cover page, header/footer, table of contents, summary section.
        Return null if not found. Extract now.
        """
        
        response = query_engine.query(query)
    
        return response
    
    @retry_policy
    def extract_resources(self, index) -> list[MineralResource]:

        parser = PydanticOutputParser(output_cls=MineralResourceList) # Notese que aqui se cambio el schema un poco para favoreser la salida como lista
        
        query_engine = index.as_query_engine(
            output_parser=parser,
            output_cls=MineralResourceList, 
            **self.query_config
            )
        
        query = """
         
        Find the Mineral Resources section/table (usually pages 40-70).

        Extract ALL resource categories found:
        - Indicated: tonnage_mt (number), grade_primary (number), contained_metal (with units)  
        - Measured: tonnage_mt (number), grade_primary (number), contained_metal (with units)
        - Inferred: tonnage_mt (number), grade_primary (number), contained_metal (with units)

        Create SEPARATE entry for each category.

        Format: 
        {
        "category": "Measured",
        "tonnage_mt": 5.2,
        "grade_primary": 2.5,
        "contained_metal": "425,000 oz Au"
        }

        If no resources section exists, say "No resources found".
        Extract now."""

        try:
            response = query_engine.query(query)

            return response.response.resources # tambien cambia el tipo de salida para facilitar la conversion a json o csv
            
        except Exception as e:
            print(f"   ❌ Error: {e}")
            return []     

    @retry_policy
    def extract_reserves(self, index) -> list[MineralReserve]:

        parser = PydanticOutputParser(output_cls=MineralReserveList)
        
        query_engine = index.as_query_engine(
            output_parser=parser,
            output_cls=MineralReserveList, 
            **self.query_config
            )
        
        query = """
        
        Find the Mineral Reserves section/table (usually pages 70-90).

        Extract ALL reserve categories found:
        - Proven: tonnage_mt (number), grade_primary (number), contained_metal (with units)
        - Probable: tonnage_mt (number), grade_primary (number), contained_metal (with units)

        Create SEPARATE entry for each category.

        Format:
        {
        "category": "Proven",
        "tonnage_mt": 3.8,
        "grade_primary": 3.2,
        "contained_metal": "380,000 oz Au"
        }

        If no reserves section exists, say "No reserves found".
        Extract now."""

        try:
            response = query_engine.query(query)

            return response.response.reserves
            
        except Exception as e:
            print(f"   ❌ Error: {e}")
            return []

    @retry_policy
    def extract_economics(self, index) -> EconomicAnalysis:  # Mucha oportunidad de mejora sobretodo en el "prompt"

        parser = PydanticOutputParser(output_cls=EconomicAnalysis)
        
        query_engine = index.as_query_engine(
            output_parser=parser,
            output_cls=EconomicAnalysis, 
            **self.query_config
            )
        
        query = """
        Find economic information (Capital and operating costs, summary, or economic analysis section):

        Extract these 4 values:
        capex_initial: Initial CAPEX with currency (e.g., "$150M USD")
        opex_life_of_mine: Operating cost with units (e.g., "$850/oz", "$45/t")
        npv_discounted: NPV with discount rate (e.g., "NPV@5% $200M USD")
        irr_after_tax: IRR with percent (e.g., "22.5% after-tax")

        Look in: Economic Analysis, Capital & Operating Costs, Summary tables.
        Return null if not found. Extract now."""
        
        response = query_engine.query(query)
        
        return response       

# ============================================================================
# Se embuelve en una unica funcion que recibe el indice creado en "index_builder.py" y only
# only puede ser una seccion en especifico i.e = "metadata", una lista de secciones i.e = ["metadata","economics"]
# o puede dejarse en None que signifca que toma todas las secciones necesarias en la prueba  

def extract_all_sections(index, only=None):

    extractor = ModularExtractor()
    
    registry = {
        "metadata": extractor.extract_metadata,
        "resources": extractor.extract_resources,
        "reserves": extractor.extract_reserves,
        "economics": extractor.extract_economics,
    }
    
    if only is None:
        sections_to_run = list(registry.keys())
    elif isinstance(only, str):
        sections_to_run = [only]
    elif isinstance(only, (list, tuple)):
        sections_to_run = list(only)
    else:
        raise ValueError("`only` must be None, str, or list[str]")

    invalid = set(sections_to_run) - set(registry.keys())
    if invalid:
        raise ValueError(f"Invalid section(s): {invalid}")
    results = {}
    
    for section in sections_to_run:
        print(f"\n▶ Extracting {section.upper()}")

        try:
            results[section] = registry[section](index)
        except Exception as e:
            print(f"❌ Error extracting {section}: {e}")
            raise

    return results