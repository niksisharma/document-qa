import streamlit as st
from openai import OpenAI
from bs4 import BeautifulSoup
import PyPDF2
import os

__import__('pysqlite3')
import sys
sys.modules['sqlite3'] = sys.modules.pop('pysqlite3')

import chromadb

# Show title and description.
st.title("# Nikita's Lab 4")

chromadb_path = "./ChromaDB_for_lab"

chroma_client = chromadb.PersistentClient(path=chromadb_path)

# Initialize clients
openai_api_key = st.secrets["OPENAI_API_KEY"]

if 'openai_client' not in st.session_state:
    st.session_state.openai_client = OpenAI(api_key=openai_api_key)

def add_to_collection(collection, text, filename):
    """Add a document to the ChromaDB collection with OpenAI embeddings"""
    openai_client = st.session_state.openai_client
    response = openai_client.embeddings.create(
        input=text,
        model="text-embedding-3-small"
    )

    embedding = response.data[0].embedding

    collection.add(
        documents=[text],
        ids=[filename],
        embeddings=[embedding],
        metadatas=[{"filename": filename}]
    )

def extract_text_from_pdf_file(file_obj):
    """Extract text from PDF file object"""
    try:
        pdf_reader = PyPDF2.PdfReader(file_obj)
        text = ""
        for page in pdf_reader.pages:
            text += page.extract_text() + "\n"
        return text
    except Exception as e:
        st.error(f"Error reading PDF: {e}")
        return ""

def create_lab4_vectordb():
    """Create ChromaDB collection and populate with PDF documents from local directory"""
    try:
        # Create or get collection
        collection = chroma_client.get_or_create_collection(
            name="Lab4Collection",
            metadata={"hnsw:space": "cosine"}
        )
        
        st.write("📁 Loading PDF files from repository...")
        
        # Define the path to your PDFs (adjust this path as needed)
        pdf_directory = "./pdfs"
        
        pdf_files = []
        pdf_path = None
        
        if os.path.exists(pdf_directory):
            files = [f for f in os.listdir(pdf_directory) if f.lower().endswith('.pdf')]
            if files:
                pdf_files = files
                pdf_path = pdf_directory
        
        if not pdf_files:
            st.error("❌ No PDF files found in the repository. Please check the file paths.")
            st.write("Looking for PDFs in these directories:", possible_paths)
            return None
        
        st.write(f"📂 Found {len(pdf_files)} PDF files in: `{pdf_path}`")
        
        # Display found files
        st.write("Files to process:")
        for pdf_file in pdf_files:
            st.write(f"- {pdf_file}")
        
        for i, pdf_filename in enumerate(pdf_files):
            pdf_file_path = os.path.join(pdf_path, pdf_filename)
            st.write(f"Processing: {pdf_filename}")
            
            try:
                # Read PDF file from local path
                with open(pdf_file_path, 'rb') as file:
                    text_content = extract_text_from_pdf_file(file)
                
                if text_content.strip(): 
                    # Add to collection
                    add_to_collection(collection, text_content, pdf_filename)
                    st.write(f"✅ Added {pdf_filename} to vector database")
                    processed_count += 1
                else:
                    st.warning(f"⚠️ No text extracted from {pdf_filename}")
                    
            except Exception as e:
                st.error(f"❌ Error processing {pdf_filename}: {e}")
        
        st.success(f"✅ Successfully processed {processed_count}/{len(pdf_files)} PDF files!")
        return collection
            
    except Exception as e:
        st.error(f"Error creating vector database: {e}")
        return None

def test_vectordb_search(collection, search_query, top_k=3):
    """Test the vector database with a search query"""
    if collection is None:
        st.error("Vector database not available for testing.")
        return
    
    try:
        openai_client = st.session_state.openai_client
        
        # Create embedding for search query
        response = openai_client.embeddings.create(
            input=search_query,
            model="text-embedding-3-small"
        )
        query_embedding = response.data[0].embedding
        
        # Search the collection
        results = collection.query(
            query_embeddings=[query_embedding],
            n_results=top_k
        )
        
        st.write(f"🔍 Search Results for: **'{search_query}'**")
        
        if results['ids'] and len(results['ids'][0]) > 0:
            st.write(f"Top {top_k} most relevant documents:")
            for i, doc_id in enumerate(results['ids'][0]):
                distance = results['distances'][0][i] if 'distances' in results else 0
                st.write(f"{i+1}. **{doc_id}** (similarity score: {1-distance:.3f})")
        else:
            st.write("No documents found matching the search query.")
            
    except Exception as e:
        st.error(f"Error during search: {e}")

# Main application logic
def main():
    st.markdown("## Vector Database Setup and Testing")
    
    # Create vector database once per session
    if 'Lab4_vectorDB' not in st.session_state:
        st.write("🚀 Creating vector database for the first time...")
        
        with st.spinner("Setting up ChromaDB collection..."):
            collection = create_lab4_vectordb()
            if collection is not None:
                st.session_state.Lab4_vectorDB = collection
                st.success("✅ Vector database created and stored in session state!")
    else:
        st.info("✅ Vector database already exists in session state.")
        collection = st.session_state.Lab4_vectorDB
    
    # Testing section
    if 'Lab4_vectorDB' in st.session_state:
        st.markdown("## Test Vector Database")
        
        # Test search options
        search_options = ["Generative AI", "Text Mining", "Data Science Overview", "Custom Query"]
        selected_option = st.selectbox("Choose a test search query:", search_options)
        
        if selected_option == "Custom Query":
            search_query = st.text_input("Enter your custom search query:")
        else:
            search_query = selected_option
        
        # Number of results to return
        top_k = st.slider("Number of top results to return:", 1, 10, 3)
        
        if st.button("🔍 Search Vector Database") and search_query:
            test_vectordb_search(st.session_state.Lab4_vectorDB, search_query, top_k)
    
    # Debug information
    with st.expander("Debug Information"):
        st.write("Session State Keys:", list(st.session_state.keys()))
        if 'Lab4_vectorDB' in st.session_state:
            try:
                collection = st.session_state.Lab4_vectorDB
                count = collection.count()
                st.write(f"Documents in collection: {count}")
            except Exception as e:
                st.write(f"Error getting collection info: {e}")
        
        # Show current directory and files for debugging
        st.write("Current working directory:", os.getcwd())
        st.write("Files in current directory:")
        try:
            current_files = os.listdir(".")
            pdf_files_found = [f for f in current_files if f.lower().endswith('.pdf')]
            st.write(f"PDF files in current directory: {pdf_files_found}")
            
            # Check common subdirectories
            common_dirs = ['pdfs', 'documents', 'files', 'data']
            for dir_name in common_dirs:
                if os.path.exists(dir_name):
                    dir_files = os.listdir(dir_name)
                    pdf_files_in_dir = [f for f in dir_files if f.lower().endswith('.pdf')]
                    st.write(f"PDF files in {dir_name}/: {pdf_files_in_dir}")
        except Exception as e:
            st.write(f"Error listing files: {e}")

if __name__ == "__main__":
    main()