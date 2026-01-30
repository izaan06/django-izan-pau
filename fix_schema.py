import pymongo

def fix_mongo_schema():
    print("Connecting to MongoDB...")
    client = pymongo.MongoClient("mongodb://localhost:27017")
    db = client["streamevents_db"]
    collection = db["events_event"]
    
    print("Updating events to include 'embedding', 'embedding_model', and 'embedding_updated_at'...")
    result = collection.update_many(
        {"embedding": {"$exists": False}},
        {"$set": {
            "embedding": None,
            "embedding_model": None,
            "embedding_updated_at": None
        }}
    )
    
    print(f"Matched: {result.matched_count}, Modified: {result.modified_count}")
    print("Done.")

if __name__ == "__main__":
    fix_mongo_schema()
