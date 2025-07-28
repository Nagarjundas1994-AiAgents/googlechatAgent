#!/usr/bin/env python3
"""
Script to set up Vertex AI Vector Search index and endpoint
"""

import os
import sys
import time
from google.cloud import aiplatform
from google.oauth2 import service_account
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def setup_vector_search():
    """Set up Vertex AI Vector Search index and endpoint"""
    
    # Get configuration
    project_id = os.getenv("GCP_PROJECT_ID")
    location = os.getenv("GCP_LOCATION", "us-central1")
    index_name = os.getenv("VECTOR_INDEX_NAME", "ai-agent-vector-index")
    endpoint_name = os.getenv("VECTOR_INDEX_ENDPOINT_NAME", "ai-agent-vector-endpoint")
    service_account_file = os.getenv("GCP_SERVICE_ACCOUNT_FILE")
    
    if not project_id:
        print("❌ Error: GCP_PROJECT_ID not set in environment")
        sys.exit(1)
    
    print(f"🚀 Setting up Vector Search for project: {project_id}")
    print(f"📍 Location: {location}")
    print(f"📊 Index name: {index_name}")
    print(f"🔗 Endpoint name: {endpoint_name}")
    
    try:
        # Initialize Vertex AI
        if service_account_file and os.path.exists(service_account_file):
            credentials = service_account.Credentials.from_service_account_file(
                service_account_file
            )
            aiplatform.init(project=project_id, location=location, credentials=credentials)
        else:
            aiplatform.init(project=project_id, location=location)
        
        print("✅ Vertex AI initialized")
        
        # Check if index already exists
        print("🔍 Checking for existing index...")
        indexes = aiplatform.MatchingEngineIndex.list()
        existing_index = None
        
        for index in indexes:
            if index.display_name == index_name:
                existing_index = index
                print(f"✅ Found existing index: {index.resource_name}")
                break
        
        # Create index if it doesn't exist
        if not existing_index:
            print("📊 Creating Vector Search index...")
            print("⏳ This may take 20-30 minutes...")
            
            # Create a GCS bucket for the index data
            bucket_name = f"{project_id}-vector-data-central"
            print(f"📦 Using GCS bucket: gs://{bucket_name}")
            
            try:
                index = aiplatform.MatchingEngineIndex.create_tree_ah_index(
                    display_name=index_name,
                    contents_delta_uri=f"gs://{bucket_name}",
                    dimensions=768,  # text-embedding-004 dimensions
                    approximate_neighbors_count=150,
                    distance_measure_type="DOT_PRODUCT_DISTANCE",
                    leaf_node_embedding_count=500,
                    leaf_nodes_to_search_percent=7,
                    description="Vector index for AI Document QA Agent"
                )
                print(f"✅ Index created: {index.resource_name}")
                existing_index = index
            except Exception as e:
                print(f"❌ Error creating index: {str(e)}")
                print("💡 You may need to create this manually in the Google Cloud Console")
                print("   Go to Vertex AI > Vector Search > Create Index")
                return False
        
        # Check if endpoint already exists
        print("🔍 Checking for existing endpoint...")
        endpoints = aiplatform.MatchingEngineIndexEndpoint.list()
        existing_endpoint = None
        
        for endpoint in endpoints:
            if endpoint.display_name == endpoint_name:
                existing_endpoint = endpoint
                print(f"✅ Found existing endpoint: {endpoint.resource_name}")
                break
        
        # Create endpoint if it doesn't exist
        if not existing_endpoint:
            print("🔗 Creating Vector Search endpoint...")
            
            try:
                endpoint = aiplatform.MatchingEngineIndexEndpoint.create(
                    display_name=endpoint_name,
                    description="Vector endpoint for AI Document QA Agent",
                    public_endpoint_enabled=True
                )
                print(f"✅ Endpoint created: {endpoint.resource_name}")
                existing_endpoint = endpoint
            except Exception as e:
                print(f"❌ Error creating endpoint: {str(e)}")
                print("💡 You may need to create this manually in the Google Cloud Console")
                return False
        
        # Deploy index to endpoint if not already deployed
        print("🚀 Checking index deployment...")
        
        try:
            # Check if index is already deployed
            deployed_indexes = existing_endpoint.list_deployed_indexes()
            index_deployed = any(
                deployed.index == existing_index.resource_name 
                for deployed in deployed_indexes
            )
            
            if not index_deployed:
                print("📤 Deploying index to endpoint...")
                print("⏳ This may take 10-15 minutes...")
                
                existing_endpoint.deploy_index(
                    index=existing_index,
                    deployed_index_id=index_name.replace("-", "_"),
                    display_name=f"{index_name}-deployment",
                    machine_type="e2-standard-2",
                    min_replica_count=1,
                    max_replica_count=2
                )
                print("✅ Index deployed to endpoint")
            else:
                print("✅ Index already deployed to endpoint")
                
        except Exception as e:
            print(f"❌ Error deploying index: {str(e)}")
            print("💡 You may need to deploy this manually in the Google Cloud Console")
            print("   Go to Vertex AI > Vector Search > Select your index > Deploy")
            return False
        
        print("\n🎉 Vector Search setup completed successfully!")
        print(f"📊 Index: {existing_index.resource_name}")
        print(f"🔗 Endpoint: {existing_endpoint.resource_name}")
        print("\n💡 Next steps:")
        print("1. Update your .env file with the index and endpoint names")
        print("2. Deploy your application to Cloud Run")
        print("3. Upload documents and test the system")
        
        return True
        
    except Exception as e:
        print(f"❌ Error setting up Vector Search: {str(e)}")
        return False

if __name__ == "__main__":
    success = setup_vector_search()
    sys.exit(0 if success else 1)