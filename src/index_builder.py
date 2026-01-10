# base de datos vectorial
import chromadb  

# Framework llamaindex
from llama_index.core import (
    VectorStoreIndex,
    SimpleDirectoryReader,
    StorageContext,
    Settings
) 
# Unstructured.io 
from llama_index.readers.file.unstructured import UnstructuredReader

# guardar en Base de datos vectorial
from llama_index.vector_stores.chroma import ChromaVectorStore

# Embedings 
from llama_index.embeddings.fastembed import FastEmbedEmbedding

# definir tamaño de chunks
from llama_index.core.node_parser import SentenceSplitter

def build_index_for_pdf(pdf_path: str, chunk_size: int = 768, chunk_overlap: int = 96):
    # Use local FastEmbed embeddings (no external API required)
    Settings.embed_model = FastEmbedEmbedding(
        model_name="BAAI/bge-base-en-v1.5"
    )

    text_splitter = SentenceSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        paragraph_separator="\n\n",  # Respect paragraph boundaries
        secondary_chunking_regex="[.!?]",  # Split on sentences
    )
    Settings.node_parser = text_splitter

    reader = SimpleDirectoryReader(
        input_files=[pdf_path],
        file_extractor={".pdf": UnstructuredReader()}
    )

    documents = reader.load_data()

    chroma_client = chromadb.Client()
    collection = chroma_client.create_collection("single_pdf_index")

    vector_store = ChromaVectorStore(
        chroma_collection=collection
    ) # no hay persistencia pero lo dejo aqui para resaltar la importancia de la base de datos vectorial y su costo computacional

    storage_context = StorageContext.from_defaults(
        vector_store=vector_store
    )

    index = VectorStoreIndex.from_documents(
        documents,
        storage_context=storage_context
    )

    return index
