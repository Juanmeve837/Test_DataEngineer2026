import pandas as pd

# herramienta para guardar metadata en formato csv, notese la extructura para disminuir alucionaciones
def save_metadata_csv(metadata, output_path, timestamp, file_id):

    data = {
        'timestamp': timestamp, 
        'file_id': file_id,
        'project_name': metadata.project_name,
        'company_name': metadata.company_name,
        'location_country': metadata.location_country,
        'location_region': metadata.location_region,
        'report_date': metadata.report_date,
    }
    
    df = pd.DataFrame([data])
    append_csv(df, output_path)
    print(f"   💾 Saved: {output_path}")

# herramienta para guardar resourses es mas abierta
def save_resources_csv(resources, output_path,timestamp, file_id):
    
    if not resources:
        df = pd.DataFrame(columns=['category', 'tonnage_mt', 'grade_primary', 'contained_metal'])
    else:
        data = [r.model_dump() for r in resources]
        
        df = pd.DataFrame(data)
    
    df.insert(0, 'file_id', file_id)
    df.insert(0, 'timestamp', timestamp)

    append_csv(df, output_path)
    print(f"   💾 Saved: {output_path} ({len(df)} rows)")

# herramienta para guardar rescursos es mas abierta
def save_reserves_csv(reserves, output_path,timestamp, file_id):
    
    if not reserves:
        df = pd.DataFrame(columns=['category', 'tonnage_mt', 'grade_primary', 'contained_metal'])
    else:
        data = [r.model_dump() for r in reserves]
        
        df = pd.DataFrame(data)
    
    df.insert(0, 'file_id', file_id)
    df.insert(0, 'timestamp', timestamp)

    append_csv(df, output_path)
    print(f"   💾 Saved: {output_path} ({len(df)} rows)")

# herramienta para guardar seccion economica en formato csv, notese la extructura para disminuir alucionaciones
def save_economics_csv(economics, output_path,timestamp, file_id):

    data = {
        'timestamp': timestamp, 
        'file_id': file_id,
        'capex_initial': economics.capex_initial,
        'opex_life_of_mine': economics.opex_life_of_mine,
        'npv_discounted': economics.npv_discounted,
        'irr_after_tax': economics.irr_after_tax,
    }
    
    df = pd.DataFrame([data])
    append_csv(df, output_path)
    print(f"   💾 Saved: {output_path}")

#Herramienta para no borrar la información si el csv existe, mas bien adicione la info y una columna timestamp y file_id
def append_csv(df, output_path):
    file_exists = output_path.exists()
    
    df.to_csv(
        output_path,
        mode='a',
        index=False,
        header=not file_exists
    )
