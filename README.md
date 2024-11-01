# RAG for Research AI: Intelligent Document Management and Exploration

**Project Overview :**
The objective of this assignment is to create an end-to-end system for extracting, managing, and interacting with research publications from the CFA Institute Research Foundation, enabling users to explore and analyze information in a seamless and efficient manner. The system begins with an automated data ingestion pipeline, where publication data, including titles, summaries, images, and PDFs, is scraped and stored. The documents are organized in an AWS S3 bucket, while metadata and links are maintained in a Snowflake database for structured access. The ingestion process is automated through Airflow, ensuring that the data retrieval, storage, and database population are efficient, reliable, and scalable.Building on this foundation, a user-facing application is developed using FastAPI and Streamlit, allowing users to interact with the stored documents. Users can explore documents, generate summaries, and conduct Q&A sessions through a multi-modal Retrieval-Augmented Generation (RAG) model that leverages NVIDIA services for on-the-fly summaries and interactive querying. To facilitate document-specific insights, the system includes indexing and search functionalities, allowing users to search within research notes or full document text to extract meaningful information. To ensure accessibility and scalability, the entire application is containerized with Docker and deployed on a public cloud, offering a robust, user-friendly platform that supports efficient document exploration and enhances the research experience.



**Key Technologies :**

AWS S3 , Snowflake , Streamlit, OpenAI, VS code, CodeLabs, Git, Docker, Python , FAISS , llama Index, Apache Airflow, FastAPI, Nvidia LLM

**Desired Outcome or Solution :**

The desired solution is a fully automated and interactive platform that allows for easy ingestion, storage, and retrieval of CFA Institute research publications.
The system should include a pipeline for scraping, storing, and structuring data in AWS S3 and Snowflake, along with an interface built with FastAPI and Streamlit.
Users should be able to browse documents, generate summaries, and conduct Q&A sessions using a multi-modal Retrieval-Augmented Generation (RAG) model.
The platform should provide accurate, document-specific insights, support incremental indexing, and offer efficient search functionality, all accessible through a publicly deployed application.


**Architecture diagram :**

![image](https://github.com/user-attachments/assets/8a6d5b50-4e06-4db7-84ad-2aaa9ac7643f)





**Contribution :**

WE ATTEST THAT WE HAVEN’T USED ANY OTHER STUDENTS’ WORK IN OUR 
ASSIGNMENT AND ABIDE BY THE POLICIES LISTED IN THE STUDENT HANDBOOK

| Name            | Contribution %                       |
|------------------|-------------------------------------|
| Shubham Agarwal  | 33.33 %                             |
| Chinmay Sawant   | 33.34 %                             |
| Pranav Sonje     | 33.33 %                             |

**Documentation files Team_9** 

**Code labs** - https://codelabs-preview.appspot.com/?file_id=1bWeRfD-PZkUzgzmZkl6oEnWgsRIx5cKflwPPp1grAXk#7

**Google Doc** - 

**Video** - 

**Web Link** - http://10.110.35.159:8501 
