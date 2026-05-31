def __init__(self, vectorstore=None, llm=None):
    self.llm = llm

    # ✅ ALWAYS ensure embeddings exist
    self.embeddings = OpenAIEmbeddings(
        model="text-embedding-3-small",
        openai_api_key=os.getenv("OPENAI_API_KEY")
    )

    # ✅ FIX: safe vectorstore initialization
    if vectorstore is None:
        self.vectorstore = Chroma(
            persist_directory="vector_db",
            embedding_function=self.embeddings
        )
    else:
        self.vectorstore = vectorstore