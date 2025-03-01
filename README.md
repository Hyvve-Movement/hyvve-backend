# Hyvve Backend - Data Collection Platform

## Overview

Hyvve is a data collection platform designed to help users create, manage, and analyze campaigns for various types of data contributions. The backend services power the management of campaigns, contributions, and analytics. **Importantly, our backend acts as a mirror for our onchain data—enhancing performance and enabling complex analytical computations that would otherwise be expensive if executed solely via RPCs.** Despite these optimizations, the Movement chain remains the single source of truth.

## Key Components

### 1. **Campaign Management**
   - **Campaign**: Represents a data collection initiative. Each campaign is defined by parameters such as title, description, data requirements, and budget.
   - **Contribution**: Represents a user's submission to a campaign, which can include text, documents, images, and other data.
   - **Activity**: Tracks campaign and contribution activity. Activity levels are updated based on contribution data and tracked separately for each contribution and overall campaign.

### 2. **Contributions Verification**
   - Users can upload various types of documents (text, images, etc.), which are then processed and verified using AI for accuracy and relevance.
   - The verification process is cached and uses a fairness adjustment to ensure that scores are unbiased.
   - The verification score is stored in Redis for fast access and efficiency.

### 3. **Analytics**
   - The system provides analytics for campaigns and contributors, including:
     - Total contributions
     - Average cost per submission
     - Peak activity hours
     - Top contributors
     - Weekly analytics (submissions and quality score)
     - Leaderboards for global contributions and campaign creators

### 4. **Task Scheduling**
   - **Celery Task**: A Celery task is set up to periodically mark campaigns whose expiration timestamp has passed as inactive. This is executed every 30 minutes.

---

## API Endpoints

### Campaigns

#### **Create a Campaign**
   - **POST** `/create-campaigns`
   - Creates a new campaign with the provided details.
   - **Request Body**: `CampaignCreate` schema
   - **Response**: Returns a serialized campaign with its details.

#### **Get All Campaigns**
   - **GET** `/all`
   - Retrieves all campaigns in the system, including a count of contributions and unique contributors.
   - **Response**: List of campaigns with their respective contribution and unique contributor counts.

#### **Get Campaign by Creator Wallet Address**
   - **GET** `/{creator_wallet_address}/campaigns/created`
   - Retrieves all campaigns created by a specific wallet address.
   - **Response**: List of campaigns created by the specified wallet.

#### **Get Active Campaigns**
   - **GET** `/active`
   - Retrieves all active campaigns, including contribution counts and unique contributor counts.
   - **Response**: List of active campaigns.

#### **Get Campaign by Onchain ID**
   - **GET** `/{onchain_campaign_id}`
   - Retrieves campaign details using the onchain campaign ID.
   - **Response**: Serialized campaign with its details.

### Contributions

#### **Submit Contribution**
   - **POST** `/submit-contributions`
   - Submits a contribution to a campaign.
   - **Request Body**: `ContributionCreate` schema
   - **Response**: Returns a serialized contribution with its quality score mapped.

#### **Get Contributions by Campaign ID**
   - **GET** `/get-contributions/{onchain_campaign_id}`
   - Retrieves all contributions for a given campaign.
   - **Response**: List of contributions with mapped quality scores.

### Analytics

#### **Get Campaign Analytics**
   - **GET** `/analytics/campaign/{onchain_campaign_id}`
   - Retrieves analytics for a given campaign, including total contributions, average cost per submission, peak activity hours, top contributors, unique contributor count, and total rewards paid.
   - **Response**: Campaign analytics.

#### **Get Weekly Campaign Analytics**
   - **GET** `/analytics/campaign/{onchain_campaign_id}/weekly`
   - Retrieves weekly analytics for a campaign, including total submissions for each day and average quality score.
   - **Response**: Weekly submission and quality score data.

#### **Get Wallet Analytics**
   - **GET** `/analytics/wallet/{wallet_address}`
   - Retrieves analytics for a given contributor (wallet address), including total submissions, average reputation score, and campaigns created or contributed to.
   - **Response**: Contributor analytics.

#### **Get Global Leaderboard for Contributors**
   - **GET** `/analytics/leaderboard/global/contributors`
   - Retrieves the top 5 global contributors based on submission count, AI verification score, and total amount earned.
   - **Response**: List of top contributors.

#### **Get Global Leaderboard for Campaign Creators**
   - **GET** `/analytics/leaderboard/global/creators`
   - Retrieves the top 5 campaign creators based on the number of campaigns created, amount spent, and reputation score.
   - **Response**: List of top campaign creators.

### Contribution Activity

#### **Get Contribution Activity**
   - **GET** `/analytics/contribution/{contribution_id}/activity`
   - Retrieves the activity level of a specific contribution.
   - **Response**: Contribution activity details.

### Campaign Expiration Task

#### **Mark Expired Campaigns Inactive**
   - **Celery Task**: Periodically runs every 30 minutes to mark campaigns whose expiration timestamp has passed as inactive.
   - **Implementation**: Uses Celery and Redis for task scheduling.

---

## Data Models

### **Campaign**
   - `id`: Unique identifier (UUID)
   - `onchain_campaign_id`: ID linked to the campaign on the blockchain
   - `creator_wallet_address`: Wallet address of the campaign creator
   - `title`: Title of the campaign
   - `description`: Description of the campaign
   - `campaign_type`: Type of campaign (e.g., data collection, feedback)
   - `data_requirements`: What data is needed for the campaign
   - `quality_criteria`: Criteria for evaluating contributions
   - `unit_price`: Price per contribution
   - `total_budget`: Total budget for the campaign
   - `min_data_count`: Minimum number of contributions required
   - `max_data_count`: Maximum number of contributions allowed
   - `expiration`: Expiration timestamp (Unix format)
   - `metadata_uri`: URI for metadata associated with the campaign
   - `transaction_hash`: Hash of the transaction that created the campaign
   - `platform_fee`: Platform fee charged for each contribution
   - `is_premium`: Whether the campaign is premium or not
   - `is_active`: Whether the campaign is active or expired
   - `created_at`: Timestamp of campaign creation

### **Contribution**
   - `contribution_id`: Unique identifier (UUID)
   - `onchain_contribution_id`: Onchain ID for the contribution
   - `campaign_id`: Linked campaign ID
   - `contributor`: Wallet address of the contributor
   - `data_url`: URL for the contribution data
   - `transaction_hash`: Transaction hash associated with the contribution
   - `ai_verification_score`: AI verification score for the contribution
   - `reputation_score`: Reputation score of the contributor
   - `quality_score`: Quality score of the contribution
   - `is_verified`: Whether the contribution is verified
   - `reward_claimed`: Whether the reward has been claimed
   - `created_at`: Timestamp of contribution submission

### **Activity**
   - `id`: Unique identifier (integer)
   - `campaign_id`: Linked campaign ID
   - `contribution_id`: Linked contribution ID
   - `timestamp`: Timestamp of the activity
   - `activity_level`: Activity level score (0-100)

---

## Task Scheduling with Celery

Hyvve uses Celery for background task processing. The task **`mark_expired_campaigns_inactive`** runs every 30 minutes to mark campaigns as inactive when their expiration date has passed.

---

*Note: While our backend optimizes performance and analytical computations by mirroring onchain data, it does not alter the integrity or role of blockchain data. The Movement chain remains the single source of truth for all onchain information.*
