import asyncio
import asyncpg
import random
import uuid
from datetime import datetime, timezone
import os
from faker import Faker
from sklearn.ensemble import IsolationForest
import numpy as np

# Supabase remote connection string
DB_CON_STR = "postgresql://postgres.uwsaqphlcrhiliklkwmb:o6UDgrZp0Y7f8ERE@aws-1-ap-southeast-2.pooler.supabase.com:5432/postgres?sslmode=require"

fake = Faker()

# Initialize a basic ML Model for our Live Agent
# We'll use IsolationForest and "warm it up" with some normal baseline data
print("🤖 Initializing ML Anomaly Detection Agent...")
iso_forest = IsolationForest(contamination=0.05, random_state=42)

# Normal data pattern: small amounts, local IPs
baseline_data = np.array([[random.uniform(5.0, 150.0), 0] for _ in range(100)]) 
iso_forest.fit(baseline_data)

async def generate_and_insert(pool):
    # 1. Generate realistic transaction
    is_fraud_attempt = random.random() < 0.2  # 20% chance to simulate a fraud attempt
    
    ref = f"TXN-{random.randint(1000000, 9999999)}"
    currency = "USD"
    account_id = f"ACC-{random.randint(10000, 99999)}"
    
    if is_fraud_attempt:
        amount = round(random.uniform(5000.0, 45000.0), 2)
        location = fake.country()
        merchant = "Crypto.com"
        device = "Unknown Android"
        merchant_category = "Cryptocurrency"
        is_foreign = 1 # feature for ML
    else:
        amount = round(random.uniform(5.0, 150.0), 2)
        location = "United States"
        merchant = fake.company()
        device = "iPhone 13"
        merchant_category = "Retail"
        is_foreign = 0 # feature for ML

    # 2. Score with ML Model
    feature_vector = np.array([[amount, is_foreign]])
    raw_score = iso_forest.score_samples(feature_vector)[0]
    
    if is_fraud_attempt:
        # Guarantee a score above the 0.8 threshold for demonstration purposes
        normalized_if_score = round(random.uniform(0.85, 0.98), 2)
        lstm_score = round(random.uniform(0.82, 0.99), 2)
    else:
        # Guarantee a normal score below 0.8
        normalized_if_score = round(random.uniform(0.1, 0.5), 2)
        lstm_score = round(random.uniform(0.1, 0.5), 2)
    
    # Calculate final ensemble score
    ensemble_score = round((normalized_if_score * 0.6) + (lstm_score * 0.4), 2)

    # 3. Generate AI Explanation if highly anomalous
    ai_explanation = ""
    status = "unreviewed"
    if ensemble_score > 0.8:
        # We simulate what an LLM would output based on the grounded data
        ai_explanation = f"CRITICAL: High-value transaction of ${amount:,.2f} initiated from a high-risk category ({merchant_category}) in a foreign location ({location}). Device is unrecognised ({device})."
    else:
        status = "cleared" # Automatically clear low-risk items

    confidence_score = round(random.uniform(0.85, 0.99), 2)
    flagged_at = datetime.now(timezone.utc)

    # 4. Insert into database ONLY if flagged (since this DB is the review queue)
    if ensemble_score > 0.8:
        async with pool.acquire() as conn:
            await conn.execute('''
                INSERT INTO transactions 
                (id, transaction_ref, amount, currency, location, merchant, device, 
                merchant_category, account_id, model_source, if_score, lstm_score, 
                ensemble_score, confidence_score, ai_explanation, status, flagged_at)
                VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13, $14, $15, $16, $17)
            ''', 
            uuid.uuid4(), ref, amount, currency, location, merchant, device, 
            merchant_category, account_id, "ensemble", 
            round(normalized_if_score, 2), round(lstm_score, 2), ensemble_score, 
            confidence_score, ai_explanation, status, flagged_at)
        print(f"[{datetime.now().strftime('%H:%M:%S')}] 🚨 FLAGGED & INJECTED: {ref} | Amount: ${amount:,.2f} | Score: {ensemble_score}")
    else:
        print(f"[{datetime.now().strftime('%H:%M:%S')}] ✅ Normal (Ignored): {ref} | Amount: ${amount:,.2f} | Score: {ensemble_score}")


async def main():
    print("🔌 Connecting to local FraudOS Database...")
    pool = await asyncpg.create_pool(
        dsn=DB_CON_STR,
        server_settings={'search_path': 'rahul, public'}
    )
    
    print("🚀 AI Data Agent is LIVE! Injecting a new transaction every 10 seconds...")
    print("Keep your FraudOS Dashboard open to watch them appear in real-time!\n")
    
    try:
        while True:
            await generate_and_insert(pool)
            await asyncio.sleep(5) # Inject every 5 seconds
    except KeyboardInterrupt:
        print("\n🛑 AI Data Agent stopped.")
    finally:
        await pool.close()

if __name__ == "__main__":
    asyncio.run(main())
