Certainly! Here is the backend documentation for your **Hive Data Marketplace** project in markdown format:

---

# Hive Data Marketplace Backend Documentation

## Overview

The Hive Data Marketplace enables users to create data contribution campaigns where contributors can submit data and get paid when their contributions are sold. The platform facilitates the creation, management, and sale of data campaigns while ensuring contributors are compensated for their valuable data. The system also includes a marketplace where campaign creators can list their campaigns once the required data is collected and verified.

## Table of Contents

- [Overview](#overview)
- [API Endpoints](#api-endpoints)
  - [Campaign Endpoints](#campaign-endpoints)
  - [Contribution Endpoints](#contribution-endpoints)
  - [Payment Endpoints](#payment-endpoints)
  - [Marketplace Endpoints](#marketplace-endpoints)
- [Models](#models)
  - [Campaign Model](#campaign-model)
  - [Contribution Model](#contribution-model)
  - [Payment Model](#payment-model)
  - [Marketplace Listing Model](#marketplace-listing-model)
- [Database Integration](#database-integration)
- [Authentication and Authorization](#authentication-and-authorization)
- [Running the Project](#running-the-project)

---

## API Endpoints

### Campaign Endpoints

#### `POST /campaigns`
**Description**: Allows a user to create a new data contribution campaign.

**Request Body**:
```json
{
  "onchain_campaign_id": "unique-campaign-id",
  "title": "Campaign Title",
  "description": "Campaign Description",
  "data_requirements": "Data requirements for contributors",
  "quality_criteria": "Quality check criteria for submissions",
  "unit_price": 100,
  "total_budget": 5000,
  "min_data_count": 10,
  "max_data_count": 100,
  "expiration": 1628505600,
  "metadata_uri": "ipfs://metadata-link",
  "transaction_hash": "0xabc123...",
  "platform_fee": 5
}
```

**Response**:
```json
{
  "campaign_id": "unique-campaign-id",
  "title": "Campaign Title",
  "description": "Campaign Description",
  "data_requirements": "Data requirements for contributors",
  "quality_criteria": "Quality check criteria for submissions",
  "unit_price": 100,
  "total_budget": 5000,
  "min_data_count": 10,
  "max_data_count": 100,
  "expiration": 1628505600,
  "metadata_uri": "ipfs://metadata-link",
  "transaction_hash": "0xabc123...",
  "platform_fee": 5,
  "is_active": true,
  "created_at": "2025-01-01T12:00:00Z"
}
```

#### `GET /campaigns/{campaign_id}`
**Description**: Retrieves details for a specific campaign.

**Response**:
```json
{
  "campaign_id": "unique-campaign-id",
  "title": "Campaign Title",
  "description": "Campaign Description",
  "data_requirements": "Data requirements for contributors",
  "quality_criteria": "Quality check criteria for submissions",
  "unit_price": 100,
  "total_budget": 5000,
  "min_data_count": 10,
  "max_data_count": 100,
  "expiration": 1628505600,
  "metadata_uri": "ipfs://metadata-link",
  "is_active": true,
  "created_at": "2025-01-01T12:00:00Z",
  "transaction_hash": "0xabc123...",
  "platform_fee": 5
}
```

#### `GET /campaigns/active`
**Description**: Lists all active campaigns.

**Response**:
```json
[
  {
    "campaign_id": "unique-campaign-id",
    "title": "Campaign Title",
    "description": "Campaign Description",
    "is_active": true,
    "expiration": 1628505600
  }
]
```

---

### Contribution Endpoints

#### `POST /contributions`
**Description**: Submits a new contribution to a campaign.

**Request Body**:
```json
{
  "contribution_id": "unique-contribution-id",
  "campaign_id": "unique-campaign-id",
  "contributor": "0x1234567890abcdef",
  "data_url": "ipfs://data-url",
  "data_hash": "0xabcdef1234567890",
  "signature": "0xdeadbeef12345678",
  "transaction_hash": "0xxyz987654321",
  "quality_score": 85
}
```

**Response**:
```json
{
  "contribution_id": "unique-contribution-id",
  "campaign_id": "unique-campaign-id",
  "contributor": "0x1234567890abcdef",
  "data_url": "ipfs://data-url",
  "data_hash": "0xabcdef1234567890",
  "signature": "0xdeadbeef12345678",
  "transaction_hash": "0xxyz987654321",
  "quality_score": 85,
  "is_verified": false,
  "reward_claimed": false,
  "created_at": "2025-01-05T12:30:00Z"
}
```

#### `GET /contributions`
**Description**: Fetches a list of contributions by campaign or contributor.

**Query Parameters**:
- `campaign_id` (optional): Filter by campaign ID.
- `contributor` (optional): Filter by contributor.

**Response**:
```json
{
  "contributions": [
    {
      "contribution_id": "unique-contribution-id",
      "campaign_id": "unique-campaign-id",
      "contributor": "0x1234567890abcdef",
      "data_url": "ipfs://data-url",
      "data_hash": "0xabcdef1234567890",
      "is_verified": false,
      "reward_claimed": false,
      "created_at": "2025-01-05T12:30:00Z"
    }
  ]
}
```

---

### Payment Endpoints

#### `POST /payments`
**Description**: Processes payment to a contributor when their data is sold.

**Request Body**:
```json
{
  "contributor": "0x1234567890abcdef",
  "campaign_id": "unique-campaign-id",
  "amount": 100,
  "payment_method": "bank_transfer"
}
```

**Response**:
```json
{
  "status": "success",
  "message": "Payment processed successfully.",
  "transaction_hash": "0xpaymenttxhash"
}
```

---

### Marketplace Endpoints

#### `GET /marketplace`
**Description**: Lists campaigns that are ready to be sold or accessed by buyers.

**Response**:
```json
[
  {
    "campaign_id": "unique-campaign-id",
    "title": "Campaign Title",
    "description": "Campaign Description",
    "data_requirements": "Data requirements for contributors",
    "price": 5000
  }
]
```

#### `POST /marketplace/sell`
**Description**: Puts a completed campaign on sale for buyers to purchase.

**Request Body**:
```json
{
  "campaign_id": "unique-campaign-id",
  "price": 5000,
  "sale_start": 1628505600,
  "sale_end": 1628509200
}
```

**Response**:
```json
{
  "status": "success",
  "message": "Campaign successfully listed for sale.",
  "transaction_hash": "0xmarketplacetxhash"
}
```

---

## Models

### Campaign Model
Represents a campaign where data collection occurs. Includes fields such as `title`, `description`, `unit_price`, and `platform_fee`.

### Contribution Model
Represents a data contribution to a campaign, including contributor information and the data URL.

### Payment Model
Represents the payment details when a contributor is compensated for their contribution.

### Marketplace Listing Model
Represents a listing for a completed campaign that is available for sale.

---

## Database Integration

- **SQLAlchemy**: Used for modeling the `Campaign`, `Contribution`, `Payment`, and `MarketplaceListing` entities.
- **PostgreSQL**: The preferred database backend for scalability and reliability.

---

## Authentication and Authorization

- **JWT Authentication**: Secure access to API endpoints is handled using JSON Web Tokens (JWT). Each user will authenticate using their credentials and receive a token to access protected routes.
- **Role-based Access**: Ensure that only campaign creators and admins can manage campaigns and process payments.

---

## Running the Project

1. **Set Up Environment**:
   - Install dependencies with `pip install -r requirements.txt`.

2. **Configure Database**:
   - Ensure that your PostgreSQL database is configured and running.
   - Apply database migrations using Alembic: `alembic upgrade head`.

3. **Run FastAPI Server**:
   - Use `uvicorn` to start the server:
     ```bash
     uvicorn app.main:app --reload
     ```

4. **Access API Docs**:
   - Visit `http://127.0.0.1:8000/docs` to explore the automatically generated Swagger UI for the API.

---

## Conclusion

This backend system powers the Hive Data Marketplace, allowing users to create campaigns, contribute data, and receive compensation when the campaign’s data is sold. It integrates several features, including campaign management, contribution tracking, and a marketplace for data transactions. The system uses FastAPI, SQLAlchemy, and PostgreSQL for fast and scalable operations.

Let me know if you'd like further details or adjustments to the documentation!

---